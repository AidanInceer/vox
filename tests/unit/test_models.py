"""Unit tests for data models (Tab, TextExtractor, TTS, Session)."""

from datetime import datetime

import pytest

from src.browser.tab_info import TabInfo
from src.extraction.text_extractor import TextExtractor
from src.session.models import ReadingSession
from src.tts.synthesizer import Synthesizer


class TestTabInfo:
    """Tests for TabInfo dataclass."""

    def test_tab_info_creation(self):
        """Test creating a TabInfo instance."""
        tab = TabInfo(browser_name="chrome", tab_id="tab_001", title="Example Page", url="https://example.com")
        assert tab.browser_name == "chrome"
        assert tab.tab_id == "tab_001"
        assert tab.title == "Example Page"
        assert tab.url == "https://example.com"

    def test_tab_info_with_window_handle(self):
        """Test TabInfo with optional window_handle."""
        tab = TabInfo(
            browser_name="edge", tab_id="tab_002", title="Google", url="https://google.com", window_handle=12345
        )
        assert tab.window_handle == 12345

    def test_tab_info_string_representation(self):
        """Test __str__ method of TabInfo."""
        tab = TabInfo(browser_name="firefox", tab_id="tab_003", title="GitHub", url="https://github.com")
        assert str(tab) == "firefox: GitHub (https://github.com)"

    def test_tab_info_repr(self):
        """Test __repr__ method of TabInfo."""
        tab = TabInfo(browser_name="chrome", tab_id="tab_001", title="Example", url="https://example.com")
        repr_str = repr(tab)
        assert "TabInfo" in repr_str
        assert "chrome" in repr_str
        assert "Example" in repr_str

    def test_tab_info_is_valid(self):
        """Test is_valid() method."""
        # Valid tab
        valid_tab = TabInfo(browser_name="chrome", tab_id="tab_001", title="Page", url="https://example.com")
        assert valid_tab.is_valid()

        # Invalid tab (missing browser_name)
        invalid_tab = TabInfo(browser_name="", tab_id="tab_001", title="Page", url="https://example.com")
        assert not invalid_tab.is_valid()

    def test_tab_info_equality(self):
        """Test TabInfo dataclass equality."""
        tab1 = TabInfo(browser_name="chrome", tab_id="tab_001", title="Example", url="https://example.com")
        tab2 = TabInfo(browser_name="chrome", tab_id="tab_001", title="Example", url="https://example.com")
        assert tab1 == tab2


class TestReadingSession:
    """Tests for ReadingSession dataclass."""

    def test_session_creation(self):
        """Test creating a ReadingSession instance."""
        session = ReadingSession(
            session_id="session_001", session_name="my-session", page_url="https://example.com", title="Example Page"
        )
        assert session.session_id == "session_001"
        assert session.session_name == "my-session"
        assert session.page_url == "https://example.com"
        assert session.title == "Example Page"
        assert session.playback_position == 0

    def test_session_with_custom_fields(self):
        """Test ReadingSession with custom settings."""
        extraction_settings = {"main_only": True}
        tts_settings = {"voice": "en_US", "speed": 1.2}

        session = ReadingSession(
            session_id="session_002",
            session_name="python-docs",
            page_url="https://docs.python.org",
            title="Python Docs",
            playback_position=1500,
            extraction_settings=extraction_settings,
            tts_settings=tts_settings,
        )
        assert session.extraction_settings == extraction_settings
        assert session.tts_settings == tts_settings
        assert session.playback_position == 1500

    def test_session_string_representation(self):
        """Test __str__ method."""
        session = ReadingSession(
            session_id="session_001", session_name="my-session", page_url="https://example.com", title="Example"
        )
        assert "Example" in str(session)
        assert "https://example.com" in str(session)

    def test_session_repr(self):
        """Test __repr__ method."""
        session = ReadingSession(
            session_id="session_001", session_name="my-session", page_url="https://example.com", title="Example"
        )
        repr_str = repr(session)
        assert "ReadingSession" in repr_str
        assert "session_001" in repr_str

    def test_session_is_valid(self):
        """Test is_valid() method."""
        # Valid session
        valid_session = ReadingSession(
            session_id="session_001", session_name="my-session", page_url="https://example.com", title="Example"
        )
        assert valid_session.is_valid()

        # Invalid session (missing title)
        invalid_session = ReadingSession(
            session_id="session_001", session_name="my-session", page_url="https://example.com", title=""
        )
        assert not invalid_session.is_valid()

    def test_session_to_dict(self):
        """Test to_dict() serialization."""
        session = ReadingSession(
            session_id="session_001",
            session_name="my-session",
            page_url="https://example.com",
            title="Example",
            playback_position=1000,
            extraction_settings={"main_only": True},
        )
        session_dict = session.to_dict()

        assert session_dict["session_id"] == "session_001"
        assert session_dict["session_name"] == "my-session"
        assert session_dict["page_url"] == "https://example.com"
        assert session_dict["title"] == "Example"
        assert session_dict["playback_position"] == 1000
        assert session_dict["extraction_settings"] == {"main_only": True}
        assert isinstance(session_dict["created_at"], str)
        assert isinstance(session_dict["last_accessed"], str)

    def test_session_from_dict(self):
        """Test from_dict() deserialization."""
        data = {
            "session_id": "session_001",
            "session_name": "my-session",
            "page_url": "https://example.com",
            "title": "Example",
            "playback_position": 1000,
            "extraction_settings": {"main_only": True},
            "tts_settings": {"voice": "en_US"},
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
        }
        session = ReadingSession.from_dict(data)

        assert session.session_id == "session_001"
        assert session.session_name == "my-session"
        assert session.page_url == "https://example.com"
        assert session.title == "Example"
        assert session.playback_position == 1000
        assert session.extraction_settings == {"main_only": True}
        assert session.tts_settings == {"voice": "en_US"}

    def test_session_serialization_roundtrip(self):
        """Test that session survives to_dict() -> from_dict() roundtrip."""
        original = ReadingSession(
            session_id="session_001",
            session_name="my-session",
            page_url="https://example.com",
            title="Example",
            playback_position=2000,
            extraction_settings={"main_only": True},
            tts_settings={"voice": "en_US", "speed": 1.5},
        )

        # Serialize and deserialize
        session_dict = original.to_dict()
        restored = ReadingSession.from_dict(session_dict)

        # Verify all fields are preserved
        assert restored.session_id == original.session_id
        assert restored.session_name == original.session_name
        assert restored.page_url == original.page_url
        assert restored.title == original.title
        assert restored.playback_position == original.playback_position
        assert restored.extraction_settings == original.extraction_settings
        assert restored.tts_settings == original.tts_settings


class TestTextExtractorInterface:
    """Tests for TextExtractor abstract interface."""

    def test_text_extractor_is_abstract(self):
        """Test that TextExtractor cannot be instantiated directly."""
        with pytest.raises(TypeError):
            TextExtractor()

    def test_text_extractor_requires_extract_method(self):
        """Test that TextExtractor requires extract() method."""

        class IncompleteExtractor(TextExtractor):
            def supports(self, source_type: str) -> bool:
                return True

        with pytest.raises(TypeError):
            IncompleteExtractor()

    def test_text_extractor_requires_supports_method(self):
        """Test that TextExtractor requires supports() method."""

        class IncompleteExtractor(TextExtractor):
            def extract(self, source: str) -> str:
                return ""

        with pytest.raises(TypeError):
            IncompleteExtractor()

    def test_concrete_text_extractor_implementation(self):
        """Test implementing TextExtractor with concrete class."""

        class MockExtractor(TextExtractor):
            def extract(self, source: str) -> str:
                return "Extracted text"

            def supports(self, source_type: str) -> bool:
                return source_type == "mock"

        extractor = MockExtractor()
        assert extractor.extract("test_source") == "Extracted text"
        assert extractor.supports("mock") is True
        assert extractor.supports("other") is False


class TestSynthesizerInterface:
    """Tests for Synthesizer abstract interface."""

    def test_synthesizer_is_abstract(self):
        """Test that Synthesizer cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Synthesizer()

    def test_synthesizer_requires_all_methods(self):
        """Test that Synthesizer requires all abstract methods."""

        class IncompleteSynthesizer(Synthesizer):
            pass

        with pytest.raises(TypeError):
            IncompleteSynthesizer()

    def test_concrete_synthesizer_implementation(self):
        """Test implementing Synthesizer with concrete class."""

        class MockSynthesizer(Synthesizer):
            def synthesize(self, text: str, speed: float = 1.0) -> bytes:
                return b"WAV_AUDIO_DATA"

            def get_voices(self) -> list[str]:
                return ["voice1", "voice2"]

            def set_voice(self, voice: str) -> None:
                self.current_voice = voice

            def is_available(self) -> bool:
                return True

        synth = MockSynthesizer()
        assert synth.synthesize("Hello") == b"WAV_AUDIO_DATA"
        assert "voice1" in synth.get_voices()
        assert synth.is_available() is True
