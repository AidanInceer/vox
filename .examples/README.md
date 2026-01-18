# vox Examples

This directory contains example files and usage scenarios for vox.

## Session Examples

The `sessions/` directory contains example session files that demonstrate the session management feature:

- **example-article.json** - A basic article with partial progress (245 characters read)
- **technical-doc.json** - API documentation at the start (0 characters read)
- **research-paper.json** - Academic paper with significant progress (892 characters read)

### Using Example Sessions

To try out the example sessions:

1. Copy the session files to your vox sessions directory:
   ```bash
   # Windows
   Copy-Item .examples\sessions\*.json $env:APPDATA\vox\sessions\

   # Or manually copy to: C:\Users\<YourUsername>\AppData\Roaming\vox\sessions\
   ```

2. List the sessions:
   ```bash
   vox list-sessions
   ```

3. Resume a session:
   ```bash
   vox resume example-article
   ```

### Session File Format

Each session file is a JSON document with the following structure:

```json
{
  "session_id": "unique-uuid-v4",
  "session_name": "user-friendly-name",
  "url": "source-url-or-file-path",
  "title": "Page or document title",
  "extracted_text": "Full text content",
  "playback_position": 0,
  "created_at": "ISO-8601-timestamp",
  "last_accessed": "ISO-8601-timestamp",
  "tts_settings": {
    "voice": "voice-model-name",
    "speed": 1.0
  },
  "extraction_settings": {}
}
```

## Command Examples

### Basic Reading

```bash
# Read from a URL
vox read --url https://example.com

# Read with custom speed
vox read --url https://example.com --speed 1.5

# Save audio to file
vox read --url https://example.com --output audio.wav
```

### Session Management

```bash
# Save a session
vox read --url https://example.com --save-session my-article

# List all sessions
vox list-sessions

# Resume a session
vox resume my-article

# Delete a session
vox delete-session my-article
```

### Interactive Playback

During playback, use these keyboard shortcuts:

- **SPACE** - Pause/Resume
- **→** (Right Arrow) - Seek forward 5 seconds
- **←** (Left Arrow) - Seek backward 5 seconds
- **Q** - Quit playback

Note: Speed adjustment must be set before playback using `--speed` flag. Runtime speed control is not supported.

## Performance Features

For longer articles (>200 words), vox automatically uses chunking:

- ✅ First audio chunk ready in <3 seconds
- ✅ Background synthesis of remaining chunks
- ✅ Seamless playback transitions
- ✅ Memory-efficient (max 10 chunks buffered)

## Troubleshooting

If sessions don't appear after copying:

1. Verify the files are in the correct location:
   ```powershell
   Get-ChildItem $env:APPDATA\vox\sessions\
   ```

2. Check the session names are valid (alphanumeric, hyphens, underscores only)

3. Ensure JSON files are properly formatted (use a JSON validator if needed)

For more information, see the main [README.md](../README.md) in the project root.
