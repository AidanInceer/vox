"""Tests for TTS synthesis (User Story 1).

These tests verify text-to-speech synthesis capability using Piper
neural TTS engine with various text inputs and configurations.
"""

import pytest
from src.tts.synthesizer import Synthesizer
from src.utils.errors import TTSError, ValidationError


class TestTTSSynthesis:
    """Test basic TTS synthesis capabilities."""

    def test_synthesize_basic_text(self):
        """Convert simple text to audio bytes."""
        synthesizer = Synthesizer()
        text = "Hello, world!"
        
        audio_bytes = synthesizer.synthesize(text)
        
        assert audio_bytes is not None
        assert isinstance(audio_bytes, bytes)
        assert len(audio_bytes) > 0

    def test_synthesize_long_text(self):
        """Synthesize text with over 1000 characters."""
        synthesizer = Synthesizer()
        
        # Create a long text (simulating a paragraph)
        long_text = " ".join([
            "This is a test sentence that will be repeated multiple times.",
        ] * 50)
        
        assert len(long_text) > 1000
        
        audio_bytes = synthesizer.synthesize(long_text)
        
        assert audio_bytes is not None
        assert isinstance(audio_bytes, bytes)
        assert len(audio_bytes) > 0

    def test_synthesize_multiple_speeds(self):
        """Verify speed parameter affects audio output."""
        synthesizer = Synthesizer()
        text = "Test sentence for speed variation"
        
        # Synthesize at different speeds
        audio_slow = synthesizer.synthesize(text, speed=0.8)
        audio_normal = synthesizer.synthesize(text, speed=1.0)
        audio_fast = synthesizer.synthesize(text, speed=1.5)
        
        # All should produce audio
        assert audio_slow is not None and len(audio_slow) > 0
        assert audio_normal is not None and len(audio_normal) > 0
        assert audio_fast is not None and len(audio_fast) > 0
        
        # Slower audio should generally be longer (more bytes)
        assert len(audio_slow) > len(audio_fast)

    def test_synthesize_with_default_voice(self):
        """Synthesize using default voice."""
        synthesizer = Synthesizer()
        text = "Default voice test"
        
        audio_bytes = synthesizer.synthesize(text)
        
        assert audio_bytes is not None
        assert len(audio_bytes) > 0

    def test_synthesize_with_different_voices(self):
        """Synthesize with different voice models."""
        synthesizer = Synthesizer()
        text = "Voice comparison test"
        
        # Get available voices
        voices = synthesizer.get_voices()
        assert len(voices) > 0
        
        # Synthesize with first voice
        voice = voices[0]
        synthesizer.set_voice(voice)
        
        audio_bytes = synthesizer.synthesize(text)
        assert audio_bytes is not None
        assert len(audio_bytes) > 0

    def test_synthesize_uppercase_text(self):
        """Handle uppercase text correctly."""
        synthesizer = Synthesizer()
        text = "THIS IS ALL UPPERCASE TEXT"
        
        audio_bytes = synthesizer.synthesize(text)
        
        assert audio_bytes is not None
        assert len(audio_bytes) > 0

    def test_synthesize_mixed_case_text(self):
        """Handle mixed case text."""
        synthesizer = Synthesizer()
        text = "ThE QuIcK bRoWn FoX"
        
        audio_bytes = synthesizer.synthesize(text)
        
        assert audio_bytes is not None
        assert len(audio_bytes) > 0

    def test_synthesize_with_numbers(self):
        """Handle text containing numbers."""
        synthesizer = Synthesizer()
        text = "The year is 2026 and it is 15 degrees"
        
        audio_bytes = synthesizer.synthesize(text)
        
        assert audio_bytes is not None
        assert len(audio_bytes) > 0

    def test_synthesize_with_punctuation(self):
        """Handle text with various punctuation."""
        synthesizer = Synthesizer()
        text = "What? Really! Yes, I'm sure. (Absolutely!)"
        
        audio_bytes = synthesizer.synthesize(text)
        
        assert audio_bytes is not None
        assert len(audio_bytes) > 0

    def test_synthesize_with_special_characters(self):
        """Handle special characters and symbols."""
        synthesizer = Synthesizer()
        text = "Email: test@example.com. Price: $19.99. Symbol: © 2026"
        
        audio_bytes = synthesizer.synthesize(text)
        
        assert audio_bytes is not None
        assert len(audio_bytes) > 0

    def test_synthesize_unicode_text(self):
        """Handle Unicode characters."""
        synthesizer = Synthesizer()
        
        # Test with accented characters
        text = "Café with naïve résumé"
        audio_bytes = synthesizer.synthesize(text)
        
        assert audio_bytes is not None
        assert len(audio_bytes) > 0

    def test_synthesize_with_emojis(self):
        """Handle emoji characters gracefully."""
        synthesizer = Synthesizer()
        text = "Party time 🎉 Celebration 🎊"
        
        # Should either synthesize successfully or raise validation error
        try:
            audio_bytes = synthesizer.synthesize(text)
            assert audio_bytes is not None
        except (ValidationError, TTSError):
            # Acceptable to reject emojis
            pass

    def test_synthesize_multiline_text(self):
        """Handle text with multiple lines."""
        synthesizer = Synthesizer()
        text = """Line one
        Line two
        Line three"""
        
        audio_bytes = synthesizer.synthesize(text)
        
        assert audio_bytes is not None
        assert len(audio_bytes) > 0


class TestTTSSynthesisErrors:
    """Test error handling in TTS synthesis."""

    def test_synthesize_empty_text(self):
        """Handle empty text gracefully."""
        synthesizer = Synthesizer()
        
        # Should either return empty audio or raise validation error
        try:
            audio_bytes = synthesizer.synthesize("")
            if audio_bytes is not None:
                assert isinstance(audio_bytes, bytes)
        except ValidationError:
            # Acceptable to reject empty text
            pass

    def test_synthesize_none_input(self):
        """Reject None input."""
        synthesizer = Synthesizer()
        
        with pytest.raises((ValidationError, TypeError)):
            synthesizer.synthesize(None)

    def test_synthesize_invalid_speed(self):
        """Reject invalid speed values."""
        synthesizer = Synthesizer()
        text = "Test"
        
        # Test with invalid speeds
        with pytest.raises(ValidationError):
            synthesizer.synthesize(text, speed=0)  # Too slow
        
        with pytest.raises(ValidationError):
            synthesizer.synthesize(text, speed=-1)  # Negative
        
        with pytest.raises(ValidationError):
            synthesizer.synthesize(text, speed=10)  # Too fast

    def test_get_voices_returns_list(self):
        """get_voices should return list of available voices."""
        synthesizer = Synthesizer()
        voices = synthesizer.get_voices()
        
        assert isinstance(voices, list)
        assert len(voices) > 0

    def test_set_voice_with_valid_voice(self):
        """Set voice with valid voice name."""
        synthesizer = Synthesizer()
        voices = synthesizer.get_voices()
        
        if len(voices) > 0:
            synthesizer.set_voice(voices[0])
            # Should not raise

    def test_set_voice_with_invalid_voice(self):
        """Reject invalid voice names."""
        synthesizer = Synthesizer()
        
        with pytest.raises(ValidationError):
            synthesizer.set_voice("nonexistent_voice_xyz")


class TestTTSSynthesizerInterface:
    """Test Synthesizer interface contract."""

    def test_synthesizer_has_synthesize_method(self):
        """Synthesizer should have synthesize method."""
        synthesizer = Synthesizer()
        assert hasattr(synthesizer, 'synthesize')
        assert callable(synthesizer.synthesize)

    def test_synthesizer_has_get_voices_method(self):
        """Synthesizer should have get_voices method."""
        synthesizer = Synthesizer()
        assert hasattr(synthesizer, 'get_voices')
        assert callable(synthesizer.get_voices)

    def test_synthesizer_has_set_voice_method(self):
        """Synthesizer should have set_voice method."""
        synthesizer = Synthesizer()
        assert hasattr(synthesizer, 'set_voice')
        assert callable(synthesizer.set_voice)

    def test_synthesizer_has_is_available_method(self):
        """Synthesizer should have is_available method."""
        synthesizer = Synthesizer()
        assert hasattr(synthesizer, 'is_available')
        assert callable(synthesizer.is_available)

    def test_is_available_returns_boolean(self):
        """is_available should return boolean."""
        synthesizer = Synthesizer()
        available = synthesizer.is_available()
        
        assert isinstance(available, bool)

    def test_synthesize_returns_bytes(self):
        """synthesize always returns bytes."""
        synthesizer = Synthesizer()
        result = synthesizer.synthesize("test")
        
        assert isinstance(result, bytes)


class TestTTSCaching:
    """Test optional TTS result caching."""

    def test_synthesize_same_text_twice(self):
        """Synthesizing same text twice produces same audio."""
        synthesizer = Synthesizer()
        text = "Same text test"
        
        audio1 = synthesizer.synthesize(text)
        audio2 = synthesizer.synthesize(text)
        
        # Both should be audio bytes
        assert audio1 is not None
        assert audio2 is not None
        # Should be identical (if caching is implemented)
        assert audio1 == audio2

    def test_synthesize_different_text_produces_different_audio(self):
        """Different text produces different audio output."""
        synthesizer = Synthesizer()
        
        audio1 = synthesizer.synthesize("First text")
        audio2 = synthesizer.synthesize("Second text")
        
        assert audio1 is not None
        assert audio2 is not None
        # Should be different audio data
        assert audio1 != audio2
