<script setup>
import { computed } from 'vue';

import NavBarBranding from '~/components/molecules/NavBarBranding.vue';
import ActivePageBanner from '~/components/molecules/ActivePageBanner.vue';
import NavCircleButton from '~/components/molecules/NavCircleButton.vue';

import IconPlane from '~/components/atoms/IconPlane.vue';
import IconWifi from '~/components/atoms/IconWifi.vue';
import IconMap from '~/components/atoms/IconMap.vue';
import IconReport from '~/components/atoms/IconReport.vue';

const props = defineProps({
  activePage: {
    type: String,
    required: true
  }
});

// Map the string keys to the actual Vue Components (Atoms)
const iconComponents = {
  'plane': IconPlane,
  'wifi': IconWifi,
  'map': IconMap,
  'doc': IconReport
};

// Define Page Data
const pages = {
  'mission-planner': {
    label: 'Mission Planner',
    path: '/mission-planner',
    color: 'bg-[#3E2723]',
    iconKey: 'plane'
  },
  'live-monitor': {
    label: 'Live Monitor',
    path: '/live-monitor',
    color: 'bg-[#C60C0C]',
    iconKey: 'wifi'
  },
  'map-geotagging': {
    label: 'Map and Geotagging',
    path: '/map-geotagging',
    color: 'bg-[#658D1B]',
    iconKey: 'map'
  },
  'report': {
    label: 'Report',
    path: '/report',
    color: 'bg-[#F57F17]',
    iconKey: 'doc'
  }
};

const currentPage = computed(() => {
  const page = pages[props.activePage];
  return page || pages['mission-planner'];
});

const navigationLinks = computed(() => {
  if (!currentPage.value) return []; 
  return Object.values(pages).filter(p => p.label !== currentPage.value.label);
});

const goTo = (path) => navigateTo(path);
const logout = () => navigateTo('/login'); 
</script>

<template>
  <header class="w-full bg-white shadow-md px-6 py-3 flex items-center justify-between z-50 relative">
    
    <NavBarBranding @click="logout" />

    <div class="flex-1 flex justify-center mx-4">
      <ActivePageBanner 
        v-if="currentPage"
        :label="currentPage.label"
        :color-class="currentPage.color"
      >
        <template #icon>
          <component :is="iconComponents[currentPage.iconKey]" />
        </template>
      </ActivePageBanner>
    </div>

    <div class="flex items-center space-x-3">
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