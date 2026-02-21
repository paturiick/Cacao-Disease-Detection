<script setup>
import { reactive, ref } from 'vue';
import DashboardNavBar from '~/components/organisms/NavBar.vue';

// --- 1. IMPORT ICONS ---
import UpIcon from '~/assets/icons/Up.svg';
import DownIcon from '~/assets/icons/Down.svg';
import LeftIcon from '~/assets/icons/Left.svg';
import RightIcon from '~/assets/icons/Right.svg';
import ForwardIcon from '~/assets/icons/Forward.svg';
import BackwardIcon from '~/assets/icons/Backward.svg';

// Import Organisms
import FlightParametersCard from '~/components/organisms/mission_planner_organism/FlightParametersCard.vue';
import MissionCommandsCard from '~/components/organisms/mission_planner_organism/MissionCommandsCard.vue';
import MissionHistoryCard from '~/components/organisms/mission_planner_organism/MissionHistoryCard.vue';
import ControlPanel from '~/components/organisms/mission_planner_organism/ControlPanel.vue';

// Import Modal
import ConfirmationModal from '~/components/molecules/mission_plan_molecules/ConfirmationModal.vue';

// --- STATE ---
const missionQueue = ref([]);
const isRunning = ref(false);
const currentStepIndex = ref(-1);

const flightParams = reactive({
  altitude: 10,
  speed: 15,
  mode: 'Stabilize'
});

const telemetry = reactive({
  gps: 'Weak',
  battery: 0,
  batteryColor: 'bg-red-500'
});

// --- NEW: Modal State ---
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
  { label: 'Fly Up',      value: 'up',      unit: 's', icon: UpIcon },
  { label: 'Fly Down',    value: 'down',    unit: 's', icon: DownIcon },
  { label: 'Fly Left',    value: 'left',    unit: 's', icon: LeftIcon },
  { label: 'Fly Right',   value: 'right',   unit: 's', icon: RightIcon },
  { label: 'Fly Forward', value: 'forward', unit: 's', icon: ForwardIcon },
  { label: 'Fly Back',    value: 'back',    unit: 's', icon: BackwardIcon },
  { label: 'Rotate CW',   value: 'cw',      unit: 's', icon: `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>` },
  { label: 'Rotate CCW',  value: 'ccw',     unit: 's', icon: `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="transform: scaleX(-1);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>` },
  { label: 'Hover',       value: 'hover',   unit: 's', icon: `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>` },
];

// --- HANDLERS ---
const handleAddCommand = (cmd) => {
  const details = commandOptions.find(c => c.value === cmd.type);
  missionQueue.value.push({
    id: Date.now(),
    type: cmd.type,
    val: cmd.val,
    label: details.label,
    icon: details.icon,
    unit: details.unit
  });
};

const handleRemoveCommand = (index) => {
  missionQueue.value.splice(index, 1);
};

const handleClear = () => {
  missionQueue.value = [];
  currentStepIndex.value = -1;
};

const handleRunMission = async () => {
  isRunning.value = true;
  currentStepIndex.value = -1;

  // Simulate Connection
  telemetry.gps = 'Strong';
  telemetry.battery = 84;
  telemetry.batteryColor = 'bg-[#658D1B]';

  // 1. Initial Config
  currentStepIndex.value = 0;
  await new Promise(r => setTimeout(r, 2000));

  // 2. Execute Steps
  for (let i = 0; i < missionQueue.value.length; i++) {
    currentStepIndex.value = i + 1;
    const stepDuration = missionQueue.value[i].val * 1000;
    await new Promise(r => setTimeout(r, stepDuration));
  }

  isRunning.value = false;
  currentStepIndex.value = -1;
  
  // --- UPDATED: Trigger Success Modal ---
  modalConfig.title = "Mission Complete";
  modalConfig.message = "The drone has successfully executed all flight plan commands.";
  modalConfig.isWarning = false; 
  modalConfig.isSuccess = true;
  modalConfig.cancelText = "Close"; 
  
  showCompleteModal.value = true;
};
</script>

<template>
  <div 
    class="flex flex-col h-screen overflow-hidden font-inter bg-cover bg-center relative"
    style="background-image: url('https://images.unsplash.com/photo-1542319084-2a6c38210350?q=80&w=2574&auto=format&fit=crop');"
  >
    <div class="absolute inset-0 bg-black/40 z-0"></div>

    <div class="z-20 relative">
      <DashboardNavBar active-page="mission-planner" />
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
           />
        </div>

        <div class="w-full xl:w-1/3 flex flex-col gap-6">
           <ControlPanel 
             :hasMission="missionQueue.length > 0"
             :isRunning="isRunning"
             :telemetry="telemetry"
             @run="handleRunMission"
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