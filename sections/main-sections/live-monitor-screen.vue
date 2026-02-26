<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue';

// 1. Import your API service
import { missionApi } from "../api/missionApi";

import DashboardNavBar from '~/components/organisms/NavBar.vue';
import MetricCard from '~/components/molecules/live_monitor_molecules/MetricCard.vue';
import VideoStreamPlayer from '~/components/molecules/live_monitor_molecules/VideoStreamPlayer.vue';

const isStreamConnected = ref(false);
const planId = ref(null);
let telemetryPoll = null;

// 2. Telemetry state initialized with fallbacks
const telemetry = reactive({
  signal: 'Offline',
  battery: 0,
  altitude: 0,
  healthyCacao: 0,
  diseasedCacao: 0
});

const toggleStream = () => {
  isStreamConnected.value = !isStreamConnected.value;
};

// 3. Connect to Backend and Poll Status on Mount
onMounted(async () => {
  try {
    // Fetch the active flight plan
    const plan = await missionApi.getActive();
    if (plan) {
      planId.value = plan.id;
      
      // Set initial state from the plan payload
      telemetry.signal = plan.gps ?? 'Weak';
      telemetry.battery = plan.battery ?? 0;
      telemetry.altitude = plan.altitude ?? 0;

      // Start the 1-second interval loop to fetch real-time updates
      telemetryPoll = setInterval(async () => {
        if (!planId.value) return;

        try {
          const s = await missionApi.status(planId.value);
          
          // Apply the real drone data to your reactive variables
          telemetry.signal = s.gps ?? telemetry.signal;
          telemetry.battery = s.battery ?? telemetry.battery;
          telemetry.altitude = s.alt ?? telemetry.altitude; 
          
          // Update detection metrics (adjust 'healthy_cacao' to match your exact backend keys)
          telemetry.healthyCacao = s.healthy_cacao ?? telemetry.healthyCacao;
          telemetry.diseasedCacao = s.diseased_cacao ?? telemetry.diseasedCacao;

        } catch (err) {
          console.error("Telemetry poll failed:", err);
        }
      }, 1000);
    }
  } catch(e) {
    console.error("Failed to load active plan or connect to drone:", e);
  }
});

// 4. Clean up the loop when leaving the screen
onUnmounted(() => {
  if (telemetryPoll) clearInterval(telemetryPoll);
});
</script>

<template>
  <div 
    class="flex flex-col h-screen overflow-hidden font-inter bg-cover bg-center relative"
    style="background-image: url('https://images.unsplash.com/photo-1542319084-2a6c38210350?q=80&w=2574&auto=format&fit=crop');"
  >
    <div class="absolute inset-0 bg-black/60 z-0"></div>
    
    <div class="z-20 relative">
      <DashboardNavBar active-page="live-monitor" />
    </div>

    <div class="flex-1 z-10 p-6 overflow-y-auto relative">
      <div class="flex flex-col h-full max-w-[1600px] mx-auto">

        <div class="w-full flex flex-col gap-6 h-full">
          
          <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
            
            <MetricCard label="Signal Strength" :value="telemetry.signal">
              <template #icon>
                <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
                </svg>
              </template>
            </MetricCard>

            <MetricCard label="Battery Level" :value="telemetry.battery + '%'">
              <template #icon>
                <svg class="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M17 6H3a2 2 0 00-2 2v8a2 2 0 002 2h14a2 2 0 002-2v-8a2 2 0 00-2-2zm4 4v4h-2v-4h2z"/>
                </svg>
              </template>
            </MetricCard>

            <MetricCard label="Altitude" :value="telemetry.altitude + ' m'">
              <template #icon>
                <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
                </svg>
              </template>
            </MetricCard>
            
            <MetricCard label="Black Pod" :value="telemetry.diseasedCacao">
              <template #icon>
                <svg class="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9v-2h2v2zm0-4H9V7h2v5z"/>
                </svg>
              </template>
            </MetricCard>

            <MetricCard label="Healthy" :value="telemetry.healthyCacao">
              <template #icon>
                <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
              </template>
            </MetricCard>

          </div>

          <div class="flex-1 min-h-[400px]">
            <VideoStreamPlayer 
              :is-connected="isStreamConnected"
              @toggle-stream="toggleStream"
            />
          </div>

        </div>

      </div>
    </div>

  </div>
</template>