<script setup>
import { ref, watch, computed, reactive } from 'vue';

// 1. Import all THREE of your main screen organisms
import FlightParametersCard from '~/components/organisms/mission_planner_organism/FlightParametersCard.vue';
import MissionCommandsCard from '~/components/organisms/mission_planner_organism/MissionCommandsCard.vue';
import MissionHistoryCard from '~/components/organisms/mission_planner_organism/MissionHistoryCard.vue';

const props = defineProps({
  isOpen: Boolean,
  presetToEdit: {
    type: Object,
    default: null
  },
  commandOptions: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['close', 'save']);

// --- Form State ---
const presetName = ref('');
const flightParams = reactive({ speed: 23 });
const steps = ref([]);

// --- Toast Notification State ---
const toastMessage = ref('');
const showToast = ref(false);
let toastTimer = null;

const triggerToast = (message) => {
  toastMessage.value = message;
  showToast.value = true;
  
  if (toastTimer) clearTimeout(toastTimer);
  
  toastTimer = setTimeout(() => {
    showToast.value = false;
  }, 3000);
};

// --- Watch for edit mode to populate fields ---
watch(() => props.isOpen, (newVal) => {
  if (newVal && props.presetToEdit) {
    presetName.value = props.presetToEdit.name;
    flightParams.speed = props.presetToEdit.speed;
    steps.value = JSON.parse(JSON.stringify(props.presetToEdit.steps)); 
  } else if (newVal) {
    presetName.value = '';
    flightParams.speed = 23;
    steps.value = [];
  }
});

// --- COMMAND ACTIONS (Passed to MissionHistoryCard & CommandsCard) ---

const handleAddCommand = (cmd) => {
  steps.value.push({
    id: Date.now() + Math.floor(Math.random() * 1000), 
    type: cmd.type,
    val: cmd.val,
    speed: null 
  });
};

const handleRemoveStep = (index) => {
  steps.value.splice(index, 1);
};

const handleClearSteps = () => {
  steps.value = [];
};

const handleReorderSteps = ({ from, to }) => {
  const movedItem = steps.value.splice(from, 1)[0];
  steps.value.splice(to, 0, movedItem);
};

const handleEditStep = ({ index, type, val, speed }) => {
  steps.value[index] = { ...steps.value[index], type, val, speed };
};

const handleDuplicateStep = (index) => {
  const itemToCopy = steps.value[index];
  steps.value.splice(index + 1, 0, {
    ...itemToCopy,
    id: Date.now() + Math.floor(Math.random() * 1000)
  });
};

// Decorate the steps so MissionHistoryCard can render icons and units
const decoratedSteps = computed(() => {
  return steps.value.map(step => {
    const details = props.commandOptions.find(c => c.value === step.type);
    return {
      ...step,
      label: details?.label ?? step.type,
      icon: details?.icon ?? null,
      unit: details?.unit ?? ''
    };
  });
});

// --- SAVE LOGIC ---

const savePreset = () => {
  if (!presetName.value.trim()) {
    triggerToast("Please enter a preset name before saving.");
    return;
  }
  
  const finalPresetData = {
    id: props.presetToEdit ? props.presetToEdit.id : Date.now(),
    name: presetName.value.trim(),
    speed: flightParams.speed,
    steps: steps.value.map(s => ({ 
      id: s.id, 
      type: s.type, 
      val: s.val, 
      speed: s.speed 
    }))
  };

  emit('save', finalPresetData);
  emit('close');
};
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-6 transition-opacity font-poppins">
    
    <div class="bg-slate-50 rounded-2xl shadow-2xl w-full max-w-[1700px] h-[90vh] flex flex-col overflow-hidden border border-slate-200 relative" @click.stop>
      
      <transition name="toast-pop">
        <div v-if="showToast" class="absolute top-6 left-1/2 -translate-x-1/2 z-[60] flex items-center gap-2.5 bg-red-600 text-white px-5 py-3 rounded-xl shadow-[0_8px_30px_rgb(0,0,0,0.12)] border border-red-500 pointer-events-none">
          <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
          <span class="text-sm font-bold tracking-wide">{{ toastMessage }}</span>
        </div>
      </transition>

      <div class="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between shrink-0">
        <div class="flex items-center gap-6 flex-1">
          <div>
            <h2 class="text-xl font-black text-slate-800">
              {{ presetToEdit ? 'Edit Flight Preset' : 'Create Flight Preset' }}
            </h2>
            <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Preset Builder Mode</p>
          </div>
          
          <div class="w-px h-8 bg-slate-200"></div>

          <div class="flex items-center gap-4">
            <div class="flex items-center gap-2">
              <label class="text-sm font-bold text-slate-600">Preset Name:</label>
              <input v-model="presetName" type="text" placeholder="e.g., Grid Scan Route" class="w-72 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-[#658D1B] outline-none text-sm font-medium transition-all shadow-sm" />
            </div>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <button @click="$emit('close')" class="px-5 py-2.5 font-bold text-slate-600 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition-colors">
            Cancel
          </button>
          <button @click="savePreset" class="px-6 py-2.5 font-bold text-white bg-[#658D1B] rounded-xl hover:bg-[#557516] transition-colors shadow-lg shadow-[#658D1B]/20 flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"></path></svg>
            Save Preset
          </button>
        </div>
      </div>

      <div class="flex-1 overflow-hidden p-6 grid grid-cols-12 gap-6">
        
        <div class="col-span-4 flex flex-col gap-6 h-full">
          <FlightParametersCard 
            v-model="flightParams" 
            class="shrink-0 border border-slate-200 shadow-sm rounded-2xl" 
          />

          <MissionCommandsCard 
            :commandOptions="commandOptions" 
            @add="handleAddCommand" 
            class="flex-1 min-h-0 border border-slate-200 shadow-sm rounded-2xl" 
          />
        </div>

        <div class="col-span-8 flex flex-col h-full relative overflow-hidden">
          <MissionHistoryCard
            :queue="decoratedSteps"
            :activeIndex="-1"
            :isRunning="false"
            :flightParams="flightParams"
            :commandOptions="commandOptions"
            mode="plan"
            @remove="handleRemoveStep"
            @clear="handleClearSteps"
            @reorder="handleReorderSteps" 
            @edit="handleEditStep"
            @duplicate="handleDuplicateStep"
            class="h-full border border-slate-200 shadow-sm rounded-2xl"
          />
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 10px; }

/* Toast Animation */
.toast-pop-enter-active,
.toast-pop-leave-active {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.toast-pop-enter-from,
.toast-pop-leave-to {
  opacity: 0;
  transform: translate(-50%, -20px);
}
</style>