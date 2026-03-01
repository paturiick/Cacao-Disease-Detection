<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue';
import { missionApi } from "../api/missionApi";
import { useTelemetry } from "~/components/composables/useTelemetry"; 

import DashboardNavBar from '~/components/organisms/NavBar.vue';
import MetricCard from '~/components/molecules/live_monitor_molecules/MetricCard.vue';
import VideoStreamPlayer from '~/components/molecules/live_monitor_molecules/VideoStreamPlayer.vue';

// --- GLOBAL TELEMETRY STATE ---
// Handles the core drone hardware stats (Battery, Signal, Altitude)
const { telemetryState, startPolling, stopPolling } = useTelemetry();

// --- STATE ---
const isStreamConnected = ref(false);
const planId = ref(null);
let missionPoll = null;

// Error handling state
const errorMessage = ref('');
let errorTimer = null;

// Local state for Cacao Detection (Specific to the mission domain)
const missionData = reactive({
  healthyCacao: 0,
  diseasedCacao: 0
});

// --- COMPUTED ---
const signalStatus = computed(() => telemetryState.connected ? 'Online' : 'Offline');

const batteryIconColor = computed(() => {
  if (telemetryState.battery >= 50) return 'text-green-500';
  if (telemetryState.battery >= 20) return 'text-yellow-500';
  return 'text-red-500';
});

// --- HELPERS ---
const showError = (msg) => {
  errorMessage.value = msg;
  if (errorTimer) clearTimeout(errorTimer);
  errorTimer = setTimeout(() => {
    errorMessage.value = '';
  }, 5000);
};

/**
 * Handle the toggle event from the VideoStreamPlayer.
 * The VideoStreamPlayer manages the actual liveApi.toggleHardware call internally.
 */
const handleStreamToggle = () => {
  isStreamConnected.value = !isStreamConnected.value;
};

// --- LIFECYCLE ---
onMounted(async () => {
  // Start hardware telemetry polling
  startPolling();

  try {
    const plan = await missionApi.getActive();
    if (plan) {
      planId.value = plan.id;
      missionData.healthyCacao = plan.healthy_cacao ?? 0;
      missionData.diseasedCacao = plan.diseased_cacao ?? 0;

      // Start mission status polling (Cacao counts)
      missionPoll = setInterval(async () => {
        if (!planId.value) return;
        try {
          const s = await missionApi.status(planId.value);
          missionData.healthyCacao = s.healthy_cacao ?? missionData.healthyCacao;
          missionData.diseasedCacao = s.diseased_cacao ?? missionData.diseasedCacao;
        } catch (err) {
          console.error("Mission status poll failed:", err);
        }
      }, 1000);
    }
  } catch(e) {
    console.error("Failed to establish drone mission connection:", e);
    showError("Could not connect to the mission controller.");
  }
});

onUnmounted(() => {
  stopPolling();
  if (missionPoll) clearInterval(missionPoll);
  if (errorTimer) clearTimeout(errorTimer);
});
</script>

<template>
  <div 
    class="flex flex-col h-screen overflow-hidden font-inter bg-cover bg-center relative"
    style="background-image: url('https://images.unsplash.com/photo-1542319084-2a6c38210350?q=80&w=2574&auto=format&fit=crop');"
  >
    <div class="absolute inset-0 bg-black/60 z-0"></div>
    
    <div class="z-20 relative">
      <DashboardNavBar active-page="live-monitor" :droneStatus="signalStatus" />
    </div>

    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform -translate-y-4 opacity-0"
      enter-to-class="transform translate-y-0 opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="transform translate-y-0 opacity-100"
      leave-to-class="transform -translate-y-4 opacity-0"
    >
      <div v-if="errorMessage" class="absolute top-24 left-1/2 transform -translate-x-1/2 z-50 flex items-center gap-3 bg-red-50 text-red-700 border border-red-200 px-4 py-3 rounded-lg shadow-xl min-w-[300px] max-w-md">
        <svg class="w-5 h-5 shrink-0 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
        <span class="text-sm font-semibold flex-1">{{ errorMessage }}</span>
        <button @click="errorMessage = ''" class="text-red-400 hover:text-red-700 transition-colors"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button>
      </div>
    </Transition>

    <div class="flex-1 z-10 p-6 overflow-y-auto relative">
      <div class="flex flex-col h-full max-w-[1600px] mx-auto">
        <div class="w-full flex flex-col gap-6 h-full">
          
          <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
            <MetricCard label="Signal Strength" :value="signalStatus">
              <template #icon><svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" /></svg></template>
            </MetricCard>

            <MetricCard label="Battery Level" :value="telemetryState.battery + '%'">
              <template #icon><svg :class="['w-4 h-4 transition-colors duration-500', batteryIconColor]" fill="currentColor" viewBox="0 0 24 24"><path d="M17 6H3a2 2 0 00-2 2v8a2 2 0 002 2h14a2 2 0 002-2v-8a2 2 0 00-2-2zm4 4v4h-2v-4h2z"/></svg></template>
            </MetricCard>

            <MetricCard label="Altitude" :value="telemetryState.altitude_m + ' m'">
              <template #icon><svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" /></svg></template>
            </MetricCard>
            
            <MetricCard label="Black Pod" :value="missionData.diseasedCacao">
              <template #icon><svg class="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9v-2h2v2zm0-4H9V7h2v5z"/></svg></template>
            </MetricCard>

            <MetricCard label="Healthy" :value="missionData.healthyCacao">
              <template #icon><svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg></template>
            </MetricCard>
          </div>

          <div class="flex-1 min-h-[400px]">
            <VideoStreamPlayer 
              :is-connected="isStreamConnected"
              @toggle-stream="handleStreamToggle"
            />
          </div>

        </div>
      </div>
    </div>
  </div>
</template>