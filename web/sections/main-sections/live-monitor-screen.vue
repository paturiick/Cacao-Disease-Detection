<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { missionApi } from "../api/missionApi"; // Kept ONLY for the emergency land function
import { useTelemetry } from "~/components/composables/useTelemetry"; 

import DashboardNavBar from '~/components/organisms/NavBar.vue';
import VideoStreamPlayer from '~/components/molecules/live_monitor_molecules/VideoStreamPlayer.vue';
import ToggleDetailsButton from '~/components/atoms/ToggleDetailsButton.vue'; 
import StreamDataCard from '~/components/molecules/live_monitor_molecules/StreamDataCard.vue'; 

// --- GLOBAL TELEMETRY STATE ---
const { telemetryState, startPolling, stopPolling } = useTelemetry();

// --- STATE ---
const isStreamConnected = ref(false);
const showTelemetry = ref(false); 

// Error handling state
const errorMessage = ref('');
let errorTimer = null;

// Emergency Landing State
const isLanding = ref(false);

// --- COMPUTED ---
const signalStatus = computed(() => telemetryState.connected ? 'Online' : 'Offline');

// --- HELPERS ---
const showError = (msg) => {
  errorMessage.value = msg;
  if (errorTimer) clearTimeout(errorTimer);
  errorTimer = setTimeout(() => {
    errorMessage.value = '';
  }, 5000);
};

const handleStreamToggle = () => {
  isStreamConnected.value = !isStreamConnected.value;
};

// --- Emergency Landing Handler ---
const handleEmergencyLand = async () => {
  if (isLanding.value) return;
  isLanding.value = true;
  
  try {
    await missionApi.forceLand();
    console.log("Emergency command dispatched.");
  } catch (e) {
    console.error("Emergency landing failed to execute:", e);
    showError("Failed to send emergency land command.");
  } finally {
    setTimeout(() => { isLanding.value = false; }, 2000);
  }
};

// --- LIFECYCLE ---
onMounted(() => {
  // Just start the silent telemetry SSE tunnel
  startPolling();
});

onUnmounted(() => {
  // Clean up when the user leaves the page
  stopPolling();
  if (errorTimer) clearTimeout(errorTimer);
});
</script>

<template>
  <div 
    class="flex flex-col h-screen overflow-hidden font-inter bg-cover bg-center relative"
    style="background-image: url('https://images.unsplash.com/photo-1542319084-2a6c38210350?q=80&w=2574&auto=format&fit=crop');"
    >
    <div class="absolute inset-0 bg-black/40 z-0"></div>
    
    <div class="z-20 relative shrink-0">
      <DashboardNavBar active-page="live-monitor" :droneStatus="signalStatus" :battery="telemetryState.battery"/>
    </div>


    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform -translate-y-4 opacity-0 scale-95"
      enter-to-class="transform translate-y-0 opacity-100 scale-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="transform translate-y-0 opacity-100 scale-100"
      leave-to-class="transform -translate-y-4 opacity-0 scale-95"
    >
      <div v-if="errorMessage" class="absolute top-24 left-1/2 transform -translate-x-1/2 z-50 flex items-center gap-3 bg-red-900/90 backdrop-blur-md text-red-100 border border-red-700/50 px-5 py-3.5 rounded-xl shadow-[0_10px_40px_rgba(220,38,38,0.2)] min-w-[320px] max-w-md">
        <svg class="w-5 h-5 shrink-0 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
        <span class="text-sm font-medium flex-1 tracking-wide">{{ errorMessage }}</span>
        <button @click="errorMessage = ''" class="text-red-400 hover:text-white transition-colors"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button>
      </div>
    </Transition>

    <div class="flex-1 z-10 p-4 lg:p-6 overflow-hidden relative flex flex-col lg:flex-row gap-4 lg:gap-6 max-w-[1920px] mx-auto w-full transition-[grid-template-columns] duration-500 ease-[cubic-bezier(0.4,0,0.2,1)]" :class="showTelemetry ? 'grid-cols-1 lg:grid-cols-[1fr_400px]' : 'grid-cols-1 lg:grid-cols-[1fr_0px]'">
      
      <div class="flex-1 min-w-0 h-full flex flex-col items-center justify-center transition-all duration-500 ease-[cubic-bezier(0.25,1,0.5,1)]">
        <div class="w-full max-h-full aspect-[4/3] flex justify-center relative">
          <VideoStreamPlayer 
            :is-connected="isStreamConnected"
            @toggle-stream="handleStreamToggle"
            class="w-full h-full shadow-2xl"
          >
            <template #header-actions>
              
              <button 
                v-if="telemetryState.connected && isStreamConnected"
                @click="handleEmergencyLand"
                :disabled="isLanding"
                class="flex items-center gap-2 px-4 py-2 bg-red-600/90 hover:bg-red-500 text-white text-xs font-bold uppercase tracking-wide rounded-full backdrop-blur-md border border-red-500 transition-all shadow-md focus:outline-none disabled:opacity-50"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13l-3 3m0 0l-3-3m3 3V8m0 13a9 9 0 110-18 9 9 0 010 18z"></path>
                </svg>
                {{ isLanding ? 'Landing...' : 'Emergency Land' }}
              </button>

              <ToggleDetailsButton 
                :is-showing="showTelemetry" 
                @toggle="showTelemetry = !showTelemetry" 
              />

            </template>
          </VideoStreamPlayer>
        </div>
      </div>

      <div class="h-full relative overflow-hidden">
        <Transition
          enter-active-class="transition-all duration-300 ease-out"
          enter-from-class="opacity-0 translate-x-12"
          enter-to-class="opacity-100 translate-x-0"
          leave-active-class="transition-all duration-200 ease-in"
          leave-from-class="opacity-100 translate-x-0"
          leave-to-class="opacity-0 translate-x-12"
        >
          <div v-show="showTelemetry" class="h-full w-full lg:w-[400px] overflow-hidden rounded-xl shadow-2xl">
            <StreamDataCard />
          </div>
        </Transition>
      </div>

    </div>
  </div>
</template>