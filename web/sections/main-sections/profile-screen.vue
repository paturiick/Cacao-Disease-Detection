<script setup>
import { ref, reactive, onMounted, computed, onBeforeUnmount } from 'vue';
import { missionApi } from "~/sections/api/missionApi";
import { useTelemetry } from "~/components/composables/useTelemetry";

import DashboardNavBar from '~/components/organisms/NavBar.vue';
import FormGroup from '~/components/molecules/profile_molecules/FormGroup.vue';

const userProfile = reactive({
  fullName: 'Loading...',
  email: 'Loading...',
  password: '',
  confirmPassword: ''
});

const stats = reactive({ total: 0, healthy: 0, diseased: 0 });
const isLoading = ref(true);
const isLoggingOut = ref(false);
const isUpdating = ref(false);
const updateStatus = reactive({ type: '', message: '' }); // For success/error banners

// Image Upload State
const fileInput = ref(null);
const profileImageUrl = ref(null);
const selectedFile = ref(null);

// Telemetry Integration
const { telemetryState, startPolling, stopPolling } = useTelemetry();

const formattedTelemetry = computed(() => {
  return {
    gps: telemetryState.connected ? 'Online' : 'Offline',
    battery: telemetryState.battery || 0,
  };
});

// Fetch the current user's details
const fetchUserProfile = async () => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) return navigateTo('/login');

    const res = await fetch('http://localhost:8000/api/auth/me/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (res.ok) {
      const data = await res.json();
      userProfile.fullName = data.full_name;
      userProfile.email = data.email;
      if (data.profile_picture) {
        profileImageUrl.value = `http://localhost:8000${data.profile_picture}`;
      }
    } else if (res.status === 401) {
      forceLocalLogout();
    }
  } catch (error) {
    console.error("Failed to fetch profile:", error);
  }
};

onMounted(async () => {
  startPolling(); 
  await fetchUserProfile();
  
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
  stopPolling(); 
});

// --- IMAGE UPLOAD LOGIC ---
const triggerFileInput = () => {
  fileInput.value.click();
};

const onFileSelected = (event) => {
  const file = event.target.files[0];
  if (file) {
    selectedFile.value = file;
    // Create a temporary local URL to show the preview instantly
    profileImageUrl.value = URL.createObjectURL(file);
  }
};

// --- UPDATE PROFILE LOGIC ---
const handleUpdateProfile = async () => {
  updateStatus.message = '';
  
  if (userProfile.password && userProfile.password !== userProfile.confirmPassword) {
    updateStatus.type = 'error';
    updateStatus.message = 'Passwords do not match.';
    return;
  }

  isUpdating.value = true;
  try {
    const token = localStorage.getItem('access_token');
    
    // We MUST use FormData instead of JSON because we are sending a file
    const formData = new FormData();
    formData.append('full_name', userProfile.fullName);
    formData.append('email', userProfile.email);
    
    if (userProfile.password) {
      formData.append('password', userProfile.password);
    }
    
    if (selectedFile.value) {
      formData.append('profile_picture', selectedFile.value);
    }

    const res = await fetch('http://localhost:8000/api/auth/me/', {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`
        // NOTE: Do NOT set Content-Type here. The browser automatically sets it to multipart/form-data with boundaries when using FormData.
      },
      body: formData
    });

    const data = await res.json();

    if (res.ok) {
      updateStatus.type = 'success';
      updateStatus.message = 'Profile updated successfully!';
      userProfile.password = ''; // Clear passwords after success
      userProfile.confirmPassword = '';
    } else {
      updateStatus.type = 'error';
      // Grab first error message returned
      const errorKey = Object.keys(data)[0];
      updateStatus.message = `${errorKey}: ${data[errorKey][0]}`;
    }
  } catch (error) {
    updateStatus.type = 'error';
    updateStatus.message = 'Connection error. Please try again.';
  } finally {
    isUpdating.value = false;
  }
};

// --- LOGOUT LOGIC ---
const handleLogout = async () => {
  if (isLoggingOut.value) return;
  isLoggingOut.value = true;

  try {
    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');

    if (accessToken && refreshToken) {
      await fetch('http://localhost:8000/api/auth/logout/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ refresh: refreshToken })
      });
    }
  } catch (error) {
    console.error("Error during server logout:", error);
  } finally {
    forceLocalLogout();
  }
};

const forceLocalLogout = async () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  await navigateTo('/login');
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
            
            <div class="relative mb-6 group cursor-pointer" @click="triggerFileInput" title="Change Profile Picture">
              <div class="w-32 h-32 rounded-full bg-white p-1.5 shadow-2xl ring-1 ring-slate-200 relative overflow-hidden">
                <img v-if="profileImageUrl" :src="profileImageUrl" class="w-full h-full object-cover rounded-full" alt="Profile" />
                <div v-else class="w-full h-full rounded-full bg-slate-100 flex items-center justify-center text-slate-300">
                  <svg class="w-14 h-14" fill="currentColor" viewBox="0 0 24 24"><path d="M24 20.993V24H0v-2.996A14.977 14.977 0 0112.004 15c4.904 0 9.26 2.354 11.996 5.993zM16.002 8.999a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
                </div>
                
                <div class="absolute inset-1.5 rounded-full bg-black/50 flex flex-col items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <svg class="w-8 h-8 text-white mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                  <span class="text-[9px] font-bold text-white uppercase tracking-wider">Upload</span>
                </div>
              </div>
              <input type="file" ref="fileInput" class="hidden" accept="image/*" @change="onFileSelected" />
              
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
                :disabled="isLoggingOut"
                class="group flex items-center gap-2 px-4 py-2 rounded-md text-sm font-bold text-slate-500 hover:text-red-600 hover:bg-red-50 disabled:opacity-50 transition-all duration-200"
              >
                <svg class="w-4 h-4 transition-transform group-hover:-translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
                </svg>
                <span>{{ isLoggingOut ? 'Signing Out...' : 'Sign Out' }}</span>
              </button>
            </div>
            
          </div>
        </div>

        <div class="md:w-[60%] p-10 md:p-12 flex flex-col justify-center">
          <div class="mb-6">
            <h3 class="text-2xl font-black text-slate-800 tracking-tight">Account Settings</h3>
            <div class="h-1 w-12 bg-[#658D1B] mt-2 rounded-full"></div>
          </div>

          <div v-if="updateStatus.message" :class="`mb-6 px-4 py-3 rounded-lg text-sm font-bold ${updateStatus.type === 'success' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-red-50 text-red-700 border border-red-200'}`">
            {{ updateStatus.message }}
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-8">
            <FormGroup label="Full Name" v-model="userProfile.fullName" placeholder="Full name" />
            <FormGroup label="Email Address" v-model="userProfile.email" type="email" placeholder="Email" />
            <FormGroup label="New Password" v-model="userProfile.password" type="password" placeholder="••••••••" />
            <FormGroup label="Confirm Password" v-model="userProfile.confirmPassword" type="password" placeholder="••••••••" />
          </div>

          <div class="mt-12 flex justify-end">
            <button 
              @click="handleUpdateProfile"
              :disabled="isUpdating"
              class="w-full sm:w-auto px-10 py-4 bg-[#658D1B] hover:bg-[#557516] disabled:bg-[#8da75a] text-white rounded-2xl font-bold text-[11px] uppercase tracking-[0.15em] transition-all shadow-[0_12px_30px_-5px_rgba(101,141,27,0.4)] active:scale-95 flex items-center justify-center gap-3">
              <svg v-if="!isUpdating" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" /></svg>
              <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              {{ isUpdating ? 'UPDATING...' : 'UPDATE PROFILE' }}
            </button>
          </div>
        </div>
        
      </div>
    </div>
  </div>
</template>