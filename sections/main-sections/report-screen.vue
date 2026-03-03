<script setup>
import { reactive } from 'vue';
import DashboardNavBar from '~/components/organisms/NavBar.vue';

import MissionHistoryCard from '~/components/molecules/report_molecules/MissionHistoryCard.vue';
import MissionSummaryCard from '~/components/molecules/report_molecules/MissionSummaryCard.vue';
import FlightStatisticsCard from '~/components/molecules/report_molecules/FlightStatisticsCard.vue';
import DetectionStatisticsCard from '~/components/molecules/report_molecules/DetectionStatisticsCard.vue';

const placeholderHistory = reactive([]);

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
  <div
    class="flex flex-col h-screen overflow-hidden font-inter bg-cover bg-center relative"
    style="background-image: url('https://images.unsplash.com/photo-1542319084-2a6c38210350?q=80&w=2574&auto=format&fit=crop');"
  >
    <div class="absolute inset-0 bg-black/50 z-0"></div>

    <div class="z-10 relative">
      <DashboardNavBar active-page="report" />
    </div>

    <div class="flex-1 z-10 p-6 overflow-y-auto relative">
      <div class="flex flex-col md:flex-row gap-6 h-full max-w-[1600px] mx-auto">

        <div class="w-full md:w-1/4 min-w-[280px] h-[calc(100vh-120px)] md:h-auto">
          <MissionHistoryCard
            :history-list="placeholderHistory"
            class="bg-white/95 backdrop-blur-sm"
          />
        </div>

        <div class="w-full md:w-3/4 flex flex-col gap-6 pb-6">
          <MissionSummaryCard :data="placeholderSummary" class="bg-white/95 backdrop-blur-sm" />
          <FlightStatisticsCard :stats="placeholderFlightStats" class="bg-white/95 backdrop-blur-sm" />
          <DetectionStatisticsCard :stats="placeholderDetectionStats" class="bg-white/95 backdrop-blur-sm" />
        </div>

      </div>
    </div>
  </div>
</template>