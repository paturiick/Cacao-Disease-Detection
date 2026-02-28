<script setup>
import { reactive, ref, onMounted, watch, onBeforeUnmount } from 'vue';
import { missionApi } from "~/sections/api/missionApi"; 

import DashboardNavBar from '~/components/organisms/NavBar.vue';

// --- ICONS ---
import UpIcon from '~/assets/icons/Up.svg';
import DownIcon from '~/assets/icons/Down.svg';
import LeftIcon from '~/assets/icons/Left.svg';
import RightIcon from '~/assets/icons/Right.svg';
import ForwardIcon from '~/assets/icons/Forward.svg';
import BackwardIcon from '~/assets/icons/Backward.svg';

// Organisms
import FlightParametersCard from '~/components/organisms/mission_planner_organism/FlightParametersCard.vue';
import MissionCommandsCard from '~/components/organisms/mission_planner_organism/MissionCommandsCard.vue';
import MissionHistoryCard from '~/components/organisms/mission_planner_organism/MissionHistoryCard.vue';
import ControlPanel from '~/components/organisms/mission_planner_organism/ControlPanel.vue';

// Modal
import ConfirmationModal from '~/components/molecules/mission_plan_molecules/ConfirmationModal.vue';

// --- STATE ---
const planId = ref(null);

const missionQueue = ref([]);
const isRunning = ref(false);
const isLanding = ref(false); 
const currentStepIndex = ref(-1);

// flightParams now includes the missionPad state controlled by FlightParametersCard
const flightParams = reactive({
  altitude: 1,
  speed: 30, 
  mode: 'Stabilize',
  missionPad: false 
});

const telemetry = reactive({
  gps: 'Weak',
  battery: 0,
  batteryColor: 'bg-red-500'
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
// Removed 'Enable Mission Pad' ('mon') since it's now a global flight parameter toggle
const commandOptions = [
  { label: 'Fly Up',      value: 'up',      unit: 'cm', icon: UpIcon },
  { label: 'Fly Down',    value: 'down',    unit: 'cm', icon: DownIcon },
  { label: 'Fly Left',    value: 'left',    unit: 'cm', icon: LeftIcon },  
  { label: 'Fly Right',   value: 'right',   unit: 'cm', icon: RightIcon },
  { label: 'Fly Forward', value: 'forward', unit: 'cm', icon: ForwardIcon },
  { label: 'Fly Back',    value: 'back',    unit: 'cm', icon: BackwardIcon },
  { label: 'Rotate CW',   value: 'cw',      unit: 'deg', icon: `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>` },
  { label: 'Rotate CCW',  value: 'ccw',     unit: 'deg', icon: `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="transform: scaleX(-1);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>` },
  { label: 'Hover',       value: 'hover',   unit: 's', icon: `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>` },
  { label: 'XYZ Coordinates', value: 'go',  unit: 'x y z spd', icon: `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122"></path></svg>` }
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
  if (!planId.value) return;

  const created = await missionApi.addStep(planId.value, {
    type: cmd.type,
    val: cmd.val
  });

  missionQueue.value.push(decorateStep(created));
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
        modalConfig.message =
          s.status === 'completed'
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
});
</script>

<template>
  <div
    class="flex flex-col h-screen overflow-hidden font-inter bg-cover bg-center relative"
    style="background-image: url('https://images.unsplash.com/photo-1542319084-2a6c38210350?q=80&w=2574&auto=format&fit=crop');"
  >
    <div class="absolute inset-0 bg-black/40 z-0"></div>

    <div class="z-20 relative">
      <DashboardNavBar :activePage="'mission-planner'" :droneStatus="telemetry.gps"/>
    </div>

    <div class="flex-1 z-10 p-6 overflow-y-auto relative">
      <div class="flex flex-col xl:flex-row gap-6 h-full max-w-[1600px] mx-auto">

        <div class="w-full xl:w-1/4 flex flex-col gap-6">
          <FlightParametersCard v-model="flightParams" />
          <MissionCommandsCard :commandOptions="commandOptions" @add="handleAddCommand" />
        </div>

        <div class="w-full xl:w-2/5 flex flex-col h-full">
          <MissionHistoryCard
            :queue="missionQueue"
            :isRunning="isRunning"
            :activeIndex="currentStepIndex"
            :flightParams="flightParams"
            @remove="handleRemoveCommand"
            @clear="handleClear"
            @reorder="handleReorderCommand" 
          />
        </div>

        <div class="w-full xl:w-1/3 flex flex-col gap-6">
          <ControlPanel
            :hasMission="missionQueue.length > 0"
            :isRunning="isRunning"
            :isLanding="isLanding" 
            :telemetry="telemetry"
            @run="handleRunMission"
            @force-land="handleEmergencyLand"
            @stop-hover="handleStopHover"
            @emergency="handleEmergencyCutoff"
          />
        </div>

      </div>
    </div>

    <ConfirmationModal
      :isOpen="showCompleteModal"
      :title="modalConfig.title"
      :message="modalConfig.message"
      :isWarning="modalConfig.isWarning"
      :isSuccess="modalConfig.isSuccess"
      :cancelText="modalConfig.cancelText"
      @cancel="showCompleteModal = false"
    />
  </div>
</template>