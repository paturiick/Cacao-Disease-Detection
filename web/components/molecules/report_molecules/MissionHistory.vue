<script setup>
import { ref } from 'vue';

const props = defineProps({
  missions: { type: Array, required: true },
  selectedId: { type: [Number, String], default: null }
});

const emit = defineEmits(['select', 'delete', 'bulkDelete']);

// State for multi-select mode
const isSelectionMode = ref(false);
const selectedForDeletion = ref([]);

const toggleSelectionMode = () => {
  isSelectionMode.value = !isSelectionMode.value;
  // Clear selections if we cancel out of selection mode
  if (!isSelectionMode.value) {
    selectedForDeletion.value = [];
  }
};

const toggleSelection = (id) => {
  const index = selectedForDeletion.value.indexOf(id);
  if (index > -1) {
    selectedForDeletion.value.splice(index, 1);
  } else {
    selectedForDeletion.value.push(id);
  }
};

const handleItemClick = (id) => {
  if (isSelectionMode.value) {
    toggleSelection(id);
  } else {
    emit('select', id);
  }
};

const executeBulkDelete = () => {
  if (selectedForDeletion.value.length === 0) return;
  emit('bulkDelete', [...selectedForDeletion.value]);
  
  // Reset mode after emitting
  isSelectionMode.value = false;
  selectedForDeletion.value = [];
};
</script>

<template>
  <div class="w-80 bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col overflow-hidden shrink-0 h-full print:hidden">
    
    <div class="p-4 border-b border-slate-100 bg-[#0F172A] flex items-center justify-between">
      <h2 class="font-poppins font-bold text-white tracking-wide uppercase text-sm flex items-center gap-2">
        <svg class="w-4 h-4 text-[#658D1B]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
        Mission Database
      </h2>
      
      <button 
        v-if="missions.length > 0"
        @click="toggleSelectionMode" 
        class="text-[10px] font-bold uppercase tracking-wider transition-colors"
        :class="isSelectionMode ? 'text-slate-300 hover:text-white' : 'text-[#658D1B] hover:text-white'"
      >
        {{ isSelectionMode ? 'Cancel' : 'Select' }}
      </button>
    </div>
    
    <div class="flex-1 overflow-y-auto p-3 space-y-2 custom-scrollbar">
      <div v-if="missions.length === 0" class="text-center p-4 text-slate-400 text-xs font-bold uppercase tracking-wider">
        No missions recorded
      </div>

      <div 
        v-for="mission in missions" 
        :key="mission.id"
        @click="handleItemClick(mission.id)"
        class="p-3 border rounded-lg cursor-pointer transition-all duration-200 relative overflow-hidden flex items-center"
        :class="[
          selectedId === mission.id && !isSelectionMode ? 'bg-[#658D1B]/10 border-[#658D1B]/40 shadow-inner' : 'bg-white border-slate-100 hover:border-slate-300 hover:bg-slate-50',
          selectedForDeletion.includes(mission.id) ? 'border-red-300 bg-red-50/50' : ''
        ]"
      >
        <div v-if="selectedId === mission.id && !isSelectionMode" class="absolute left-0 top-0 bottom-0 w-1 bg-[#658D1B]"></div>
        
        <div v-if="isSelectionMode" class="shrink-0 mr-3">
          <input 
            type="checkbox" 
            :checked="selectedForDeletion.includes(mission.id)"
            class="w-4 h-4 text-red-600 rounded border-slate-300 focus:ring-red-500 accent-red-500 pointer-events-none"
          />
        </div>

        <div class="flex-1 pr-8 truncate">
          <p class="text-sm font-bold text-[#0F172A] truncate">{{ mission.name }}</p>
          <p class="text-[10px] font-semibold text-slate-500 mt-1">ID: #{{ mission.id }} • {{ mission.date }}</p>
        </div>

        <button 
          v-if="!isSelectionMode"
          @click.stop="$emit('delete', mission.id)"
          class="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-md transition-colors"
          title="Delete Mission"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>

    <div v-if="isSelectionMode" class="p-3 border-t border-slate-100 bg-slate-50 shrink-0">
      <button 
        @click="executeBulkDelete"
        :disabled="selectedForDeletion.length === 0"
        class="w-full py-2 bg-red-600 hover:bg-red-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white text-xs font-bold uppercase tracking-wider rounded-lg transition-colors flex justify-center items-center gap-2 shadow-sm"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
        Delete Selected ({{ selectedForDeletion.length }})
      </button>
    </div>

  </div>
</template>