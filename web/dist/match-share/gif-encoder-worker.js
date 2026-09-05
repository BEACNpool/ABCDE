/* BEACN match GIF worker. Local, pinned gifenc (MIT); see vendor license/manifest.
 * One job per worker. Terminate this worker to cancel or release it after done.
 */
import { GIFEncoder, quantize, applyPalette } from './vendor/gifenc-1.0.3/index.js';

const LIMITS = Object.freeze({
  maxWidth: 1024, maxHeight: 768, maxPixels: 800 * 600, maxFrames: 48,
  maxRawBytes: 96 * 1024 * 1024, maxDurationMs: 10000,
  targetBytes: 2 * 1024 * 1024, maxOutputBytes: 5 * 1024 * 1024,
});
const PALETTE_SAMPLE_PIXELS = 131072;
// RGB444 bounds the quantizer to at most 4096 bins. This flat-graphic export
// favors predictable mobile CPU/memory over photo/video dithering.
const FORMAT = 'rgb444';
let job = null;
let terminal = false;

function problem(code, message) {
  const error = new Error(message);
  error.code = code;
  throw error;
}

function integer(value, low, high, name) {
  if (!Number.isSafeInteger(value) || value < low || value > high) {
    problem('INVALID_INPUT', `${name} must be an integer from ${low} to ${high}.`);
  }
  return value;
}

function send(type, fields = {}, transfer = []) {
  self.postMessage({ type, jobId: job?.jobId ?? null, ...fields }, transfer);
}

function release() {
  if (job) job.frames.length = 0;
  job = null;
  terminal = true;
}

function init(message) {
  if (job || terminal) problem('INVALID_STATE', 'Create a new worker for each GIF job.');
  if (typeof message.jobId !== 'string' || !/^[A-Za-z0-9_.:-]{1,80}$/.test(message.jobId)) {
    problem('INVALID_INPUT', 'jobId must be a short unique string.');
  }
  const width = integer(message.width, 16, LIMITS.maxWidth, 'width');
  const height = integer(message.height, 16, LIMITS.maxHeight, 'height');
  const frameCount = integer(message.frameCount, 1, LIMITS.maxFrames, 'frameCount');
  const pixels = width * height;
  const rawBytes = pixels * 4 * frameCount;
  if (pixels > LIMITS.maxPixels || rawBytes > LIMITS.maxRawBytes) {
    problem('INPUT_LIMIT', 'GIF dimensions and frame count exceed the memory budget.');
  }
  const repeat = integer(message.repeat ?? 0, -1, 65535, 'repeat');
  const maxColors = integer(message.maxColors ?? 128, 16, 256, 'maxColors');
  const background = message.background ?? [9, 12, 24];
  if (!Array.isArray(background) || background.length !== 3) {
    problem('INVALID_INPUT', 'background must contain three RGB bytes.');
  }
  background.forEach((value) => integer(value, 0, 255, 'background channel'));
  job = { jobId: message.jobId, width, height, pixels, frameCount, repeat,
    maxColors, background: [...background], frames: [], receivedBytes: 0,
    expectedRawBytes: rawBytes, durationMs: 0, phase: 'collect' };
  send('ready', { limits: LIMITS });
}

function frame(message) {
  if (job.phase !== 'collect') problem('INVALID_STATE', 'This GIF job is no longer collecting frames.');
  const index = integer(message.index, 0, job.frameCount - 1, 'frame index');
  if (index !== job.frames.length) problem('FRAME_ORDER', 'Frames must arrive once, in ascending index order.');
  if (!(message.rgba instanceof ArrayBuffer) || message.rgba.byteLength !== job.pixels * 4) {
    problem('FRAME_SIZE', 'rgba must be an exact, attached RGBA ArrayBuffer for the declared dimensions.');
  }
  const delay = integer(message.delay, 20, 1000, 'frame delay');
  if (delay % 10 !== 0) problem('INVALID_DELAY', 'GIF delays must use whole 10 ms units.');
  if (job.durationMs + delay > LIMITS.maxDurationMs) problem('DURATION_LIMIT', 'GIF duration exceeds 10 seconds.');
  if (job.receivedBytes + message.rgba.byteLength > job.expectedRawBytes ||
      job.receivedBytes + message.rgba.byteLength > LIMITS.maxRawBytes) {
    problem('INPUT_LIMIT', 'Received frame data exceeds the declared memory budget.');
  }
  const rgba = new Uint8Array(message.rgba);
  const background = job.background;
  // Canvas export is intended to be opaque. Explicitly flatten alpha so the
  // only GIF transparency is our internal unchanged-pixel optimization.
  for (let offset = 0; offset < rgba.length; offset += 4) {
    const alpha = rgba[offset + 3];
    if (alpha !== 255) {
      for (let channel = 0; channel < 3; channel++) {
        rgba[offset + channel] = Math.floor(
          (rgba[offset + channel] * alpha + background[channel] * (255 - alpha) + 127) / 255);
      }
      rgba[offset + 3] = 255;
    }
  }
  job.frames.push({ rgba, delay });
  job.receivedBytes += rgba.byteLength;
  job.durationMs += delay;
  send('ack', { index, received: job.frames.length, total: job.frameCount });
}

function paletteSamples() {
  const perFrame = Math.min(job.pixels, Math.floor(PALETTE_SAMPLE_PIXELS / job.frameCount));
  const samples = new Uint8Array(perFrame * job.frameCount * 4);
  let cursor = 0;
  for (const { rgba } of job.frames) {
    // Deterministic coverage across every frame, without a second full RGBA copy.
    for (let sample = 0; sample < perFrame; sample++) {
      const offset = Math.floor((sample + 0.5) * job.pixels / perFrame) * 4;
      samples[cursor++] = rgba[offset];
      samples[cursor++] = rgba[offset + 1];
      samples[cursor++] = rgba[offset + 2];
      samples[cursor++] = 255;
    }
  }
  return samples;
}

function stablePaletteLookup(palette) {
  // Upstream applyPalette caches a bin's first encountered RGB value. Calling
  // it separately per frame lets moving art change unchanged text's mapping.
  // Visit every RGB444 bin exactly once at a fixed center, then reuse this
  // immutable mapping for the whole animation.
  const centers = new Uint8Array(4096 * 4);
  for (let bin = 0; bin < 4096; bin++) {
    const offset = bin * 4;
    centers[offset] = ((bin >> 8) & 15) * 16 + 8;
    centers[offset + 1] = ((bin >> 4) & 15) * 16 + 8;
    centers[offset + 2] = (bin & 15) * 16 + 8;
    centers[offset + 3] = 255;
  }
  return applyPalette(centers, palette, FORMAT);
}

function mapStablePalette(rgba, lookup) {
  const indexed = new Uint8Array(rgba.length / 4);
  for (let offset = 0, pixel = 0; offset < rgba.length; offset += 4, pixel++) {
    const bin = ((rgba[offset] >> 4) << 8) | (rgba[offset + 1] & 0xf0) | (rgba[offset + 2] >> 4);
    indexed[pixel] = lookup[bin];
  }
  return indexed;
}

function finish() {
  if (job.phase !== 'collect' || job.frames.length !== job.frameCount ||
      job.receivedBytes !== job.expectedRawBytes) {
    problem('INCOMPLETE_FRAMES', 'All declared frames must be acknowledged before finish.');
  }
  job.phase = 'encode';
  send('progress', { phase: 'palette', completed: 0, total: 1, progress: 0 });
  const palette = quantize(paletteSamples(), job.maxColors - 1, { format: FORMAT });
  if (!Array.isArray(palette) || palette.length < 1 || palette.length > 255) {
    problem('ENCODE_FAILED', 'The encoder could not construct a valid palette.');
  }
  const transparentIndex = palette.length;
  const globalPalette = [...palette, [0, 0, 0]];
  const lookup = stablePaletteLookup(palette);
  send('progress', { phase: 'palette', completed: 1, total: 1, progress: 0.1 });

  const gif = GIFEncoder({ initialCapacity: 128 * 1024 });
  let previous = null;
  for (let index = 0; index < job.frames.length; index++) {
    const source = job.frames[index];
    const current = mapStablePalette(source.rgba, lookup);
    source.rgba = null; // release each retained input as encoding advances
    let encoded = current;
    if (previous) {
      encoded = current.slice();
      for (let pixel = 0; pixel < encoded.length; pixel++) {
        if (current[pixel] === previous[pixel]) encoded[pixel] = transparentIndex;
      }
    }
    gif.writeFrame(encoded, job.width, job.height, {
      palette: index === 0 ? globalPalette : undefined,
      delay: source.delay, repeat: job.repeat, dispose: 1,
      transparent: index > 0, transparentIndex, colorDepth: 8,
    });
    previous = current;
    if (gif.bytesView().byteLength > LIMITS.maxOutputBytes) {
      problem('OUTPUT_LIMIT', 'GIF exceeds the 5 MiB download limit.');
    }
    send('progress', { phase: 'encode', completed: index + 1,
      total: job.frameCount, progress: 0.1 + 0.9 * (index + 1) / job.frameCount });
  }
  gif.finish();
  const bytes = gif.bytes();
  if (bytes.byteLength > LIMITS.maxOutputBytes) problem('OUTPUT_LIMIT', 'GIF exceeds the 5 MiB download limit.');
  send('done', { buffer: bytes.buffer, byteLength: bytes.byteLength,
    width: job.width, height: job.height, frameCount: job.frameCount,
    durationMs: job.durationMs, repeat: job.repeat, paletteColors: palette.length,
    deltaFrames: true, opaque: true, overTarget: bytes.byteLength > LIMITS.targetBytes,
  }, [bytes.buffer]);
  release();
}

self.addEventListener('message', ({ data: message }) => {
  try {
    if (!message || typeof message !== 'object' || Array.isArray(message)) {
      problem('INVALID_INPUT', 'Expected a GIF worker message object.');
    }
    if (message.type === 'init') return init(message);
    if (!job || terminal) problem('INVALID_STATE', 'Initialize a new GIF worker before sending frames.');
    if (message.jobId !== job.jobId) problem('JOB_MISMATCH', 'Message does not belong to this GIF job.');
    if (message.type === 'frame') return frame(message);
    if (message.type === 'finish') return finish();
    problem('INVALID_INPUT', 'Unknown GIF worker message type.');
  } catch (error) {
    const messageJobId = typeof message?.jobId === 'string' &&
      /^[A-Za-z0-9_.:-]{1,80}$/.test(message.jobId) ? message.jobId : null;
    send('error', { jobId: job?.jobId ?? messageJobId, code: error?.code || 'ENCODE_FAILED',
      message: error?.message || 'GIF encoding failed.' });
    release();
  }
});
