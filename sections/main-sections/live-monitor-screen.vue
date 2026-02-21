<script setup>
import { ref } from 'vue';

import DashboardNavBar from '~/components/organisms/NavBar.vue';
import MetricCard from '~/components/molecules/live_monitor_molecules/MetricCard.vue';
import VideoStreamPlayer from '~/components/molecules/live_monitor_molecules/VideoStreamPlayer.vue';

const isStreamConnected = ref(false);

const toggleStream = () => {
  isStreamConnected.value = !isStreamConnected.value;
};
</script>

<template>
  <div class="flex flex-col h-screen overflow-hidden font-inter">
    
    <div class="z-10">
      <DashboardNavBar active-page="live-monitor" />
    </div>

    <div class="flex-1 z-10 p-6 overflow-y-auto">
      <div class="flex flex-col h-full max-w-[1600px] mx-auto">

        <div class="w-full flex flex-col gap-6 h-full">
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <MetricCard label="Signal Strength" value="-68 dBm" />
            <MetricCard label="Latency" value="45 ms" />
            <MetricCard label="Bitrate" value="2.4 Mbps" />
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