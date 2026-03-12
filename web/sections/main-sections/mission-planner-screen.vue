<script setup>
import { reactive, ref, onMounted, watch, onBeforeUnmount, computed } from 'vue';
import { missionApi } from "~/sections/api/missionApi"; 
import { useTelemetry } from "~/components/composables/useTelemetry"; 

import DashboardNavBar from '~/components/organisms/NavBar.vue';

import UpIcon from '~/assets/icons/Up.svg';
import DownIcon from '~/assets/icons/Down.svg';
import LeftIcon from '~/assets/icons/Left.svg';
import RightIcon from '~/assets/icons/Right.svg';
import ForwardIcon from '~/assets/icons/Forward.svg';
import BackwardIcon from '~/assets/icons/Backward.svg';
import ClockwiseIcon from '~/assets/icons/Clockwise.svg';
import CounterClockwiseIcon from '~/assets/icons/Counter-clockwise.svg';
import HoverIcon from '~/assets/icons/Hover.svg';

import ConfirmationModal from '~/components/molecules/mission_plan_molecules/ConfirmationModal.vue';
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

// Tracks Drawing Mode state centrally
const isDrawingMode = ref(false);

const flightParams = reactive({ 
  altitude: 2,
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
  title: '', message: '', isWarning: false, isSuccess: false, cancelText: 'Close'
});

const commandOptions = [
  { label: 'Fly Up',      value: 'up',      unit: 'cm', icon: UpIcon },
  { label: 'Fly Down',    value: 'down',    unit: 'cm', icon: DownIcon },
  { label: 'Fly Left',    value: 'left',    unit: 'cm', icon: LeftIcon },  
  { label: 'Fly Right',   value: 'right',   unit: 'cm', icon: RightIcon },
  { label: 'Fly Forward', value: 'forward', unit: 'cm', icon: ForwardIcon },
  { label: 'Fly Back',    value: 'back',    unit: 'cm', icon: BackwardIcon },
  { label: 'Rotate CW',   value: 'cw',      unit: 'deg', icon: ClockwiseIcon},
  { label: 'Rotate CCW',  value: 'ccw',     unit: 'deg', icon: CounterClockwiseIcon},
  { label: 'Hover',       value: 'hover',   unit: 's',   icon: HoverIcon },
  { label: 'XYZ Coordinates', value: 'go',  unit: 'x y z spd', icon: `<svg...` }
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
    missionQueue.value = (plan.steps || []).sort((a, b) => (a.order ?? 0) - (b.order ?? 0)).map(decorateStep);
    const s = await missionApi.status();
    if (s.status === 'running' || s.status === 'queued') {
      isRunning.value = true;
      startStatusPoll();
    }
  } catch(e) {}
});

let fpTimer = null;
watch(() => ({ ...flightParams }), () => {
  if (!planId.value) return;
  clearTimeout(fpTimer);
  fpTimer = setTimeout(() => { missionApi.patchPlan(planId.value, { ...flightParams }); }, 350);
}, { deep: true });

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
  if (missionApi.updateStep) await missionApi.updateStep(step.id, { type, val });
};

const handleSyncDrawnCommands = async (newCommands) => {
  if (!planId.value) return;
  await missionApi.clearSteps(planId.value);
  missionQueue.value = [];
  currentStepIndex.value = -1;
  for (const cmd of newCommands) {
    const created = await missionApi.addStep(planId.value, { type: cmd.type, val: cmd.val });
    missionQueue.value.push(decorateStep(created));
  }
};

let statusPoll = null;
const stopStatusPoll = () => { if (statusPoll) clearInterval(statusPoll); statusPoll = null; };
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
        modalConfig.message = s.status === 'completed' ? 'The drone successfully executed the flight plan.' : (s.message || `Status: ${s.status}`);
        modalConfig.isWarning = s.status !== 'completed';
        modalConfig.isSuccess = s.status === 'completed';
        showCompleteModal.value = true;
      }
    } catch (e) {}
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
    isRunning.value = false;
  }
};

const handleEmergencyLand = async () => {
  if (isLanding.value) return;
  isLanding.value = true;
  try { await missionApi.forceLand(); } catch (e) {} finally { setTimeout(() => { isLanding.value = false; }, 2000); }
};

onBeforeUnmount(() => {
  stopStatusPoll();
  clearTimeout(fpTimer);
  stopPolling();
});
</script>

<template>
  <div class="flex flex-col h-screen overflow-hidden font-inter bg-cover bg-center relative" style="background-image: url('https://images.unsplash.com/photo-1542319084-2a6c38210350?q=80&w=2574&auto=format&fit=crop');">
    <div class="absolute inset-0 bg-black/40 z-0"></div>

    <div class="z-20 relative">
      <DashboardNavBar :activePage="'mission-planner'" :droneStatus="formattedTelemetry.gps"/>
    </div>

    <div class="flex-1 z-10 p-6 overflow-hidden relative">
      <div class="flex flex-col xl:flex-row gap-6 h-full max-w-[1800px] mx-auto transition-all duration-700">

        <div class="w-full xl:w-80 flex flex-col gap-6 shrink-0 h-full">
          <FlightParametersCard v-model="flightParams" />
          
          <Transition name="card-fold">
            <div v-if="!isDrawingMode" class="flex-1 flex flex-col min-h-0 origin-top">
              <MissionCommandsCard :commandOptions="commandOptions" @add="handleAddCommand" />
            </div>
          </Transition>
        </div>

        <div class="flex flex-col h-full min-h-0 transition-all duration-700 ease-in-out"
             :class="isDrawingMode ? 'flex-[2.5]' : 'flex-1'">
          <MissionHistoryCard
            :queue="missionQueue"
            :isRunning="isRunning"
            :activeIndex="currentStepIndex"
            :flightParams="flightParams"
            :commandOptions="commandOptions"
            :isDrawingMode="isDrawingMode"
            @mode-change="isDrawingMode = $event"
            @remove="handleRemoveCommand"
            @clear="handleClear"
            @reorder="handleReorderCommand" 
            @edit="handleEditCommand"
            @sync-drawn-commands="handleSyncDrawnCommands"
          />
        </div>

        <div class="w-full xl:w-96 flex flex-col gap-6 shrink-0 h-full">
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
      :isOpen="showCompleteModal" :title="modalConfig.title" :message="modalConfig.message"
      :isWarning="modalConfig.isWarning" :isSuccess="modalConfig.isSuccess" :cancelText="modalConfig.cancelText"
      @cancel="showCompleteModal = false"
    />
  </div>
</template>

<style scoped>
/* THE "FOLD & BLUR" TRANSITION 
  Uses scaleY and translateY to make the card feel like a physical panel 
  retracting into the component above it.
*/
.card-fold-enter-active {
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1); /* Slight spring bounce on entry */
}

.card-fold-leave-active {
  transition: all 0.4s cubic-bezier(0.36, 0, 0.66, -0.56); /* Acceleration on exit */
}

.card-fold-enter-from,
.card-fold-leave-to {
  opacity: 0;
  transform: scaleY(0.8) translateY(-40px);
  filter: blur(10px);
  flex-grow: 0.0001; /* Animates the flex container collapse without height math */
  margin-top: -24px; /* Eliminates the gap-6 spacing smoothly */
}

/* LAYOUT STABILITY
  Ensures the middle column resizes at the exact same speed as the card animation
*/
.flex-1, .flex-\[2\.5\] {
  transition: flex 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: flex;
}

/* Prevents scrollbar flickering during the half-second animation */
.overflow-hidden {
  scrollbar-width: none;
}
</style>