<script setup>
import { ref, reactive, onMounted, computed, onBeforeUnmount } from 'vue';
import { missionApi } from "~/sections/api/missionApi";
import { useTelemetry } from "~/components/composables/useTelemetry";

import DashboardNavBar from '~/components/organisms/NavBar.vue';
import FormGroup from '~/components/molecules/profile_molecules/FormGroup.vue';

const userProfile = reactive({
  fullName: 'Juan Dela Cruz',
  email: 'juan.delacruz@globe.com.ph',
  password: '',
  confirmPassword: ''
});

const stats = reactive({ total: 0, healthy: 0, diseased: 0 });
const isLoading = ref(true);

// Telemetry Integration
const { telemetryState, startPolling, stopPolling } = useTelemetry();

const formattedTelemetry = computed(() => {
  return {
    gps: telemetryState.connected ? 'Online' : 'Offline',
    battery: telemetryState.battery || 0,
  };
});

onMounted(async () => {
  startPolling(); // Start listening for live battery/connection status
  
  try {
    const res = await missionApi.getDetectionAnalytics();
    stats.total = res.total_pods || 0;
    stats.diseased = res.unhealthy || 0;
    stats.healthy = Math.max(0, stats.total - stats.diseased);
  } catch (error) {
    console.error("Failed to fetch analytics:", error);
  } finally {
    isLoading.value = false;
  }
});

onBeforeUnmount(() => {
  stopPolling(); // Clean up the polling loop when leaving the profile page
});

const handleLogout = () => {
  console.log("Signing out... clear tokens/session here.");
  // Example: navigateTo('/login');
};
</script>

<template>
  <div class="flex flex-col h-screen overflow-hidden font-inter bg-cover bg-center" style="background-image: url('https://images.unsplash.com/photo-1542319084-2a6c38210350?q=80&w=2574&auto=format&fit=crop');">
    <div class="absolute inset-0 bg-slate-900/70 z-0 backdrop-blur-[4px]"></div>

    <div class="z-20 relative">
      <DashboardNavBar 
        activePage="profile" 
        :droneStatus="formattedTelemetry.gps" 
        :battery="formattedTelemetry.battery"
      />
    </div>

    <div class="flex-1 z-10 p-4 md:p-8 flex justify-center items-center overflow-hidden">
      <div class="w-full max-w-[950px] bg-white/95 backdrop-blur-xl rounded-[2rem] shadow-[0_20px_60px_rgba(0,0,0,0.4)] flex flex-col md:flex-row overflow-hidden border border-white/20 transition-all duration-500">
        
        <div class="md:w-[40%] bg-slate-50/80 p-10 border-b md:border-b-0 md:border-r border-slate-100 flex flex-col items-center justify-between">
          
          <div class="flex flex-col items-center w-full">
            <div class="relative mb-6">
              <div class="w-32 h-32 rounded-full bg-white p-1.5 shadow-2xl ring-1 ring-slate-200">
                <div class="w-full h-full rounded-full bg-slate-100 flex items-center justify-center text-slate-300">
                  <svg class="w-14 h-14" fill="currentColor" viewBox="0 0 24 24"><path d="M24 20.993V24H0v-2.996A14.977 14.977 0 0112.004 15c4.904 0 9.26 2.354 11.996 5.993zM16.002 8.999a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
                </div>
              </div>
              <div class="absolute bottom-1 right-3 bg-[#658D1B] w-6 h-6 rounded-full border-4 border-white shadow-lg animate-pulse"></div>
            </div>

            <h2 class="text-2xl font-black text-slate-800 tracking-tight text-center">{{ userProfile.fullName }}</h2>
          </div>

          <div class="w-full space-y-3 mt-10">
            <div class="group bg-white p-4 rounded-2xl border border-slate-100 shadow-sm transition-all hover:border-[#658D1B]/30 hover:shadow-md">
              <p class="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-1">Lifetime Pods Detected</p>
              <p class="text-2xl font-black text-slate-800">{{ stats.total.toLocaleString() }}</p>
            </div>

            <div class="flex gap-3">
              <div class="flex-1 bg-emerald-50/60 p-4 rounded-2xl border border-emerald-100">
                <span class="block text-[8px] font-bold text-emerald-600 uppercase mb-1">Healthy</span>
                <span class="text-xl font-black text-emerald-700">{{ stats.healthy.toLocaleString() }}</span>
              </div>
              <div class="flex-1 bg-rose-50/60 p-4 rounded-2xl border border-rose-100">
                <span class="block text-[8px] font-bold text-rose-600 uppercase mb-1">Diseased</span>
                <span class="text-xl font-black text-rose-700">{{ stats.diseased.toLocaleString() }}</span>
              </div>
            </div>
            
            <div class="mt-8 pt-6 border-t border-gray-200 flex justify-center w-full">
              <button 
                @click="handleLogout" 
                class="group flex items-center gap-2 px-4 py-2 rounded-md text-sm font-bold text-slate-500 hover:text-red-600 hover:bg-red-50 transition-all duration-200"
              >
                <svg class="w-4 h-4 transition-transform group-hover:-translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
                </svg>
                <span>Sign Out</span>
              </button>
            </div>
            
          </div>
        </div>

        <div class="md:w-[60%] p-10 md:p-12 flex flex-col justify-center">
          <div class="mb-10">
            <h3 class="text-2xl font-black text-slate-800 tracking-tight">Account Settings</h3>
            <div class="h-1 w-12 bg-[#658D1B] mt-2 rounded-full"></div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-8">
            <FormGroup label="Full Name" v-model="userProfile.fullName" placeholder="Full name" />
            <FormGroup label="Email Address" v-model="userProfile.email" type="email" placeholder="Email" />
            <FormGroup label="New Password" v-model="userProfile.password" type="password" placeholder="••••••••" />
            <FormGroup label="Confirm Password" v-model="userProfile.confirmPassword" type="password" placeholder="••••••••" />
          </div>

          <div class="mt-12 flex justify-end">
            <button class="w-full sm:w-auto px-10 py-4 bg-[#658D1B] hover:bg-[#557516] text-white rounded-2xl font-bold text-[11px] uppercase tracking-[0.15em] transition-all shadow-[0_12px_30px_-5px_rgba(101,141,27,0.4)] active:scale-95 flex items-center justify-center gap-3">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" /></svg>
              Update Profile
            </button>
          </div>
        </div>
        
      </div>
    </div>
  </div>
</template>