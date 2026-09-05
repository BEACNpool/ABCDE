# Local GIF encoder for match sharing

`web/dist/match-share/gif-encoder-worker.js` encodes caller-rendered Canvas2D
RGBA frames in a dedicated module worker. It contains no DOM capture, network
request, wallet access or financial logic. The client owns the frozen snapshot,
frame drawing, cancel controls, preview, download and native share interaction.

The encoder is [gifenc 1.0.3](https://github.com/mattdesl/gifenc), pinned to
commit [`27db5b982dba701ca440b55ea36fad3999040973`](https://github.com/mattdesl/gifenc/tree/27db5b982dba701ca440b55ea36fad3999040973).
Its eight source modules are vendored **without modification** under
`web/dist/match-share/vendor/gifenc-1.0.3/`, alongside the complete upstream
MIT license and a `VENDOR.json` provenance/hash manifest. All imports are
relative local files; there is no runtime CDN or npm dependency. The source
and license total 32,455 bytes before HTTP compression. Original attribution
comments, including the quantizer and LZW contributors, are preserved.

## Message contract

Create a fresh worker for each export:

```js
const worker = new Worker(
  new URL('match-share/gif-encoder-worker.js', location.href),
  { type: 'module' }
);
worker.postMessage({
  type: 'init', jobId: 'export-123',
  width: 800, height: 600, frameCount: 36, repeat: 0
});
```

The worker replies `{type:'ready', jobId, limits}`. `jobId` must be a string of
1–80 letters, digits, underscores, periods, colons or hyphens. Every later
message must carry that same ID.

After `ready`, submit frames in exact index order. Transfer the **whole exact
ArrayBuffer** returned by `getImageData`, not its typed-array wrapper:

```js
const rgba = context.getImageData(0, 0, 800, 600).data.buffer;
worker.postMessage({
  type: 'frame', jobId: 'export-123', index,
  rgba, delay: [80, 90, 80][index % 3]
}, [rgba]);
// rgba is now detached from the caller.
```

Wait for `{type:'ack', jobId, index, received, total}` before drawing/sending
the next frame. This avoids an unbounded caller-side message queue. The
36 delays `[80,90,80] × 12` total exactly 3,000 ms. Acknowledgment means that
frame was validated and retained, not yet encoded.

After the final acknowledgment, send `{type:'finish', jobId}`. Encoding emits:

```js
{
  type: 'progress', jobId,
  phase: 'palette' /* or 'encode' */,
  completed, total,
  progress // monotonic 0..1 across both phases
}
```

Palette work occupies progress 0–0.1; frame encoding occupies 0.1–1. The result
is a transferable buffer:

```js
{
  type: 'done', jobId, buffer, byteLength,
  width, height, frameCount, durationMs, repeat, paletteColors,
  deltaFrames: true, opaque: true, overTarget
}
```

Use `new Blob([buffer], {type:'image/gif'})` or a `File` with the same MIME
type. `byteLength` equals the buffer's byte length. The worker transfers its
ownership of that buffer to the caller; it does not encode a data URL.

Failures emit `{type:'error', jobId, code, message}` and release retained
frames. A valid submitted ID is included even when initialization fails.
Malformed/missing IDs can produce `jobId:null`. Codes include `INVALID_INPUT`,
`INVALID_STATE`, `INPUT_LIMIT`, `FRAME_SIZE`, `FRAME_ORDER`, `INVALID_DELAY`,
`DURATION_LIMIT`, `JOB_MISMATCH`, `INCOMPLETE_FRAMES`, `OUTPUT_LIMIT` and
`ENCODE_FAILED`. No incomplete GIF is returned on failure.

## Bounds and cancellation

| Setting | Bound/default |
| --- | --- |
| Width / height | Integer 16–1,024 / 16–768 |
| Total pixels per frame | At most 480,000; 800 × 600 is supported |
| Frames | Integer 1–48 |
| Retained RGBA | Declared total at most 96 MiB; every frame must be exactly width × height × 4 bytes |
| Frame delay | Integer 20–1,000 ms, divisible by 10 |
| Total duration | At most 10,000 ms |
| `repeat` | Default 0: infinite loop; −1: play once; otherwise integer repetitions up to 65,535 |
| `maxColors` | Optional integer 16–256; default 128, with one entry reserved for delta transparency |
| `background` | Optional three RGB bytes; default `[9,12,24]` |
| Output | 2 MiB target; 5 MiB hard limit |

The standard 800 × 600 × 36 export retains 69,120,000 RGBA bytes (about
65.9 MiB) for its global palette. It does not accumulate an additional full
RGBA copy. After palette selection, each retained frame is released as it is
encoded; only small indexed-frame buffers and the GIF stream remain.

Cancel with `worker.terminate()`. This also stops synchronous quantization or
LZW encoding, so cancellation does not wait for a queued worker command. The
client should terminate after `done` or `error` as well. A finished/failed
worker cannot be reused; retry with a fresh worker and newly rendered buffers.

The client must keep its own timeout and stale-job guard around worker startup
and message delivery. The worker cannot impose limits on messages that a
hostile caller has already queued outside its execution context; the supported
UI sends only one frame at a time and waits for acknowledgment.

## Encoding and image semantics

All nonopaque RGBA pixels are composited onto the chosen opaque background
before quantization. A deterministic sample spread across **every frame**
builds one global palette, bounded to 131,072 samples. RGB444 quantization
bounds the histogram to 4,096 bins, keeping work predictable for this mostly
flat scoreboard. There is no dithering. This trades some photographic color
detail for compact, stable text and graphic colors.

The palette alone is insufficient to guarantee stable colors. Upstream
`applyPalette` memoizes the first RGB value encountered in each RGB444 bin
**per call**. Calling it separately on every frame allowed moving artwork
earlier in scan order to change the mapped color of unchanged score text.
The worker therefore constructs one 4,096-entry bin-to-palette lookup per job:
it passes all fixed RGB444 bin centers through upstream `applyPalette` once,
then maps every frame through that same immutable lookup. Identical source
RGB values always get the same palette index, regardless of animation or
scan order. This adds a 4 KiB lookup and a temporary 16 KiB center table;
the upstream vendor files remain unchanged.

The first GIF frame paints the complete opaque image. Every later frame uses
the same palette; pixels unchanged from the previous fully rendered frame are
replaced with a reserved transparent index. GIF disposal method 1 retains the
previous image. Pixels exposed behind moving artwork are painted with their
new background color, preventing trails or holes. These are full-size delta
frames, not cropped rectangles. GIF formatting and compression are entirely
provided by the pinned library; this is not a handwritten GIF/LZW encoder.

`opaque:true` describes the **composited animation**, even though later GIF
frames use transparency internally. The 2 MiB target is not guaranteed for
arbitrary input; `overTarget:true` reports a valid GIF between 2 and 5 MiB. An
output above 5 MiB is rejected before any downloadable buffer is exposed.

## Verification evidence

The worker was executed as an actual worker with transferred buffers, using a
small Node worker-thread bridge for the standard Web Worker event methods.
Independent Pillow decoding checked all pixels and GIF metadata, rather than
trusting encoder metadata alone. Local test artifacts are under
`~/tmp/beacnbot-gif-encoder-test/` on midnight:

- `test-worker.mjs`, `worker-shim.mjs`: reproducible protocol/encoder harness.
- `worker-test-receipt.json`: 13 passing behavioral/failure checks, including
  a real high-entropy export rejected at the 5 MiB cap.
- `synthetic-scoreboard.gif`: 800 × 600, 36 frames, exactly 3,000 ms, loop 0,
  57,375 bytes. All input buffers detached after transfer; 38 progress messages
  were monotonic. Measured harness time was about 0.26 seconds on midnight, not a mobile
  performance guarantee.
- `pillow-decoder-receipt.json`: all 36 decoded RGB frames exactly match the
  synthetic source pixels, all composed alpha values are 255, and every
  disposal method/delay matches the intended sequence.

The synthetic GIF SHA256 is
`812d2b2cefd73ae5e6904e8f575f48e90970da9ae28fa94e11fae146e29e30d9`.
Separate browser QA exercises the actual renderer, download and client
cancellation/retry lifecycle. When intercepting test data, intercept only the
fixture JSON URLs: broad Puppeteer interception was observed to stall module
worker startup and falsely resemble an encoder timeout. With worker imports
untouched, actual setup and profit scenes encoded successfully below 130 KB.
Root also independently encoded and Pillow-decoded the actual loss scene:
140,468 bytes, 800 × 600, 36 frames, 3,000 ms, loop 0, with a successful visual
review. This confirms the target on real rendered match artwork as well as
the synthetic pixel-exact fixture.

The stable-palette patch reran all 13 encoder checks and added an adversarial
decoded-image regression. `test-stable-palette.mjs` places a moving gray patch
earlier in scan order than unchanged gray text. Patch values 80/95 and text
value 85 occupy the same RGB444 bin; neighboring palette values expose the
old first-encounter cache behavior. `stable-palette-regression-receipt.json`
records **144 changed static-text pixels before the fix, zero after**; the
maximum channel change falls from 17 to zero. The before/after GIFs are
retained beside that receipt. This test explicitly fails under the archived
old worker and passes under the fixed worker.

Independent browser download/Pillow checks then verified the actual latest
setup GIF (95,031 bytes) and actual loss GIF (135,493 bytes). Both have
**zero changed score or move-caption pixels across all 36 decoded frames**.
The comparison uses exact pixel equality, with no relaxed tolerance.
