"""Text chunking and streaming synthesis for faster TTS feedback.

This module provides chunking functionality to split text into
manageable pieces, synthesize audio incrementally, and enable
streaming playback.
"""

import logging
import queue
import re
import threading
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from src import config
from src.tts.synthesizer import PiperSynthesizer

logger = logging.getLogger(__name__)


class SynthesisStatus(Enum):
    """Status of audio chunk synthesis."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AudioChunk:
    """Represents a chunk of text and its synthesized audio.

    Attributes:
        chunk_index: Sequential index of this chunk (0-based)
        text_content: The text content for this chunk
        audio_data: Synthesized audio bytes (None if not yet synthesized)
        duration_ms: Duration of the audio in milliseconds
        synthesis_status: Current status of synthesis for this chunk
    """

    chunk_index: int
    text_content: str
    audio_data: Optional[bytes] = None
    duration_ms: int = 0
    synthesis_status: SynthesisStatus = SynthesisStatus.PENDING


class ChunkSynthesizer:
    """Manages text chunking and streaming synthesis for faster TTS.

    This class splits large text into chunks (~150 words), synthesizes the
    first chunk immediately (<3s), and synthesizes remaining chunks in the
    background for seamless playback.

    Attributes:
        synthesizer: PiperSynthesizer instance for audio generation
        speed: Speech speed multiplier
        chunks: List of all text chunks
        chunk_buffer: Queue of synthesized chunks ready for playback
        shutdown_event: Event to signal worker threads to stop
    """

    DEFAULT_CHUNK_SIZE = 150  # Target words per chunk
    MAX_BUFFER_SIZE = 10  # Maximum chunks to buffer

    def __init__(
        self, voice: str = "en_US-libritts-high", speed: float = 1.0
    ):
        """Initialize ChunkSynthesizer.

        Args:
            voice: Voice model to use for synthesis
            speed: Speech speed multiplier (0.5-2.0)
        """
        self.synthesizer = PiperSynthesizer(voice=voice)
        self.speed = speed
        self.chunks: List[AudioChunk] = []
        self.chunk_buffer: List[AudioChunk] = []
        self.shutdown_event = threading.Event()
        self._worker_threads: List[threading.Thread] = []
        self._lock = threading.Lock()
        logger.info(
            f"ChunkSynthesizer initialized (voice={voice}, speed={speed})"
        )

    def prepare_chunks(self, text: str) -> None:
        """Split text into chunks and prepare for synthesis.

        Args:
            text: Full text to chunk

        Raises:
            ValueError: If text is empty
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        logger.info(f"Preparing chunks for {len(text)} characters")

        # Split into sentences
        sentences = self._split_into_sentences(text)

        # Group sentences into chunks
        chunk_texts = self._group_sentences_into_chunks(sentences)

        # Create AudioChunk objects
        self.chunks = [
            AudioChunk(
                chunk_index=i,
                text_content=chunk_text,
                audio_data=None,
                duration_ms=0,
                synthesis_status=SynthesisStatus.PENDING,
            )
            for i, chunk_text in enumerate(chunk_texts)
        ]

        logger.info(f"Created {len(self.chunks)} chunks")

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex.

        Args:
            text: Text to split

        Returns:
            List of sentence strings
        """
        # Split on sentence boundaries (.!?) followed by whitespace
        pattern = r'(?<=[.!?])\s+'
        sentences = re.split(pattern, text)
        return [s.strip() for s in sentences if s.strip()]

    def _group_sentences_into_chunks(
        self, sentences: List[str]
    ) -> List[str]:
        """Group sentences into chunks of target word count.

        Args:
            sentences: List of sentence strings

        Returns:
            List of chunk texts
        """
        chunks = []
        current_chunk = []
        current_word_count = 0

        for sentence in sentences:
            sentence_words = len(sentence.split())

            # If adding this sentence exceeds target, start new chunk
            if (
                current_word_count > 0
                and current_word_count + sentence_words
                > self.DEFAULT_CHUNK_SIZE
            ):
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_word_count = sentence_words
            else:
                current_chunk.append(sentence)
                current_word_count += sentence_words

        # Add final chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def synthesize_first_chunk(self) -> None:
        """Synthesize the first chunk immediately (blocking).

        This method blocks until the first chunk is synthesized,
        ensuring fast time-to-first-audio.

        Raises:
            RuntimeError: If no chunks prepared
        """
        if not self.chunks:
            raise RuntimeError("No chunks prepared. Call prepare_chunks() first")

        logger.info("Synthesizing first chunk (blocking)...")

        first_chunk = self.chunks[0]
        first_chunk.synthesis_status = SynthesisStatus.IN_PROGRESS

        try:
            audio_data = self.synthesizer.synthesize(
                first_chunk.text_content, speed=self.speed
            )
            first_chunk.audio_data = audio_data
            first_chunk.synthesis_status = SynthesisStatus.COMPLETED
            logger.info(
                f"First chunk synthesized ({len(audio_data)} bytes)"
            )
        except Exception as e:
            logger.error(f"Failed to synthesize first chunk: {e}")
            first_chunk.synthesis_status = SynthesisStatus.FAILED
            raise

    def start_background_synthesis(self, num_workers: int = 2) -> None:
        """Start background synthesis of remaining chunks.

        Args:
            num_workers: Number of worker threads to spawn
        """
        if len(self.chunks) <= 1:
            logger.info("Only one chunk, no background synthesis needed")
            return

        logger.info(f"Starting {num_workers} background synthesis workers")

        for i in range(num_workers):
            worker = threading.Thread(
                target=self._synthesis_worker_thread,
                args=(i,),
                daemon=True,
            )
            worker.start()
            self._worker_threads.append(worker)

    def _synthesis_worker_thread(self, worker_id: int) -> None:
        """Background worker thread for synthesizing chunks.

        Args:
            worker_id: ID of this worker thread
        """
        logger.debug(f"Worker {worker_id} started")

        # Start from chunk 1 (chunk 0 already synthesized)
        chunk_index = 1

        while not self.shutdown_event.is_set():
            # Find next pending chunk
            with self._lock:
                pending_chunk = None
                for i in range(chunk_index, len(self.chunks)):
                    if (
                        self.chunks[i].synthesis_status
                        == SynthesisStatus.PENDING
                    ):
                        pending_chunk = self.chunks[i]
                        pending_chunk.synthesis_status = (
                            SynthesisStatus.IN_PROGRESS
                        )
                        chunk_index = i + 1
                        break

                if pending_chunk is None:
                    # No more chunks to synthesize
                    break

            # Synthesize chunk (outside lock)
            try:
                audio_data = self.synthesizer.synthesize(
                    pending_chunk.text_content, speed=self.speed
                )

                with self._lock:
                    pending_chunk.audio_data = audio_data
                    pending_chunk.synthesis_status = (
                        SynthesisStatus.COMPLETED
                    )

                    # Add to buffer if space available
                    if len(self.chunk_buffer) < self.MAX_BUFFER_SIZE:
                        self.chunk_buffer.append(pending_chunk)

                logger.debug(
                    f"Worker {worker_id} synthesized chunk "
                    f"{pending_chunk.chunk_index}"
                )

            except Exception as e:
                logger.error(
                    f"Worker {worker_id} failed to synthesize chunk "
                    f"{pending_chunk.chunk_index}: {e}"
                )
                with self._lock:
                    pending_chunk.synthesis_status = SynthesisStatus.FAILED

        logger.debug(f"Worker {worker_id} stopped")

    def get_next_chunk(self) -> Optional[AudioChunk]:
        """Get the next synthesized chunk from buffer.

        Returns:
            Next AudioChunk, or None if buffer is empty
        """
        with self._lock:
            if self.chunk_buffer:
                return self.chunk_buffer.pop(0)
            return None

    def synthesize_chunk_on_demand(self, chunk_index: int) -> None:
        """Synthesize a specific chunk on-demand (e.g., for seeking).

        Args:
            chunk_index: Index of chunk to synthesize

        Raises:
            IndexError: If chunk_index is out of range
        """
        if chunk_index < 0 or chunk_index >= len(self.chunks):
            raise IndexError(f"Chunk index {chunk_index} out of range")

        chunk = self.chunks[chunk_index]

        if chunk.synthesis_status == SynthesisStatus.COMPLETED:
            logger.debug(f"Chunk {chunk_index} already synthesized")
            return

        logger.info(f"Synthesizing chunk {chunk_index} on-demand")

        chunk.synthesis_status = SynthesisStatus.IN_PROGRESS

        try:
            audio_data = self.synthesizer.synthesize(
                chunk.text_content, speed=self.speed
            )
            chunk.audio_data = audio_data
            chunk.synthesis_status = SynthesisStatus.COMPLETED
            logger.info(f"Chunk {chunk_index} synthesized on-demand")
        except Exception as e:
            logger.error(
                f"Failed to synthesize chunk {chunk_index}: {e}"
            )
            chunk.synthesis_status = SynthesisStatus.FAILED
            raise

    def stop(self) -> None:
        """Stop background synthesis and clean up."""
        logger.info("Stopping ChunkSynthesizer")

        # Signal shutdown
        self.shutdown_event.set()

        # Wait for worker threads
        for worker in self._worker_threads:
            worker.join(timeout=1.0)

        # Clear buffer
        with self._lock:
            self.chunk_buffer.clear()

        logger.info("ChunkSynthesizer stopped")

    def get_chunk_count(self) -> int:
        """Get the total number of chunks.

        Returns:
            Total chunk count
        """
        return len(self.chunks)

    def get_buffer_status(self) -> dict:
        """Get current buffer status.

        Returns:
            Dictionary with buffered count and total count
        """
        with self._lock:
            return {
                "buffered": len(self.chunk_buffer),
                "total": len(self.chunks),
            }
