"""Test script to verify pygame.mixer initialization on Windows 11."""

import sys

import pygame


def test_pygame_mixer_init():
    """Test pygame.mixer initialization and basic functionality."""
    print("Testing pygame.mixer initialization...")

    try:
        # Initialize pygame mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        print("✓ pygame.mixer.init() successful")

        # Check mixer initialization
        if pygame.mixer.get_init():
            print("✓ pygame.mixer is initialized")
            freq, size, channels = pygame.mixer.get_init()
            print(f"  - Frequency: {freq} Hz")
            print(f"  - Size: {size} bits")
            print(f"  - Channels: {channels}")
        else:
            print("✗ pygame.mixer is not initialized")
            return False

        # Test basic mixer functionality
        print("\nTesting mixer capabilities...")
        num_channels = pygame.mixer.get_num_channels()
        print(f"✓ Available mixer channels: {num_channels}")

        # Test pause/unpause
        pygame.mixer.pause()
        print("✓ pygame.mixer.pause() works")

        pygame.mixer.unpause()
        print("✓ pygame.mixer.unpause() works")

        # Clean up
        pygame.mixer.quit()
        print("\n✓ pygame.mixer.quit() successful")

        print("\n✅ All pygame.mixer tests passed!")
        return True

    except Exception as e:
        print(f"\n✗ Error testing pygame.mixer: {e}")
        return False


if __name__ == "__main__":
    success = test_pygame_mixer_init()
    sys.exit(0 if success else 1)
