<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import DashboardNavBar from '~/components/organisms/NavBar.vue';

// 1. IMPORT TELEMETRY COMPOSABLE (This was missing)
import { useTelemetry } from "~/components/composables/useTelemetry"; 
import { reportApi } from '~/sections/api/reportApi'; // Adjust path as needed

import MissionHistory from '~/components/molecules/report_molecules/MissionHistory.vue';
import DetectionStatisticsCard from '~/components/molecules/report_molecules/DetectionStatisticsCard.vue';
import FlightStatisticsCard from '~/components/molecules/report_molecules/FlightStatisticsCard.vue';
import MissionSummaryCard from '~/components/molecules/report_molecules/MissionSummaryCard.vue';

// --- MAKE SURE THESE 3 LINES EXIST ---
const missions = ref([]); 
const selectedMissionId = ref(null); 
const activeMissionData = ref(null); 
// -------------------------------------

// Telemetry State
const { telemetryState, startPolling, stopPolling } = useTelemetry();
const signalStatus = computed(() => telemetryState.connected ? 'Online' : 'Offline');

onMounted(() => {
  startPolling();
  fetchMissionList();
});

onUnmounted(() => {
  stopPolling();
});

const fetchMissionList = async () => {
  try {
    const data = await reportApi.getHistory();
    missions.value = data.missions || [];
    
    if (missions.value.length > 0) {
      selectedMissionId.value = missions.value[0].id;
    }
  } catch (error) {
    console.error("Failed to load mission history:", error);
  }
};

const handleDeleteMission = async (id) => { 
  try {
    if (reportApi.deleteMission) {
      await reportApi.deleteMission(id);
    }
    
    missions.value = missions.value.filter(m => m.id !== id);
    
    if (selectedMissionId.value === id) {
      selectedMissionId.value = missions.value.length > 0 ? missions.value[0].id : null;
    }
  } catch (error) {
    console.error(`Failed to delete mission ${id}:`, error);
    alert("Failed to delete the mission. Please check your connection.");
  }
};

watch(selectedMissionId, async (newId) => {
  if (!newId) return;
  
  try {
    const data = await reportApi.getMissionReport(newId);
    activeMissionData.value = data;
  } catch (error) {
    console.error(`Failed to fetch report for mission ${newId}:`, error);
    activeMissionData.value = null; 
  }
});

const activeMission = computed(() => {
  return activeMissionData.value || {
    id: '--', name: 'Loading...', altitude_m: 0, speed: 0, mode: '--', date: '--',
    telemetry: {}, detection: { total_pods: 0, unhealthy: 0 }, trees: [], steps: []
  };
});

const avgAccuracy = computed(() => {
  const currentTrees = activeMission.value.trees || [];
  if (currentTrees.length === 0) return 0;
  const sum = currentTrees.reduce((acc, tree) => acc + tree.accuracy, 0);
  return (sum / currentTrees.length).toFixed(2);
});

const handleBulkDeleteMissions = async (idsToDelete) => {
  // REMOVED: native browser confirm()
  // The custom modal in MissionHistory.vue handles confirmation now.

  try {
    // Loop through and delete each ID. 
    // (If you want to optimize this later, you can create a bulk delete endpoint in Django!)
    for (const id of idsToDelete) {
      if (reportApi.deleteMission) {
        await reportApi.deleteMission(id);
      }
    }
    
    // Remove the deleted IDs from the frontend list
    missions.value = missions.value.filter(m => !idsToDelete.includes(m.id));
    
    // If the currently selected mission was deleted, select the first available one
    if (idsToDelete.includes(selectedMissionId.value)) {
      selectedMissionId.value = missions.value.length > 0 ? missions.value[0].id : null;
    }
  } catch (error) {
    console.error("Failed during bulk deletion:", error);
    alert("Failed to delete some missions. Please refresh and try again.");
  }
};

const handleExportPDF = () => {
  window.print(); 
};
</script>

<template>
  <div class="flex flex-col h-screen overflow-hidden font-inter bg-cover bg-center relative print:bg-none print:h-auto print:overflow-visible"
    style="background-image: url('https://images.unsplash.com/photo-1542319084-2a6c38210350?q=80&w=2574&auto=format&fit=crop');"
    >
    <div class="absolute inset-0 bg-black/40 z-0 print:hidden"></div>
    
    <div class="z-20 relative shrink-0 print:hidden">
      <DashboardNavBar 
        active-page="report" 
        :connectionStatus="signalStatus" 
        :battery="telemetryState.battery"
      />
    </div>

    <div class="flex-1 z-10 p-4 lg:p-6 overflow-hidden flex gap-4 lg:gap-6 max-w-[1920px] mx-auto w-full print:p-0 print:block print:overflow-visible">
      
      <MissionHistory 
        :missions="missions" 
        :selected-id="selectedMissionId" 
        @select="selectedMissionId = $event" 
        @delete="handleDeleteMission"
        @bulkDelete="handleBulkDeleteMissions"
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