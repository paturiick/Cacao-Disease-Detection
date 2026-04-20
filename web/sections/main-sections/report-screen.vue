<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import DashboardNavBar from '~/components/organisms/NavBar.vue';
import { useTelemetry } from "~/components/composables/useTelemetry"; 
import { reportApi } from '~/sections/api/reportApi'; 

import MissionHistory from '~/components/molecules/report_molecules/MissionHistory.vue';
import DetectionStatisticsCard from '~/components/molecules/report_molecules/DetectionStatisticsCard.vue';
import FlightStatisticsCard from '~/components/molecules/report_molecules/FlightStatisticsCard.vue';
import MissionSummaryCard from '~/components/molecules/report_molecules/MissionSummaryCard.vue';

const missions = ref([]); 
const selectedMissionId = ref(null); 
const activeMissionData = ref(null); 

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
    if (reportApi.deleteMission) await reportApi.deleteMission(id);
    missions.value = missions.value.filter(m => m.id !== id);
    if (selectedMissionId.value === id) {
      selectedMissionId.value = missions.value.length > 0 ? missions.value[0].id : null;
    }
  } catch (error) {
    console.error(`Failed to delete mission ${id}:`, error);
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
  try {
    for (const id of idsToDelete) {
      if (reportApi.deleteMission) await reportApi.deleteMission(id);
    }
    missions.value = missions.value.filter(m => !idsToDelete.includes(m.id));
    if (idsToDelete.includes(selectedMissionId.value)) {
      selectedMissionId.value = missions.value.length > 0 ? missions.value[0].id : null;
    }
  } catch (error) {
    console.error("Failed during bulk deletion:", error);
  }
};

const handleExportPDF = () => {
  window.print(); 
};
</script>

<template>
  <div>
    <div class="flex flex-col h-screen overflow-hidden font-inter bg-cover bg-center relative print:hidden"
      style="background-image: url('https://images.unsplash.com/photo-1542319084-2a6c38210350?q=80&w=2574&auto=format&fit=crop');"
      >
      <div class="absolute inset-0 bg-black/40 z-0"></div>
      
      <div class="z-20 relative shrink-0">
        <DashboardNavBar 
          active-page="report" 
          :connectionStatus="signalStatus" 
          :battery="telemetryState.battery"
        />
      </div>

      <div class="flex-1 z-10 p-4 lg:p-6 overflow-hidden flex gap-4 lg:gap-6 max-w-[1920px] mx-auto w-full">
        <MissionHistory 
          :missions="missions" 
          :selected-id="selectedMissionId" 
          @select="selectedMissionId = $event" 
          @delete="handleDeleteMission"
          @bulkDelete="handleBulkDeleteMissions"
        />

        <div class="flex-1 bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col overflow-hidden relative">
          <div class="px-8 py-6 border-b border-slate-100 flex items-center justify-between bg-white shrink-0">
            <div>
              <h1 class="text-2xl font-bold text-[#0F172A] font-poppins tracking-tight">{{ activeMission.name }} <span class="text-slate-300 font-normal">|</span> Report</h1>
              <p class="text-sm text-slate-500 font-medium mt-1">Executed on: {{ activeMission.date }} • Mission ID: {{ activeMission.id }}</p>
            </div>
            <button @click="handleExportPDF" class="flex items-center gap-2 px-5 py-2.5 bg-[#0F172A] text-white text-sm font-bold rounded-lg hover:bg-slate-800 transition-colors shadow-md">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
              Export PDF
            </button>
          </div>

          <div class="flex-1 overflow-y-auto p-8 space-y-8 bg-slate-50/50">
            <DetectionStatisticsCard :detection="activeMission.detection" :avgAccuracy="avgAccuracy" />
            <FlightStatisticsCard :mission="activeMission" />
            <MissionSummaryCard :steps="activeMission.steps" :trees="activeMission.trees" />
          </div>
        </div>
      </div>
    </div>

    <div class="hidden print:block w-full bg-white text-black font-sans text-[11pt]">
      
      <div class="mb-6 pb-2 border-b-2 border-slate-800">
        <h1 class="text-2xl font-bold uppercase tracking-wide">{{ activeMission.name }} - Full Data Report</h1>
        <div class="flex justify-between text-sm mt-2 font-medium">
          <span><strong>Execution Date:</strong> {{ activeMission.date }}</span>
          <span><strong>Mission ID:</strong> {{ activeMission.id }}</span>
        </div>
      </div>

      <table class="w-full border-collapse mb-8 text-sm">
        <thead>
          <tr class="bg-slate-800 text-white">
            <th class="border border-slate-400 p-2 text-left font-bold uppercase tracking-wider" colspan="4">Mission Overview Metrics</th>
          </tr>
          <tr class="bg-slate-100 font-bold text-slate-700">
            <td class="border border-slate-400 p-2 w-1/4">Total Pods Scanned</td>
            <td class="border border-slate-400 p-2 w-1/4">Healthy Pods</td>
            <td class="border border-slate-400 p-2 w-1/4">Diseased Pods</td>
            <td class="border border-slate-400 p-2 w-1/4">Avg. Target Speed</td>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="border border-slate-400 p-2">{{ activeMission.detection?.total_pods || 0 }}</td>
            <td class="border border-slate-400 p-2">{{ (activeMission.detection?.total_pods || 0) - (activeMission.detection?.unhealthy || 0) }}</td>
            <td class="border border-slate-400 p-2 text-red-600 font-bold">{{ activeMission.detection?.unhealthy || 0 }}</td>
            <td class="border border-slate-400 p-2">{{ activeMission.speed || 0 }} cm/s</td>
          </tr>
        </tbody>
      </table>

      <table class="w-full border-collapse mb-8 text-sm">
        <thead>
          <tr class="bg-[#475569] text-white">
            <th class="border border-slate-400 p-2 text-left font-bold uppercase tracking-wider" colspan="4">Flight Command Sequence</th>
          </tr>
          <tr class="bg-slate-100 font-bold text-slate-700">
            <td class="border border-slate-400 p-2 w-[10%]">Order</td>
            <td class="border border-slate-400 p-2 w-[25%]">Step ID</td>
            <td class="border border-slate-400 p-2 w-[25%]">Command Type</td>
            <td class="border border-slate-400 p-2 w-[40%]">Execution Value</td>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!activeMission.steps || activeMission.steps.length === 0">
            <td colspan="4" class="border border-slate-400 p-4 text-center text-slate-500 italic">No flight sequence data available.</td>
          </tr>
          <tr v-for="(step, idx) in activeMission.steps" :key="step.id || idx" class="even:bg-slate-50">
            <td class="border border-slate-400 p-2 text-center">{{ idx + 1 }}</td>
            <td class="border border-slate-400 p-2 font-mono text-xs">{{ step.id || 'N/A' }}</td>
            <td class="border border-slate-400 p-2 font-bold uppercase">{{ step.type }}</td>
            <td class="border border-slate-400 p-2">{{ step.val || '--' }}</td>
          </tr>
        </tbody>
      </table>

      <table class="w-full border-collapse mb-8 text-sm">
        <thead>
          <tr class="bg-[#658D1B] text-white">
            <th class="border border-slate-400 p-2 text-left font-bold uppercase tracking-wider" colspan="4">Mapped Cacao Pods (Detection Log)</th>
          </tr>
          <tr class="bg-slate-100 font-bold text-slate-700">
            <td class="border border-slate-400 p-2 w-[25%]">Pod ID</td>
            <td class="border border-slate-400 p-2 w-[25%]">Health Status</td>
            <td class="border border-slate-400 p-2 w-[25%]">Latitude</td>
            <td class="border border-slate-400 p-2 w-[25%]">Longitude</td>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!activeMission.trees || activeMission.trees.length === 0">
            <td colspan="4" class="border border-slate-400 p-4 text-center text-slate-500 italic">No pods mapped during this mission.</td>
          </tr>
          <tr v-for="tree in activeMission.trees" :key="tree.id" class="even:bg-slate-50">
            <td class="border border-slate-400 p-2 font-mono text-xs">{{ tree.id }}</td>
            <td class="border border-slate-400 p-2 font-bold" :class="tree.status === 'Healthy' ? 'text-green-600' : 'text-red-600'">
              {{ tree.status || 'Unknown' }}
            </td>
            <td class="border border-slate-400 p-2 font-mono">{{ tree.lat || '--' }}</td>
            <td class="border border-slate-400 p-2 font-mono">{{ tree.lng || '--' }}</td>
          </tr>
        </tbody>
      </table>

    </div>
  </div>
</template>

<style>
@media print {
  /* Set standard A4 paper size and margin */
  @page {
    size: A4 portrait;
    margin: 15mm;
  }
  
  body {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    background-color: #ffffff !important;
  }

  /* Ensure page breaks don't chop tables in half */
  table {
    page-break-inside: auto;
  }
  tr {
    page-break-inside: avoid;
    page-break-after: auto;
  }
  thead {
    display: table-header-group;
  }
}
</style>