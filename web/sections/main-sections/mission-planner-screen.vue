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
const isDrawingMode = ref(false);

const currentMode = ref('plan'); 

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

const isFlying = computed(() => {
  return telemetryState.connected && (telemetryState.alt > 0);
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
  { label: 'XYZ Coordinates', value: 'go',  unit: 'x y z', icon: ForwardIcon },
  { label: 'RC Override', value: 'rc', unit: 'a b c d s', icon: HoverIcon }
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
  // Removed the strict frontend telemetry check.
  // The backend API will now dictate if it's safe/possible to run the mission.

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

const handleLiveRcCommand = async (rcData) => {
  try {
    const rcString = `${rcData.a} ${rcData.b} ${rcData.c} ${rcData.d}`;
    await missionApi.start([{ command: 'rc', value: rcString }]);
  } catch (error) {
    console.error("RC transmission failed", error);
  }
};

const handleTakeoff = async () => {
  try { await missionApi.start([{ command: 'takeoff', value: null }]); } 
  catch (e) { console.error("Takeoff failed", e); }
};

const handleLand = async () => {
  try { await missionApi.start([{ command: 'land', value: null }]); } 
  catch (e) { console.error("Land failed", e); }
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
      <DashboardNavBar :activePage="'mission-planner'" :droneStatus="formattedTelemetry.gps" :battery="formattedTelemetry.battery"/>
    </div>

    <div class="flex-1 z-10 p-6 overflow-hidden relative">
      <div class="flex flex-col xl:flex-row gap-6 h-full max-w-[1800px] mx-auto transition-all duration-700">

        <div 
          v-show="currentMode === 'plan'" 
          class="w-full xl:w-80 flex flex-col gap-6 shrink-0 h-full overflow-y-auto custom-scrollbar pr-2"
        >
          <FlightParametersCard v-model="flightParams" />
          
          <Transition name="card-fold">
            <div v-if="!isDrawingMode" class="flex flex-col gap-6 origin-top">
              <MissionCommandsCard :commandOptions="commandOptions" @add="handleAddCommand" />
            </div>
          </Transition>
        </div>

        <div class="flex flex-col h-full min-h-0 transition-all duration-700 ease-in-out"
             :class="(isDrawingMode || currentMode === 'rc') ? 'flex-[2.5]' : 'flex-1'">
          <MissionHistoryCard
            :queue="missionQueue"
            :isRunning="isRunning"
            :activeIndex="currentStepIndex"
            :flightParams="flightParams"
            :commandOptions="commandOptions"
            :isDrawingMode="isDrawingMode"
            :mode="currentMode"
            @update:mode="currentMode = $event"
            @mode-change="isDrawingMode = $event"
            @remove="handleRemoveCommand"
            @clear="handleClear"
            @reorder="handleReorderCommand" 
            @edit="handleEditCommand"
            @sync-drawn-commands="handleSyncDrawnCommands"
            @send-rc="handleLiveRcCommand"
            @save-to-plan="(rc) => handleAddCommand({ type: 'rc', val: `${rc.a} ${rc.b} ${rc.c} ${rc.d} 5` })"
          />
        </div>

        <div class="w-full xl:w-96 flex flex-col gap-6 shrink-0 h-full overflow-y-auto custom-scrollbar pl-2">
          
          <ControlPanel
            v-show="currentMode === 'plan'"
            :hasMission="missionQueue.length > 0"
            :isRunning="isRunning"
            :isLanding="isLanding" 
            :telemetry="formattedTelemetry"
            @run="handleRunMission"
            @force-land="handleEmergencyLand"
          />

          <div v-show="currentMode === 'rc'" class="bg-slate-50 rounded-xl border border-slate-200 shadow-sm p-4 w-full flex flex-col shrink-0">
            <h3 class="font-bold text-slate-800 text-sm flex items-center gap-2 mb-3">
              <svg class="w-4 h-4 text-[#658D1B]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
              RC Flight Control
            </h3>
            
            <div class="flex gap-3 w-full mb-3">
              <button @click="handleTakeoff" :disabled="isFlying" class="flex-1 py-3 rounded-lg font-bold text-sm tracking-wide uppercase transition-colors flex justify-center items-center gap-2" :class="isFlying ? 'bg-slate-200 text-slate-400 cursor-not-allowed shadow-none' : 'bg-[#658D1B] hover:bg-[#557516] text-white shadow-md'"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"></path></svg>Takeoff</button>
              <button @click="handleLand" :disabled="!isFlying" class="flex-1 py-3 rounded-lg font-bold text-sm tracking-wide uppercase transition-colors flex justify-center items-center gap-2" :class="!isFlying ? 'bg-slate-200 text-slate-400 cursor-not-allowed shadow-none' : 'bg-slate-800 hover:bg-slate-900 text-white shadow-md'"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg>Land</button>
            </div>

            <button @click="handleEmergencyLand" :disabled="!isFlying" class="w-full py-3 rounded-lg font-bold text-sm tracking-wide uppercase transition-colors flex justify-center items-center gap-2" :class="!isFlying ? 'bg-red-100 text-red-300 cursor-not-allowed shadow-none' : 'bg-red-600 hover:bg-red-700 text-white shadow-md'"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>Emergency Land</button>
          </div>
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
.card-fold-enter-active { transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1); }
.card-fold-leave-active { transition: all 0.4s cubic-bezier(0.36, 0, 0.66, -0.56); }
.card-fold-enter-from, .card-fold-leave-to { opacity: 0; transform: scaleY(0.8) translateY(-40px); filter: blur(10px); margin-top: -24px; }

.flex-1, .flex-\[2\.5\] { transition: flex 0.6s cubic-bezier(0.4, 0, 0.2, 1); will-change: flex; }

/* CUSTOM SCROLLBAR LOGIC */
.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(101, 141, 27, 0.4);
}

.overflow-hidden { scrollbar-width: none; }
</style>