type RecorderState = "idle" | "recording" | "processing" | "ready";

const app = document.createElement("main");
app.innerHTML = `
  <h1>麦克风录音与音频处理</h1>
  <p id="status">准备就绪</p>
  <button id="start" type="button">开始录音</button>
  <button id="stop" type="button" disabled>停止并处理</button>
  <audio id="player" controls></audio>
  <a id="download" hidden>下载处理后的 WAV</a>
`;
document.body.append(app);

const statusElement = getElement<HTMLParagraphElement>("status");
const startButton = getElement<HTMLButtonElement>("start");
const stopButton = getElement<HTMLButtonElement>("stop");
const player = getElement<HTMLAudioElement>("player");
const downloadLink = getElement<HTMLAnchorElement>("download");

let mediaRecorder: MediaRecorder | null = null;
let microphoneStream: MediaStream | null = null;
let chunks: Blob[] = [];
let resultUrl: string | null = null;

startButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
window.addEventListener("beforeunload", releaseResources);

async function startRecording(): Promise<void> {
  try {
    setState("processing", "正在请求麦克风权限...");
    microphoneStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    });

    chunks = [];
    mediaRecorder = new MediaRecorder(microphoneStream);
    mediaRecorder.addEventListener("dataavailable", (event) => {
      if (event.data.size > 0) chunks.push(event.data);
    });
    mediaRecorder.addEventListener("stop", processRecording, { once: true });
    mediaRecorder.start();
    setState("recording", "正在录音...");
  } catch (error) {
    releaseMicrophone();
    setState("idle", formatError(error));
  }
}

function stopRecording(): void {
  if (mediaRecorder?.state === "recording") {
    setState("processing", "正在处理音频...");
    mediaRecorder.stop();
    releaseMicrophone();
  }
}

async function processRecording(): Promise<void> {
  try {
    const recordedBlob = new Blob(chunks, {
      type: mediaRecorder?.mimeType || "audio/webm",
    });
    const audioContext = new AudioContext();
    const sourceBuffer = await audioContext.decodeAudioData(
      await recordedBlob.arrayBuffer(),
    );
    await audioContext.close();

    const filteredBuffer = await filterAudio(sourceBuffer);
    normalizeAudio(filteredBuffer, 0.9);
    const wavBlob = encodeWav(filteredBuffer);

    if (resultUrl) URL.revokeObjectURL(resultUrl);
    resultUrl = URL.createObjectURL(wavBlob);
    player.src = resultUrl;
    downloadLink.href = resultUrl;
    downloadLink.download = `recording-${Date.now()}.wav`;
    downloadLink.hidden = false;
    setState("ready", "处理完成，可以试听或下载");
  } catch (error) {
    setState("idle", `处理失败：${formatError(error)}`);
  }
}

async function filterAudio(input: AudioBuffer): Promise<AudioBuffer> {
  const offlineContext = new OfflineAudioContext(
    input.numberOfChannels,
    input.length,
    input.sampleRate,
  );
  const source = offlineContext.createBufferSource();
  const highPass = offlineContext.createBiquadFilter();
  const lowPass = offlineContext.createBiquadFilter();
  const compressor = offlineContext.createDynamicsCompressor();

  source.buffer = input;
  highPass.type = "highpass";
  highPass.frequency.value = 80;
  lowPass.type = "lowpass";
  lowPass.frequency.value = 12_000;
  compressor.threshold.value = -24;
  compressor.knee.value = 20;
  compressor.ratio.value = 4;
  compressor.attack.value = 0.01;
  compressor.release.value = 0.25;

  source.connect(highPass);
  highPass.connect(lowPass);
  lowPass.connect(compressor);
  compressor.connect(offlineContext.destination);
  source.start();

  return offlineContext.startRendering();
}

function normalizeAudio(buffer: AudioBuffer, targetPeak: number): void {
  let peak = 0;
  for (let channel = 0; channel < buffer.numberOfChannels; channel += 1) {
    const samples = buffer.getChannelData(channel);
    for (const sample of samples) peak = Math.max(peak, Math.abs(sample));
  }

  if (peak === 0) return;
  const gain = targetPeak / peak;
  for (let channel = 0; channel < buffer.numberOfChannels; channel += 1) {
    const samples = buffer.getChannelData(channel);
    for (let index = 0; index < samples.length; index += 1) {
      samples[index] *= gain;
    }
  }
}

function encodeWav(buffer: AudioBuffer): Blob {
  const channelCount = buffer.numberOfChannels;
  const bytesPerSample = 2;
  const dataSize = buffer.length * channelCount * bytesPerSample;
  const wav = new ArrayBuffer(44 + dataSize);
  const view = new DataView(wav);

  writeText(view, 0, "RIFF");
  view.setUint32(4, 36 + dataSize, true);
  writeText(view, 8, "WAVE");
  writeText(view, 12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, channelCount, true);
  view.setUint32(24, buffer.sampleRate, true);
  view.setUint32(28, buffer.sampleRate * channelCount * bytesPerSample, true);
  view.setUint16(32, channelCount * bytesPerSample, true);
  view.setUint16(34, bytesPerSample * 8, true);
  writeText(view, 36, "data");
  view.setUint32(40, dataSize, true);

  let offset = 44;
  for (let frame = 0; frame < buffer.length; frame += 1) {
    for (let channel = 0; channel < channelCount; channel += 1) {
      const sample = Math.max(-1, Math.min(1, buffer.getChannelData(channel)[frame]));
      view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true);
      offset += bytesPerSample;
    }
  }

  return new Blob([wav], { type: "audio/wav" });
}

function writeText(view: DataView, offset: number, text: string): void {
  for (let index = 0; index < text.length; index += 1) {
    view.setUint8(offset + index, text.charCodeAt(index));
  }
}

function setState(state: RecorderState, message: string): void {
  statusElement.textContent = message;
  startButton.disabled = state === "recording" || state === "processing";
  stopButton.disabled = state !== "recording";
}

function releaseMicrophone(): void {
  microphoneStream?.getTracks().forEach((track) => track.stop());
  microphoneStream = null;
}

function releaseResources(): void {
  releaseMicrophone();
  if (resultUrl) URL.revokeObjectURL(resultUrl);
}

function formatError(error: unknown): string {
  if (error instanceof DOMException && error.name === "NotAllowedError") {
    return "没有麦克风权限，请在浏览器设置中允许访问";
  }
  return error instanceof Error ? error.message : String(error);
}

function getElement<T extends HTMLElement>(id: string): T {
  const element = document.getElementById(id);
  if (!element) throw new Error(`找不到元素 #${id}`);
  return element as T;
}
