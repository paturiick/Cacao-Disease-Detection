<script setup>
const props = defineProps({
  isRcMode: { type: Boolean, default: false },
  isMissionRunning: { type: Boolean, default: false },
  queueLength: { type: Number, default: 0 },
  isFlying: { type: Boolean, default: false } // NEW: Tracks if the drone has taken off
});

const emit = defineEmits(['run-mission', 'takeoff', 'land', 'emergency-land']); // NEW: added emergency-land
</script>

<template>
  <div class="bg-slate-50 rounded-xl border border-slate-200 shadow-sm p-4 w-full flex flex-col">
    <h3 class="font-bold text-slate-800 text-sm flex items-center gap-2 mb-3">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
      Mission Control
    </h3>

    <button 
      v-if="!isRcMode"
      @click="$emit('run-mission')"
      :disabled="queueLength === 0 || isMissionRunning"
      class="w-full py-3 rounded-lg font-bold text-sm tracking-wide uppercase transition-all duration-200 flex justify-center items-center gap-2"
      :class="(queueLength === 0 || isMissionRunning) ? 'bg-slate-400 text-white cursor-not-allowed' : 'bg-[#0F172A] text-white hover:bg-slate-800 shadow-md'"
    >
      <svg v-if="!isMissionRunning" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M4 4l12 6-12 6z"></path></svg>
      <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
      {{ isMissionRunning ? 'Mission in Progress...' : 'Run Mission Plan' }}
    </button>

    <div v-else class="flex flex-col gap-3 w-full">
      <div class="flex gap-3 w-full">
        <button 
          @click="$emit('takeoff')"
          :disabled="isFlying"
          class="flex-1 py-3 rounded-lg font-bold text-sm tracking-wide uppercase transition-colors flex justify-center items-center gap-2"
          :class="isFlying ? 'bg-slate-200 text-slate-400 cursor-not-allowed shadow-none' : 'bg-[#658D1B] hover:bg-[#557516] text-white shadow-md'"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"></path></svg>
          Takeoff
        </button>

        <button 
          @click="$emit('land')"
          :disabled="!isFlying"
          class="flex-1 py-3 rounded-lg font-bold text-sm tracking-wide uppercase transition-colors flex justify-center items-center gap-2"
          :class="!isFlying ? 'bg-slate-200 text-slate-400 cursor-not-allowed shadow-none' : 'bg-slate-800 hover:bg-slate-900 text-white shadow-md'"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg>
          Land
        </button>
      </div>

      <button 
        @click="$emit('emergency-land')"
        :disabled="!isFlying"
        class="w-full py-3 rounded-lg font-bold text-sm tracking-wide uppercase transition-colors flex justify-center items-center gap-2"
        :class="!isFlying ? 'bg-red-100 text-red-300 cursor-not-allowed shadow-none' : 'bg-red-600 hover:bg-red-700 text-white shadow-md'"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
        Emergency Land
      </button>
    </div>
  </div>
</template>