<script setup>
import { ref, computed } from 'vue';
import DashboardNavBar from '~/components/organisms/NavBar.vue';

import MissionHistory from '~/components/molecules/report_molecules/MissionHistory.vue';
import DetectionStatisticsCard from '~/components/molecules/report_molecules/DetectionStatisticsCard.vue';
import FlightStatisticsCard from '~/components/molecules/report_molecules/FlightStatisticsCard.vue';
import MissionSummaryCard from '~/components/molecules/report_molecules/MissionSummaryCard.vue';

//Sample Database State
const missions = ref([
  { 
    id: 1, name: 'Mission 1 ', altitude_m: 1, speed: 5, mode: 'Stabilize', date: '2026-03-07',
    telemetry: { recorded_at: '2026-03-07', battery_end: 28, max_altitude: 1, flight_time: 379, avg_temp: 90 },
    detection: { total_pods: 80, unhealthy: 30 },
    trees: [ { tree_id: 1, lat: 8.49918863, lon: 124.3104652, accuracy: 90 } ],
    steps: [ { step_id: 82, order: 2, command: 'right', value: 150 }, 
              { step_id: 83, order: 3, command: 'down', value: 100 },
              { step_id: 84, order: 4, command: 'left', value: 150 }
    ]
  },
  { 
    id: 2, name: 'Mission 2', altitude_m: 2, speed: 10, mode: 'Stabilize', date: '2026-03-05',
    telemetry: { recorded_at: '2026-03-05', battery_end: 45, max_altitude: 2.1, flight_time: 450, avg_temp: 88 },
    detection: { total_pods: 120, unhealthy: 15 },
    trees: [ { tree_id: 101, lat: 8.500123, lon: 124.320123, accuracy: 95 } ],
    steps: [ { step_id: 90, order: 1, command: 'up', value: 200 } ]
  }
]);

const selectedMissionId = ref(missions.value[0]?.id || null);

const activeMission = computed(() => {
  return missions.value.find(m => m.id === selectedMissionId.value) || {
    id: '--', name: 'No Mission Selected', altitude_m: 0, speed: 0, mode: '--', date: '--',
    telemetry: {}, detection: { total_pods: 0, unhealthy: 0 }, trees: [], steps: []
  };
});

const avgAccuracy = computed(() => {
  const currentTrees = activeMission.value.trees || [];
  if (currentTrees.length === 0) return 0;
  const sum = currentTrees.reduce((acc, tree) => acc + tree.accuracy, 0);
  return (sum / currentTrees.length).toFixed(2);
});

const handleExportPDF = () => {
  window.print(); 
};
</script>

<template>
  <div class="flex flex-col h-screen overflow-hidden font-inter bg-cover bg-center relative print:bg-none print:h-auto print:overflow-visible"
    style="background-image: url('https://images.unsplash.com/photo-1542319084-2a6c38210350?q=80&w=2574&auto=format&fit=crop');"
    >
    
    <div class="z-20 relative shrink-0 print:hidden">
      <DashboardNavBar active-page="report" droneStatus="Offline" />
    </div>

    <div class="flex-1 z-10 p-4 lg:p-6 overflow-hidden flex gap-4 lg:gap-6 max-w-[1920px] mx-auto w-full print:p-0 print:block print:overflow-visible">
      
      <MissionHistory 
        :missions="missions" 
        :selected-id="selectedMissionId" 
        @select="selectedMissionId = $event" 
      />

      <div class="flex-1 bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col overflow-hidden relative print:shadow-none print:border-none print:rounded-none print:overflow-visible">
        
        <div class="px-8 py-6 border-b border-slate-100 flex items-center justify-between bg-white shrink-0 print:px-0">
          <div>
            <h1 class="text-2xl font-bold text-[#0F172A] font-poppins tracking-tight">{{ activeMission.name }} <span class="text-slate-300 font-normal">|</span> Report</h1>
            <p class="text-sm text-slate-500 font-medium mt-1">Executed on: {{ activeMission.date }} • Mission ID: {{ activeMission.id }}</p>
          </div>
          
          <button @click="handleExportPDF" class="flex items-center gap-2 px-5 py-2.5 bg-[#0F172A] text-white text-sm font-bold rounded-lg hover:bg-slate-800 transition-colors shadow-md print:hidden">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
            Export PDF
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-8 space-y-8 bg-slate-50/50 print:overflow-visible print:bg-white print:p-0 print:mt-6">
          
          <DetectionStatisticsCard :detection="activeMission.detection" :avgAccuracy="avgAccuracy" />
          <FlightStatisticsCard :mission="activeMission" />
          <MissionSummaryCard :steps="activeMission.steps" :trees="activeMission.trees" />

        </div>
      </div>
    </div>
  </div>
</template>