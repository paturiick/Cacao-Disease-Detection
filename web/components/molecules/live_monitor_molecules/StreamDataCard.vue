<script setup>
import { ref, watch, onUnmounted } from 'vue';
import { useTelemetry } from "~/components/composables/useTelemetry"; 
import { isStreamActive, activeSessionId } from '~/components/composables/droneStore';
import BaseCard from '~/components/atoms/BaseCard.vue';

// 1. Telemetry is automatically handled by the composable's SSE stream!
const { telemetryState } = useTelemetry();

const healthyCount = ref(0);
const diseasedCount = ref(0);
const sickPods = ref([]);

// 2. Variable to hold our persistent AI Detection tunnel
let detectionStream = null;
const BASE_URL = import.meta.env.VITE_API_BASE_URL;

const startDetectionStream = () => {
  if (!activeSessionId.value) return;
  
  // Close any existing connections before opening a new one
  if (detectionStream) detectionStream.close();

  // Open the one-way SSE tunnel to Django for AI Stats
  // (Make sure you added the stream_detection_stats view to Django as discussed earlier!)
  detectionStream = new EventSource(`${BASE_URL}/api/detections/stream-stats/?session_id=${activeSessionId.value}`);

  // Listen for incoming AI data packets
  detectionStream.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.status === 'success') {
      healthyCount.value = data.healthy_count || 0;
      diseasedCount.value = data.unhealthy_count || 0;
      sickPods.value = (data.pods || []).filter(pod => pod.status === 'unhealthy');
    }
  };

  detectionStream.onerror = () => {
    console.warn("[Detection Stream] Interrupted. Browser will auto-reconnect...");
  };
};

// Watch the global stream state
watch(isStreamActive, (isActive) => {
  console.log("[DEBUG] Stream State Changed! Is Active:", isActive, "| Session ID:", activeSessionId.value);

  if (isActive) {
    healthyCount.value = 0;
    diseasedCount.value = 0;
    sickPods.value = [];
    
    // Start the SSE tunnel instead of polling
    startDetectionStream();
  } else {
    // If stream turns off, cleanly close the tunnel
    if (detectionStream) {
      detectionStream.close();
      detectionStream = null;
    }
  }
}, { immediate: true }); 

// Clean up if the user leaves the page
onUnmounted(() => {
  if (detectionStream) detectionStream.close();
});
</script>

<template>
  <BaseCard class="h-full flex flex-col bg-white/95 backdrop-blur-md overflow-hidden shadow-2xl">
    
    <div class="px-5 py-4 bg-slate-800 shrink-0 flex items-center justify-between border-b border-slate-700">
      <h3 class="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
        <svg class="w-4 h-4 text-[#658D1B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        Flight Telemetry
      </h3>
      <span 
        class="text-[10px] px-2 py-1 rounded-full font-bold tracking-widest border"
        :class="telemetryState.connected ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50' : 'bg-red-500/20 text-red-400 border-red-500/50'"
      >
        {{ telemetryState.connected ? 'ONLINE' : 'OFFLINE' }}
      </span>
    </div>

    <div class="flex-1 overflow-y-auto p-5 flex flex-col gap-6">
      
      <div class="space-y-3">
        
        <div class="grid grid-cols-2 gap-3">
          <div class="flex flex-col p-4 bg-emerald-50 rounded-xl border border-emerald-100 shadow-sm relative overflow-hidden group hover:shadow-md transition-shadow">
            <div class="absolute -right-4 -top-4 opacity-10 group-hover:scale-110 transition-transform duration-500">
               <svg class="w-20 h-20 text-emerald-600" fill="currentColor" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
            </div>
            <span class="text-[10px] font-bold text-emerald-600 uppercase tracking-wider mb-1 z-10">Healthy</span>
            <span class="text-3xl font-black text-emerald-800 z-10">{{ healthyCount }}</span>
          </div>

          <div class="flex flex-col p-4 bg-red-50 rounded-xl border border-red-100 shadow-sm relative overflow-hidden group hover:shadow-md transition-shadow">
            <div class="absolute -right-4 -top-4 opacity-10 group-hover:scale-110 transition-transform duration-500">
               <svg class="w-20 h-20 text-red-600" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9v-2h2v2zm0-4H9V7h2v5z"/></svg>
            </div>
            <span class="text-[10px] font-bold text-red-600 uppercase tracking-wider mb-1 z-10">Black Pod</span>
            <span class="text-3xl font-black text-red-800 z-10">{{ diseasedCount }}</span>
          </div>
        </div>

        <div v-if="sickPods.length > 0" class="flex flex-col gap-2 mt-4 bg-red-50/50 p-3 rounded-xl border border-red-100">
          <p class="text-[10px] font-bold text-red-600 uppercase tracking-widest flex items-center justify-between">
            <span>Critical Detections</span>
            <span class="bg-red-500 text-white px-1.5 py-0.5 rounded-full text-[9px]">{{ sickPods.length }}</span>
          </p>
          
          <div class="max-h-32 overflow-y-auto pr-1 space-y-1.5 scrollbar-thin scrollbar-thumb-red-200">
            <div v-for="pod in sickPods" :key="pod.track_id" class="flex items-center justify-between bg-white px-2 py-1.5 rounded text-xs border border-red-100 shadow-sm">
              <span class="font-bold text-slate-700">Pod #{{ pod.track_id }}</span>
              <div class="flex items-center gap-2">
                <span class="text-[9px] font-bold text-red-500 uppercase">{{ pod.status }}</span>
                <span class="text-[9px] text-slate-400">
                  {{ new Date(pod.last_seen).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) }}
                </span>
              </div>
            </div>
          </div>
        </div>

      </div>

      <div class="space-y-3">
        <p class="text-xs font-black text-slate-800 uppercase tracking-widest flex items-center gap-2">
          <svg class="w-4 h-4 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path></svg>
          Flight Dynamics
        </p>

        <div class="grid grid-cols-3 gap-2">
          
          <div class="col-span-3 p-3 bg-slate-800 rounded-lg flex items-center justify-between relative overflow-hidden shadow-md">
            <div class="flex items-center gap-3 z-10">
               <svg :class="telemetryState.battery <= 20 ? 'text-red-400 animate-pulse' : 'text-emerald-400'" class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M17 6H3a2 2 0 00-2 2v8a2 2 0 002 2h14a2 2 0 002-2v-8a2 2 0 00-2-2zm4 4v4h-2v-4h2z"/></svg>
               <span class="text-[10px] font-bold text-slate-300 uppercase tracking-widest">Battery Level</span>
            </div>
            <span class="text-lg font-black text-white z-10">{{ telemetryState.battery ?? 0 }}%</span>
            <div class="absolute bottom-0 left-0 h-1 transition-all duration-1000" 
                 :class="telemetryState.battery <= 20 ? 'bg-red-500' : 'bg-emerald-500'" 
                 :style="{ width: `${telemetryState.battery ?? 0}%` }">
            </div>
          </div>

          <div class="p-2 bg-slate-50 rounded-lg border border-slate-100 flex flex-col items-center justify-center shadow-sm">
            <span class="text-[9px] font-bold text-slate-400 uppercase mb-0.5">Altitude</span>
            <span class="text-sm font-black text-slate-800">{{ telemetryState.altitude_m?.toFixed(1) ?? '0.0' }} <span class="text-[10px] text-slate-500 font-normal">m</span></span>
          </div>

          <div class="p-2 bg-slate-50 rounded-lg border border-slate-100 flex flex-col items-center justify-center shadow-sm">
            <span class="text-[9px] font-bold text-slate-400 uppercase mb-0.5">Speed</span>
            <span class="text-sm font-black text-slate-800">{{ (telemetryState.speed / 10).toFixed(1) }} <span class="text-[10px] text-slate-500 font-normal">m/s</span></span>
          </div>

          <div class="p-2 bg-slate-50 rounded-lg border border-slate-100 flex flex-col items-center justify-center shadow-sm">
            <span class="text-[9px] font-bold text-slate-400 uppercase mb-0.5">Air Time</span>
            <span class="text-sm font-black text-slate-800">{{ telemetryState.flight_time ?? 0 }} <span class="text-[10px] text-slate-500 font-normal">s</span></span>
          </div>

          <div class="p-2 bg-slate-50 rounded-lg border border-slate-100 flex flex-col items-center justify-center shadow-sm">
            <span class="text-[9px] font-bold text-slate-400 uppercase mb-0.5">Pitch</span>
            <span class="text-sm font-black text-slate-800">{{ telemetryState.pitch ?? 0 }}°</span>
          </div>

          <div class="p-2 bg-slate-50 rounded-lg border border-slate-100 flex flex-col items-center justify-center shadow-sm">
            <span class="text-[9px] font-bold text-slate-400 uppercase mb-0.5">Roll</span>
            <span class="text-sm font-black text-slate-800">{{ telemetryState.roll ?? 0 }}°</span>
          </div>

          <div class="p-2 bg-slate-50 rounded-lg border border-slate-100 flex flex-col items-center justify-center shadow-sm">
            <span class="text-[9px] font-bold text-slate-400 uppercase mb-0.5">Yaw</span>
            <span class="text-sm font-black text-slate-800">{{ telemetryState.yaw ?? 0 }}°</span>
          </div>

        </div>
      </div>

      <hr class="border-slate-100" />

      <div class="space-y-3 pb-4">
        <p class="text-xs font-black text-slate-800 uppercase tracking-widest flex items-center gap-2">
          <svg class="w-4 h-4 text-cyan-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
          Environmental Sensors
        </p>

        <div class="grid grid-cols-2 gap-3">
          
          <div class="p-3 bg-slate-50 rounded-lg border border-slate-100 flex items-center justify-between shadow-sm">
            <div class="flex flex-col">
              <span class="text-[10px] font-bold text-slate-400 uppercase mb-0.5">ToF Distance</span>
              <span class="text-lg font-black text-slate-800">{{ telemetryState.tof_cm ?? 0 }} <span class="text-xs text-slate-500 font-normal">cm</span></span>
            </div>
            <svg class="w-6 h-6 text-indigo-400/50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg>
          </div>

          <div class="p-3 bg-slate-50 rounded-lg border border-slate-100 flex items-center justify-between shadow-sm">
            <div class="flex flex-col">
              <span class="text-[10px] font-bold text-slate-400 uppercase mb-0.5">Internal Temp</span>
              <span class="text-lg font-black text-slate-800">{{ telemetryState.temp_c ?? 0 }} <span class="text-xs text-slate-500 font-normal">°C</span></span>
            </div>
            <svg class="w-6 h-6 text-rose-400/50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19c-1.657 0-3-1.343-3-3a3 3 0 013-3h.5V5a2.5 2.5 0 015 0v8h.5a3 3 0 013 3c0 1.657-1.343 3-3 3H9z"></path></svg>
          </div>

        </div>
      </div>

    </div>
  </BaseCard>
</template>