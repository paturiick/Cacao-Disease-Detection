<script setup>
import { ref } from 'vue';
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';
import MissionListEmpty from '~/components/molecules/mission_plan_molecules/MissionListEmpty.vue';
import MissionListItem from '~/components/molecules/mission_plan_molecules/MissionListItem.vue';
import MissionStatusBadge from '~/components/molecules/mission_plan_molecules/MissionStatusBadge.vue';
// 1. Import the ConfirmationModal component
import ConfirmationModal from '~/components/molecules/mission_plan_molecules/ConfirmationModal.vue';

const props = defineProps(['queue', 'isRunning', 'activeIndex', 'flightParams']);
const emit = defineEmits(['remove', 'clear']);

// 2. Modal State Management
const showModal = ref(false);
const modalConfig = ref({
  title: '',
  message: '',
  isWarning: false,
  confirmText: 'Confirm',
  cancelText: 'Cancel'
});

// 3. New Handler: Sets up the modal instead of calling alert()
const handleClearAttempt = () => {
  if (props.isRunning) {
    // Case A: Mission is running -> Show Blocking Warning
    modalConfig.value = {
      title: 'Mission in Progress',
      message: 'You cannot clear the flight plan while a mission is currently executing. Please wait for the mission to complete.',
      isWarning: true, // This hides the confirm button (blocking action)
      confirmText: 'OK',
      cancelText: 'Close'
    };
    showModal.value = true;
  } else {
    // Case B: Mission is idle -> Show Confirmation Prompt
    modalConfig.value = {
      title: 'Clear Flight Plan?',
      message: 'Are you sure you want to remove all commands from the current mission? This action cannot be undone.',
      isWarning: false, // This shows both buttons
      confirmText: 'Yes, Clear All',
      cancelText: 'Cancel'
    };
    showModal.value = true;
  }
};

// 4. Confirm Action Handler
const onModalConfirm = () => {
  // Only clear if it wasn't a warning/blocking modal
  if (!modalConfig.value.isWarning) {
    emit('clear');
  }
  showModal.value = false;
};

const onModalCancel = () => {
  showModal.value = false;
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

      <MissionListItem 
        v-for="(item, idx) in queue" 
        :key="item.id"
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