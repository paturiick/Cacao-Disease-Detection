<script setup>
defineProps({
  missions: { type: Array, required: true },
  selectedId: { type: [Number, String], default: null }
});

defineEmits(['select']);
</script>

<template>
  <div class="w-80 bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col overflow-hidden shrink-0 h-full print:hidden">
    <div class="p-4 border-b border-slate-100 bg-[#0F172A]">
      <h2 class="font-poppins font-bold text-white tracking-wide uppercase text-sm flex items-center gap-2">
        <svg class="w-4 h-4 text-[#658D1B]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
        Mission Database
      </h2>
    </div>
    
    <div class="flex-1 overflow-y-auto p-3 space-y-2">
      <div v-if="missions.length === 0" class="text-center p-4 text-slate-400 text-xs font-bold uppercase tracking-wider">
        No missions recorded
      </div>

      <div 
        v-for="mission in missions" 
        :key="mission.id"
        @click="$emit('select', mission.id)"
        class="p-3 border rounded-lg cursor-pointer transition-all duration-200 relative overflow-hidden"
        :class="selectedId === mission.id ? 'bg-[#658D1B]/10 border-[#658D1B]/40 shadow-inner' : 'bg-white border-slate-100 hover:border-slate-300 hover:bg-slate-50'"
      >
        <div v-if="selectedId === mission.id" class="absolute left-0 top-0 bottom-0 w-1 bg-[#658D1B]"></div>
        <p class="text-sm font-bold text-[#0F172A]">{{ mission.name }}</p>
        <p class="text-[10px] font-semibold text-slate-500 mt-1">ID: #{{ mission.id }} • {{ mission.date }}</p>
      </div>
    </div>
  </div>
</template>