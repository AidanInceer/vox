# PlaybackController API Contract

**Module**: `src/tts/controller.py`  
**Purpose**: Manage interactive playback controls via keyboard input during audio playback  
**Owner**: Playback Controls (Feature 002)

---

## Class: PlaybackController

**Responsibilities**:
- Detect keyboard input during audio playback (non-blocking)
- Handle pause/resume, quit, seek, and speed adjustment commands
- Manage PlaybackState (shared state between keyboard and playback threads)
- Coordinate with AudioPlayback for actual playback control
- Provide clean shutdown on quit command

**Dependencies**:
- `src/tts/playback.AudioPlayback`: Audio playback engine
- `msvcrt`: Windows keyboard input (non-blocking)
- `threading`: Background keyboard input thread
- `queue.Queue`: Thread-safe command queue
- `typing`: Type annotations
- `logging`: Event logging

---

## Methods

### `__init__(audio_playback: AudioPlayback)`

**Purpose**: Initialize PlaybackController with audio playback engine

**Parameters**:
- `audio_playback` (AudioPlayback): Audio playback instance to control

**Returns**: None

**Side Effects**:
- Creates PlaybackState instance (in-memory state)
- Initializes command queue (queue.Queue)
- Initializes shutdown event (threading.Event)

**Raises**: None

**Example**:
```python
from src.tts.playback import AudioPlayback
from src.tts.controller import PlaybackController

playback = AudioPlayback()
controller = PlaybackController(playback)
```

---

### `start(audio_bytes: bytes, text_chunks: list[str]) -> None`

**Purpose**: Start playback with keyboard control enabled

**Parameters**:
- `audio_bytes` (bytes): Audio data to play (WAV format)
- `text_chunks` (list[str]): List of text chunks corresponding to audio segments (for seeking)

**Returns**: None

**Side Effects**:
- Sets PlaybackState.is_playing = True
- Starts keyboard input thread (background)
- Starts audio playback in current thread (blocking until completion or quit)
- Monitors command queue for keyboard commands

**Raises**:
- `ValueError`: If audio_bytes is empty
- `RuntimeError`: If playback fails to start

**Blocking**: Yes - blocks until playback completes or user quits (Q key)

**Example**:
```python
controller.start(audio_bytes=wav_data, text_chunks=chunks)
# Blocks here until playback done or user presses Q
```

---

### `pause() -> None`

**Purpose**: Pause playback (triggered by spacebar)

**Parameters**: None

**Returns**: None

**Side Effects**:
- Sets PlaybackState.is_paused = True, is_playing = False
- Calls AudioPlayback.pause()
- Prints "Paused" status to stdout

**Raises**:
- `RuntimeError`: If playback not active

**Idempotent**: Yes - multiple pause calls have no additional effect

**Example**:
```python
# User presses spacebar during playback
controller.pause()
# Output: [*] Paused
```

---

### `resume() -> None`

**Purpose**: Resume playback from paused state (triggered by spacebar)

**Parameters**: None

**Returns**: None

**Side Effects**:
- Sets PlaybackState.is_playing = True, is_paused = False
- Calls AudioPlayback.resume()
- Prints "Resumed" status to stdout

**Raises**:
- `RuntimeError`: If playback not paused

**Idempotent**: Yes - multiple resume calls when already playing have no effect

**Example**:
```python
# User presses spacebar while paused
controller.resume()
# Output: [*] Resumed
```

---

### `seek(offset_seconds: int) -> None`

**Purpose**: Skip forward (positive offset) or backward (negative offset)

**Parameters**:
- `offset_seconds` (int): Seconds to skip (positive = forward, negative = backward)

**Returns**: None

**Side Effects**:
- Updates PlaybackState.current_position_ms
- Calls AudioPlayback.seek(offset_ms)
- Prints new position to stdout
- If seeking beyond bounds, clamps to start (0:00) or end

**Raises**:
- `RuntimeError`: If playback not active

**Bounds Checking**:
- Forward seek beyond end: Stops playback, displays "End of content reached"
- Backward seek before start: Seeks to 0:00, displays "Start of content"

**Example**:
```python
# User presses right arrow (skip forward 10s)
controller.seek(10)
# Output: [*] Skipped to 1:23 / 5:45

# User presses left arrow (skip backward 10s)
controller.seek(-10)
# Output: [*] Skipped to 1:03 / 5:45
```

---

### `adjust_speed(delta: float) -> None`

**Purpose**: Adjust playback speed by delta (triggered by up/down arrows)

**Parameters**:
- `delta` (float): Speed adjustment (typically ±0.25x)

**Returns**: None

**Side Effects**:
- Updates PlaybackState.playback_speed (clamped to [0.5, 2.0])
- Calls AudioPlayback.set_speed()
- Prints new speed to stdout with min/max indicator

**Raises**:
- `RuntimeError`: If playback not active

**Bounds Checking**:
- Speed clamped to range [0.5, 2.0]
- If at min/max, displays "(min)" or "(max)" indicator

**Example**:
```python
# User presses up arrow (increase speed)
controller.adjust_speed(0.25)
# Output: [*] Speed: 1.25x

# User presses up arrow repeatedly until max
controller.adjust_speed(0.25)  # 1.5x
controller.adjust_speed(0.25)  # 1.75x
controller.adjust_speed(0.25)  # 2.0x (clamped)
# Output: [*] Speed: 2.0x (max)
```

---

### `quit() -> None`

**Purpose**: Stop playback and exit cleanly (triggered by Q key)

**Parameters**: None

**Returns**: None

**Side Effects**:
- Sets shutdown_event (signals all threads to stop)
- Stops audio playback immediately
- Joins keyboard input thread (with 5s timeout)
- Sets PlaybackState.is_playing = False
- Returns playback position for session save (if session active)
- Prints "Playback stopped" to stdout

**Raises**: None (graceful shutdown, no exceptions)

**Cleanup**:
- Stops audio playback
- Clears command queue
- Joins background threads
- Releases audio resources

**Example**:
```python
# User presses Q
controller.quit()
# Output: [*] Playback stopped
# Returns control to main CLI
```

---

### `get_current_position() -> tuple[int, int]`

**Purpose**: Get current playback position and total duration

**Parameters**: None

**Returns**:
- `tuple[int, int]`: (current_position_ms, total_duration_ms)

**Side Effects**: None (read-only)

**Raises**: None

**Example**:
```python
position_ms, duration_ms = controller.get_current_position()
print(f"Position: {position_ms // 1000}s / {duration_ms // 1000}s")
# Output: Position: 83s / 345s
```

---

### `_keyboard_input_thread() -> None` (Private)

**Purpose**: Background thread that monitors keyboard input and enqueues commands

**Parameters**: None

**Returns**: None (runs until shutdown_event set)

**Side Effects**:
- Polls msvcrt.kbhit() every 50ms (non-blocking)
- Reads key via msvcrt.getch()
- Enqueues command to command queue
- Checks shutdown_event every iteration

**Key Mapping**:
- Space (0x20): Enqueue "PAUSE" or "RESUME" (toggle)
- Q (0x71 or 0x51): Enqueue "QUIT"
- Arrow keys (0xE0 prefix):
  - 0x48 (Up): Enqueue "SPEED_UP"
  - 0x50 (Down): Enqueue "SPEED_DOWN"
  - 0x4D (Right): Enqueue "SEEK_FORWARD"
  - 0x4B (Left): Enqueue "SEEK_BACKWARD"

**Debouncing**: 100ms delay after key press to prevent double-triggers

**Graceful Shutdown**: Exits loop when shutdown_event is set

**Note**: Internal method, not part of public API

---

### `_process_commands() -> None` (Private)

**Purpose**: Process commands from command queue in main playback thread

**Parameters**: None

**Returns**: None

**Side Effects**:
- Reads commands from queue (non-blocking, timeout 100ms)
- Dispatches to appropriate handler (pause, resume, seek, speed, quit)
- Updates PlaybackState

**Command Dispatch**:
- "PAUSE": Call pause()
- "RESUME": Call resume()
- "QUIT": Call quit()
- "SEEK_FORWARD": Call seek(10)
- "SEEK_BACKWARD": Call seek(-10)
- "SPEED_UP": Call adjust_speed(0.25)
- "SPEED_DOWN": Call adjust_speed(-0.25)

**Note**: Internal method, not part of public API

---

## Thread Safety

**Status**: Thread-safe via locks and queues

**Shared State**: PlaybackState protected by threading.Lock

**Synchronization**:
- Command queue (queue.Queue): Thread-safe by design
- shutdown_event (threading.Event): Thread-safe signal
- PlaybackState lock: Protects is_playing, is_paused, speed, position

**Threads**:
1. **Main thread**: Audio playback + command processing
2. **Keyboard thread**: Non-blocking keyboard input monitoring

---

## Performance Characteristics

| Operation | Latency | Notes |
|-----------|---------|-------|
| Key detection | <50ms | msvcrt.kbhit() polling interval |
| Command dispatch | <50ms | Queue.get() timeout 100ms |
| Pause/resume | <10ms | AudioPlayback.pause/resume |
| Seek | <100ms | Depends on AudioPlayback seek performance |
| Speed adjustment | <50ms | AudioPlayback.set_speed |
| Quit | <100ms | Thread join with 5s timeout |

**CPU Usage**: <1% (50ms polling, minimal CPU load)

---

## Error Handling

**Philosophy**: Degrade gracefully - keyboard errors should not crash playback

**Error Categories**:
1. **Keyboard Input Errors**: Log error, continue playback (no user impact)
2. **Audio Playback Errors**: Log error, attempt recovery, notify user
3. **Command Dispatch Errors**: Log error, skip command, continue playback

**Error Recovery**:
- Keyboard read error: Log, sleep 1s, retry (prevent tight loop)
- Audio pause/resume error: Log, notify user, continue playback
- Seek beyond bounds: Clamp to valid range, notify user

---

## Testing Requirements

**Unit Tests** (`tests/unit/test_playback_controller.py`):
- ✅ Test pause command (state transition, AudioPlayback.pause called)
- ✅ Test resume command (state transition, AudioPlayback.resume called)
- ✅ Test quit command (shutdown_event set, threads joined)
- ✅ Test seek forward (position updated, bounds checked)
- ✅ Test seek backward (position updated, bounds checked)
- ✅ Test seek beyond end (clamped, error message)
- ✅ Test seek before start (clamped to 0:00)
- ✅ Test speed increase (speed updated, clamped to 2.0x)
- ✅ Test speed decrease (speed updated, clamped to 0.5x)
- ✅ Test command queue processing (commands dispatched correctly)
- ✅ Test debouncing (rapid key presses handled)
- ✅ Test thread safety (concurrent access to PlaybackState)

**Integration Tests** (`tests/integration/test_playback_controls.py`):
- ✅ Full workflow: Start playback → pause → resume → seek → quit
- ✅ Keyboard simulation: Inject key events, verify state changes
- ✅ Multi-command sequence: Pause → seek → speed up → resume → quit
- ✅ Graceful shutdown: Verify all threads cleaned up on quit

**Coverage Target**: >80% line coverage for PlaybackController

---

## Example Usage

```python
from src.tts.playback import AudioPlayback
from src.tts.controller import PlaybackController

# Initialize components
playback = AudioPlayback()
controller = PlaybackController(playback)

# Start playback with keyboard controls
# (Blocks until playback done or user quits)
controller.start(audio_bytes=wav_data, text_chunks=chunks)

# During playback, user can press:
# - Space: Pause/Resume
# - Q: Quit
# - Arrow keys: Navigate and adjust speed

# When playback ends or user quits, control returns here
position_ms, _ = controller.get_current_position()
print(f"Playback ended at {position_ms}ms")
```

---

**Contract Status**: ✅ Complete - All public methods documented with inputs, outputs, side effects, errors, threading model, and examples.
