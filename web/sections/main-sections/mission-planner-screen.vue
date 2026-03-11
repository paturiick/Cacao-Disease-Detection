<script setup>
import { reactive, ref, onMounted, watch, onBeforeUnmount, computed } from 'vue';
import { missionApi } from "~/sections/api/missionApi"; 
import { useTelemetry } from "~/components/composables/useTelemetry"; 

import DashboardNavBar from '~/components/organisms/NavBar.vue';

// --- ICONS ---
import UpIcon from '~/assets/icons/Up.svg';
import DownIcon from '~/assets/icons/Down.svg';
import LeftIcon from '~/assets/icons/Left.svg';
import RightIcon from '~/assets/icons/Right.svg';
import ForwardIcon from '~/assets/icons/Forward.svg';
import BackwardIcon from '~/assets/icons/Backward.svg';

// Molecules
import ConfirmationModal from '~/components/molecules/mission_plan_molecules/ConfirmationModal.vue';

// Organisms
import FlightParametersCard from '~/components/organisms/mission_planner_organism/FlightParametersCard.vue';
import MissionCommandsCard from '~/components/organisms/mission_planner_organism/MissionCommandsCard.vue';
import MissionHistoryCard from '~/components/organisms/mission_planner_organism/MissionHistoryCard.vue';
import ControlPanel from '~/components/organisms/mission_planner_organism/ControlPanel.vue';

const { telemetryState, startPolling, stopPolling } = useTelemetry();

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
  { label: 'Rotate CW',   value: 'cw',      unit: 'deg', icon: `<svg class="w-6 h-6" ...` },
  { label: 'Rotate CCW',  value: 'ccw',     unit: 'deg', icon: `<svg class="w-6 h-6" ...` },
  { label: 'Hover',       value: 'hover',   unit: 's',   icon: `<svg class="w-6 h-6" ...` },
  { label: 'XYZ Coordinates', value: 'go',  unit: 'x y z spd', icon: `<svg class="w-6 h-6" ...` }
];

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

let fpTimer = null;
watch(
  () => ({ ...flightParams }),
  () => {
    if (!planId.value) return;
    clearTimeout(fpTimer);
    fpTimer = setTimeout(() => {
      missionApi.patchPlan(planId.value, { ...flightParams });
    }, 350);
  },
  { deep: true }
);

// --- HANDLERS (Manual Mode Only) ---
const handleAddCommand = async (cmd) => {
  if (!planId.value) return;
  const created = await missionApi.addStep(planId.value, { type: cmd.type, val: cmd.val });
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

const handleEditCommand = async ({ index, type, val }) => {
  const step = missionQueue.value[index];
  if (!step || !planId.value) return;

  step.type = type;
  step.val = val;
  missionQueue.value.splice(index, 1, decorateStep(step));

  try {
    if (missionApi.updateStep) {
      await missionApi.updateStep(step.id, { type, val });
    }
  } catch (error) {
    console.error("Failed to update step:", error);
  }
};

// --- STATUS POLLING ---
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
      currentStepIndex.value = s.status === 'running' ? (s.active_index ?? -1) : -1;

      if (['completed', 'failed', 'cancelled', 'inactive'].includes(s.status)) {
        stopStatusPoll();
        isRunning.value = false;
        isLanding.value = false; 
        currentStepIndex.value = -1;

        modalConfig.title = s.status === 'completed' ? 'Mission Complete' : 'Mission Ended';
        modalConfig.message = s.status === 'completed' 
          ? 'The drone successfully executed the flight plan.' 
          : (s.message || `Status: ${s.status}`);

        modalConfig.isWarning = s.status !== 'completed';
        modalConfig.isSuccess = s.status === 'completed';
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
      modalConfig.title = "Mission Failed to Start";
      modalConfig.message = res.message || "An error occurred.";
      modalConfig.isWarning = true;
      showCompleteModal.value = true;
      isRunning.value = false;
      return;
    }
    startStatusPoll();
  } catch (e) {
    console.error("Mission run failed", e);
    isRunning.value = false;
  }
};

const handleEmergencyLand = async () => {
  if (isLanding.value) return;
  isLanding.value = true;
  try {
    await missionApi.forceLand();
  } catch (e) {
    console.error("Landing failed:", e);
  } finally {
    setTimeout(() => { isLanding.value = false; }, 2000);
  }
};

onBeforeUnmount(() => {
  stopStatusPoll();
  clearTimeout(fpTimer);
  stopPolling();
});
</script>

<template>
  <div
    class="flex flex-col h-screen overflow-hidden font-inter bg-cover bg-center relative"
    style="background-image: url('https://images.unsplash.com/photo-1542319084-2a6c38210350?q=80&w=2574&auto=format&fit=crop');"
  >
    <div class="absolute inset-0 bg-black/40 z-0"></div>

    <div class="z-20 relative">
      <DashboardNavBar :activePage="'mission-planner'" :droneStatus="formattedTelemetry.gps"/>
    </div>

    <div class="flex-1 z-10 p-6 overflow-y-auto relative">
      <div class="flex flex-col xl:flex-row gap-6 h-full max-w-[1600px] mx-auto">

        <div class="w-full xl:w-1/4 flex flex-col gap-6">
          <FlightParametersCard v-model="flightParams" />
          <div class="flex-1 flex flex-col">
            <MissionCommandsCard :commandOptions="commandOptions" @add="handleAddCommand" />
          </div>
        </div>

        <div class="w-full xl:w-2/5 flex flex-col h-full">
          <MissionHistoryCard
            :queue="missionQueue"
            :isRunning="isRunning"
            :activeIndex="currentStepIndex"
            :flightParams="flightParams"
            :commandOptions="commandOptions"
            @remove="handleRemoveCommand"
            @clear="handleClear"
            @reorder="handleReorderCommand" 
            @edit="handleEditCommand"
          />
        </div>

        <div class="w-full xl:w-1/3 flex flex-col gap-6">
          <ControlPanel
            :hasMission="missionQueue.length > 0"
            :isRunning="isRunning"
            :isLanding="isLanding" 
            :telemetry="formattedTelemetry"
            @run="handleRunMission"
            @force-land="handleEmergencyLand"
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