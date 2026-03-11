<script setup>
import { ref, reactive, computed } from 'vue';
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';
import MissionListEmpty from '~/components/molecules/mission_plan_molecules/MissionListEmpty.vue';
import MissionListItem from '~/components/molecules/mission_plan_molecules/MissionListItem.vue';
import MissionStatusBadge from '~/components/molecules/mission_plan_molecules/MissionStatusBadge.vue';
import ConfirmationModal from '~/components/molecules/mission_plan_molecules/ConfirmationModal.vue';

// Added commandOptions to props, and 'edit' to emits
const props = defineProps(['queue', 'isRunning', 'activeIndex', 'flightParams', 'commandOptions']);
const emit = defineEmits(['remove', 'clear', 'reorder', 'edit']);

// Modal State Management
const showModal = ref(false);
const modalConfig = ref({
  title: '',
  message: '',
  isWarning: false,
  confirmText: 'Confirm',
  cancelText: 'Cancel'
});

const handleClearAttempt = () => {
  if (props.isRunning) {
    modalConfig.value = {
      title: 'Mission in Progress',
      message: 'You cannot clear the flight plan while a mission is currently executing. Please wait for the mission to complete.',
      isWarning: true,
      confirmText: 'OK',
      cancelText: 'Close'
    };
    showModal.value = true;
  } else {
    modalConfig.value = {
      title: 'Clear Flight Plan?',
      message: 'Are you sure you want to remove all commands from the current mission? This action cannot be undone.',
      isWarning: false,
      confirmText: 'Yes, Clear All',
      cancelText: 'Cancel'
    };
    showModal.value = true;
  }
};

const onModalConfirm = () => {
  if (!modalConfig.value.isWarning) { 
    emit('clear');
  }
  showModal.value = false;
};

const onModalCancel = () => {
  showModal.value = false;
};

// --- DRAG AND DROP STATE & HANDLERS ---
const draggedIndex = ref(null);
const dragOverIndex = ref(null);

const handleDragStart = (index, event) => {
  if (props.isRunning) {
    event.preventDefault();
    return;
  }
  draggedIndex.value = index;
  event.dataTransfer.effectAllowed = 'move';
  event.dataTransfer.setData('text/plain', index); 
};

const handleDragOver = (index, event) => {
  event.preventDefault(); 
  if (props.isRunning || draggedIndex.value === null) return;
  dragOverIndex.value = index;
};

const handleDrop = (index, event) => {
  event.preventDefault();
  if (props.isRunning || draggedIndex.value === null) return;

  if (draggedIndex.value !== index) {
    emit('reorder', { from: draggedIndex.value, to: index });
  }

  draggedIndex.value = null;
  dragOverIndex.value = null;
};

const handleDragEnd = () => {
  draggedIndex.value = null;
  dragOverIndex.value = null;
};

// --- EDIT COMMAND STATE & HANDLERS ---
const showEditModal = ref(false);
const editErrorMessage = ref('');
const editIndex = ref(-1);
const editForm = reactive({ type: '', val: '' });
const editGoParams = reactive({ x: 0, y: 0, z: 0 });

const currentEditCmdDetails = computed(() => {
  if (!props.commandOptions) return { unit: '' };
  return props.commandOptions.find(c => c.value === editForm.type) || { unit: '' };
});

const openEditModal = (idx) => {
  if (props.isRunning) return;
  editErrorMessage.value = '';
  const item = props.queue[idx];
  editIndex.value = idx;
  editForm.type = item.type;
  
  if (item.type === 'go') {
    const parts = String(item.val).split(' ');
    editGoParams.x = parseInt(parts[0]) || 0;
    editGoParams.y = parseInt(parts[1]) || 0;
    editGoParams.z = parseInt(parts[2]) || 0;
  } else {
    editForm.val = item.val;
  }
  
  showEditModal.value = true;
};

const saveEdit = () => {
  editErrorMessage.value = '';

  if (!editForm.type) {
    editErrorMessage.value = "Please select a command type.";
    return;
  }

  let finalVal = editForm.val;

  if (editForm.type === 'go') {
    const { x, y, z } = editGoParams;
    if (x < -500 || x > 500 || y < -500 || y > 500 || z < -500 || z > 500) {
      editErrorMessage.value = "Safety Error: Coordinates must be between -500 and 500.";
      return;
    }
    if (x > -20 && x < 20 && y > -20 && y < 20 && z > -20 && z < 20) {
      editErrorMessage.value = "Safety Error: X, Y, and Z cannot all be between -20 and 20 at the same time.";
      return;
    }
    finalVal = `${x} ${y} ${z}`;
  } else if (!editForm.val) {
    editErrorMessage.value = "Please enter a valid duration or value.";
    return;
  }

  emit('edit', { index: editIndex.value, type: editForm.type, val: finalVal });
  showEditModal.value = false;
};
</script>

<template>
  <BaseCard class="h-full flex flex-col bg-white/95 backdrop-blur-sm relative">
    
    <div class="flex justify-between items-center mb-4 border-b border-gray-100 pb-4">
      <SectionHeader class="!mb-0">
        <template #icon>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path></svg>
        </template>
        Flight Plan
      </SectionHeader>
      
      <div class="flex gap-2 items-center">
         <MissionStatusBadge :isActive="isRunning" />
         
         <button 
           v-if="queue.length > 0" 
           @click="handleClearAttempt" 
           class="text-xs font-medium transition-colors"
           :class="isRunning ? 'text-gray-400 cursor-not-allowed' : 'text-red-500 hover:text-red-700 underline'"
         >
           Clear
         </button>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-thin scrollbar-thumb-gray-300">
      
      <MissionListItem 
        :isConfig="true" 
        label="Initial Configuration" 
        :isActive="activeIndex === 0" 
        :isRunning="isRunning"
      >
        <template #details>
           <div class="grid grid-cols-3 gap-2 text-xs mt-2">
             <div class="bg-white rounded border border-gray-200 p-1 text-center"><span class="block text-gray-400 font-bold text-[10px] uppercase">Alt</span>{{ flightParams.altitude || 0 }}m</div>
             <div class="bg-white rounded border border-gray-200 p-1 text-center"><span class="block text-gray-400 font-bold text-[10px] uppercase">Spd</span>{{ flightParams.speed || 0 }}m/s</div>
             <div class="bg-white rounded border border-gray-200 p-1 text-center"><span class="block text-gray-400 font-bold text-[10px] uppercase">Mode</span>{{ flightParams.mode || '-' }}</div>
           </div>
        </template>
      </MissionListItem>

      <MissionListEmpty v-if="queue.length === 0" />

      <div 
        v-for="(item, idx) in queue" 
        :key="item.id"
        :draggable="!isRunning"
        @dragstart="handleDragStart(idx, $event)"
        @dragover="handleDragOver(idx, $event)"
        @dragenter.prevent
        @drop="handleDrop(idx, $event)"
        @dragend="handleDragEnd"
        @dblclick="openEditModal(idx)"
        class="transition-all duration-200 ease-in-out relative group"
        :title="!isRunning ? 'Drag to reorder, Double-click to edit' : ''"
        :class="{
          'cursor-grab active:cursor-grabbing': !isRunning,
          'opacity-40 scale-[0.98]': draggedIndex === idx,
          'border-t-2 border-[#658D1B] pt-2 mt-2': dragOverIndex === idx && draggedIndex !== idx && dragOverIndex < draggedIndex,
          'border-b-2 border-[#658D1B] pb-2 mb-2': dragOverIndex === idx && draggedIndex !== idx && dragOverIndex > draggedIndex
        }"
      >
        <button 
          v-if="!isRunning" 
          @click.stop="openEditModal(idx)" 
          class="absolute -left-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 z-10 bg-white border border-gray-200 text-[#658D1B] p-1.5 rounded-full shadow-md hover:bg-gray-50 transition-opacity"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
        </button>

        <MissionListItem 
          :index="idx"
          :label="item.label"
          :value="item.val"
          :unit="item.unit"
          :icon="item.icon"
          :isActive="activeIndex === idx + 1"
          :isRunning="isRunning"
          @remove="$emit('remove', idx)"
        />
      </div>
    </div>

    <div v-if="showEditModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-sm overflow-hidden flex flex-col" @click.stop>
        <div class="bg-gray-50 px-5 py-4 border-b border-gray-100 flex justify-between items-center">
          <h3 class="font-bold text-gray-800 flex items-center gap-2">
            <svg class="w-4 h-4 text-[#658D1B]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
            Edit Command Step {{ editIndex + 1 }}
          </h3>
          <button @click="showEditModal = false" class="text-gray-400 hover:text-gray-600"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button>
        </div>

        <div class="p-5 space-y-4">
          <div class="flex flex-col">
            <label class="text-gray-600 text-xs font-bold mb-1.5 uppercase tracking-wide">Command Type</label>
            <select v-model="editForm.type" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm bg-white focus:border-[#658D1B] focus:ring-1 outline-none">
              <option v-for="opt in commandOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>

          <div v-if="editForm.type === 'go'" class="grid grid-cols-2 gap-3 p-3 bg-gray-50 border border-gray-200 rounded-md">
            <div class="flex flex-col"><label class="text-[10px] text-gray-500 font-bold uppercase mb-1">X (-500 to 500)</label><input type="number" v-model="editGoParams.x" class="border border-gray-300 rounded px-2 py-1.5 text-sm outline-none focus:border-[#658D1B] focus:ring-1" /></div>
            <div class="flex flex-col"><label class="text-[10px] text-gray-500 font-bold uppercase mb-1">Y (-500 to 500)</label><input type="number" v-model="editGoParams.y" class="border border-gray-300 rounded px-2 py-1.5 text-sm outline-none focus:border-[#658D1B] focus:ring-1" /></div>
            <div class="flex flex-col col-span-2"><label class="text-[10px] text-gray-500 font-bold uppercase mb-1">Z (-500 to 500)</label><input type="number" v-model="editGoParams.z" class="border border-gray-300 rounded px-2 py-1.5 text-sm outline-none focus:border-[#658D1B] focus:ring-1" /></div>
          </div>

          <div v-else class="flex flex-col">
            <label class="text-gray-600 text-xs font-bold mb-1.5 uppercase tracking-wide">Value ({{ currentEditCmdDetails.unit }})</label>
            <div class="flex relative">
              <input type="number" v-model="editForm.val" min="1" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm outline-none focus:border-[#658D1B] focus:ring-1" />
              <div class="absolute right-0 top-0 bottom-0 px-3 flex items-center bg-gray-100 border-l border-gray-300 rounded-r-md text-gray-500 text-xs font-bold">{{ currentEditCmdDetails.unit }}</div>
            </div>
          </div>

          <div v-if="editErrorMessage" class="text-red-600 bg-red-50 p-2 rounded border border-red-200 text-xs font-medium flex items-center gap-2">
            <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
            {{ editErrorMessage }}
          </div>
        </div>

        <div class="bg-gray-50 px-5 py-3 border-t border-gray-100 flex justify-end gap-2">
          <button @click="showEditModal = false" class="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-md transition-colors">Cancel</button>
          <button @click="saveEdit" class="px-4 py-2 text-sm font-bold text-white bg-[#658D1B] hover:bg-[#557516] rounded-md transition-colors shadow-sm">Save Changes</button>
        </div>
      </div>
    </div>

    <ConfirmationModal 
      :isOpen="showModal"
      :title="modalConfig.title"
      :message="modalConfig.message"
      :isWarning="modalConfig.isWarning"
      :confirmText="modalConfig.confirmText"
      :cancelText="modalConfig.cancelText"
      @confirm="onModalConfirm"
      @cancel="onModalCancel"
    />

  </BaseCard>
</template>