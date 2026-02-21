<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';
import Button from '~/components/atoms/Button.vue';

defineProps({
  isRunning: Boolean,
  isDisabled: Boolean,
  // Added to track the specific landing execution state
  isLanding: { type: Boolean, default: false }
});

defineEmits(['run', 'force-land']);
</script>

<template>
  <BaseCard class="bg-white/95 backdrop-blur-sm">
    <SectionHeader>
      <template #icon>
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
        </svg>
      </template>
      Mission Control
    </SectionHeader>

    <div class="mt-4 flex flex-col gap-3">
      <Button 
        @click="$emit('run')" 
        :disabled="isDisabled || isRunning" 
        class="w-full py-4 text-sm font-bold rounded shadow-md transition-all flex justify-center items-center gap-2 uppercase tracking-wide bg-[#3E2723] hover:bg-[#2c1b18] text-white disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        <span v-if="isRunning" class="flex items-center gap-2">
           <svg class="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24">
             <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
             <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
           </svg>
           Mission in Progress...
        </span>
        <span v-else>▶ Run Mission Plan</span>
      </Button>

      <button 
        v-if="isRunning"
        @click="$emit('force-land')"
        :disabled="isLanding"
        class="w-full py-4 bg-red-600 hover:bg-red-700 text-white font-bold rounded shadow-xl flex items-center justify-center gap-2 transition-all active:scale-95 animate-pulse uppercase text-sm tracking-wide"
      >
        <svg v-if="!isLanding" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
        <svg v-else class="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24">
           <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
           <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        {{ isLanding ? 'Landing Initiated...' : '⚠ Force Landing' }}
      </button>
    </div>
  </BaseCard>
</template>