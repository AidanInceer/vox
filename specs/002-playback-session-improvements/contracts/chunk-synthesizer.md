# ChunkSynthesizer API Contract

**Module**: `src/tts/chunking.py`  
**Purpose**: Split text into chunks and synthesize audio in background for streaming playback  
**Owner**: Chunking Performance (Feature 002)

---

## Class: ChunkSynthesizer

**Responsibilities**:
- Split extracted text into sentence-aware chunks (~150 words each)
- Synthesize first chunk immediately (blocking) for fast playback start
- Synthesize remaining chunks in background threads
- Maintain chunk buffer (queue of ready AudioChunk instances)
- Handle on-demand synthesis when user seeks to unsynthesized chunk
- Coordinate with PlaybackState for chunk tracking

**Dependencies**:
- `src/tts/synthesizer.PiperSynthesizer`: TTS synthesis engine
- `threading`: Background synthesis threads
- `queue.Queue`: Thread-safe chunk buffer
- `re`: Regular expressions for sentence splitting
- `typing`: Type annotations
- `logging`: Performance logging

---

## Methods

### `__init__(synthesizer: PiperSynthesizer, chunk_size: int = 150, max_buffer_size: int = 10)`

**Purpose**: Initialize ChunkSynthesizer with TTS engine and configuration

**Parameters**:
- `synthesizer` (PiperSynthesizer): TTS synthesis engine instance
- `chunk_size` (int, optional): Target words per chunk (default: 150, range: 50-300)
- `max_buffer_size` (int, optional): Maximum chunks in buffer (default: 10, prevents memory bloat)

**Returns**: None

**Side Effects**:
- Initializes chunk buffer (queue.Queue)
- Initializes synthesis thread pool (2-4 threads)
- Initializes shutdown event (threading.Event)

**Raises**:
- `ValueError`: If chunk_size not in range [50, 300]
- `ValueError`: If max_buffer_size < 2

**Example**:
```python
from src.tts.synthesizer import PiperSynthesizer
from src.tts.chunking import ChunkSynthesizer

synthesizer = PiperSynthesizer(voice="en_US-libritts-high")
chunker = ChunkSynthesizer(synthesizer, chunk_size=150, max_buffer_size=10)
```

---

### `prepare_chunks(text: str) -> list[str]`

**Purpose**: Split text into sentence-aware chunks for synthesis

**Parameters**:
- `text` (str): Full extracted text to split

**Returns**:
- `list[str]`: List of text chunks (~150 words each, sentence boundaries respected)

**Side Effects**:
- Stores chunks in internal list for reference
- Resets chunk buffer (clears any previous chunks)

**Raises**:
- `ValueError`: If text is empty or only whitespace

**Algorithm**:
1. Split text into sentences (regex: `[.!?]+\s+`)
2. Group sentences into chunks targeting ~150 words
3. Allow ±20% variance to respect sentence boundaries (120-180 words)
4. Minimum chunk: 50 words (avoid too-short chunks)
5. Maximum chunk: 300 words (avoid long synthesis delays)
6. If text <50 words, treat as single chunk (no splitting overhead)

**Example**:
```python
text = "Full article text with many sentences. More content here. Even more..."
chunks = chunker.prepare_chunks(text)
# Returns: ["First chunk with ~150 words...", "Second chunk...", ...]
print(f"Split into {len(chunks)} chunks")
# Output: Split into 8 chunks
```

---

### `synthesize_first_chunk() -> bytes`

**Purpose**: Synthesize first chunk immediately (blocking) for fast playback start

**Parameters**: None (uses first chunk from prepare_chunks)

**Returns**:
- `bytes`: Audio data for first chunk (WAV format)

**Side Effects**:
- Marks first AudioChunk as COMPLETE
- Adds first chunk to buffer
- Updates PlaybackState.current_chunk_index = 0

**Raises**:
- `ValueError`: If prepare_chunks not called first
- `TTSError`: If synthesis fails

**Blocking**: Yes - blocks until first chunk synthesized (typically 1-2 seconds for 150 words)

**Performance**: Target <3 seconds for first chunk synthesis (measured from extraction complete)

**Example**:
```python
# After prepare_chunks
audio_data = chunker.synthesize_first_chunk()
print(f"First chunk ready: {len(audio_data)} bytes")
# Output: First chunk ready: 524288 bytes (512 KB WAV)
```

---

### `start_background_synthesis() -> None`

**Purpose**: Start background threads to synthesize remaining chunks

**Parameters**: None (uses chunks from prepare_chunks)

**Returns**: None

**Side Effects**:
- Spawns 2-4 background threads (thread pool)
- Each thread synthesizes chunks sequentially (chunks 1, 2, 3, ...)
- Adds synthesized chunks to buffer (queue.Queue)
- Monitors shutdown_event for graceful stop

**Raises**: None (errors logged, synthesis continues)

**Non-Blocking**: Yes - returns immediately after starting threads

**Performance**:
- Synthesizes ~2-3 chunks per second (per thread, CPU-dependent)
- Maintains buffer of 3-5 ready chunks ahead of playback

**Example**:
```python
# After synthesize_first_chunk
chunker.start_background_synthesis()
print("Background synthesis started")
# Synthesis happens in background while first chunk plays
```

---

### `get_next_chunk() -> Optional[bytes]`

**Purpose**: Get next chunk audio from buffer (non-blocking)

**Parameters**: None

**Returns**:
- `bytes`: Audio data for next chunk (WAV format)
- `None`: If buffer empty (no chunks ready yet)

**Side Effects**:
- Pops chunk from buffer (removes from queue)
- Updates PlaybackState.current_chunk_index
- Logs warning if buffer empty (indicates buffering delay)

**Raises**: None (returns None if no chunk available)

**Buffering Logic**:
- If buffer empty: Return None, display "Buffering..." indicator
- PlaybackController should wait ~100ms and retry
- Background synthesis will fill buffer soon

**Example**:
```python
# During playback loop
next_audio = chunker.get_next_chunk()
if next_audio:
    play_audio(next_audio)
else:
    print("Buffering...")
    time.sleep(0.1)  # Wait for synthesis
```

---

### `synthesize_chunk_on_demand(chunk_index: int) -> bytes`

**Purpose**: Synthesize a specific chunk immediately (blocking) when user seeks to unsynthesized chunk

**Parameters**:
- `chunk_index` (int): Index of chunk to synthesize (0-based)

**Returns**:
- `bytes`: Audio data for requested chunk (WAV format)

**Side Effects**:
- Marks AudioChunk as COMPLETE
- Adds chunk to buffer
- Updates PlaybackState.current_chunk_index

**Raises**:
- `ValueError`: If chunk_index out of bounds
- `TTSError`: If synthesis fails

**Blocking**: Yes - blocks until chunk synthesized (typically 1-2 seconds)

**Use Case**: User seeks forward beyond buffer (e.g., skip 5 chunks ahead)

**Example**:
```python
# User seeks to chunk 10, but only chunks 0-3 synthesized
audio_data = chunker.synthesize_chunk_on_demand(10)
print("On-demand synthesis complete")
# Resumes playback at chunk 10
```

---

### `get_chunk_count() -> int`

**Purpose**: Get total number of chunks

**Parameters**: None

**Returns**:
- `int`: Total chunk count

**Side Effects**: None (read-only)

**Raises**: None

**Example**:
```python
total = chunker.get_chunk_count()
print(f"Total chunks: {total}")
# Output: Total chunks: 8
```

---

### `get_buffer_status() -> dict`

**Purpose**: Get current buffer status for monitoring/debugging

**Parameters**: None

**Returns**:
- `dict`: Buffer status with keys:
  - `buffer_size` (int): Current number of chunks in buffer
  - `max_buffer_size` (int): Maximum buffer capacity
  - `chunks_synthesized` (int): Total chunks completed
  - `chunks_pending` (int): Chunks not yet synthesized

**Side Effects**: None (read-only)

**Raises**: None

**Example**:
```python
status = chunker.get_buffer_status()
print(f"Buffer: {status['buffer_size']}/{status['max_buffer_size']}")
print(f"Progress: {status['chunks_synthesized']}/{status['chunks_synthesized'] + status['chunks_pending']}")
# Output:
# Buffer: 4/10
# Progress: 5/8
```

---

### `stop() -> None`

**Purpose**: Stop background synthesis and clean up resources

**Parameters**: None

**Returns**: None

**Side Effects**:
- Sets shutdown_event (signals threads to stop)
- Joins all synthesis threads (with 5s timeout)
- Clears chunk buffer
- Resets internal state

**Raises**: None (graceful shutdown)

**Cleanup**:
- Stops synthesis threads
- Discards unsynthesized chunks
- Frees memory (clears buffer)

**Example**:
```python
# User quits during playback
chunker.stop()
print("Background synthesis stopped")
```

---

### `_split_into_sentences(text: str) -> list[str]` (Private)

**Purpose**: Split text into sentences using regex

**Parameters**:
- `text` (str): Text to split

**Returns**:
- `list[str]`: List of sentences

**Algorithm**:
- Regex: `[.!?]+\s+` (sentence terminators followed by whitespace)
- Edge cases: Handle abbreviations (Mr., Dr.), URLs, decimal numbers

**Note**: Internal method, not part of public API

---

### `_group_sentences_into_chunks(sentences: list[str], target_words: int) -> list[str]` (Private)

**Purpose**: Group sentences into chunks targeting specific word count

**Parameters**:
- `sentences` (list[str]): List of sentences
- `target_words` (int): Target words per chunk (~150)

**Returns**:
- `list[str]`: List of text chunks

**Algorithm**:
1. Iterate sentences, accumulate words
2. When word count ≈ target ± 20%, finalize chunk
3. Respect sentence boundaries (never split mid-sentence)

**Note**: Internal method, not part of public API

---

### `_synthesis_worker_thread() -> None` (Private)

**Purpose**: Background thread that synthesizes chunks from work queue

**Parameters**: None (reads from internal work queue)

**Returns**: None (runs until shutdown_event set)

**Side Effects**:
- Pops chunk index from work queue
- Synthesizes chunk via PiperSynthesizer
- Adds synthesized audio to buffer
- Marks chunk COMPLETE or FAILED
- Checks shutdown_event every iteration

**Error Handling**:
- If synthesis fails: Mark chunk FAILED, log error, continue with next chunk
- If buffer full: Wait 100ms, retry (backpressure)

**Note**: Internal method, not part of public API

---

## Thread Safety

**Status**: Thread-safe via locks and queues

**Shared State**:
- Chunk buffer (queue.Queue): Thread-safe by design
- AudioChunk status: Protected by individual chunk locks
- Work queue: Thread-safe by design

**Synchronization**:
- Buffer queue: thread-safe producer-consumer
- shutdown_event: thread-safe signal
- chunk_lock: Protects AudioChunk.synthesis_status updates

**Threads**:
1. **Main thread**: prepare_chunks, synthesize_first_chunk, get_next_chunk
2. **Synthesis threads (2-4)**: Background chunk synthesis
3. **Playback thread**: Consumes chunks from buffer

---

## Performance Characteristics

| Operation | Time Complexity | Typical Duration | Notes |
|-----------|----------------|------------------|-------|
| `prepare_chunks()` | O(n) | <100ms | n = text length (regex + sentence grouping) |
| `synthesize_first_chunk()` | O(m) | 1-2s | m = chunk words (~150), CPU-bound |
| `start_background_synthesis()` | O(1) | <10ms | Thread spawn, non-blocking |
| `get_next_chunk()` | O(1) | <5ms | Queue pop, non-blocking |
| `synthesize_chunk_on_demand()` | O(m) | 1-2s | Same as synthesize_first_chunk |
| `stop()` | O(t) | <100ms | t = number of threads, join timeout |

**Memory**:
- Each chunk audio: ~500KB-1MB (16-bit WAV, 22050 Hz, mono)
- Buffer capacity: 10 chunks = ~5-10MB
- Total memory: <50MB for 50 chunks

**CPU**:
- Synthesis: CPU-bound, benefits from multi-threading
- Thread count: 2-4 (balances throughput vs CPU contention)

---

## Error Handling

**Philosophy**: Continue playback even if some chunks fail synthesis

**Error Categories**:
1. **Synthesis Errors** (TTSError): Piper synthesis fails for a chunk
2. **Memory Errors** (MemoryError): Buffer full, cannot add more chunks
3. **Threading Errors**: Thread spawn/join failures

**Error Recovery**:
- Chunk synthesis fails: Mark FAILED, log error, skip chunk, continue
- Buffer full: Backpressure - wait 100ms, retry
- Thread error: Log error, continue with remaining threads

**User Impact**:
- Failed chunk: Brief gap in audio, warning message displayed
- Multiple failures: Playback continues with successful chunks

---

## Testing Requirements

**Unit Tests** (`tests/unit/test_chunking.py`):
- ✅ Test prepare_chunks with various text lengths (short, medium, long)
- ✅ Test prepare_chunks respects sentence boundaries
- ✅ Test prepare_chunks with text <50 words (single chunk)
- ✅ Test prepare_chunks with empty/whitespace text (ValueError)
- ✅ Test synthesize_first_chunk returns valid audio
- ✅ Test synthesize_first_chunk with no chunks prepared (ValueError)
- ✅ Test start_background_synthesis spawns threads
- ✅ Test get_next_chunk returns chunks in order
- ✅ Test get_next_chunk with empty buffer (returns None)
- ✅ Test synthesize_chunk_on_demand for specific chunk
- ✅ Test buffer size limit (max 10 chunks)
- ✅ Test stop gracefully shuts down threads
- ✅ Test thread safety (concurrent synthesis + consumption)

**Integration Tests** (`tests/integration/test_chunked_playback.py`):
- ✅ Full workflow: prepare → synthesize first → background synthesis → playback
- ✅ Long article (10,000 words): Verify first chunk within 3s
- ✅ Seamless transitions: Verify <50ms gaps between chunks
- ✅ On-demand synthesis: Seek to unsynthesized chunk, verify recovery
- ✅ Error handling: Inject synthesis failure, verify playback continues

**Performance Tests**:
- ✅ Measure time to first audio (target <3s for 10,000 word article)
- ✅ Measure chunk transition gaps (target <50ms, 95th percentile)
- ✅ Measure memory usage (target <50MB for 50 chunks)

**Coverage Target**: >80% line coverage for ChunkSynthesizer

---

## Example Usage

```python
from src.tts.synthesizer import PiperSynthesizer
from src.tts.chunking import ChunkSynthesizer

# Initialize synthesizer and chunker
synthesizer = PiperSynthesizer(voice="en_US-libritts-high")
chunker = ChunkSynthesizer(synthesizer, chunk_size=150, max_buffer_size=10)

# Split text into chunks
text = "Full article text with thousands of words..."
chunks = chunker.prepare_chunks(text)
print(f"Prepared {len(chunks)} chunks")

# Synthesize first chunk (blocking)
first_audio = chunker.synthesize_first_chunk()
print("First chunk ready, starting playback")

# Start background synthesis for remaining chunks
chunker.start_background_synthesis()

# Play first chunk
play_audio(first_audio)

# Playback loop: consume chunks as they become available
while True:
    next_audio = chunker.get_next_chunk()
    if next_audio:
        play_audio(next_audio)
    else:
        # Buffer empty, wait for synthesis
        print("Buffering...")
        time.sleep(0.1)
    
    if playback_complete():
        break

# Clean up
chunker.stop()
print("Playback complete")
```

---

**Contract Status**: ✅ Complete - All public methods documented with inputs, outputs, side effects, errors, threading model, performance, and examples.
