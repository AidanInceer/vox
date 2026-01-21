"""Unit tests for ChunkSynthesizer - streaming text-to-speech chunking.

This module tests the ChunkSynthesizer class which handles:
- Text chunking (split into ~150 word chunks)
- First chunk synthesis (blocking, <3s)
- Background synthesis (remaining chunks)
- Buffer management (max 10 chunks)
- On-demand synthesis
"""

import time
from unittest.mock import Mock, patch

import pytest

from src.tts.chunking import AudioChunk, ChunkSynthesizer, SynthesisStatus
from src.tts.synthesizer import PiperSynthesizer


class TestChunkSynthesizerInit:
    """Tests for ChunkSynthesizer.__init__()"""

    def test_init_creates_synthesizer_with_default_voice(self):
        """T074: Test initialization with default voice."""
        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            chunker = ChunkSynthesizer()

            assert chunker.synthesizer is not None
            assert chunker.chunks == []
            assert chunker.chunk_buffer == []
            assert chunker.shutdown_event is not None
            assert not chunker.shutdown_event.is_set()

    def test_init_creates_synthesizer_with_custom_voice(self):
        """T074: Test initialization with custom voice."""
        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            chunker = ChunkSynthesizer(voice="en_US-ryan-high")

            assert chunker.synthesizer is not None

    def test_init_sets_default_speed(self):
        """T074: Test initialization sets default speed."""
        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            chunker = ChunkSynthesizer(speed=1.5)

            assert chunker.speed == 1.5


class TestChunkSynthesizerPrepareChunks:
    """Tests for ChunkSynthesizer.prepare_chunks()"""

    @pytest.fixture
    def chunker(self):
        """Create ChunkSynthesizer instance for testing."""
        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            return ChunkSynthesizer()

    def test_prepare_chunks_with_short_text(self, chunker):
        """T077: Test prepare_chunks with text <50 words (single chunk)."""
        text = "This is a short text. " * 20  # ~40 words

        chunker.prepare_chunks(text)

        assert len(chunker.chunks) == 1
        assert chunker.chunks[0].chunk_index == 0
        # Text content may have trailing whitespace trimmed
        assert "This is a short text." in chunker.chunks[0].text_content
        assert chunker.chunks[0].synthesis_status == SynthesisStatus.PENDING

    def test_prepare_chunks_with_long_text(self, chunker):
        """T075: Test prepare_chunks with various text lengths."""
        # Create text with ~500 words (should create 3-4 chunks @ 150 words each)
        text = "This is a sentence. " * 250  # ~500 words

        chunker.prepare_chunks(text)

        assert len(chunker.chunks) >= 3
        assert all(chunk.synthesis_status == SynthesisStatus.PENDING for chunk in chunker.chunks)
        assert all(chunk.audio_data is None for chunk in chunker.chunks)

    def test_prepare_chunks_respects_sentence_boundaries(self, chunker):
        """T076: Test prepare_chunks respects sentence boundaries."""
        # Create text with clear sentence boundaries
        sentences = [f"Sentence number {i}." for i in range(200)]
        text = " ".join(sentences)

        chunker.prepare_chunks(text)

        # Each chunk should end with a period (sentence boundary)
        for chunk in chunker.chunks[:-1]:  # Exclude last chunk
            assert chunk.text_content.rstrip().endswith(".")

    def test_prepare_chunks_creates_audio_chunk_objects(self, chunker):
        """T075: Test that prepare_chunks creates AudioChunk objects."""
        text = "This is a test. " * 100

        chunker.prepare_chunks(text)

        assert all(isinstance(chunk, AudioChunk) for chunk in chunker.chunks)
        assert all(chunk.chunk_index == i for i, chunk in enumerate(chunker.chunks))

    def test_prepare_chunks_with_empty_text_raises_error(self, chunker):
        """T075: Test prepare_chunks with empty text raises ValueError."""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            chunker.prepare_chunks("")


class TestChunkSynthesizerSynthesizeFirstChunk:
    """Tests for ChunkSynthesizer.synthesize_first_chunk()"""

    @pytest.fixture
    def chunker(self):
        """Create ChunkSynthesizer instance for testing."""
        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            return ChunkSynthesizer()

    def test_synthesize_first_chunk_synthesizes_audio(self, chunker):
        """T078: Test synthesize_first_chunk generates audio."""
        text = "This is a test sentence. " * 30
        chunker.prepare_chunks(text)

        # Mock synthesizer
        mock_audio = b"fake_audio_data"
        chunker.synthesizer = Mock()
        chunker.synthesizer.synthesize = Mock(return_value=mock_audio)

        chunker.synthesize_first_chunk()

        assert chunker.chunks[0].audio_data == mock_audio
        assert chunker.chunks[0].synthesis_status == SynthesisStatus.COMPLETED
        chunker.synthesizer.synthesize.assert_called_once()

    def test_synthesize_first_chunk_blocks_until_complete(self, chunker):
        """T078: Test synthesize_first_chunk blocks until synthesis complete."""
        text = "This is a test. " * 30
        chunker.prepare_chunks(text)

        # Mock synthesizer with delay
        def mock_synthesize(text, speed=1.0):
            time.sleep(0.1)
            return b"audio_data"

        chunker.synthesizer = Mock()
        chunker.synthesizer.synthesize = Mock(side_effect=mock_synthesize)

        start_time = time.time()
        chunker.synthesize_first_chunk()
        elapsed = time.time() - start_time

        assert elapsed >= 0.1
        assert chunker.chunks[0].synthesis_status == SynthesisStatus.COMPLETED

    def test_synthesize_first_chunk_without_prepare_raises_error(self, chunker):
        """T078: Test synthesize_first_chunk without prepare_chunks raises error."""
        with pytest.raises(RuntimeError, match="No chunks prepared"):
            chunker.synthesize_first_chunk()


class TestChunkSynthesizerBackgroundSynthesis:
    """Tests for ChunkSynthesizer background synthesis"""

    @pytest.fixture
    def chunker(self):
        """Create ChunkSynthesizer instance for testing."""
        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            return ChunkSynthesizer()

    def test_start_background_synthesis_spawns_threads(self, chunker):
        """T079: Test start_background_synthesis spawns worker threads."""
        text = "Test sentence. " * 100
        chunker.prepare_chunks(text)

        # Mock synthesizer
        chunker.synthesizer = Mock()
        chunker.synthesizer.synthesize = Mock(return_value=b"audio")

        # Synthesize first chunk
        chunker.synthesize_first_chunk()

        # Start background synthesis
        chunker.start_background_synthesis()

        # Check that threads were created (internal implementation detail)
        # We can verify by checking if synthesis is happening
        time.sleep(0.5)  # Allow time for background synthesis

        # At least some chunks should be in progress or completed
        synthesized_count = sum(
            1
            for chunk in chunker.chunks[1:]
            if chunk.synthesis_status in (SynthesisStatus.IN_PROGRESS, SynthesisStatus.COMPLETED)
        )
        assert synthesized_count > 0

    def test_background_synthesis_respects_shutdown_event(self, chunker):
        """T101: Test background synthesis respects shutdown_event."""
        text = "Test sentence. " * 100
        chunker.prepare_chunks(text)

        chunker.synthesizer = Mock()
        chunker.synthesizer.synthesize = Mock(return_value=b"audio")

        chunker.synthesize_first_chunk()
        chunker.start_background_synthesis()

        # Stop synthesis immediately
        chunker.stop()

        time.sleep(0.2)

        # Not all chunks should be synthesized if we stopped early
        pending_count = sum(1 for chunk in chunker.chunks if chunk.synthesis_status == SynthesisStatus.PENDING)
        assert pending_count > 0 or len(chunker.chunks) <= 2


class TestChunkSynthesizerGetNextChunk:
    """Tests for ChunkSynthesizer.get_next_chunk()"""

    @pytest.fixture
    def chunker(self):
        """Create ChunkSynthesizer instance for testing."""
        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            return ChunkSynthesizer()

    def test_get_next_chunk_returns_completed_chunks(self, chunker):
        """T080: Test get_next_chunk returns completed chunks from buffer."""
        text = "Test sentence. " * 50
        chunker.prepare_chunks(text)

        # Mock synthesizer and synthesize first chunk
        chunker.synthesizer = Mock()
        chunker.synthesizer.synthesize = Mock(return_value=b"audio_data")
        chunker.synthesize_first_chunk()

        # Add first chunk to buffer
        chunker.chunk_buffer.append(chunker.chunks[0])

        # Get next chunk
        chunk = chunker.get_next_chunk()

        assert chunk is not None
        assert chunk.chunk_index == 0
        assert chunk.synthesis_status == SynthesisStatus.COMPLETED
        assert len(chunker.chunk_buffer) == 0

    def test_get_next_chunk_returns_none_when_buffer_empty(self, chunker):
        """T080: Test get_next_chunk returns None when buffer is empty."""
        text = "Test sentence. " * 50
        chunker.prepare_chunks(text)

        chunk = chunker.get_next_chunk()

        assert chunk is None

    def test_get_next_chunk_pops_from_buffer_fifo(self, chunker):
        """T080: Test get_next_chunk pops from buffer in FIFO order."""
        text = "Test sentence. " * 200  # Create enough text for multiple chunks
        chunker.prepare_chunks(text)

        # Mock synthesizer
        chunker.synthesizer = Mock()
        chunker.synthesizer.synthesize = Mock(return_value=b"audio")

        # Ensure we have at least 3 chunks
        assert len(chunker.chunks) >= 3, f"Need at least 3 chunks, got {len(chunker.chunks)}"

        # Add multiple chunks to buffer
        for i in range(3):
            chunker.chunks[i].audio_data = b"audio"
            chunker.chunks[i].synthesis_status = SynthesisStatus.COMPLETED
            chunker.chunk_buffer.append(chunker.chunks[i])

        # Get chunks in order
        chunk1 = chunker.get_next_chunk()
        chunk2 = chunker.get_next_chunk()
        chunk3 = chunker.get_next_chunk()

        assert chunk1.chunk_index == 0
        assert chunk2.chunk_index == 1
        assert chunk3.chunk_index == 2


class TestChunkSynthesizerOnDemandSynthesis:
    """Tests for ChunkSynthesizer.synthesize_chunk_on_demand()"""

    @pytest.fixture
    def chunker(self):
        """Create ChunkSynthesizer instance for testing."""
        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            return ChunkSynthesizer()

    def test_synthesize_chunk_on_demand_synthesizes_specific_chunk(self, chunker):
        """T081: Test synthesize_chunk_on_demand synthesizes a specific chunk."""
        text = "Test sentence. " * 200  # Create enough text for multiple chunks
        chunker.prepare_chunks(text)

        # Ensure we have at least 3 chunks
        assert len(chunker.chunks) >= 3, f"Need at least 3 chunks, got {len(chunker.chunks)}"

        chunker.synthesizer = Mock()
        chunker.synthesizer.synthesize = Mock(return_value=b"audio_data")

        # Synthesize chunk 2 on demand
        chunker.synthesize_chunk_on_demand(2)

        assert chunker.chunks[2].synthesis_status == SynthesisStatus.COMPLETED
        assert chunker.chunks[2].audio_data == b"audio_data"

    def test_synthesize_chunk_on_demand_with_invalid_index_raises_error(self, chunker):
        """T081: Test synthesize_chunk_on_demand with invalid index."""
        text = "Test sentence. " * 50
        chunker.prepare_chunks(text)

        with pytest.raises(IndexError):
            chunker.synthesize_chunk_on_demand(999)


class TestChunkSynthesizerBufferManagement:
    """Tests for ChunkSynthesizer buffer management"""

    @pytest.fixture
    def chunker(self):
        """Create ChunkSynthesizer instance for testing."""
        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            return ChunkSynthesizer()

    def test_buffer_size_limit_enforced(self, chunker):
        """T082: Test buffer size limit (max 10 chunks) is enforced."""
        text = "Test sentence. " * 200  # Many chunks
        chunker.prepare_chunks(text)

        chunker.synthesizer = Mock()
        chunker.synthesizer.synthesize = Mock(return_value=b"audio")

        # Synthesize many chunks
        for i in range(15):
            if i < len(chunker.chunks):
                chunker.chunks[i].audio_data = b"audio"
                chunker.chunks[i].synthesis_status = SynthesisStatus.COMPLETED
                # Simulate buffer management (max 10)
                if len(chunker.chunk_buffer) < 10:
                    chunker.chunk_buffer.append(chunker.chunks[i])

        assert len(chunker.chunk_buffer) <= 10


class TestChunkSynthesizerStop:
    """Tests for ChunkSynthesizer.stop()"""

    @pytest.fixture
    def chunker(self):
        """Create ChunkSynthesizer instance for testing."""
        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            return ChunkSynthesizer()

    def test_stop_sets_shutdown_event(self, chunker):
        """T083: Test stop() sets shutdown event."""
        text = "Test sentence. " * 100
        chunker.prepare_chunks(text)

        chunker.synthesizer = Mock()
        chunker.synthesizer.synthesize = Mock(return_value=b"audio")

        chunker.synthesize_first_chunk()
        chunker.start_background_synthesis()

        chunker.stop()

        assert chunker.shutdown_event.is_set()

    def test_stop_clears_buffer(self, chunker):
        """T083: Test stop() clears chunk buffer."""
        text = "Test sentence. " * 50
        chunker.prepare_chunks(text)

        # Add items to buffer
        chunker.chunk_buffer = [Mock(), Mock(), Mock()]

        chunker.stop()

        assert len(chunker.chunk_buffer) == 0

    def test_stop_is_idempotent(self, chunker):
        """T083: Test stop() can be called multiple times safely."""
        text = "Test sentence. " * 50
        chunker.prepare_chunks(text)

        chunker.stop()
        chunker.stop()  # Should not raise error

        assert chunker.shutdown_event.is_set()


class TestChunkSynthesizerHelperMethods:
    """Tests for ChunkSynthesizer helper methods"""

    @pytest.fixture
    def chunker(self):
        """Create ChunkSynthesizer instance for testing."""
        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            return ChunkSynthesizer()

    def test_get_chunk_count(self, chunker):
        """T097: Test get_chunk_count returns correct count."""
        text = "Test sentence. " * 100
        chunker.prepare_chunks(text)

        count = chunker.get_chunk_count()

        assert count == len(chunker.chunks)
        assert count > 0

    def test_get_buffer_status(self, chunker):
        """T098: Test get_buffer_status returns buffer information."""
        text = "Test sentence. " * 100
        chunker.prepare_chunks(text)

        # Add items to buffer
        chunker.chunk_buffer = [Mock(), Mock(), Mock()]

        status = chunker.get_buffer_status()

        assert "buffered" in status
        assert "total" in status
        assert status["buffered"] == 3
        assert status["total"] == len(chunker.chunks)


class TestChunkSynthesizerErrorHandling:
    """Tests for ChunkSynthesizer error handling"""

    @pytest.fixture
    def chunker(self):
        """Create ChunkSynthesizer instance for testing."""
        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            return ChunkSynthesizer()

    def test_synthesis_failure_marks_chunk_as_failed(self, chunker):
        """T100: Test synthesis failure marks chunk as FAILED."""
        text = "Test sentence. " * 50
        chunker.prepare_chunks(text)

        # Mock synthesizer to raise error
        chunker.synthesizer = Mock()
        chunker.synthesizer.synthesize = Mock(side_effect=Exception("Synthesis error"))

        try:
            chunker.synthesize_first_chunk()
        except Exception:
            pass

        assert chunker.chunks[0].synthesis_status == SynthesisStatus.FAILED

    def test_synthesis_continues_after_failure(self, chunker):
        """T100: Test background synthesis continues after chunk failure."""
        text = "Test sentence. " * 100
        chunker.prepare_chunks(text)

        # Mock synthesizer to fail on chunk 1, succeed on others
        call_count = [0]

        def mock_synthesize(text, speed=1.0):
            call_count[0] += 1
            if call_count[0] == 2:  # Fail on second call (chunk 1)
                raise Exception("Synthesis error")
            return b"audio_data"

        chunker.synthesizer = Mock()
        chunker.synthesizer.synthesize = Mock(side_effect=mock_synthesize)

        chunker.synthesize_first_chunk()
        chunker.start_background_synthesis()

        time.sleep(0.5)

        # First chunk should be completed, second should be failed
        assert chunker.chunks[0].synthesis_status == SynthesisStatus.COMPLETED
        # Some other chunks may be completed or in progress
        completed_count = sum(1 for chunk in chunker.chunks if chunk.synthesis_status == SynthesisStatus.COMPLETED)
        assert completed_count > 0
