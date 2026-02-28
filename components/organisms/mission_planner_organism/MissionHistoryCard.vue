<script setup>
import { ref } from 'vue';
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';
import MissionListEmpty from '~/components/molecules/mission_plan_molecules/MissionListEmpty.vue';
import MissionListItem from '~/components/molecules/mission_plan_molecules/MissionListItem.vue';
import MissionStatusBadge from '~/components/molecules/mission_plan_molecules/MissionStatusBadge.vue';
import ConfirmationModal from '~/components/molecules/mission_plan_molecules/ConfirmationModal.vue';

const props = defineProps(['queue', 'isRunning', 'activeIndex', 'flightParams']);
// NEW: Added 'reorder' to the emits array
const emit = defineEmits(['remove', 'clear', 'reorder']);

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

// --- NEW: DRAG AND DROP STATE & HANDLERS ---
const draggedIndex = ref(null);
const dragOverIndex = ref(null);

const handleDragStart = (index, event) => {
  if (props.isRunning) {
    event.preventDefault();
    return;
  }
  draggedIndex.value = index;
  event.dataTransfer.effectAllowed = 'move';
  event.dataTransfer.setData('text/plain', index); // Required for Firefox
};

const handleDragOver = (index, event) => {
  event.preventDefault(); // Necessary to allow dropping
  if (props.isRunning || draggedIndex.value === null) return;
  dragOverIndex.value = index;
};

const handleDrop = (index, event) => {
  event.preventDefault();
  if (props.isRunning || draggedIndex.value === null) return;

  // Only emit if the item was actually moved to a new spot
  if (draggedIndex.value !== index) {
    emit('reorder', { from: draggedIndex.value, to: index });
  }

  // Cleanup
  draggedIndex.value = null;
  dragOverIndex.value = null;
};

const handleDragEnd = () => {
  draggedIndex.value = null;
  dragOverIndex.value = null;
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
        class="transition-all duration-200 ease-in-out"
        :class="{
          'cursor-grab active:cursor-grabbing': !isRunning,
          'opacity-40 scale-[0.98]': draggedIndex === idx,
          'border-t-2 border-[#658D1B] pt-2 mt-2': dragOverIndex === idx && draggedIndex !== idx && dragOverIndex < draggedIndex,
          'border-b-2 border-[#658D1B] pb-2 mb-2': dragOverIndex === idx && draggedIndex !== idx && dragOverIndex > draggedIndex
        }"
      >
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