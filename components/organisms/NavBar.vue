<script setup>
import { computed } from 'vue';

const props = defineProps({
  activePage: {
    type: String,
    required: true
  }
});

const pages = {
  'mission-planner': {
    label: 'Mission Planner',
    path: '/mission-planner',
    color: 'bg-[#3E2723]', // Brown
    icon: 'plane'
  },
  'live-monitor': {
    label: 'Live Monitor',
    path: '/live-monitor',
    color: 'bg-[#C60C0C]', // Red
    icon: 'wifi'
  },
  'map-geotagging': {
    label: 'Map and Geotagging',
    path: '/map-geotagging',
    color: 'bg-[#658D1B]', // Green
    icon: 'map'
  },
  'report': {
    label: 'Report',
    path: '/report',
    color: 'bg-[#F57F17]', // Orange
    icon: 'doc'
  }
};

// FIX: Add a fallback to prevent the crash if activePage is invalid
const currentPage = computed(() => {
  // Try to find the page
  const page = pages[props.activePage];
  
  // If found, return it. If not, return a default (e.g., mission-planner)
  // This prevents 'undefined.color' errors
  return page || pages['mission-planner'];
});

// Filter out the current page for navigation links
const navigationLinks = computed(() => {
  // Ensure currentPage exists before accessing label
  if (!currentPage.value) return []; 
  return Object.values(pages).filter(p => p.label !== currentPage.value.label);
});

const goTo = (path) => navigateTo(path);
const logout = () => navigateTo('/login'); 
</script>

<template>
  <header class="w-full bg-white shadow-md px-6 py-3 flex items-center justify-between z-50 relative">
    
    <button 
      @click="logout" 
      class="flex items-center space-x-4 hover:opacity-70 transition-opacity duration-200 text-left focus:outline-none"
      title="Return to Login"
    >
      <div class="w-12 h-12 flex items-center justify-center">
         <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#5D4037" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-10 h-10">
            <path d="M12 13a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/>
            <path d="M12 13v4"/>
            <path d="M12 13l-4-2"/>
            <path d="M12 13l4-2"/>
            <path d="M4 10a2 2 0 1 0 4 0"/>
            <path d="M16 10a2 2 0 1 0 4 0"/>
            <path d="M2 10h2"/>
            <path d="M20 10h2"/>
         </svg>
      </div>
      <div class="flex flex-col">
        <h1 class="text-[#3E2723] font-bold text-xl leading-none tracking-wide font-poppins">LUPAD</h1>
        <span class="text-gray-500 text-sm font-inter">Welcome to LUPAD!</span>
      </div>
    </button>

    <div class="flex-1 flex justify-center mx-4">
      <div 
        v-if="currentPage"
        class="flex items-center justify-center space-x-2 text-white px-12 py-3 rounded-md shadow w-full max-w-md select-none"
        :class="currentPage.color"
      >
        <svg v-if="currentPage.icon === 'plane'" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12h20"/><path d="M13 12l3-7h4l-5 7V5"/><path d="M11 12l-3 7H4l5-7V5"/></svg>
        <svg v-if="currentPage.icon === 'wifi'" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z"/><path d="M5 12.859a10 10 0 0 1 14 0"/><path d="M8.5 16.429a5 5 0 0 1 7 0"/></svg>
        <svg v-if="currentPage.icon === 'map'" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" x2="9" y1="3" y2="18"/><line x1="15" x2="15" y1="6" y2="21"/></svg>
        <svg v-if="currentPage.icon === 'doc'" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/><line x1="10" x2="8" y1="9" y2="9"/></svg>
        
        <span class="font-medium text-lg font-poppins">{{ currentPage.label }}</span>
      </div>
    </div>

    <div class="flex items-center space-x-3">
      <button 
        v-for="page in navigationLinks" 
        :key="page.path"
        @click="goTo(page.path)"
        class="w-10 h-10 rounded-full flex items-center justify-center text-white hover:opacity-90 transition shadow-sm p-0 border-none outline-none"
        :class="page.color"
        :title="`Go to ${page.label}`"
      >
        <svg v-if="page.icon === 'plane'" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12h20"/><path d="M13 12l3-7h4l-5 7V5"/><path d="M11 12l-3 7H4l5-7V5"/></svg>
        <svg v-if="page.icon === 'wifi'" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z"/><path d="M5 12.859a10 10 0 0 1 14 0"/><path d="M8.5 16.429a5 5 0 0 1 7 0"/></svg>
        <svg v-if="page.icon === 'map'" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" x2="9" y1="3" y2="18"/><line x1="15" x2="15" y1="6" y2="21"/></svg>
        <svg v-if="page.icon === 'doc'" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/><line x1="10" x2="8" y1="9" y2="9"/></svg>
      </button>
    </div>

  </header>
</template>