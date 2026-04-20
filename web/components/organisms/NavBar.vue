<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router'; 
import { useDrone } from '~/sections/api/statusApi.js'; 

import { useTelemetry } from '~/components/composables/useTelemetry.js';
import { missionApi } from '~/sections/api/missionApi.js';

import NavBarBranding from '~/components/molecules/NavBarBranding.vue';
import ActivePageBanner from '~/components/molecules/ActivePageBanner.vue';
import NavCircleButton from '~/components/molecules/NavCircleButton.vue';

import IconPlane from '~/components/atoms/IconPlane.vue';
import IconWifi from '~/components/atoms/IconWifi.vue';
import IconMap from '~/components/atoms/IconMap.vue';
import IconReport from '~/components/atoms/IconReport.vue';

const { telemetryState, startPolling, stopPolling } = useTelemetry();

onMounted(() => startPolling());
onUnmounted(() => stopPolling());

const getSignalColor = (type, value) => {
  if (type === 'rssi') {
    // 2.4GHz RSSI: >-60 excellent, -60 to -80 fair, <-80 poor
    if (value >= -60) return 'text-emerald-500';
    if (value >= -80) return 'text-amber-500';
    return 'text-red-500';
  }
  return 'text-gray-400';
};

const props = defineProps({
  battery: { type: Number, default: null } 
});

const route = useRoute();
const { isConnected, isConnecting, connectDrone } = useDrone();

const currentDroneStatus = computed(() => {
  if (isConnecting?.value) return 'Syncing...';
  return isConnected?.value ? 'Connected' : 'Disconnected';
});

const iconComponents = { 'plane': IconPlane, 'wifi': IconWifi, 'map': IconMap, 'doc': IconReport };

const pages = {
  'mission-planner': { label: 'Mission Planner', path: '/mission-planner', color: 'bg-[#3E2723]', iconKey: 'plane' },
  'live-monitor': { label: 'Live Monitor', path: '/live-monitor', color: 'bg-[#C60C0C]', iconKey: 'wifi' },
  'map-geotagging': { label: 'Map and Geotagging', path: '/map-geotagging', color: 'bg-[#658D1B]', iconKey: 'map' },
  'report': { label: 'Report', path: '/report', color: 'bg-[#F57F17]', iconKey: 'doc' }
};

const currentPage = computed(() => {
  const foundPage = Object.values(pages).find(p => p.path === route.path);
  return foundPage || pages['mission-planner']; // Default fallback
});

// REMOVED THE FILTER: Now it always returns all pages for the circle buttons
const navigationLinks = computed(() => Object.values(pages));

const goTo = (path) => navigateTo(path);

// Changed to redirect to home instead of the deleted login page
const goHome = () => navigateTo('/'); 

const syncMessage = ref('');
const isError = ref(false);

const handleSync = async () => {
  if (isConnecting.value) return;
  
  syncMessage.value = '';
  isError.value = false;
  let didTimeout = false;

  const timeoutTimer = setTimeout(() => {
    didTimeout = true;
    isError.value = true;
    syncMessage.value = 'Cannot sync with the drone (Timeout).';
    setTimeout(() => { syncMessage.value = ''; }, 5000);
  }, 10000);

  await connectDrone();
  
  clearTimeout(timeoutTimer);

  if (!didTimeout) {
    if (isConnected.value) {
      isError.value = false;
      syncMessage.value = 'Synced successfully!';
    } else {
      isError.value = true;
      syncMessage.value = 'Cannot reach Drone Wi-Fi.'; 
    }
    setTimeout(() => { syncMessage.value = ''; }, 5000);
  }
};

// --- MOTOR COOLING STATE ---
const isMotorOn = ref(false); 
const isMotorToggling = ref(false);

const handleMotorToggle = async () => {
  if (isMotorToggling.value || !isConnected.value) return;
  
  syncMessage.value = '';
  isError.value = false;
  isMotorToggling.value = true;
  
  const targetCmd = isMotorOn.value ? 'motoroff' : 'motoron';

  try {
    const response = await missionApi.sendCommand(targetCmd);
    
    if (response && response.ok) {
      isMotorOn.value = !isMotorOn.value; // Flip the UI state
      isError.value = false;
      syncMessage.value = isMotorOn.value ? 'Cooling Motors: ON' : 'Cooling Motors: OFF';
    } else {
      throw new Error(response.text || "Drone rejected command");
    }
  } catch (error) {
    console.error("Motor Toggle Error:", error);
    isError.value = true;
    syncMessage.value = 'Failed to toggle motors.';
  } finally {
    isMotorToggling.value = false;
    setTimeout(() => { syncMessage.value = ''; }, 4000);
  }
};
</script>

<template>
  <header class="w-full bg-white shadow-md px-6 py-3 flex items-center justify-between z-50 relative">
    
    <NavBarBranding 
      :connectionStatus="currentDroneStatus" 
      :battery="props.battery"
      @click="goHome" 
    />

    <div class="flex-1 flex justify-center mx-4">
      <ActivePageBanner v-if="currentPage" :label="currentPage.label" :color-class="currentPage.color">
        <template #icon>
          <component :is="iconComponents[currentPage.iconKey]" class="text-white" />
        </template>
      </ActivePageBanner>
    </div>

    <div class="flex items-center space-x-3">
      <span 
        v-if="syncMessage" 
        class="text-[10px] font-bold whitespace-nowrap" 
        :class="isError ? 'text-red-500' : 'text-emerald-500'"
      >
        {{ syncMessage }}
      </span>

      <button 
        @click="handleSync"
        :disabled="isConnecting"
        class="flex items-center gap-2 px-4 py-2 bg-slate-800 text-white text-xs font-bold rounded-full border border-slate-700 hover:bg-slate-700 transition-all shadow-sm disabled:opacity-50"
      >
        <svg 
          class="w-4 h-4" 
          :class="{'animate-spin text-[#658D1B]': isConnecting, 'text-[#658D1B]': isConnected && !isConnecting}" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
        </svg>
        {{ isConnecting ? 'Syncing...' : 'Sync Drone' }}
      </button>

      <div class="h-8 w-px bg-gray-200"></div>

      <NavCircleButton 
        v-for="page in navigationLinks" 
        :key="page.path" 
        :label="page.label" 
        :color-class="page.color" 
        @click="goTo(page.path)"
        :class="{ 'ring-2 ring-offset-2 ring-slate-300 scale-105': currentPage.path === page.path }" 
      >
        <template #icon>
          <component :is="iconComponents[page.iconKey]" />
        </template>
      </NavCircleButton>
      
    </div>
  </header> 
</template>