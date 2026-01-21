"""Integration tests for chunked playback workflow.

This module tests the end-to-end chunked playback flow including:
- Text chunking and preparation
- First chunk synthesis (<3s)
- Background synthesis
- Chunk buffer management
- Performance benchmarks
"""

import time
from unittest.mock import Mock, patch

import pytest

from src.tts.chunking import ChunkSynthesizer, SynthesisStatus
from src.tts.synthesizer import PiperSynthesizer


class TestChunkedPlaybackWorkflow:
    """Integration test for complete chunked playback workflow"""

    def test_full_chunked_playback_workflow(self):
        """T084: Test complete workflow: prepare → first chunk → background → playback."""
        # Create a long text article (~1000 words)
        text = "This is a test sentence with multiple words. " * 200

        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            chunker = ChunkSynthesizer()

            # Mock synthesizer
            chunker.synthesizer = Mock()
            chunker.synthesizer.synthesize = Mock(return_value=b"fake_audio_data")

            # Step 1: Prepare chunks
            chunker.prepare_chunks(text)
            assert len(chunker.chunks) > 0
            assert all(chunk.synthesis_status == SynthesisStatus.PENDING for chunk in chunker.chunks)

            # Step 2: Synthesize first chunk (blocking)
            start_time = time.time()
            chunker.synthesize_first_chunk()
            first_chunk_time = time.time() - start_time

            assert chunker.chunks[0].synthesis_status == SynthesisStatus.COMPLETED
            assert chunker.chunks[0].audio_data == b"fake_audio_data"

            # Step 3: Start background synthesis
            chunker.start_background_synthesis()

            # Step 4: Simulate playback by consuming chunks
            time.sleep(0.5)  # Allow background synthesis to progress

            # Add synthesized chunks to buffer (simulate worker threads)
            for chunk in chunker.chunks[:5]:
                if chunk.synthesis_status == SynthesisStatus.PENDING:
                    chunk.audio_data = b"fake_audio_data"
                    chunk.synthesis_status = SynthesisStatus.COMPLETED
                if len(chunker.chunk_buffer) < 10:
                    chunker.chunk_buffer.append(chunk)

            # Consume first few chunks
            consumed_chunks = []
            for _ in range(min(3, len(chunker.chunk_buffer))):
                chunk = chunker.get_next_chunk()
                if chunk:
                    consumed_chunks.append(chunk)

            assert len(consumed_chunks) > 0
            assert all(chunk.synthesis_status == SynthesisStatus.COMPLETED for chunk in consumed_chunks)

            # Step 5: Clean shutdown
            chunker.stop()
            assert chunker.shutdown_event.is_set()
            assert len(chunker.chunk_buffer) == 0

    def test_chunked_playback_with_on_demand_synthesis(self):
        """T084: Test chunked playback with on-demand synthesis for seeking."""
        text = "This is a test sentence. " * 200

        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            chunker = ChunkSynthesizer()
            chunker.synthesizer = Mock()
            chunker.synthesizer.synthesize = Mock(return_value=b"audio_data")

            # Prepare chunks
            chunker.prepare_chunks(text)
            chunker.synthesize_first_chunk()

            # Simulate seeking to chunk 5 (not yet synthesized)
            assert chunker.chunks[5].synthesis_status == SynthesisStatus.PENDING

            # On-demand synthesis
            chunker.synthesize_chunk_on_demand(5)

            assert chunker.chunks[5].synthesis_status == SynthesisStatus.COMPLETED
            assert chunker.chunks[5].audio_data == b"audio_data"

            chunker.stop()

    def test_chunked_playback_handles_empty_buffer(self):
        """T084: Test playback handles empty buffer gracefully."""
        text = "Test sentence. " * 100

        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            chunker = ChunkSynthesizer()
            chunker.synthesizer = Mock()
            chunker.synthesizer.synthesize = Mock(return_value=b"audio")

            chunker.prepare_chunks(text)
            chunker.synthesize_first_chunk()

            # Try to get chunk when buffer is empty
            chunk = chunker.get_next_chunk()
            assert chunk is None

            # Add chunk to buffer
            chunker.chunk_buffer.append(chunker.chunks[0])

            # Now should get chunk
            chunk = chunker.get_next_chunk()
            assert chunk is not None

            chunker.stop()


class TestPerformanceTimeToFirstAudio:
    """Performance test: Time to first audio <3s for 10,000 word article"""

    @pytest.mark.slow
    def test_time_to_first_audio_under_3_seconds(self):
        """T085: Test time to first audio <3s for 10,000 word article."""
        # Create a very long text (~10,000 words)
        text = "This is a test sentence with about ten words. " * 1000

        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            chunker = ChunkSynthesizer()

            # Mock synthesizer with realistic timing (~100ms for first chunk)
            def mock_synthesize(text, speed=1.0):
                # Simulate synthesis time proportional to text length
                word_count = len(text.split())
                synthesis_time = min(word_count / 1000, 0.2)  # Max 200ms
                time.sleep(synthesis_time)
                return b"fake_audio_data"

            chunker.synthesizer = Mock()
            chunker.synthesizer.synthesize = Mock(side_effect=mock_synthesize)

            # Measure time to first audio
            start_time = time.time()

            chunker.prepare_chunks(text)
            chunker.synthesize_first_chunk()

            elapsed = time.time() - start_time

            # Should be much less than 3 seconds (even with mocked delay)
            assert elapsed < 3.0, f"Time to first audio was {elapsed:.2f}s, expected <3s"

            # First chunk should be ready
            assert chunker.chunks[0].synthesis_status == SynthesisStatus.COMPLETED
            assert chunker.chunks[0].audio_data is not None

            chunker.stop()

    @pytest.mark.slow
    def test_time_to_first_audio_with_real_text(self):
        """T085: Test time to first audio with realistic article text."""
        # Simulate a real article with paragraphs and sentences
        paragraph = (
            "This is a test paragraph that contains multiple sentences. "
            "Each sentence provides meaningful content for the reader. "
            "The text is structured to simulate a real article. "
            "We want to ensure that chunking works correctly with natural text. "
            "The synthesizer should handle this efficiently. "
        )
        text = (paragraph + "\n\n") * 400  # ~10,000 words

        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            chunker = ChunkSynthesizer()
            chunker.synthesizer = Mock()
            chunker.synthesizer.synthesize = Mock(return_value=b"audio_data")

            start_time = time.time()

            chunker.prepare_chunks(text)
            chunker.synthesize_first_chunk()

            elapsed = time.time() - start_time

            # With mocked synthesis, should be near-instant
            assert elapsed < 1.0

            # Verify chunks were created
            assert len(chunker.chunks) > 5
            assert chunker.chunks[0].synthesis_status == SynthesisStatus.COMPLETED

            chunker.stop()


class TestPerformanceChunkTransitions:
    """Performance test: Chunk transition gaps <50ms (95th percentile)"""

    @pytest.mark.slow
    def test_chunk_transition_gaps_under_50ms(self):
        """T086: Test chunk transition gaps <50ms (95th percentile)."""
        text = "Test sentence. " * 500

        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            chunker = ChunkSynthesizer()
            chunker.synthesizer = Mock()
            chunker.synthesizer.synthesize = Mock(return_value=b"audio_data")

            # Prepare and synthesize all chunks
            chunker.prepare_chunks(text)
            chunker.synthesize_first_chunk()

            # Manually synthesize remaining chunks (simulate background)
            for i in range(1, len(chunker.chunks)):
                chunker.chunks[i].audio_data = b"audio_data"
                chunker.chunks[i].synthesis_status = SynthesisStatus.COMPLETED
                chunker.chunk_buffer.append(chunker.chunks[i])

            # Measure transition times
            transition_times = []

            for i in range(len(chunker.chunk_buffer) - 1):
                start_time = time.time()
                chunk = chunker.get_next_chunk()
                elapsed = (time.time() - start_time) * 1000  # Convert to ms

                if chunk:
                    transition_times.append(elapsed)

            # Calculate 95th percentile
            if transition_times:
                transition_times.sort()
                percentile_95_index = int(len(transition_times) * 0.95)
                percentile_95 = transition_times[percentile_95_index]

                # 95th percentile should be <50ms
                assert percentile_95 < 50.0, (
                    f"95th percentile transition time was {percentile_95:.2f}ms, expected <50ms"
                )

            chunker.stop()

    @pytest.mark.slow
    def test_seamless_chunk_playback(self):
        """T086: Test seamless chunk playback with minimal gaps."""
        text = "This is a test sentence. " * 200

        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            chunker = ChunkSynthesizer()
            chunker.synthesizer = Mock()
            chunker.synthesizer.synthesize = Mock(return_value=b"audio_data")

            chunker.prepare_chunks(text)
            chunker.synthesize_first_chunk()

            # Synthesize all chunks
            for i in range(1, len(chunker.chunks)):
                chunker.chunks[i].audio_data = b"audio_data"
                chunker.chunks[i].synthesis_status = SynthesisStatus.COMPLETED
                chunker.chunk_buffer.append(chunker.chunks[i])

            # Simulate playback - consume all chunks
            playback_times = []
            previous_time = time.time()

            while True:
                chunk = chunker.get_next_chunk()
                if not chunk:
                    break

                current_time = time.time()
                gap = (current_time - previous_time) * 1000  # ms
                playback_times.append(gap)
                previous_time = current_time

            # All gaps should be minimal (<50ms)
            if playback_times:
                max_gap = max(playback_times[1:])  # Exclude first (startup)
                assert max_gap < 50.0, f"Maximum gap was {max_gap:.2f}ms"

            chunker.stop()


class TestChunkSynthesizerStressTest:
    """Stress tests for ChunkSynthesizer"""

    @pytest.mark.slow
    def test_large_document_handling(self):
        """Test ChunkSynthesizer handles very large documents."""
        # Create a very large document (~50,000 words)
        text = "This is a test sentence with ten words here. " * 5000

        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            chunker = ChunkSynthesizer()
            chunker.synthesizer = Mock()
            chunker.synthesizer.synthesize = Mock(return_value=b"audio")

            # Should handle chunking without errors
            chunker.prepare_chunks(text)

            assert len(chunker.chunks) > 100
            assert all(isinstance(chunk.text_content, str) for chunk in chunker.chunks)

            chunker.synthesize_first_chunk()
            assert chunker.chunks[0].synthesis_status == SynthesisStatus.COMPLETED

            chunker.stop()

    @pytest.mark.slow
    def test_rapid_chunk_consumption(self):
        """Test rapid chunk consumption from buffer."""
        text = "Test sentence. " * 500

        with patch.object(PiperSynthesizer, "__init__", return_value=None):
            chunker = ChunkSynthesizer()
            chunker.synthesizer = Mock()
            chunker.synthesizer.synthesize = Mock(return_value=b"audio")

            chunker.prepare_chunks(text)

            # Synthesize all chunks rapidly
            for chunk in chunker.chunks:
                chunk.audio_data = b"audio"
                chunk.synthesis_status = SynthesisStatus.COMPLETED
                chunker.chunk_buffer.append(chunk)

            # Rapidly consume chunks
            consumed_count = 0
            while True:
                chunk = chunker.get_next_chunk()
                if not chunk:
                    break
                consumed_count += 1

            assert consumed_count == len(chunker.chunks)

            chunker.stop()
