<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue';

const props = defineProps({
  queue:           { type: Array,   default: () => [] },
  activeIndex:     { type: Number,  default: -1 },
  gpsLat:          { type: Number,  default: 8.4803 },
  gpsLng:          { type: Number,  default: 124.6498 },
  heading:         { type: Number,  default: 0 },
  isRunning:       { type: Boolean, default: false },
  mapClickEnabled: { type: Boolean, default: false },
  pendingPins:     { type: Array,   default: () => [] },
});

const emit = defineEmits(['add-waypoint', 'update-waypoint', 'update-pending-pin']);

// ── DOM / Leaflet state ────────────────────────────────────────────────────
const mapContainer = ref(null);
let map         = null;
let L           = null;
let droneMarker = null;
let wpMarkers   = [];
let routeLine   = null;
let distLabels  = [];
let pendingMarkers = []; // preview pins while picker is active

// ── Helpers ────────────────────────────────────────────────────────────────
const toRad = (d) => (d * Math.PI) / 180;

// Move (lat,lng) by forwardM metres along heading and rightM metres perpendicular-right
const applyMove = (lat, lng, hdgDeg, forwardM, rightM) => {
  const latPerM = 1 / 111320;
  const lngPerM = 1 / (111320 * Math.cos(toRad(lat)));
  const θ = toRad(hdgDeg);
  return [
    lat + (Math.cos(θ) * forwardM - Math.sin(θ) * rightM) * latPerM,
    lng + (Math.sin(θ) * forwardM + Math.cos(θ) * rightM) * lngPerM,
  ];
};

// Haversine distance in metres
const distM = (a, b) => {
  const R = 6371000;
  const dLat = toRad(b.lat - a.lat);
  const dLng = toRad(b.lng - a.lng);
  const x =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(a.lat)) * Math.cos(toRad(b.lat)) * Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(x), Math.sqrt(1 - x));
};

// ── Build GPS waypoints from relative commands ─────────────────────────────
const buildWaypoints = () => {
  let lat = props.gpsLat;
  let lng = props.gpsLng;
  let hdg = props.heading || 0;

  const points = [{ lat, lng, idx: -1, label: 'Origin', val: '' }];

  props.queue.forEach((cmd, i) => {
    const v = parseFloat(cmd.val) || 0;
    const m = v / 100; // cm → metres

    switch (cmd.type) {
      case 'forward': [lat, lng] = applyMove(lat, lng, hdg, m,  0); break;
      case 'back':    [lat, lng] = applyMove(lat, lng, hdg, -m, 0); break;
      case 'right':   [lat, lng] = applyMove(lat, lng, hdg, 0,  m); break;
      case 'left':    [lat, lng] = applyMove(lat, lng, hdg, 0, -m); break;
      case 'go': {
        const parts = (cmd.val || '').split(' ');
        const x = (parseFloat(parts[0]) || 0) / 100; // right (cm→m)
        const y = (parseFloat(parts[1]) || 0) / 100; // forward (cm→m)
        [lat, lng] = applyMove(lat, lng, hdg, y, x);
        break;
      }
      case 'cw':  hdg = (hdg + v) % 360; return;
      case 'ccw': hdg = ((hdg - v) % 360 + 360) % 360; return;
      case 'waypoint': {
        const parts = (cmd.val || '').split(' ');
        const wpLat = parseFloat(parts[0]);
        const wpLng = parseFloat(parts[1]);
        if (!isNaN(wpLat) && !isNaN(wpLng)) { lat = wpLat; lng = wpLng; }
        break;
      }
      default: return; // up/down/hover → no horizontal movement
    }

    points.push({ lat, lng, idx: i, label: cmd.label, val: cmd.val, type: cmd.type, unit: cmd.unit });
  });

  return points;
};

// ── Icon factories ─────────────────────────────────────────────────────────
const makeCirclePin = (leaflet, stepNum, state) => {
  const isActive    = state === 'active';
  const isCompleted = state === 'completed';
  const bg   = isActive ? '#F59E0B' : isCompleted ? '#EF4444' : '#3B82F6';
  const ring = isActive ? '#B45309' : isCompleted ? '#991B1B' : '#1D4ED8';
  const sz   = isActive ? 30 : 24;
  const wrap = sz + 16;
  const half = wrap / 2;
  return leaflet.divIcon({
    html: `
      <div style="position:relative;width:${wrap}px;height:${wrap}px;display:flex;align-items:center;justify-content:center;">
        ${isActive ? `<div class="mp-pulse-ring" style="position:absolute;inset:0;border-radius:50%;border:2px solid ${bg}55;"></div>` : ''}
        <div style="
          width:${sz}px;height:${sz}px;
          background:${bg};
          border:2.5px solid ${ring};
          border-radius:50%;
          display:flex;align-items:center;justify-content:center;
          font-size:${Math.round(sz * 0.38)}px;
          font-weight:900;color:white;font-family:ui-monospace,monospace;
          box-shadow:0 0 0 4px ${bg}25, 0 4px 18px rgba(0,0,0,0.65);
          position:relative;z-index:1;
          letter-spacing:-0.5px;
        ">${stepNum}</div>
      </div>`,
    className:  '',
    iconSize:   [wrap, wrap],
    iconAnchor: [half, half],
  });
};

const makeDroneIcon = (leaflet, heading) =>
  leaflet.divIcon({
    html: `
      <div style="
        width:46px;height:46px;
        display:flex;align-items:center;justify-content:center;
        transform:rotate(${heading}deg);transform-origin:50% 50%;
        transition:transform 0.35s ease;
      ">
        <svg xmlns="http://www.w3.org/2000/svg" width="34" height="34" viewBox="0 0 24 24" fill="white"
             style="filter:drop-shadow(0 0 8px rgba(255,255,255,0.85)) drop-shadow(0 2px 6px rgba(0,0,0,0.7));">
          <path d="M12 2L4.5 20.29L5.21 21L12 18L18.79 21L19.5 20.29L12 2Z"/>
        </svg>
      </div>`,
    className:  '',
    iconSize:   [46, 46],
    iconAnchor: [23, 23],
  });

// Cyan dashed icon for uncommitted preview pins
const makePendingPin = (leaflet, num) => leaflet.divIcon({
  html: `
    <div style="position:relative;width:40px;height:40px;display:flex;align-items:center;justify-content:center;">
      <div class="mp-pulse-ring" style="position:absolute;inset:0;border-radius:50%;border:2px solid rgba(6,182,212,0.5);"></div>
      <div style="
        width:26px;height:26px;
        background:rgba(6,182,212,0.22);
        border:2px solid rgb(6,182,212);
        border-radius:50%;
        display:flex;align-items:center;justify-content:center;
        font-size:10px;font-weight:900;color:rgb(6,182,212);font-family:ui-monospace,monospace;
        box-shadow:0 0 0 4px rgba(6,182,212,0.18), 0 4px 14px rgba(0,0,0,0.6);
        position:relative;z-index:1;cursor:grab;
      ">${num}</div>
    </div>`,
  className: '',
  iconSize:   [40, 40],
  iconAnchor: [20, 20],
});

// ── Clear overlays ─────────────────────────────────────────────────────────
const clearOverlays = () => {
  wpMarkers.forEach((m) => m.remove());   wpMarkers = [];
  distLabels.forEach((l) => l.remove()); distLabels = [];
  if (routeLine) { routeLine.remove(); routeLine = null; }
};

const clearPendingMarkers = () => {
  pendingMarkers.forEach((m) => m.remove());
  pendingMarkers = [];
};

// ── Render preview (pending) pins ──────────────────────────────────────────
// Shows instant draggable cyan pins for uncommitted "Fly to Waypoint" clicks.
const renderPendingPins = () => {
  if (!map || !L) return;
  clearPendingMarkers();

  if (!props.pendingPins.length) return;

  // Dashed preview polyline: last committed point → through all pending pins
  const committedPts = buildWaypoints();
  const start = committedPts[committedPts.length - 1] ?? { lat: props.gpsLat, lng: props.gpsLng };
  const previewLls = [[start.lat, start.lng], ...props.pendingPins.map((p) => [p.lat, p.lng])];
  if (previewLls.length > 1) {
    const previewLine = L.polyline(previewLls, {
      color:     'rgba(6,182,212,0.55)',
      weight:    1.5,
      dashArray: '6 5',
    }).addTo(map);
    pendingMarkers.push(previewLine);
  }

  // Pending pin markers — draggable, cyan, pulsing
  props.pendingPins.forEach((pin, idx) => {
    const marker = L.marker([pin.lat, pin.lng], {
      icon:         makePendingPin(L, idx + 1),
      draggable:    true,
      zIndexOffset: 2000,
    });

    marker.on('dragend', () => {
      const ll = marker.getLatLng();
      emit('update-pending-pin', { idx, lat: ll.lat, lng: ll.lng });
    });

    marker.bindTooltip(
      `<b>Pending ${idx + 1}</b> — drag to adjust · click Done to add`,
      { direction: 'top', className: 'mp-tt' }
    );

    marker.addTo(map);
    pendingMarkers.push(marker);
  });
};

// ── Render path + markers ──────────────────────────────────────────────────
const renderPath = () => {
  if (!map || !L) return;
  clearOverlays();

  const pts = buildWaypoints();
  if (pts.length < 1) return;

  const lls = pts.map((p) => [p.lat, p.lng]);

  // Polyline
  if (lls.length > 1) {
    routeLine = L.polyline(lls, {
      color:  'rgba(255,255,255,0.85)',
      weight: 2,
    }).addTo(map);
  }

  // Segment distance labels
  for (let i = 0; i + 1 < pts.length; i++) {
    const pt   = pts[i + 1];
    const mid  = [(pts[i].lat + pt.lat) / 2, (pts[i].lng + pt.lng) / 2];
    // Show command value or computed distance. For 'waypoint' always show haversine metres.
    const raw  = (pt.type === 'waypoint' || pt.val == null || pt.val === '')
      ? `${Math.round(distM(pts[i], pt))}m`
      : `${pt.val}${pt.unit ?? 'cm'}`;
    const lbl  = L.marker(mid, {
      icon: L.divIcon({
        html: `<div style="
          background:rgba(10,20,40,0.8);backdrop-filter:blur(5px);
          color:white;font-size:10px;font-weight:700;
          padding:2px 7px;border-radius:5px;
          border:1px solid rgba(255,255,255,0.18);white-space:nowrap;
          pointer-events:none;">
          ${raw}
        </div>`,
        className:   '',
        iconAnchor:  [0, 0],
      }),
      interactive: false,
    }).addTo(map);
    distLabels.push(lbl);
  }

  // Waypoint markers (skip index 0 = origin / drone position)
  pts.forEach((pt, i) => {
    if (i === 0) return;

    const isActive    = props.activeIndex === pt.idx;
    const isCompleted = props.isRunning && props.activeIndex > pt.idx;
    const state       = isActive ? 'active' : isCompleted ? 'completed' : 'pending';

    const isDraggable = pt.type === 'waypoint' && !props.isRunning;

    const marker = L.marker([pt.lat, pt.lng], {
      icon:         makeCirclePin(L, i, state),
      zIndexOffset: isActive ? 500 : 0,
      draggable:    isDraggable,
    });

    // Draggable waypoint — emit new position on drop
    if (isDraggable) {
      marker.on('dragend', () => {
        const ll = marker.getLatLng();
        emit('update-waypoint', { idx: pt.idx, lat: ll.lat, lng: ll.lng });
      });
      // Show a drag cursor on hover
      marker.on('mouseover', () => {
        marker.getElement()?.style.setProperty('cursor', 'grab');
      });
    }

    marker.bindTooltip(
      `<b>Step ${pt.idx + 1}</b>: ${pt.label}${pt.val ? ` — ${pt.val} ${pt.unit ?? ''}` : ''}`,
      { direction: 'top', className: 'mp-tt' }
    );

    marker.addTo(map);
    wpMarkers.push(marker);
  });
};

// ── Lifecycle ──────────────────────────────────────────────────────────────
onMounted(async () => {
  L = (await import('leaflet')).default ?? (await import('leaflet'));
  delete L.Icon.Default.prototype._getIconUrl;
  L.Icon.Default.mergeOptions({ iconUrl: '', shadowUrl: '' });

  map = L.map(mapContainer.value, {
    center:             [props.gpsLat, props.gpsLng],
    zoom:               18,
    zoomControl:        false,
    attributionControl: false,
  });

  // ESRI World Imagery — satellite tiles
  L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    { maxZoom: 22, attribution: 'Tiles © Esri' }
  ).addTo(map);

  // Attribution pill (bottom-right, small)
  L.control.attribution({ position: 'bottomright', prefix: '' }).addTo(map);

  // Drone marker
  droneMarker = L.marker([props.gpsLat, props.gpsLng], {
    icon:         makeDroneIcon(L, props.heading),
    zIndexOffset: 1000,
  }).addTo(map);

  renderPath();
  renderPendingPins();

  // ── Map-click waypoint picker ─────────────────────────────────────────────
  map.on('click', (e) => {
    if (props.mapClickEnabled) {
      emit('add-waypoint', { lat: e.latlng.lat, lng: e.latlng.lng });
    }
  });
});

onUnmounted(() => {
  clearOverlays();
  clearPendingMarkers();
  if (map) { map.remove(); map = null; }
  droneMarker = null;
  L = null;
});

// ── Watchers ───────────────────────────────────────────────────────────────
watch(() => props.queue,       () => renderPath(), { deep: true });
watch(() => props.activeIndex, () => renderPath());
watch(() => props.isRunning,   () => renderPath());

watch([() => props.gpsLat, () => props.gpsLng], ([lat, lng]) => {
  if (!map || !droneMarker) return;
  droneMarker.setLatLng([lat, lng]);
  map.panTo([lat, lng], { animate: true });
  renderPath();
});

watch(() => props.heading, (h) => {
  if (!droneMarker || !L) return;
  droneMarker.setIcon(makeDroneIcon(L, h));
});

// ── Cursor style + pending cleanup when picker toggles ────────────────────
watch(() => props.mapClickEnabled, (enabled) => {
  if (!map) return;
  map.getContainer().style.cursor = enabled ? 'crosshair' : '';
  if (!enabled) clearPendingMarkers(); // clear preview pins when picker is dismissed
});

// Re-render pending pins whenever the array changes (new click or drag update)
watch(() => props.pendingPins, () => renderPendingPins(), { deep: true });

// Expose for parent to call map.flyTo / setZoom
defineExpose({ getMap: () => map });
</script>

<template>
  <div ref="mapContainer" class="w-full h-full" />
</template>

<style>
@keyframes mp-pulse {
  0%   { transform: scale(0.7); opacity: 0.8; }
  70%  { transform: scale(1.9); opacity: 0;   }
  100% { opacity: 0; }
}
.mp-pulse-ring {
  animation: mp-pulse 2s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
}
.mp-tt {
  background: rgba(10, 20, 40, 0.88) !important;
  color: white !important;
  border: 1px solid rgba(255, 255, 255, 0.15) !important;
  border-radius: 6px !important;
  font-size: 11px !important;
  padding: 4px 9px !important;
  box-shadow: 0 4px 14px rgba(0,0,0,0.55) !important;
  white-space: nowrap;
}
.mp-tt::before { display: none !important; }
</style>
