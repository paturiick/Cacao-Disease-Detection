<script setup>
import BaseBadge from '~/components/atoms/BaseBadge.vue';

defineProps({
  user: { type: Object, required: true }
});
</script>

<template>
  <div class="bg-white/95 backdrop-blur-sm rounded-2xl shadow-sm border border-gray-100 p-8 flex flex-col md:flex-row items-center gap-8 relative overflow-hidden">
    <div class="absolute inset-0 bg-gradient-to-r from-transparent via-transparent to-gray-50/50 pointer-events-none"></div>
    
    <div class="w-28 h-28 rounded-full border-4 border-white shadow-md overflow-hidden shrink-0 bg-gray-50 flex items-center justify-center relative z-10">
      <img v-if="user.avatar" :src="user.avatar" alt="Profile" class="w-full h-full object-cover" />
      <svg v-else class="w-12 h-12 text-gray-300" fill="currentColor" viewBox="0 0 24 24"><path d="M24 20.993V24H0v-2.996A14.977 14.977 0 0112.004 15c4.904 0 9.26 2.354 11.996 5.993zM16.002 8.999a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
    </div>

    <div class="flex-1 text-center md:text-left relative z-10">
      <h2 class="text-3xl font-black text-slate-800 tracking-tight mb-1">{{ user.fullName }}</h2>
      <p class="text-sm font-medium text-gray-500 mb-4">{{ user.callsign }} • {{ user.organization }}</p>
      <div class="flex flex-wrap justify-center md:justify-start gap-2.5">
        <BaseBadge>{{ user.role }}</BaseBadge>
        <BaseBadge v-if="user.isActive" class="!bg-blue-50 !text-blue-600 !border !border-blue-100">Cleared for Flight</BaseBadge>
      </div>
    </div>
  </div>
</template>