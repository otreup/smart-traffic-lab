const canvas = document.getElementById("networkCanvas");
const ctx = canvas.getContext("2d");
const snapshot = document.getElementById("snapshot");
const detCount = document.getElementById("detCount");
const modelName = document.getElementById("modelName");
const networkState = document.getElementById("networkState");
const detectionsList = document.getElementById("detectionsList");
const lastUpdate = document.getElementById("lastUpdate");
const cameraStatus = document.getElementById("cameraStatus");
const mapStatus = document.getElementById("mapStatus");
const refreshBtn = document.getElementById("refreshBtn");
const toggleSimBtn = document.getElementById("toggleSimBtn");
const webcamBtn = document.getElementById("webcamBtn");
const esp32Btn = document.getElementById("esp32Btn");
const autoBtn = document.getElementById("autoBtn");
const pcViewBtn = document.getElementById("pcViewBtn");
const apiViewBtn = document.getElementById("apiViewBtn");
const directViewBtn = document.getElementById("directViewBtn");
const pcCamera = document.getElementById("pcCamera");
const directCamera = document.getElementById("directCamera");
const openCameraLink = document.getElementById("openCameraLink");

let network = null;
let vehicles = [];
let running = true;
let currentDecision = null;
let modelReady = false;
let cameraStreamStarted = false;
let activeCameraView = "pc";
let cameraSource = "webcam";
let cameraStreamVersion = 0;
let pcStream = null;

async function startPcCamera() {
  if (pcStream) return;
  try {
    pcStream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 640 }, height: { ideal: 480 } },
      audio: false,
    });
    pcCamera.srcObject = pcStream;
    cameraStatus.textContent = "PC activa";
    detectionsList.innerHTML = '<div class="item"><strong>Webcam PC</strong><span>video continuo del navegador</span></div>';
  } catch (error) {
    cameraStatus.textContent = "Permiso camara";
    detectionsList.innerHTML = `<div class="item"><strong>No abrio la webcam</strong><span>${error.message}</span></div>`;
  }
}

function startCameraStream(force = false) {
  if (cameraStreamStarted && !force) return;
  snapshot.src = `/video_feed?v=${cameraStreamVersion}&t=${Date.now()}`;
  cameraStreamStarted = true;
}

function updateCameraButtons() {
  webcamBtn.classList.toggle("active", cameraSource === "webcam");
  esp32Btn.classList.toggle("active", cameraSource === "esp32");
  autoBtn.classList.toggle("active", cameraSource === "auto");
}

async function setCameraSource(source) {
  const response = await fetch(`/api/camera/${source}`, { method: "POST" });
  const data = await response.json();
  if (!data.ok) {
    detectionsList.innerHTML = `<div class="item"><strong>Error camara</strong><span>${data.error}</span></div>`;
    return;
  }
  cameraSource = data.camera.source;
  cameraStreamVersion = data.camera.stream_version;
  updateCameraButtons();
  if (source === "webcam") {
    pcViewBtn.click();
  } else if (source === "esp32") {
    directViewBtn.click();
  } else {
    apiViewBtn.click();
    startCameraStream(true);
  }
}

snapshot.addEventListener("error", () => {
  cameraStatus.textContent = "Reintentando";
  snapshot.src = `/snapshot?t=${Date.now()}`;
});

function resizeCanvas() {
  const rect = canvas.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;
  canvas.width = Math.max(600, Math.floor(rect.width * ratio));
  canvas.height = Math.max(360, Math.floor(rect.height * ratio));
}

function transform(point, bounds) {
  const padding = 42;
  const width = canvas.width - padding * 2;
  const height = canvas.height - padding * 2;
  const dx = Math.max(1, bounds.max_x - bounds.min_x);
  const dy = Math.max(1, bounds.max_y - bounds.min_y);
  const scale = Math.min(width / dx, height / dy);
  const x = padding + (point[0] - bounds.min_x) * scale;
  const y = canvas.height - padding - (point[1] - bounds.min_y) * scale;
  return [x, y];
}

function drawNetwork() {
  resizeCanvas();
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#0f1417";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  if (!network || !network.found || !network.bounds) {
    ctx.fillStyle = "#9aa7b2";
    ctx.font = "18px Arial";
    ctx.fillText("Copia tu archivo SUMO en la carpeta sumo/ para ver la carretera aqui.", 34, 58);
    return;
  }

  ctx.lineCap = "round";
  for (const edge of network.edges) {
    for (const lane of edge.lanes) {
      if (!lane.shape || lane.shape.length < 2) continue;
      ctx.beginPath();
      lane.shape.forEach((point, index) => {
        const [x, y] = transform(point, network.bounds);
        if (index === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.strokeStyle = "#52616d";
      ctx.lineWidth = 3;
      ctx.stroke();
    }
  }

  for (const junction of network.junctions) {
    const [x, y] = transform([junction.x, junction.y], network.bounds);
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fillStyle = junction.type === "traffic_light" ? "#f59e0b" : "#22c55e";
    ctx.fill();
  }

  for (const vehicle of vehicles) {
    const lane = vehicle.lane;
    if (!lane.shape || lane.shape.length < 2) continue;
    const segmentIndex = Math.floor(vehicle.t * (lane.shape.length - 1));
    const nextIndex = Math.min(segmentIndex + 1, lane.shape.length - 1);
    const local = vehicle.t * (lane.shape.length - 1) - segmentIndex;
    const a = lane.shape[segmentIndex];
    const b = lane.shape[nextIndex];
    const point = [a[0] + (b[0] - a[0]) * local, a[1] + (b[1] - a[1]) * local];
    const [x, y] = transform(point, network.bounds);
    ctx.fillStyle = vehicle.color;
    ctx.fillRect(x - 5, y - 5, 10, 10);
  }

  if (currentDecision) {
    ctx.fillStyle = "#edf2f4";
    ctx.font = "16px Arial";
    ctx.fillText(`Verde: ${currentDecision.green_label} (${currentDecision.green_seconds}s)`, 34, canvas.height - 34);
  }
}

function buildVehicles() {
  vehicles = [];
  if (!network || !network.found) return;
  const lanes = network.edges.flatMap(edge => edge.lanes).filter(lane => lane.shape && lane.shape.length > 1);
  for (let i = 0; i < Math.min(22, lanes.length); i += 1) {
    vehicles.push({ lane: lanes[i], t: Math.random(), speed: 0.0015 + Math.random() * 0.003, color: i % 3 === 0 ? "#22c55e" : i % 3 === 1 ? "#38bdf8" : "#f59e0b" });
  }
}

async function loadNetwork() {
  const response = await fetch("/api/network");
  network = await response.json();
  if (network.found) {
    mapStatus.textContent = `${network.edge_count} vias, ${network.junction_count} nodos`;
    networkState.textContent = "OK";
  } else {
    mapStatus.textContent = "Sin red";
    networkState.textContent = "Pendiente";
  }
  buildVehicles();
  drawNetwork();
}

async function refreshCamera() {
  try {
    if (activeCameraView === "pc") {
      await startPcCamera();
      detCount.textContent = "0";
      lastUpdate.textContent = new Date().toLocaleTimeString();
      return;
    }

    if (activeCameraView === "direct") {
      detCount.textContent = "0";
      cameraStatus.textContent = "ESP32 web";
      detectionsList.innerHTML = '<div class="item"><strong>Vista ESP32</strong><span>YOLO se activa en pestaña API</span></div>';
      lastUpdate.textContent = new Date().toLocaleTimeString();
      return;
    }

    startCameraStream();
    if (!modelReady) {
      detCount.textContent = "0";
      detectionsList.innerHTML = '<div class="item"><strong>IA pendiente</strong><span>descargar o entrenar YOLO</span></div>';
      cameraStatus.textContent = "Camara";
      lastUpdate.textContent = new Date().toLocaleTimeString();
      return;
    }
    const response = await fetch("/detect/live");
    const data = await response.json();
    if (!data.ok) {
      detCount.textContent = "0";
      currentDecision = data.decision || currentDecision;
      detectionsList.innerHTML = `<div class="item"><strong>YOLO sin iniciar</strong><span>${data.error || "revisa el modelo"}</span></div>`;
      cameraStatus.textContent = "Camara";
      lastUpdate.textContent = new Date().toLocaleTimeString();
      return;
    }
    detCount.textContent = data.count ?? 0;
    currentDecision = data.decision || currentDecision;
    detectionsList.innerHTML = "";
    for (const item of data.detections || []) {
      const row = document.createElement("div");
      row.className = "item";
      row.innerHTML = `<strong>${item.label}</strong><span>${Math.round(item.confidence * 100)}%</span>`;
      detectionsList.appendChild(row);
    }
    if (!data.detections || data.detections.length === 0) {
      detectionsList.innerHTML = '<div class="item"><strong>Sin detecciones</strong><span>0%</span></div>';
    }
    cameraStatus.textContent = "Activa";
    lastUpdate.textContent = new Date().toLocaleTimeString();
  } catch (error) {
    cameraStatus.textContent = "Sin conexion";
    detectionsList.innerHTML = `<div class="item"><strong>Error</strong><span>${error.message}</span></div>`;
  }
}

async function loadStatus() {
  try {
    const response = await fetch("/api/status");
    const data = await response.json();
    modelName.textContent = String(data.model || "-").split(/[\\/]/).pop();
  if (data.camera_status) {
      cameraSource = data.camera_status.source;
      cameraStreamVersion = data.camera_status.stream_version;
      updateCameraButtons();
    }
    if (data.camera_url) {
      directCamera.src = data.camera_url;
      openCameraLink.href = data.camera_url;
    }
    modelReady = Boolean(data.model_ready);
    if (data.model_status && !data.model_status.ready) {
      detectionsList.innerHTML = `<div class="item"><strong>IA pendiente</strong><span>${data.model_status.message}</span></div>`;
    }
    currentDecision = data.decision;
  } catch {
    modelName.textContent = "-";
  }
}

async function stepSimulation() {
  try {
    const response = await fetch("/api/simulation/step");
    const data = await response.json();
    currentDecision = data.decision;
  } catch {
    currentDecision = null;
  }
}

function animate() {
  if (running) {
    for (const vehicle of vehicles) {
      vehicle.t = (vehicle.t + vehicle.speed) % 1;
    }
  }
  drawNetwork();
  requestAnimationFrame(animate);
}

refreshBtn.addEventListener("click", () => {
  loadStatus();
  loadNetwork();
  refreshCamera();
});

toggleSimBtn.addEventListener("click", () => {
  running = !running;
  toggleSimBtn.textContent = running ? "Pausar simulacion" : "Continuar simulacion";
});

webcamBtn.addEventListener("click", () => setCameraSource("webcam"));
esp32Btn.addEventListener("click", () => setCameraSource("esp32"));
autoBtn.addEventListener("click", () => setCameraSource("auto"));

pcViewBtn.addEventListener("click", () => {
  activeCameraView = "pc";
  pcViewBtn.classList.add("active");
  apiViewBtn.classList.remove("active");
  directViewBtn.classList.remove("active");
  pcCamera.classList.add("active");
  snapshot.classList.remove("active");
  directCamera.classList.remove("active");
  refreshCamera();
});

apiViewBtn.addEventListener("click", () => {
  activeCameraView = "api";
  pcViewBtn.classList.remove("active");
  apiViewBtn.classList.add("active");
  directViewBtn.classList.remove("active");
  pcCamera.classList.remove("active");
  snapshot.classList.add("active");
  directCamera.classList.remove("active");
  refreshCamera();
});

directViewBtn.addEventListener("click", () => {
  activeCameraView = "direct";
  pcViewBtn.classList.remove("active");
  directViewBtn.classList.add("active");
  apiViewBtn.classList.remove("active");
  pcCamera.classList.remove("active");
  directCamera.classList.add("active");
  snapshot.classList.remove("active");
  refreshCamera();
});

window.addEventListener("resize", drawNetwork);

loadStatus();
loadNetwork();
refreshCamera();
setInterval(refreshCamera, 4000);
setInterval(stepSimulation, 1200);
animate();
