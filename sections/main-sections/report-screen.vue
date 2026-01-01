<script setup>
import { reactive } from 'vue';
import DashboardNavBar from '~/components/organisms/NavBar.vue';

import MissionHistoryCard from '~/components/molecules/report_molecules/MissionHistoryCard.vue';
import MissionSummaryCard from '~/components/molecules/report_molecules/MissionSummaryCard.vue';
import FlightStatisticsCard from '~/components/molecules/report_molecules/FlightStatisticsCard.vue';
import DetectionStatisticsCard from '~/components/molecules/report_molecules/DetectionStatisticsCard.vue';

// Initialize with an empty array. Data will be pushed here from DB later.
const placeholderHistory = reactive([]);

// Initialize with default placeholders ('--') to preserve layout height
const placeholderSummary = reactive({
  id: '--',
  duration: '--',
  startTime: '--',
  endTime: '--'
});

const placeholderFlightStats = reactive({
  distance: '--',
  altitude: '--',
  speed: '--',
  waypoints: '--',
  photos: '--',
  battery: '--'
});

const placeholderDetectionStats = reactive({
  totalDetected: '--',
  unhealthy: '--'
});
</script>

<template>
  <div class="flex flex-col h-screen overflow-hidden font-inter">
    
    <div class="z-10">
      <DashboardNavBar active-page="report" />
    </div>

    <div class="flex-1 z-10 p-6 overflow-y-auto">
      <div class="flex flex-col md:flex-row gap-6 h-full max-w-[1600px] mx-auto">
        
        <div class="w-full md:w-1/4 min-w-[300px] h-[calc(100vh-120px)] md:h-auto">
          <MissionHistoryCard :history-list="placeholderHistory" />
        </div>

        <div class="w-full md:w-3/4 flex flex-col gap-6 pb-6">
          <MissionSummaryCard :data="placeholderSummary" />
          <FlightStatisticsCard :stats="placeholderFlightStats" />
          <DetectionStatisticsCard :stats="placeholderDetectionStats" />
        </div>

      </div>
    </div>

  </div>
</template>