<script setup>
defineProps({ hasMission: Boolean });
</script>

<template>
  <div 
    class="border-l-4 p-4 rounded shadow-sm flex items-start gap-3 transition-colors"
    :class="hasMission ? 'bg-[#E3F2FD] border-blue-500' : 'bg-[#FFF8E1] border-[#FFC107]'"
  >
      <div class="mt-0.5">
        <svg v-if="!hasMission" class="w-5 h-5 text-[#FFC107]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
        <svg v-else class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
      </div>
      <div>
        <h4 class="text-sm font-bold" :class="hasMission ? 'text-blue-800' : 'text-[#795548]'">
          {{ hasMission ? 'Ready to Launch' : 'No mission plan loaded' }}
        </h4>
        <p class="text-xs mt-1" :class="hasMission ? 'text-blue-600' : 'text-[#8D6E63]'">
          {{ hasMission ? 'Review flight parameters and safety protocols.' : 'Please create a mission in Mission Planner before starting.' }}
        </p>
      </div>
  </div>
</template>