<script setup>
import { reactive, onMounted, onBeforeUnmount } from 'vue';

const emit = defineEmits(['send-rc', 'save-to-plan']);

// RC Channels: a(Roll), b(Pitch), c(Throttle), d(Yaw)
const rcState = reactive({ a: 0, b: 0, c: 0, d: 0 });
let rcInterval = null;

// Instantly stops the drone by resetting all velocities to 0
const emergencyStop = () => {
  rcState.a = 0;
  rcState.b = 0;
  rcState.c = 0;
  rcState.d = 0;
};

// Continuous Loop to send RC command to maintain drone velocity
const startRcLoop = () => {
  rcInterval = setInterval(() => {
    emit('send-rc', { a: rcState.a, b: rcState.b, c: rcState.c, d: rcState.d });
  }, 100); // 10Hz transmission rate
};

onMounted(() => {
  startRcLoop();
});

onBeforeUnmount(() => {
  if (rcInterval) clearInterval(rcInterval);
  // Send absolute stop command when navigating away to prevent runaways
  emit('send-rc', { a: 0, b: 0, c: 0, d: 0 }); 
});
</script>

<template>
  <div class="flex flex-col items-center justify-center w-full h-full bg-white p-6 relative overflow-y-auto custom-scrollbar">
    
    <div class="text-center mb-8 shrink-0">
      <h2 class="text-2xl font-black text-slate-800 uppercase tracking-widest">Live RC Active</h2>
      <p class="text-sm text-slate-500 font-medium mt-1">Set velocity to cruise. Values hold until reset.</p>
    </div>

    <div class="w-full max-w-md flex flex-col gap-6 shrink-0">
      
      <div class="flex flex-col gap-2">
        <div class="flex justify-between items-center">
          <span class="text-xs font-bold text-slate-500 uppercase tracking-widest">Roll (Left / Right)</span>
          <span class="text-xs font-mono font-bold px-2 py-1 bg-slate-100 rounded text-slate-700">{{ rcState.a }}</span>
        </div>
        <input 
          type="range" min="-100" max="100" v-model.number="rcState.a"
          class="w-full h-3 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#38BDF8]"
        />
      </div>

      <div class="flex flex-col gap-2">
        <div class="flex justify-between items-center">
          <span class="text-xs font-bold text-slate-500 uppercase tracking-widest">Pitch (Forward / Back)</span>
          <span class="text-xs font-mono font-bold px-2 py-1 bg-slate-100 rounded text-slate-700">{{ rcState.b }}</span>
        </div>
        <input 
          type="range" min="-100" max="100" v-model.number="rcState.b"
          class="w-full h-3 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#38BDF8]"
        />
      </div>

      <div class="flex flex-col gap-2 mt-4">
        <div class="flex justify-between items-center">
          <span class="text-xs font-bold text-[#658D1B] uppercase tracking-widest">Throttle (Alt Up / Down)</span>
          <span class="text-xs font-mono font-bold px-2 py-1 bg-[#658D1B]/10 rounded text-[#658D1B]">{{ rcState.c }}</span>
        </div>
        <input 
          type="range" min="-100" max="100" v-model.number="rcState.c"
          class="w-full h-3 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#658D1B]"
        />
      </div>

      <div class="flex flex-col gap-2">
        <div class="flex justify-between items-center">
          <span class="text-xs font-bold text-[#658D1B] uppercase tracking-widest">Yaw (Rotate)</span>
          <span class="text-xs font-mono font-bold px-2 py-1 bg-[#658D1B]/10 rounded text-[#658D1B]">{{ rcState.d }}</span>
        </div>
        <input 
          type="range" min="-100" max="100" v-model.number="rcState.d"
          class="w-full h-3 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#658D1B]"
        />
      </div>

    </div>

    <div class="w-full max-w-md mt-10 shrink-0 flex flex-col gap-4">
      <button 
        @click="$emit('save-to-plan', rcState)"
        class="w-full py-3 bg-[#0F172A] hover:bg-slate-800 text-white rounded-lg font-bold text-sm tracking-wide uppercase transition-colors shadow-md flex justify-center items-center gap-2"
      >
        <svg class="w-4 h-4 text-[#658D1B]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        Add Values to Mission Plan
      </button>

      <button 
        @click="emergencyStop"
        class="w-full px-8 py-3 bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 rounded-lg font-bold text-sm tracking-wide uppercase transition-colors shadow-sm flex justify-center items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"></path></svg>
        Stop All Movement (Set to 0)
      </button>
    </div>

  </div>
</template>

<style scoped>
input[type=range] { outline: none; }
input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; appearance: none; width: 24px; height: 24px; border-radius: 50%; background: currentColor; cursor: pointer; box-shadow: 0 2px 6px rgba(0,0,0,0.2); transition: transform 0.1s; }
input[type=range]::-webkit-slider-thumb:hover { transform: scale(1.15); }
input[type=range]::-moz-range-thumb { width: 24px; height: 24px; border-radius: 50%; background: currentColor; cursor: pointer; box-shadow: 0 2px 6px rgba(0,0,0,0.2); border: none; transition: transform 0.1s; }
input[type=range]::-moz-range-thumb:hover { transform: scale(1.15); }
</style>