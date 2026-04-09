<script setup>
import { computed, ref, onMounted } from 'vue';
import { useRoute } from 'vue-router'; // <-- Added this to auto-detect the URL
import { useDrone } from '~/sections/api/statusApi.js'; 

import { telemetryApi } from '~/sections/api/telemetryApi.js';

import NavBarBranding from '~/components/molecules/NavBarBranding.vue';
import ActivePageBanner from '~/components/molecules/ActivePageBanner.vue';
import NavCircleButton from '~/components/molecules/NavCircleButton.vue';

import IconPlane from '~/components/atoms/IconPlane.vue';
import IconWifi from '~/components/atoms/IconWifi.vue';
import IconMap from '~/components/atoms/IconMap.vue';
import IconReport from '~/components/atoms/IconReport.vue';

// 1. Removed activePage from props (it's automatic now!)
const props = defineProps({
  battery: { type: Number, default: null } 
});

const route = useRoute(); // <-- Initialize the route
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

// 2. Automatically find the current page based on the browser's URL path
const currentPage = computed(() => {
  const foundPage = Object.values(pages).find(p => p.path === route.path);
  return foundPage || pages['mission-planner']; // Default fallback
});

const navigationLinks = computed(() => Object.values(pages).filter(p => p.label !== currentPage.value.label));

const goTo = (path) => navigateTo(path);
const logout = () => navigateTo('/login'); 

const syncMessage = ref('');
const isError = ref(false);

// --- BLUETOOTH STATE ---
const isBtConnecting = ref(false);
const isBtConnected = ref(false);

onMounted(async () => {
  try {
    const state = await telemetryApi.getBluetoothState();
    isBtConnected.value = state.active;
  } catch (error) {
    console.error("Failed to fetch initial BLE state:", error);
  }
});

const handleBtSync = async () => {
  if (isBtConnecting.value) return;
  
  syncMessage.value = '';
  isError.value = false;
  isBtConnecting.value = true;
  
  // Determine if we are turning it ON or OFF
  const targetState = !isBtConnected.value;

  try {
    // Send the real POST request to Django
    const response = await telemetryApi.setBluetoothState(targetState);
    
    if (response && response.status === 'success') {
      isBtConnected.value = response.active;
      isError.value = false;
      syncMessage.value = response.active ? 'Bluetooth Synced!' : 'Bluetooth Disconnected';
    } else {
      throw new Error("Unexpected API response");
    }
  } catch (error) {
    console.error("BLE Sync Error:", error);
    isError.value = true;
    syncMessage.value = 'Cannot sync Bluetooth.';
  } finally {
    isBtConnecting.value = false;
    setTimeout(() => { syncMessage.value = ''; }, 5000);
  }
};

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
      syncMessage.value = 'Cannot sync with the drone.';
    }
    setTimeout(() => { syncMessage.value = ''; }, 5000);
  }
};
</script>

<template>
  <header class="w-full bg-white shadow-md px-6 py-3 flex items-center justify-between z-50 relative">
    
    <NavBarBranding 
      :connectionStatus="currentDroneStatus" 
      :battery="props.battery"
      @click="logout" 
    />

    <div class="flex-1 flex justify-center mx-4">
      <ActivePageBanner v-if="currentPage" :label="currentPage.label" :color-class="currentPage.color">
        <template #icon>
          <component :is="iconComponents[currentPage.iconKey]" class="text-white" />
        </template>
      </ActivePageBanner>
    </div>

    <div class="flex items-center space-x-4">
      
      <span 
        v-if="syncMessage" 
        class="text-xs font-bold transition-opacity" 
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

      <button 
        @click="handleBtSync"
        :disabled="isBtConnecting"
        title="Sync Bluetooth"
        class="flex items-center justify-center w-9 h-9 bg-slate-800 text-white rounded-full border border-slate-700 hover:bg-slate-700 transition-all shadow-sm disabled:opacity-50"
      >
        <svg 
          class="w-4 h-4 transition-colors" 
          :class="{
            'animate-pulse text-[#38BDF8]': isBtConnecting, 
            'text-[#38BDF8]': isBtConnected && !isBtConnecting,
            'text-white': !isBtConnected && !isBtConnecting
          }" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6.75 7.5l10.5 9-6 5.25V2.25l6 5.25-10.5 9"></path>
        </svg>
      </button>

      <div class="h-8 w-px bg-gray-200"></div>

      <NavCircleButton 
        v-for="page in navigationLinks" 
        :key="page.path" 
        :label="page.label" 
        :color-class="page.color" 
        @click="goTo(page.path)"
      >
        <template #icon>
          <component :is="iconComponents[page.iconKey]" />
        </template>
      </NavCircleButton>
      
    </div>
  </header> 
</template>