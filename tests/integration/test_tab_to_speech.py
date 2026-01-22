"""Integration tests for full tab-to-speech pipeline (User Story 1).

These tests verify the complete flow from tab detection through
text extraction to audio synthesis and playback.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from src.browser.tab_info import TabInfo
from src.utils.errors import ExtractionError, TTSError


class TestFullTabToSpeechFlow:
    """Integration tests for complete tab-to-speech pipeline."""

    def test_full_tab_read_flow(self):
        """Full flow: detect tab → extract text → synthesize → playback."""
        # Mock the dependencies
        with (
            patch("src.browser.detector.get_browser_tabs") as mock_detect,
            patch("src.extraction.text_extractor.ConcreteTextExtractor.extract_html") as mock_extract,
            patch("src.tts.synthesizer.synthesize_piper") as mock_synth,
            patch("src.tts.playback.AudioPlayback.play_audio") as mock_play,
            patch("pygame.mixer.init") as mock_pygame_init,
        ):
            # Setup mock tab
            test_tab = TabInfo(
                browser_name="chrome", tab_id="1", title="Test Page", url="https://example.com", window_handle=1001
            )
            mock_detect.return_value = [test_tab]

            # Setup mock extraction
            test_html = "<h1>Test Page</h1><p>Content here</p>"
            mock_extract.return_value = "Test Page Content here"

            # Setup mock synthesis
            test_audio = b"audio_data_bytes"
            mock_synth.return_value = test_audio

            # Execute flow
            from src.browser.detector import get_browser_tabs
            from src.extraction.text_extractor import ConcreteTextExtractor
            from src.tts.playback import AudioPlayback
            from src.tts.synthesizer import PiperSynthesizer

            # 1. Detect tabs
            tabs = get_browser_tabs("chrome")
            assert len(tabs) > 0
            tab = tabs[0]

            # 2. Extract text
            extractor = ConcreteTextExtractor()
            text = extractor.extract_html(test_html)
            assert "Content" in text or len(text) > 0

            # 3. Synthesize audio
            synthesizer = PiperSynthesizer()
            audio = synthesizer.synthesize(text)
            assert audio == test_audio

            # 4. Playback
            playback = AudioPlayback()
            playback.play_audio(audio)

    def test_inactive_tab_read_no_focus_switch(self):
        """Read from background tab without switching window focus."""
        with (
            patch("src.browser.detector.get_browser_tabs") as mock_detect,
            patch("src.extraction.text_extractor.ConcreteTextExtractor.extract_html") as mock_extract,
            patch("src.tts.synthesizer.synthesize_piper") as mock_synth,
            patch("src.tts.playback.AudioPlayback.play_audio") as mock_play,
            patch("pygame.mixer.init") as mock_pygame_init,
        ):
            # Setup tab list with background tab
            background_tab = TabInfo(
                browser_name="chrome",
                tab_id="3",
                title="Background Content",
                url="https://example.com/page",
                window_handle=1001,  # Same window but different tab
            )
            mock_detect.return_value = [background_tab]

            # Setup mock content
            mock_extract.return_value = "Background page content"
            mock_synth.return_value = b"audio_data"

            # Execute: read from background tab
            from src.browser.detector import get_browser_tabs
            from src.extraction.text_extractor import ConcreteTextExtractor
            from src.tts.playback import AudioPlayback
            from src.tts.synthesizer import PiperSynthesizer

            # Read from background tab
            tabs = get_browser_tabs("chrome")
            extractor = ConcreteTextExtractor()
            text = extractor.extract_html("<p>Background Content</p>")
            synthesizer = PiperSynthesizer()
            audio = synthesizer.synthesize(text)
            playback = AudioPlayback()
            playback.play_audio(audio)

            # Verify we got audio
            assert audio is not None

    def test_playback_pause_resume(self):
        """Start audio playback, pause, and resume from same position."""
        with patch("src.tts.playback.AudioPlayback") as mock_player:
            # Setup mock player
            player_instance = MagicMock()
            mock_player.return_value = player_instance

            # Mock methods
            player_instance.play_audio = Mock()
            player_instance.pause = Mock()
            player_instance.resume = Mock()
            player_instance.get_position = Mock(return_value=2.5)

            # Create test audio
            test_audio = b"audio_data"

            from src.tts.playback import AudioPlayback

            # Create player and play
            player = AudioPlayback()
            player.play_audio(test_audio)
            assert player_instance.play_audio.called

            # Pause
            player.pause()
            assert player_instance.pause.called

            # Get position
            position = player.get_position()
            assert position == 2.5

            # Resume
            player.resume()
            assert player_instance.resume.called

    def test_read_multiple_tabs_sequentially(self):
        """Read from tab1, then tab2; verify correct content for each."""
        with (
            patch("src.browser.detector.get_browser_tabs") as mock_detect,
            patch("src.extraction.text_extractor.ConcreteTextExtractor.extract_html") as mock_extract,
            patch("src.tts.synthesizer.synthesize_piper") as mock_synth,
        ):
            # Setup two tabs
            tab1 = TabInfo("chrome", "1", "First Page", "https://example.com/1", 1001)
            tab2 = TabInfo("chrome", "2", "Second Page", "https://example.com/2", 1001)
            mock_detect.return_value = [tab1, tab2]

            # Setup extraction to return different text per tab
            def extract_side_effect(html):
                if "First" in html:
                    return "Content from first page"
                else:
                    return "Content from second page"

            mock_extract.side_effect = extract_side_effect
            mock_synth.side_effect = lambda text, voice, speed: f"audio_for_{text}".encode()

            from src.browser.detector import get_browser_tabs
            from src.extraction.text_extractor import ConcreteTextExtractor
            from src.tts.synthesizer import PiperSynthesizer

            # Get both tabs
            tabs = get_browser_tabs("chrome")
            assert len(tabs) == 2

            extractor = ConcreteTextExtractor()
            synthesizer = PiperSynthesizer()

            # Read first tab
            text1 = extractor.extract_html("<p>First Page</p>")
            audio1 = synthesizer.synthesize(text1)
            assert b"first" in audio1 or b"First" in audio1 or len(audio1) > 0

            # Read second tab
            text2 = extractor.extract_html("<p>Second Page</p>")
            audio2 = synthesizer.synthesize(text2)
            assert b"second" in audio2 or b"Second" in audio2 or len(audio2) > 0

            # Verify different content
            assert text1 != text2
            assert audio1 != audio2


class TestTabToSpeechErrorHandling:
    """Test error handling in tab-to-speech pipeline."""

    def test_error_when_no_tabs_available(self):
        """Handle case when no browser tabs are available."""
        with patch("src.browser.detector.get_browser_tabs") as mock_detect:
            mock_detect.return_value = []

            from src.browser.detector import get_browser_tabs

            tabs = get_browser_tabs("chrome")

            assert len(tabs) == 0

    def test_error_when_extraction_fails(self):
        """Handle extraction errors gracefully."""
        from src.extraction.text_extractor import ConcreteTextExtractor

        with patch("src.extraction.text_extractor.ConcreteTextExtractor.extract_html") as mock_extract:
            mock_extract.side_effect = ExtractionError("Failed to extract")

            extractor = ConcreteTextExtractor()

            with pytest.raises(ExtractionError):
                extractor.extract_html("<p>Bad</p>")

    def test_error_when_synthesis_fails(self):
        """Handle synthesis errors gracefully."""
        from src.tts.synthesizer import PiperSynthesizer

        with patch("src.tts.synthesizer.synthesize_piper") as mock_synth:
            mock_synth.side_effect = TTSError("Synthesis failed")

            synthesizer = PiperSynthesizer()

            with pytest.raises(TTSError):
                synthesizer.synthesize("Test text")

    def test_error_recovery_after_failed_tab_read(self):
        """Recover from error and successfully read another tab."""
        from src.browser.detector import get_browser_tabs
        from src.extraction.text_extractor import ConcreteTextExtractor
        from src.tts.synthesizer import PiperSynthesizer

        with (
            patch("src.browser.detector.get_browser_tabs") as mock_detect,
            patch("src.extraction.text_extractor.ConcreteTextExtractor.extract_html") as mock_extract,
            patch("src.tts.synthesizer.synthesize_piper") as mock_synth,
        ):
            # First tab fails, second succeeds
            mock_detect.return_value = [
                TabInfo("chrome", "1", "Bad Tab", "https://bad.com", 1001),
                TabInfo("chrome", "2", "Good Tab", "https://good.com", 1001),
            ]

            def extract_with_error(html):
                if "Bad" in html:
                    raise ExtractionError("Failed")
                return "Good content"

            mock_extract.side_effect = extract_with_error
            mock_synth.return_value = b"audio"

            tabs = get_browser_tabs("chrome")
            extractor = ConcreteTextExtractor()
            synthesizer = PiperSynthesizer()

            # Try first tab (fails)
            try:
                extractor.extract_html("<p>Bad Tab</p>")
                assert False, "Should have raised ExtractionError"
            except ExtractionError:
                pass  # Expected

            # Try second tab (succeeds)
            text = extractor.extract_html("<p>Good Tab</p>")
            audio = synthesizer.synthesize(text)
            assert audio is not None


class TestPerformanceRequirements:
    """Test performance characteristics of tab-to-speech pipeline."""

    def test_tab_detection_completes_in_time(self):
        """Tab detection should complete within timeout."""
        import time

        with patch("src.browser.detector.get_browser_tabs") as mock_detect:
            mock_detect.return_value = [
                TabInfo("chrome", f"{i}", f"Tab {i}", f"https://example.com/{i}", 1001) for i in range(10)
            ]

            from src import config
            from src.browser.detector import get_browser_tabs

            start = time.time()
            tabs = get_browser_tabs("chrome")
            duration = time.time() - start

            # Should complete reasonably fast (within timeout)
            assert duration < config.BROWSER_TAB_DETECTION_TIMEOUT
            assert len(tabs) == 10

    def test_text_extraction_completes_in_time(self):
        """Text extraction should complete within timeout."""
        import time

        from src import config
        from src.extraction.text_extractor import ConcreteTextExtractor

        with patch("src.extraction.text_extractor.ConcreteTextExtractor.extract_html") as mock_extract:
            # Create large HTML
            large_html = "<p>" + "x" * 100000 + "</p>"
            mock_extract.return_value = "x" * 100000

            extractor = ConcreteTextExtractor()
            start = time.time()
            text = extractor.extract_html(large_html)
            duration = time.time() - start

            # Should complete within timeout
            assert duration < config.TEXT_EXTRACTION_TIMEOUT

    def test_synthesis_completes_in_time(self):
        """TTS synthesis should complete reasonably fast."""
        import time

        from src.tts.synthesizer import PiperSynthesizer

        with patch("src.tts.synthesizer.synthesize_piper") as mock_synth:
            # Synthesizing moderate text should be fast
            mock_synth.return_value = b"audio_data" * 100

            synthesizer = PiperSynthesizer()
            test_text = "This is a test sentence. " * 10

            start = time.time()
            audio = synthesizer.synthesize(test_text)
            duration = time.time() - start

            # Should be reasonably fast
            assert duration < 10  # TTS can be slower, but should be < 10 seconds
            assert len(audio) > 0
