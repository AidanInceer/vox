"""Verification script for pygame.mixer initialization on Windows 11."""

import sys

import pygame


def test_pygame_mixer():
    """Test pygame.mixer initialization."""
    print("Testing pygame.mixer initialization...")
    print(f"pygame version: {pygame.version.ver}")

    try:
        pygame.mixer.init()
        print("✓ pygame.mixer.init() successful")

        # Check mixer settings
        freq, size, channels = pygame.mixer.get_init()
        print(f"  Frequency: {freq} Hz")
        print(f"  Sample size: {size} bits")
        print(f"  Channels: {channels}")

        pygame.mixer.quit()
        print("✓ pygame.mixer.quit() successful")

        print("\n✅ All tests passed - pygame.mixer ready for use")
        return True

    except Exception as e:
        print(f"\n❌ pygame.mixer initialization failed: {e}")
        return False


if __name__ == "__main__":
    success = test_pygame_mixer()
    sys.exit(0 if success else 1)
