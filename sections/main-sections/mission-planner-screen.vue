<script setup>
import { reactive, ref, onMounted, watch, onBeforeUnmount, computed } from 'vue';
import { missionApi } from "~/sections/api/missionApi"; 
import { useTelemetry } from "~/components/composables/useTelemetry";

import DashboardNavBar       from '~/components/organisms/NavBar.vue';
import MissionPlannerMap     from '~/components/molecules/mission_plan_molecules/MissionPlannerMap.vue';
import ConfirmationModal     from '~/components/molecules/mission_plan_molecules/ConfirmationModal.vue';

// --- ICONS ---
import UpIcon      from '~/assets/icons/Up.svg';
import DownIcon    from '~/assets/icons/Down.svg';
import LeftIcon    from '~/assets/icons/Left.svg';
import RightIcon   from '~/assets/icons/Right.svg';
import ForwardIcon from '~/assets/icons/Forward.svg';
import BackwardIcon from '~/assets/icons/Backward.svg';

// --- GLOBAL TELEMETRY STATE ---
const { telemetryState, startPolling, stopPolling } = useTelemetry();

// --- STATE ---
const planId = ref(null);

const missionQueue = ref([]);
const isRunning = ref(false);
const isLanding = ref(false); 
const currentStepIndex = ref(-1);

const flightParams = reactive({ 
  altitude: 1,
  speed: 30, 
  mode: 'Stabilize',
  missionPad: false 
});

const formattedTelemetry = computed(() => {
  let color = 'bg-red-500';
  if (telemetryState.battery >= 50) {
    color = 'bg-green-500';
  } else if (telemetryState.battery >= 20) {
    color = 'bg-yellow-500';
  }
  return {
    gps: telemetryState.connected ? 'Online' : 'Offline',
    battery: telemetryState.battery || 0,
    batteryColor: color
  };
});

const showCompleteModal = ref(false);
const modalConfig = reactive({
  title: '',
  message: '',
  isWarning: false,
  isSuccess: false,
  cancelText: 'Close'
});

// --- COMMAND OPTIONS ---
const commandOptions = [
  { label: 'Fly Up',      value: 'up',      unit: 'cm', icon: UpIcon },
  { label: 'Fly Down',    value: 'down',    unit: 'cm', icon: DownIcon },
  { label: 'Fly Left',    value: 'left',    unit: 'cm', icon: LeftIcon },  
  { label: 'Fly Right',   value: 'right',   unit: 'cm', icon: RightIcon },
  { label: 'Fly Forward', value: 'forward', unit: 'cm', icon: ForwardIcon },
  { label: 'Fly Back',    value: 'back',    unit: 'cm', icon: BackwardIcon },
  { label: 'Rotate CW',   value: 'cw',      unit: 'deg', icon: `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>` },
  { label: 'Rotate CCW',  value: 'ccw',     unit: 'deg', icon: `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="transform: scaleX(-1);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>` },
  { label: 'Hover',       value: 'hover',   unit: 's',   icon: `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>` },
  { label: 'XYZ Coordinates', value: 'go', unit: 'x y z spd', icon: `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122"></path></svg>` },
  { label: 'Fly to Waypoint', value: 'waypoint', unit: '', icon: `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>` }
];

// --- helpers ---
const decorateStep = (stepDto) => {
  const details = commandOptions.find(c => c.value === stepDto.type);
  return {
    id: stepDto.id,         
    type: stepDto.type,
    val: stepDto.val,
    label: details?.label ?? stepDto.type,
    icon: details?.icon ?? null,
    unit: details?.unit ?? 's' 
  };
};

// --- Load active plan on mount ---
onMounted(async () => {
  try {
    startPolling();
    const plan = await missionApi.getActive();
    planId.value = plan.id;
    flightParams.altitude = plan.altitude;
    flightParams.speed = plan.speed;
    flightParams.mode = plan.mode;
    flightParams.missionPad = plan.missionPad ?? false; 
    missionQueue.value = (plan.steps || [])
      .sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
      .map(decorateStep);
    const s = await missionApi.status();
    if (s.status === 'running' || s.status === 'queued') {
      isRunning.value = true;
      startStatusPoll();
    }
  } catch(e) {
    console.error("Failed to load active plan:", e);
  }
});

// --- autosave flight params (debounced) ---
let fpTimer = null;
watch(
  () => ({ ...flightParams }),
  () => {
    if (!planId.value) return;
    clearTimeout(fpTimer);
    fpTimer = setTimeout(() => {
      missionApi.patchPlan(planId.value, {
        altitude: flightParams.altitude,
        speed: flightParams.speed,
        mode: flightParams.mode,
        missionPad: flightParams.missionPad 
      });
    }, 350);
  },
  { deep: true }
);

// --- HANDLERS ---
const handleAddCommand = async (cmd) => {
  if (!planId.value) { cmdError.value = 'No active plan loaded — try reloading the page.'; return; }
  try {
    const created = await missionApi.addStep(planId.value, { type: cmd.type, val: cmd.val });
    missionQueue.value.push(decorateStep(created));
  } catch (e) {
    cmdError.value = 'Failed to add step — check backend connection.';
    console.error('addStep failed:', e);
  }
};

const handleRemoveCommand = async (index) => {
  const step = missionQueue.value[index];
  if (!step) return;
  await missionApi.deleteStep(step.id);
  missionQueue.value.splice(index, 1);
};

const handleClear = async () => {
  if (!planId.value) return;
  await missionApi.clearSteps(planId.value);
  missionQueue.value = [];
  currentStepIndex.value = -1;
};

const handleReorderCommand = async ({ from, to }) => {
  const movedItem = missionQueue.value.splice(from, 1)[0];
  missionQueue.value.splice(to, 0, movedItem);
};

// --- RUN + POLL STATUS ---
let statusPoll = null;

const stopStatusPoll = () => {
  if (statusPoll) clearInterval(statusPoll);
  statusPoll = null;
};

const startStatusPoll = () => {
  stopStatusPoll();
  statusPoll = setInterval(async () => {
    try {
      const s = await missionApi.status();
      if (s.status === 'running') {
        currentStepIndex.value = s.active_index ?? -1;
      } else {
        currentStepIndex.value = -1;
      }
      if (['completed', 'failed', 'cancelled', 'inactive'].includes(s.status)) {
        stopStatusPoll();
        isRunning.value = false;
        isLanding.value = false; 
        currentStepIndex.value = -1;
        modalConfig.title = s.status === 'completed' ? 'Mission Complete' : 'Mission Ended';
        modalConfig.message = s.status === 'completed'
          ? 'The drone has successfully executed all flight plan commands.'
          : (s.message || `Mission status: ${s.status}`);
        modalConfig.isWarning = s.status !== 'completed';
        modalConfig.isSuccess = s.status === 'completed';
        modalConfig.cancelText = 'Close';
        showCompleteModal.value = true;
      }
    } catch (e) {
      console.error("Status poll failed", e);
    }
  }, 1000);
};

const handleRunMission = async () => {
  isRunning.value = true;
  currentStepIndex.value = -1;
  try {
    const res = await missionApi.run();
    if (!res.ok) {
      alert("Mission failed to start: " + res.text);
      isRunning.value = false;
      return;
    }
    startStatusPoll();
  } catch (e) {
    console.error("Mission run failed", e);
    isRunning.value = false;
  }
};

// --- LIVE OVERRIDE HANDLERS ---
const handleEmergencyLand = async () => {
  if (isLanding.value) return;
  isLanding.value = true;
  try {
    await missionApi.forceLand();
    console.log("Emergency command dispatched.");
  } catch (e) {
    console.error("Emergency landing failed to execute:", e);
  } finally {
    setTimeout(() => { isLanding.value = false; }, 2000);
  }
};

const handleStopHover = async () => {
  try {
    await missionApi.sendCommand('stop'); 
    console.log("Drone braking and hovering.");
  } catch (e) {
    console.error("Failed to stop drone:", e);
  }
};

const handleEmergencyCutoff = async () => {
  try {
    await missionApi.sendCommand('emergency'); 
    console.warn("EMERGENCY CUTOFF TRIGGERED! Motors stopped.");
  } catch (e) {
    console.error("Emergency cutoff failed:", e);
  }
};

onBeforeUnmount(() => {
  stopStatusPoll();
  clearTimeout(fpTimer);
  stopPolling();
});

// ── Sidebar drawer state ───────────────────────────────────────────────────
const activeDrawer = ref(null);
const toggleDrawer = (id) => {
  activeDrawer.value = activeDrawer.value === id ? null : id;
};
const drawerTitles = {
  route:    'Mission Route',
  mission:  'Mission Control',
  params:   'Parameters',
  telemetry: 'Live Telemetry',
};

// ── Distance helpers ───────────────────────────────────────────────────────
const getCmdDistance = (cmd) => {
  const v = parseFloat(cmd.val) || 0;
  if (['forward', 'back', 'left', 'right'].includes(cmd.type)) return v;
  if (cmd.type === 'go') {
    const parts = (cmd.val || '').split(' ');
    return Math.sqrt((parseFloat(parts[0]) || 0) ** 2 + (parseFloat(parts[1]) || 0) ** 2);
  }
  return 0;
};

const totalDistanceCm = computed(() =>
  missionQueue.value.reduce((s, c) => s + getCmdDistance(c), 0)
);

const completedDistanceCm = computed(() => {
  if (currentStepIndex.value < 0) return 0;
  return missionQueue.value
    .slice(0, Math.max(0, currentStepIndex.value))
    .reduce((s, c) => s + getCmdDistance(c), 0);
});

const progressPercent = computed(() =>
  totalDistanceCm.value > 0
    ? Math.min(100, (completedDistanceCm.value / totalDistanceCm.value) * 100)
    : 0
);

const timelineWaypoints = computed(() => {
  if (!totalDistanceCm.value) return [];
  let cum = 0;
  return missionQueue.value.reduce((acc, cmd, i) => {
    const d = getCmdDistance(cmd);
    if (d > 0) {
      cum += d;
      acc.push({
        pct:    (cum / totalDistanceCm.value) * 100,
        idx:    i,
        done:   isRunning.value && currentStepIndex.value > i,
        active: currentStepIndex.value === i,
      });
    }
    return acc;
  }, []);
});

const fmtDist = (cm) => {
  if (!cm) return '0m';
  if (cm >= 100) return `${Math.round(cm / 100)}m`;
  return `${Math.round(cm)}cm`;
};

// ── Inline Add-Command form state ──────────────────────────────────────────
const newCmdType = ref('');
const newCmdVal  = ref('');
const goX = ref(0); const goY = ref(0); const goZ = ref(0);
const cmdError   = ref('');

// ── Waypoint picker state ──────────────────────────────────────────────────
const mapClickEnabled = ref(false);
const waypointLat = ref('');
const waypointLng = ref('');
const waypointPickCount = ref(0);
const pendingPins = ref([]); // preview pins on map, committed on Done

const stopMapPick = () => {
  mapClickEnabled.value = false;
  waypointPickCount.value = 0;
  pendingPins.value = [];   // remove cyan preview pins from map
};

// Each map click immediately records a waypoint step (optimistic queue update)
const handleMapWaypoint = ({ lat, lng }) => {
  const val    = `${lat.toFixed(6)} ${lng.toFixed(6)}`;
  const tempId = `_tmp_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
  const cmdOpt = commandOptions.find(c => c.value === 'waypoint');

  // 1. Push into the queue immediately so the pin & step list appear NOW
  missionQueue.value.push({
    id:    tempId,
    type:  'waypoint',
    val,
    label: cmdOpt?.label ?? 'Fly to Waypoint',
    unit:  '',
    icon:  cmdOpt?.icon ?? null,
  });
  waypointPickCount.value++;

  // 2. Confirm with API; swap temp entry for real one when it resolves
  if (planId.value) {
    missionApi.addStep(planId.value, { type: 'waypoint', val })
      .then((step) => {
        const i = missionQueue.value.findIndex(s => s.id === tempId);
        if (i !== -1) missionQueue.value[i] = decorateStep(step);
      })
      .catch(() => {
        // Roll back on failure
        const i = missionQueue.value.findIndex(s => s.id === tempId);
        if (i !== -1) { missionQueue.value.splice(i, 1); waypointPickCount.value--; }
      });
  }
};

// Update position when a pending pin is dragged
const handleUpdatePendingPin = ({ idx, lat, lng }) => {
  if (pendingPins.value[idx]) {
    pendingPins.value[idx] = { lat, lng };
  }
};

// ── Drag-update from map ───────────────────────────────────────────────────
const handleUpdateWaypoint = async ({ idx, lat, lng }) => {
  const step = missionQueue.value[idx];
  if (!step || step.type !== 'waypoint') return;
  const newVal = `${lat.toFixed(6)} ${lng.toFixed(6)}`;
  step.val = newVal;                        // instant local update → map re-renders
  activeDrawer.value = 'route';             // open step list so user sees the update
  try { await missionApi.patchStep(step.id, { val: newVal }); }
  catch (e) { console.warn('Step patch failed (local only):', e); }
};

// ── Inline step editing ────────────────────────────────────────────────────
const editingStepIdx = ref(-1);
const editingVal     = ref('');
const editingLat     = ref('');
const editingLng     = ref('');
const editGoX        = ref('0');
const editGoY        = ref('0');
const editGoZ        = ref('0');

const handleStartEdit = (idx) => {
  if (isRunning.value) return;
  const step = missionQueue.value[idx];
  if (!step) return;
  editingStepIdx.value = idx;
  if (step.type === 'waypoint') {
    const p = (step.val || '').split(' ');
    editingLat.value = p[0] || '';
    editingLng.value = p[1] || '';
  } else if (step.type === 'go') {
    const p = (step.val || '').split(' ');
    editGoX.value = p[0] || '0';
    editGoY.value = p[1] || '0';
    editGoZ.value = p[2] || '0';
  } else {
    editingVal.value = step.val || '';
  }
};

const handleCancelEdit = () => { editingStepIdx.value = -1; };

const handleSaveEdit = async (idx) => {
  const step = missionQueue.value[idx];
  if (!step) return;
  let newVal;
  if (step.type === 'waypoint') {
    if (!editingLat.value || !editingLng.value) return;
    newVal = `${Number(editingLat.value).toFixed(6)} ${Number(editingLng.value).toFixed(6)}`;
  } else if (step.type === 'go') {
    newVal = `${editGoX.value} ${editGoY.value} ${editGoZ.value}`;
  } else {
    if (!editingVal.value) return;
    newVal = editingVal.value;
  }
  step.val = newVal;
  editingStepIdx.value = -1;
  try { await missionApi.patchStep(step.id, { val: newVal }); }
  catch (e) { console.warn('Step patch failed (local only):', e); }
};

// Helper: format waypoint val for display in step list
const fmtWaypointVal = (val) => {
  const p = (val || '').split(' ');
  const la = parseFloat(p[0]), ln = parseFloat(p[1]);
  if (isNaN(la) || isNaN(ln)) return val;
  return `${la.toFixed(4)}, ${ln.toFixed(4)}`;
};

watch(newCmdType, () => { cmdError.value = ''; stopMapPick(); });

const currentCmdDetails = computed(() =>
  commandOptions.find((c) => c.value === newCmdType.value) || { unit: '' }
);

const handleAddInline = () => {
  cmdError.value = '';
  if (!planId.value) { cmdError.value = 'No active plan loaded — try reloading the page.'; return; }
  if (!newCmdType.value) { cmdError.value = 'Select a command type.'; return; }
  if (newCmdType.value === 'go') {
    const x = Number(goX.value), y = Number(goY.value), z = Number(goZ.value);
    if (Math.abs(x) > 500 || Math.abs(y) > 500 || Math.abs(z) > 500) {
      cmdError.value = 'Coordinates must be between -500 and 500 cm.'; return;
    }
    if (Math.abs(x) < 20 && Math.abs(y) < 20 && Math.abs(z) < 20) {
      cmdError.value = 'X/Y/Z cannot all be between -20 and 20 cm.'; return;
    }
    handleAddCommand({ type: 'go', val: `${x} ${y} ${z}` });
    goX.value = goY.value = goZ.value = 0;
  } else if (newCmdType.value === 'mon') {
    handleAddCommand({ type: 'mon', val: '' });
  } else if (newCmdType.value === 'waypoint') {
    if (mapClickEnabled.value) {
      // Steps already recorded on each click — just exit picker mode
      stopMapPick();
      return;
    }
    // Manual entry fallback (when picker is off)
    if (!waypointLat.value || !waypointLng.value) {
      cmdError.value = 'Set a waypoint — pick on map or enter coordinates.'; return;
    }
    handleAddCommand({ type: 'waypoint', val: `${waypointLat.value} ${waypointLng.value}` });
    waypointLat.value = '';
    waypointLng.value = '';
  } else {
    if (!newCmdVal.value) { cmdError.value = 'Enter a value.'; return; }
    handleAddCommand({ type: newCmdType.value, val: newCmdVal.value });
    newCmdVal.value = '';
  }
};

// ── Flight time formatter ──────────────────────────────────────────────────
const flightTimeFormatted = computed(() => {
  const s = telemetryState.flight_time || 0;
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
});

</script>

<template>
  <div class="flex flex-col h-screen overflow-hidden bg-gray-950 font-inter select-none">

    <!-- NavBar -->
    <div class="z-30 relative shrink-0">
      <DashboardNavBar :activePage="'mission-planner'" :droneStatus="formattedTelemetry.gps" />
    </div>

    <!-- ════════ MAIN CANVAS ════════ -->
    <div class="flex-1 relative overflow-hidden">

      <!-- Map-click waypoint banner -->
      <Transition
        enter-active-class="transition-all duration-200 ease-out"
        leave-active-class="transition-all duration-150 ease-in"
        enter-from-class="opacity-0 translate-y-3"
        leave-to-class="opacity-0 translate-y-3">
        <div v-if="mapClickEnabled"
          class="absolute bottom-[78px] left-1/2 -translate-x-1/2 z-30 pointer-events-none">
          <div class="bg-blue-600/85 backdrop-blur-xl border border-blue-400/40 rounded-xl px-5 py-2.5 flex items-center gap-3 shadow-2xl">
            <svg class="w-4 h-4 text-white shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            <span class="text-[11px] font-black text-white uppercase tracking-widest whitespace-nowrap">
              <template v-if="waypointPickCount === 0">Click on the map to place waypoints</template>
              <template v-else>{{ waypointPickCount }} waypoint{{ waypointPickCount > 1 ? 's' : '' }} added — keep clicking or close</template>
            </span>
            <button class="pointer-events-auto ml-1 text-white/60 hover:text-white transition-colors"
              @click="stopMapPick()">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>
      </Transition>

      <!-- ① SATELLITE MAP (full background) -->
      <div class="absolute inset-0 z-0">
        <MissionPlannerMap
          :queue="missionQueue"
          :activeIndex="currentStepIndex"
          :gpsLat="telemetryState.gps_lat"
          :gpsLng="telemetryState.gps_lon"
          :heading="telemetryState.heading"
          :isRunning="isRunning"
          :mapClickEnabled="mapClickEnabled"
          :pendingPins="pendingPins"
          @add-waypoint="handleMapWaypoint"
          @update-waypoint="handleUpdateWaypoint"
          @update-pending-pin="handleUpdatePendingPin"
        />
      </div>

      <!-- ② LEFT: Icon sidebar + slide-out drawer -->
      <div class="absolute left-0 top-0 bottom-[70px] z-20 flex">

        <!-- Icon bar (52px) -->
        <div class="w-[52px] h-full bg-black/55 backdrop-blur-xl border-r border-white/8 flex flex-col items-center pt-4 pb-4 gap-1.5">

          <!-- Route / Waypoints -->
          <button @click="toggleDrawer('route')"
            class="group w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-150"
            :class="activeDrawer === 'route' ? 'bg-white/18 text-white' : 'text-white/35 hover:text-white/75 hover:bg-white/8'"
            title="Mission Route">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
            </svg>
          </button>

          <!-- Mission Control -->
          <button @click="toggleDrawer('mission')"
            class="group w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-150"
            :class="activeDrawer === 'mission'
              ? 'bg-[#658D1B]/35 text-[#9CC435]'
              : isRunning
                ? 'text-[#9CC435]/70 bg-[#658D1B]/15 hover:bg-[#658D1B]/25'
                : 'text-white/35 hover:text-white/75 hover:bg-white/8'"
            title="Mission Control">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
              <path stroke-linecap="round" stroke-linejoin="round" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </button>

          <!-- Parameters -->
          <button @click="toggleDrawer('params')"
            class="group w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-150"
            :class="activeDrawer === 'params' ? 'bg-white/18 text-white' : 'text-white/35 hover:text-white/75 hover:bg-white/8'"
            title="Parameters">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/>
            </svg>
          </button>

          <!-- Telemetry -->
          <button @click="toggleDrawer('telemetry')"
            class="group w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-150"
            :class="activeDrawer === 'telemetry' ? 'bg-white/18 text-white' : 'text-white/35 hover:text-white/75 hover:bg-white/8'"
            title="Telemetry">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0"/>
            </svg>
          </button>

          <div class="flex-1"></div>

          <!-- Connection indicator dot -->
          <div class="w-2 h-2 rounded-full mb-1 transition-colors"
            :class="telemetryState.connected ? 'bg-green-400 shadow-[0_0_6px_rgba(74,222,128,0.7)]' : 'bg-red-500'">
          </div>
        </div>

        <!-- ── Slide-out drawer ── -->
        <Transition
          enter-active-class="transition-all duration-220 ease-out"
          leave-active-class="transition-all duration-180 ease-in"
          enter-from-class="-translate-x-3 opacity-0"
          leave-to-class="-translate-x-3 opacity-0"
        >
          <div v-if="activeDrawer" class="w-[278px] h-full bg-black/65 backdrop-blur-2xl border-r border-white/8 flex flex-col overflow-hidden">

            <!-- Drawer header -->
            <div class="px-4 pt-4 pb-3 border-b border-white/8 flex items-center justify-between shrink-0">
              <span class="text-[11px] font-black uppercase tracking-[0.16em] text-white/50">
                {{ drawerTitles[activeDrawer] }}
              </span>
              <button @click="activeDrawer = null" class="text-white/25 hover:text-white/70 transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>

            <!-- ── ROUTE drawer: Add Command + Step List ── -->
            <div v-if="activeDrawer === 'route'" class="flex-1 flex flex-col overflow-hidden">

              <!-- Add command section -->
              <div class="p-3 border-b border-white/8 shrink-0 space-y-2">
                <p class="text-[9px] font-black uppercase tracking-[0.18em] text-white/35 mb-2">Add Command</p>

                <select v-model="newCmdType"
                  class="w-full bg-white/6 border border-white/10 rounded-lg px-3 py-2 text-white text-xs outline-none focus:border-amber-500/50 transition appearance-none">
                  <option value="" disabled class="bg-gray-900">Select Command...</option>
                  <option v-for="opt in commandOptions" :key="opt.value" :value="opt.value" class="bg-gray-900">{{ opt.label }}</option>
                </select>

                <div v-if="newCmdType === 'go'" class="grid grid-cols-3 gap-1.5">
                  <div v-for="[label,model] in [['X (right)', goX],['Y (fwd)', goY],['Z (up)', goZ]]" :key="label" class="flex flex-col gap-0.5">
                    <label class="text-[8px] text-white/35 uppercase tracking-wide">{{ label }}</label>
                    <input type="number"
                      :value="label==='X (right)' ? goX : label==='Y (fwd)' ? goY : goZ"
                      @input="label==='X (right)' ? goX=$event.target.value : label==='Y (fwd)' ? goY=$event.target.value : goZ=$event.target.value"
                      class="bg-white/6 border border-white/10 rounded px-2 py-1.5 text-white text-xs outline-none focus:border-amber-500/50 transition"/>
                  </div>
                </div>
                <div v-else-if="newCmdType === 'waypoint'" class="space-y-2">
                  <!-- Map pick toggle -->
                  <button @click="mapClickEnabled ? stopMapPick() : (mapClickEnabled = true)"
                    class="w-full py-2 text-[10px] font-black uppercase tracking-[0.14em] rounded-lg transition-all flex items-center justify-center gap-2 border"
                    :class="mapClickEnabled
                      ? 'bg-blue-500/25 border-blue-400/50 text-blue-300'
                      : 'bg-white/6 border-white/10 text-white/60 hover:bg-white/10 hover:text-white'">
                    <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                      <path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                    </svg>
                    <span v-if="!mapClickEnabled">Pick from Map</span>
                    <span v-else-if="waypointPickCount === 0" class="animate-pulse">● Waiting for click...</span>
                    <span v-else class="animate-pulse">● {{ waypointPickCount }} point{{ waypointPickCount > 1 ? 's' : '' }} placed — Stop</span>
                  </button>
                  <!-- Manual lat/lng inputs -->
                  <div class="grid grid-cols-2 gap-1.5">
                    <div class="flex flex-col gap-0.5">
                      <label class="text-[8px] text-white/35 uppercase tracking-wide">Latitude</label>
                      <input type="number" v-model="waypointLat" step="0.000001" placeholder="e.g. 8.4803"
                        class="bg-white/6 border border-white/10 rounded px-2 py-1.5 text-white text-xs outline-none focus:border-blue-500/50 transition placeholder:text-white/20"/>
                    </div>
                    <div class="flex flex-col gap-0.5">
                      <label class="text-[8px] text-white/35 uppercase tracking-wide">Longitude</label>
                      <input type="number" v-model="waypointLng" step="0.000001" placeholder="e.g. 124.65"
                        class="bg-white/6 border border-white/10 rounded px-2 py-1.5 text-white text-xs outline-none focus:border-blue-500/50 transition placeholder:text-white/20"/>
                    </div>
                  </div>
                  <!-- Last-picked coords preview -->
                  <div v-if="waypointLat && waypointLng"
                    class="text-[9px] font-mono text-blue-300 bg-blue-500/10 border border-blue-400/20 rounded-lg px-3 py-1.5 flex items-center gap-1.5">
                    <svg class="w-3 h-3 shrink-0" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                    </svg>
                    <span class="text-white/40 mr-0.5">Last:</span>
                    {{ Number(waypointLat).toFixed(5) }}, {{ Number(waypointLng).toFixed(5) }}
                  </div>
                </div>
                <div v-else-if="newCmdType === 'mon'" class="text-[10px] text-blue-300 bg-blue-500/10 border border-blue-500/20 rounded-lg px-3 py-2">
                  Enables downward camera — no parameters needed.
                </div>
                <div v-else-if="newCmdType" class="flex">
                  <input type="number" v-model="newCmdVal" min="1"
                    class="flex-1 bg-white/6 border border-white/10 rounded-l-lg px-3 py-2 text-white text-xs outline-none focus:border-amber-500/50 transition"/>
                  <div class="px-2.5 flex items-center bg-white/5 border border-white/10 border-l-0 rounded-r-lg text-white/35 text-[9px] font-bold">{{ currentCmdDetails.unit }}</div>
                </div>

                <div v-if="cmdError" class="text-[9px] text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-1.5 flex items-center gap-1.5">
                  <svg class="w-3 h-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                  {{ cmdError }}
                </div>

                <button @click="handleAddInline"
                  class="w-full py-2 font-black text-[10px] uppercase tracking-[0.14em] rounded-lg transition-colors"
                  :class="newCmdType === 'waypoint' && mapClickEnabled
                    ? 'bg-blue-500 hover:bg-blue-400 text-white'
                    : 'bg-amber-500 hover:bg-amber-400 text-gray-900'">
                  <span v-if="newCmdType === 'waypoint' && mapClickEnabled">
                    ✓ Done Picking — {{ waypointPickCount }} step{{ waypointPickCount !== 1 ? 's' : '' }} added
                  </span>
                  <span v-else>+ Add Step</span>
                </button>
              </div>

              <!-- Step list -->
              <div class="flex items-center justify-between px-3 py-2 border-b border-white/6 shrink-0">
                <span class="text-[9px] font-black uppercase tracking-[0.16em] text-white/35">
                  Steps ({{ missionQueue.length }})
                </span>
                <button v-if="missionQueue.length" @click="handleClear"
                  class="text-[9px] font-bold uppercase tracking-wide text-red-400/60 hover:text-red-400 transition-colors">
                  Clear
                </button>
              </div>

              <div class="flex-1 overflow-y-auto p-2 space-y-1">
                <div v-if="!missionQueue.length" class="flex flex-col items-center justify-center h-full py-8 text-center">
                  <div class="w-9 h-9 rounded-full bg-white/5 flex items-center justify-center mb-2">
                    <svg class="w-4 h-4 text-white/15" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/>
                    </svg>
                  </div>
                  <p class="text-[11px] text-white/20 font-medium">No commands added yet</p>
                </div>

                <div v-for="(step, i) in missionQueue" :key="step.id"
                  class="rounded-lg border transition-all overflow-hidden"
                  :class="editingStepIdx === i
                    ? 'bg-white/7 border-blue-500/30'
                    : currentStepIndex === i
                      ? 'bg-amber-500/15 border-amber-500/35'
                      : 'bg-white/4 border-white/6 hover:bg-white/7'">

                  <!-- Normal row -->
                  <div class="flex items-center gap-2 px-3 py-2">
                    <!-- Step badge -->
                    <div class="w-5 h-5 rounded-full flex items-center justify-center shrink-0 text-[8px] font-black"
                      :class="currentStepIndex === i
                        ? 'bg-amber-500 text-gray-900 animate-pulse'
                        : currentStepIndex > i && isRunning
                          ? 'bg-green-500 text-white'
                          : step.type === 'waypoint'
                            ? 'bg-blue-500/80 text-white'
                            : 'bg-white/10 text-white/50'">
                      {{ currentStepIndex > i && isRunning ? '✓' : i + 1 }}
                    </div>
                    <!-- Label + value -->
                    <div class="flex-1 min-w-0">
                      <p class="text-white text-[11px] font-semibold leading-tight truncate flex items-center gap-1">
                        {{ step.label }}
                        <!-- drag hint for waypoints -->
                        <span v-if="step.type === 'waypoint' && !isRunning"
                          class="text-[8px] text-blue-400/50 font-normal">drag pin</span>
                      </p>
                      <p class="text-white/35 text-[9px] leading-tight font-mono">
                        <template v-if="step.type === 'waypoint'">{{ fmtWaypointVal(step.val) }}</template>
                        <template v-else>{{ step.val }} {{ step.unit }}</template>
                      </p>
                    </div>
                    <!-- Edit button -->
                    <button @click="editingStepIdx === i ? handleCancelEdit() : handleStartEdit(i)"
                      :disabled="isRunning"
                      class="transition-colors disabled:opacity-20 shrink-0 p-0.5 rounded"
                      :class="editingStepIdx === i ? 'text-blue-400' : 'text-white/20 hover:text-blue-400'">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                        <path v-if="editingStepIdx !== i" stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                        <path v-else stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                      </svg>
                    </button>
                    <!-- Delete button -->
                    <button @click="handleRemoveCommand(i)" :disabled="isRunning || editingStepIdx === i"
                      class="text-white/20 hover:text-red-400 transition-colors disabled:opacity-20 shrink-0">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                      </svg>
                    </button>
                  </div>

                  <!-- Edit form (expands below row) -->
                  <div v-if="editingStepIdx === i" class="px-3 pb-3 pt-1 space-y-2 border-t border-white/8">
                    <!-- Waypoint: lat + lng -->
                    <template v-if="step.type === 'waypoint'">
                      <div class="grid grid-cols-2 gap-1.5">
                        <div class="flex flex-col gap-0.5">
                          <label class="text-[8px] text-white/35 uppercase tracking-wide">Latitude</label>
                          <input type="number" v-model="editingLat" step="0.000001"
                            class="bg-white/6 border border-white/10 rounded px-2 py-1.5 text-white text-xs outline-none focus:border-blue-500/50 transition font-mono"/>
                        </div>
                        <div class="flex flex-col gap-0.5">
                          <label class="text-[8px] text-white/35 uppercase tracking-wide">Longitude</label>
                          <input type="number" v-model="editingLng" step="0.000001"
                            class="bg-white/6 border border-white/10 rounded px-2 py-1.5 text-white text-xs outline-none focus:border-blue-500/50 transition font-mono"/>
                        </div>
                      </div>
                    </template>
                    <!-- XYZ: three fields -->
                    <template v-else-if="step.type === 'go'">
                      <div class="grid grid-cols-3 gap-1">
                        <div class="flex flex-col gap-0.5">
                          <label class="text-[8px] text-white/35 uppercase tracking-wide">X</label>
                          <input type="number" v-model="editGoX" class="bg-white/6 border border-white/10 rounded px-2 py-1.5 text-white text-xs outline-none focus:border-amber-500/50 transition"/>
                        </div>
                        <div class="flex flex-col gap-0.5">
                          <label class="text-[8px] text-white/35 uppercase tracking-wide">Y</label>
                          <input type="number" v-model="editGoY" class="bg-white/6 border border-white/10 rounded px-2 py-1.5 text-white text-xs outline-none focus:border-amber-500/50 transition"/>
                        </div>
                        <div class="flex flex-col gap-0.5">
                          <label class="text-[8px] text-white/35 uppercase tracking-wide">Z</label>
                          <input type="number" v-model="editGoZ" class="bg-white/6 border border-white/10 rounded px-2 py-1.5 text-white text-xs outline-none focus:border-amber-500/50 transition"/>
                        </div>
                      </div>
                    </template>
                    <!-- Single value for all other types -->
                    <template v-else>
                      <div class="flex gap-0">
                        <input type="number" v-model="editingVal" min="1"
                          class="flex-1 bg-white/6 border border-white/10 rounded-l px-2 py-1.5 text-white text-xs outline-none focus:border-amber-500/50 transition"/>
                        <div class="px-2 flex items-center bg-white/5 border border-white/10 border-l-0 rounded-r text-white/35 text-[9px] font-bold">{{ step.unit }}</div>
                      </div>
                    </template>
                    <!-- Save / Cancel -->
                    <div class="flex gap-1.5 pt-0.5">
                      <button @click="handleSaveEdit(i)"
                        class="flex-1 py-1.5 bg-green-500/20 hover:bg-green-500/30 border border-green-500/30 text-green-400 text-[9px] font-black uppercase tracking-wide rounded-lg transition-colors flex items-center justify-center gap-1">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                        </svg>
                        Save
                      </button>
                      <button @click="handleCancelEdit"
                        class="flex-1 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 text-white/40 hover:text-white/70 text-[9px] font-black uppercase tracking-wide rounded-lg transition-colors">
                        Cancel
                      </button>
                    </div>
                  </div>

                </div>
              </div>
            </div>

            <!-- ── MISSION CONTROL drawer ── -->
            <div v-else-if="activeDrawer === 'mission'" class="flex-1 p-4 flex flex-col gap-4 overflow-y-auto">

              <!-- Status + progress -->
              <div class="flex items-center justify-between">
                <span class="text-[9px] font-black uppercase tracking-[0.16em] text-white/40">Status</span>
                <span class="text-[9px] font-black uppercase tracking-[0.16em] px-2.5 py-1 rounded-full"
                  :class="isRunning ? 'bg-amber-500/20 text-amber-400' : 'bg-white/8 text-white/40'">
                  {{ isRunning ? '● RUNNING' : 'IDLE' }}
                </span>
              </div>

              <div v-if="isRunning" class="flex flex-col gap-1.5">
                <div class="flex justify-between text-[9px] text-white/35 font-bold uppercase tracking-wide">
                  <span>Progress</span>
                  <span>{{ Math.max(0, currentStepIndex) }}/{{ missionQueue.length }}</span>
                </div>
                <div class="h-1.5 bg-white/8 rounded-full overflow-hidden">
                  <div class="h-full bg-amber-500 rounded-full transition-all duration-500"
                    :style="{ width: missionQueue.length ? `${(Math.max(0,currentStepIndex)/missionQueue.length)*100}%` : '0%' }"></div>
                </div>
              </div>

              <!-- Run button -->
              <button @click="handleRunMission"
                :disabled="!missionQueue.length || isRunning"
                class="w-full py-3.5 rounded-xl font-black text-sm tracking-wider transition-all flex items-center justify-center gap-2"
                :class="isRunning || !missionQueue.length
                  ? 'bg-white/5 text-white/25 cursor-not-allowed'
                  : 'bg-[#658D1B] hover:bg-[#7aA821] text-white shadow-lg hover:-translate-y-0.5 active:translate-y-0'">
                <svg v-if="isRunning" class="animate-spin w-4 h-4" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z"/>
                </svg>
                {{ isRunning ? 'Mission Running...' : 'Run Mission Plan' }}
              </button>

              <!-- Emergency Land -->
              <button v-if="isRunning" @click="handleEmergencyLand" :disabled="isLanding"
                class="w-full py-3 bg-red-600/80 hover:bg-red-500 disabled:opacity-50 text-white font-black text-sm rounded-xl flex items-center justify-center gap-2 transition-all border border-red-500/30">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                </svg>
                {{ isLanding ? 'Aborting...' : '⚠ Emergency Land' }}
              </button>

              <div class="border-t border-white/8 pt-1">
                <p class="text-[9px] font-black uppercase tracking-[0.16em] text-white/30 mb-3">Live Overrides</p>
                <div class="grid grid-cols-2 gap-2">
                  <button @click="handleStopHover"
                    class="py-3 bg-yellow-500/12 hover:bg-yellow-500/22 border border-yellow-500/20 text-yellow-400 font-black text-[10px] uppercase tracking-wide rounded-xl flex items-center justify-center gap-1.5 transition-all">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0zM9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"/>
                    </svg>
                    Brake
                  </button>
                  <button @click="handleEmergencyCutoff"
                    class="py-3 bg-red-500/12 hover:bg-red-500/22 border border-red-500/20 text-red-400 font-black text-[10px] uppercase tracking-wide rounded-xl flex items-center justify-center gap-1.5 transition-all">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"/>
                    </svg>
                    E-Stop
                  </button>
                </div>
              </div>
            </div>

            <!-- ── PARAMETERS drawer ── -->
            <div v-else-if="activeDrawer === 'params'" class="flex-1 p-4 flex flex-col gap-3 overflow-y-auto">
              <div class="grid grid-cols-2 gap-2.5">
                <div class="flex flex-col gap-1">
                  <label class="text-[9px] text-white/40 font-black uppercase tracking-wide">Altitude (m)</label>
                  <input v-model="flightParams.altitude" type="number"
                    class="bg-white/6 border border-white/10 rounded-lg px-3 py-2 text-white text-sm outline-none focus:border-amber-500/50 transition"/>
                </div>
                <div class="flex flex-col gap-1">
                  <label class="text-[9px] text-white/40 font-black uppercase tracking-wide">Speed (cm/s)</label>
                  <input v-model="flightParams.speed" type="number"
                    class="bg-white/6 border border-white/10 rounded-lg px-3 py-2 text-white text-sm outline-none focus:border-amber-500/50 transition"/>
                </div>
                <div class="flex flex-col gap-1 col-span-2">
                  <label class="text-[9px] text-white/40 font-black uppercase tracking-wide">Flight Mode</label>
                  <input v-model="flightParams.mode"
                    class="bg-white/6 border border-white/10 rounded-lg px-3 py-2 text-white text-sm outline-none focus:border-amber-500/50 transition"/>
                </div>
                <div class="col-span-2 flex items-center justify-between px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl">
                  <div>
                    <p class="text-xs font-bold text-white/75">Downward Camera</p>
                    <p class="text-[10px] text-white/35">Mission Pad detection</p>
                  </div>
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" v-model="flightParams.missionPad" class="sr-only peer"/>
                    <div class="w-10 h-[22px] bg-white/10 peer-checked:bg-amber-500 rounded-full transition-colors after:content-[''] after:absolute after:top-[3px] after:left-[3px] after:w-4 after:h-4 after:bg-white after:rounded-full after:transition-all peer-checked:after:translate-x-4.5"></div>
                  </label>
                </div>
              </div>
            </div>

            <!-- ── TELEMETRY drawer ── -->
            <div v-else-if="activeDrawer === 'telemetry'" class="flex-1 p-3 overflow-y-auto">
              <div class="grid grid-cols-2 gap-2">
                <div v-for="item in [
                  { label: 'Pitch',    val: telemetryState.pitch.toFixed(1),       unit: '°'    },
                  { label: 'Roll',     val: telemetryState.roll.toFixed(1),        unit: '°'    },
                  { label: 'Yaw',      val: telemetryState.yaw.toFixed(1),         unit: '°'    },
                  { label: 'Altitude', val: telemetryState.altitude_m.toFixed(2),  unit: 'm'    },
                  { label: 'ToF',      val: telemetryState.tof_cm,                 unit: 'cm'   },
                  { label: 'Temp',     val: telemetryState.temp_c,                 unit: '°C'   },
                  { label: 'Baro',     val: telemetryState.baro.toFixed(1),        unit: 'hPa'  },
                  { label: 'Speed',    val: telemetryState.speed,                  unit: 'cm/s' },
                ]" :key="item.label"
                  class="bg-white/5 border border-white/8 rounded-xl px-3 py-2.5 flex flex-col gap-0.5">
                  <p class="text-[8px] text-white/35 font-black uppercase tracking-wider">{{ item.label }}</p>
                  <p class="text-base font-black font-mono text-white/80 leading-none">
                    {{ item.val }}<span class="text-[10px] font-normal text-white/30 ml-0.5">{{ item.unit }}</span>
                  </p>
                </div>
              </div>
            </div>

          </div>
        </Transition>
      </div>

      <!-- ③ GPS PILL — top left, shifts right when drawer is open -->
      <div class="absolute top-3 z-10 transition-all duration-220"
        :style="{ left: (activeDrawer ? 52 + 278 + 10 : 52 + 10) + 'px' }">
        <div class="bg-black/55 backdrop-blur-lg border border-white/10 rounded-lg px-3 py-1.5 flex items-center gap-3">
          <span class="w-1.5 h-1.5 rounded-full shrink-0 transition-colors"
            :class="telemetryState.connected ? 'bg-green-400 animate-pulse' : 'bg-red-400'"></span>
          <span class="text-[9px] font-mono font-bold text-white/65 uppercase tracking-widest">
            LAT {{ telemetryState.gps_lat.toFixed(5) }}
          </span>
          <span class="text-white/18">·</span>
          <span class="text-[9px] font-mono font-bold text-white/65 uppercase tracking-widest">
            LON {{ telemetryState.gps_lon.toFixed(5) }}
          </span>
          <span class="text-white/18">·</span>
          <span class="text-[9px] font-mono font-bold text-white/35 uppercase tracking-widest">
            {{ Math.round(telemetryState.heading) }}°
          </span>
        </div>
      </div>

      <!-- ④ RIGHT FLOATING CARDS: Compass + Battery + Flight Time -->
      <div class="absolute top-3 right-3 z-10 flex flex-col items-center gap-2.5">

        <!-- Compass card -->
        <div class="bg-black/55 backdrop-blur-xl border border-white/10 rounded-2xl p-2.5 w-[88px] h-[88px] flex items-center justify-center">
          <svg viewBox="0 0 80 80" class="w-[72px] h-[72px]" xmlns="http://www.w3.org/2000/svg">
            <circle cx="40" cy="40" r="36" fill="rgba(0,0,0,0.35)" stroke="rgba(255,255,255,0.12)" stroke-width="1.5"/>
            <circle cx="40" cy="40" r="27" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="0.8"/>
            <!-- Major tick marks -->
            <g stroke="rgba(255,255,255,0.25)" stroke-width="1.2">
              <line v-for="a in [0,45,90,135,180,225,270,315]" :key="a"
                x1="40" y1="7" x2="40" y2="13"
                :transform="`rotate(${a}, 40, 40)`"/>
            </g>
            <!-- Minor tick marks -->
            <g stroke="rgba(255,255,255,0.1)" stroke-width="0.7">
              <line v-for="a in [22,67,112,157,202,247,292,337]" :key="a"
                x1="40" y1="8" x2="40" y2="12"
                :transform="`rotate(${a}, 40, 40)`"/>
            </g>
            <!-- Cardinal text -->
            <text x="40" y="20.5" text-anchor="middle" fill="white" font-size="8.5" font-weight="900" font-family="ui-monospace,monospace">N</text>
            <text x="40" y="65"   text-anchor="middle" fill="rgba(255,255,255,0.35)" font-size="7.5" font-family="ui-monospace,monospace">S</text>
            <text x="64" y="43.5" text-anchor="middle" fill="rgba(255,255,255,0.35)" font-size="7.5" font-family="ui-monospace,monospace">E</text>
            <text x="16" y="43.5" text-anchor="middle" fill="rgba(255,255,255,0.35)" font-size="7.5" font-family="ui-monospace,monospace">W</text>
            <!-- Rotating needle -->
            <g :style="`transform-origin:40px 40px;transform:rotate(${telemetryState.heading}deg);transition:transform 0.45s ease`">
              <polygon points="40,14 43,40 40,34 37,40" fill="white" opacity="0.92"/>
              <polygon points="40,34 43,40 40,64 37,40" fill="rgba(239,68,68,0.6)"/>
            </g>
            <!-- Center dot -->
            <circle cx="40" cy="40" r="3" fill="white"/>
            <circle cx="40" cy="40" r="1.5" fill="rgba(0,0,0,0.5)"/>
          </svg>
        </div>

        <!-- Battery card -->
        <div class="bg-black/55 backdrop-blur-xl border border-white/10 rounded-xl px-3 py-2.5 w-[88px]">
          <p class="text-[8px] font-black uppercase tracking-[0.16em] text-white/35 mb-1.5">Battery</p>
          <p class="text-[26px] font-black font-mono leading-none"
            :class="telemetryState.battery >= 50 ? 'text-green-400' : telemetryState.battery >= 20 ? 'text-yellow-400' : 'text-red-400'">
            {{ telemetryState.connected ? telemetryState.battery : '--' }}<span class="text-xs font-normal text-white/25">%</span>
          </p>
          <div class="mt-2 h-[3px] bg-white/8 rounded-full overflow-hidden">
            <div class="h-full rounded-full transition-all duration-700"
              :class="telemetryState.battery >= 50 ? 'bg-green-400' : telemetryState.battery >= 20 ? 'bg-yellow-400' : 'bg-red-400'"
              :style="{ width: telemetryState.connected ? `${telemetryState.battery}%` : '0%' }"></div>
          </div>
        </div>

        <!-- Flight time card -->
        <div class="bg-black/55 backdrop-blur-xl border border-white/10 rounded-xl px-3 py-2.5 w-[88px]">
          <p class="text-[8px] font-black uppercase tracking-[0.16em] text-white/35 mb-1.5">Flight Time</p>
          <p class="text-sm font-black font-mono leading-none text-white/80 tracking-tight">{{ flightTimeFormatted }}</p>
          <p class="text-[8px] text-white/25 mt-1">mm:ss</p>
        </div>

      </div>

      <!-- ⑤ BOTTOM HUD BAR -->
      <div class="absolute bottom-0 left-0 right-0 z-20 bg-black/72 backdrop-blur-xl border-t border-white/8 flex items-stretch"
        style="height:70px;">

        <!-- Left: COMPLETED / REMAINING -->
        <div class="flex items-center gap-5 px-5 shrink-0">
          <div>
            <p class="text-[7.5px] font-black uppercase tracking-[0.2em] text-white/32 mb-0.5">COMPLETED</p>
            <p class="text-[22px] font-black font-mono text-white leading-none">{{ fmtDist(completedDistanceCm) }}</p>
          </div>
          <svg class="w-5 h-5 text-white/22 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
          </svg>
          <div>
            <p class="text-[7.5px] font-black uppercase tracking-[0.2em] text-white/32 mb-0.5">REMAINING DISTANCE</p>
            <p class="text-[22px] font-black font-mono text-white leading-none">{{ fmtDist(totalDistanceCm - completedDistanceCm) }}</p>
          </div>
        </div>

        <div class="w-px my-4 bg-white/8 shrink-0 mx-2"></div>

        <!-- Center: play/stop + timeline -->
        <div class="flex-1 flex items-center gap-4 px-3">

          <!-- Play / Stop button -->
          <button @click="isRunning ? handleEmergencyLand() : handleRunMission()"
            :disabled="!missionQueue.length && !isRunning"
            class="w-9 h-9 rounded-full flex items-center justify-center border transition-all shrink-0 disabled:opacity-30"
            :class="isRunning
              ? 'bg-red-600/75 border-red-500/40 hover:bg-red-500'
              : 'bg-white/10 border-white/20 hover:bg-white/22'">
            <svg v-if="isRunning" class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
              <rect x="6" y="6" width="12" height="12" rx="1"/>
            </svg>
            <svg v-else class="w-4 h-4 text-white ml-0.5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </button>

          <!-- Timeline track -->
          <div class="flex-1 relative h-[3px] bg-white/12 rounded-full">
            <div class="absolute left-0 top-0 h-full bg-white/75 rounded-full transition-all duration-500"
              :style="{ width: `${progressPercent}%` }"></div>
            <div v-for="wp in timelineWaypoints" :key="wp.idx"
              class="absolute top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 transition-all duration-300"
              :style="{ left: `${wp.pct}%` }"
              :class="wp.done
                ? 'w-3 h-3 bg-white border-white'
                : wp.active
                  ? 'w-3.5 h-3.5 bg-amber-400 border-amber-300 shadow-[0_0_8px_rgba(251,191,36,0.7)]'
                  : 'w-2 h-2 bg-gray-800 border-white/45'">
            </div>
          </div>
        </div>

        <div class="w-px my-4 bg-white/8 shrink-0 mx-2"></div>

        <!-- Right: alt + speed + steps mini-stats -->
        <div class="flex items-center gap-5 px-5 shrink-0">
          <div class="text-center">
            <p class="text-[7.5px] font-black uppercase tracking-[0.2em] text-white/28 mb-0.5">ALT</p>
            <p class="text-sm font-black font-mono text-cyan-300/75 leading-none">
              {{ telemetryState.altitude_m.toFixed(1) }}<span class="text-[9px] font-normal text-white/22">m</span>
            </p>
          </div>
          <div class="text-center">
            <p class="text-[7.5px] font-black uppercase tracking-[0.2em] text-white/28 mb-0.5">SPD</p>
            <p class="text-sm font-black font-mono text-cyan-300/75 leading-none">
              {{ telemetryState.speed }}<span class="text-[9px] font-normal text-white/22">cm/s</span>
            </p>
          </div>
          <div class="text-center">
            <p class="text-[7.5px] font-black uppercase tracking-[0.2em] text-white/28 mb-0.5">STEPS</p>
            <p class="text-sm font-black font-mono text-white/65 leading-none">
              {{ Math.max(0, currentStepIndex) }}<span class="text-[9px] font-normal text-white/25">/{{ missionQueue.length }}</span>
            </p>
          </div>
        </div>

      </div>

      <!-- Active step label (floats above HUD when running) -->
      <Transition enter-active-class="transition-all duration-300 ease-out" leave-active-class="transition-all duration-200 ease-in"
        enter-from-class="translate-y-2 opacity-0" leave-to-class="translate-y-2 opacity-0">
        <div v-if="isRunning && currentStepIndex >= 0 && missionQueue[currentStepIndex]"
          class="absolute bottom-[74px] left-1/2 -translate-x-1/2 z-20 pointer-events-none">
          <div class="bg-amber-500/20 backdrop-blur-lg border border-amber-500/35 rounded-lg px-4 py-1.5 flex items-center gap-2">
            <span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping shrink-0"></span>
            <span class="text-[10px] font-black text-amber-300 uppercase tracking-widest">
              Step {{ currentStepIndex + 1 }}: {{ missionQueue[currentStepIndex]?.label }}
            </span>
          </div>
        </div>
      </Transition>

      <!-- ⑥ Confirmation Modal -->
      <ConfirmationModal
        :isOpen="showCompleteModal"
        :title="modalConfig.title"
        :message="modalConfig.message"
        :isWarning="modalConfig.isWarning"
        :isSuccess="modalConfig.isSuccess"
        :cancelText="modalConfig.cancelText"
        @cancel="showCompleteModal = false"
      />

    </div><!-- /main canvas -->
  </div>
</template>

<style scoped>
/* ── Drawer inputs: dark text on opaque bg so content is readable ── */
input[type="number"],
input[type="text"],
select {
  background-color: rgba(255, 255, 255, 0.92) !important;
  color: #111827 !important;            /* gray-900 */
  border-color: rgba(255,255,255,0.25) !important;
}

input[type="number"]::placeholder,
input[type="text"]::placeholder {
  color: #9ca3af !important;            /* gray-400 */
}

/* Keep the select option list dark */
select option {
  background-color: #111827;
  color: #ffffff;
}
</style>
