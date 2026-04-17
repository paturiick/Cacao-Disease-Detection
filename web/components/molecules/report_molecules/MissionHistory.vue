<script setup>
import { ref } from 'vue';

const props = defineProps({
  missions: { type: Array, required: true },
  selectedId: { type: [Number, String], default: null }
});

const emit = defineEmits(['select', 'delete', 'bulkDelete']);

// --- STATE: SELECTION MODE ---
const isSelectionMode = ref(false);
const selectedForDeletion = ref([]);

// --- STATE: MODAL ---
const isModalOpen = ref(false);
const deleteMode = ref(''); // 'single' or 'bulk'
const targetMissionId = ref(null);

const toggleSelectionMode = () => {
  isSelectionMode.value = !isSelectionMode.value;
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

// --- MODAL ACTIONS ---
const confirmSingleDelete = (id) => {
  targetMissionId.value = id;
  deleteMode.value = 'single';
  isModalOpen.value = true;
};

const confirmBulkDelete = () => {
  if (selectedForDeletion.value.length === 0) return;
  deleteMode.value = 'bulk';
  isModalOpen.value = true;
};

const cancelDelete = () => {
  isModalOpen.value = false;
  targetMissionId.value = null;
  deleteMode.value = '';
};

const executeDelete = () => {
  if (deleteMode.value === 'single') {
    emit('delete', targetMissionId.value);
  } else if (deleteMode.value === 'bulk') {
    emit('bulkDelete', [...selectedForDeletion.value]);
    isSelectionMode.value = false;
    selectedForDeletion.value = [];
  }
  
  cancelDelete();
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
          @click.stop="confirmSingleDelete(mission.id)"
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
        @click="confirmBulkDelete"
        :disabled="selectedForDeletion.length === 0"
        class="w-full py-2 bg-red-600 hover:bg-red-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white text-xs font-bold uppercase tracking-wider rounded-lg transition-colors flex justify-center items-center gap-2 shadow-sm"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
        Delete Selected ({{ selectedForDeletion.length }})
      </button>
    </div>

    <div v-if="isModalOpen" class="fixed inset-0 z-[9999] flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
      <div class="bg-white rounded-xl shadow-2xl max-w-sm w-full overflow-hidden transform transition-all">
        <div class="p-5 border-b border-slate-100 flex items-center gap-3 text-red-600 bg-red-50/50">
          <div class="p-2 bg-red-100 rounded-full">
            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 class="font-bold text-lg text-slate-800">Confirm Deletion</h3>
        </div>
        
        <div class="p-5">
          <p class="text-sm text-slate-600 leading-relaxed">
            <span v-if="deleteMode === 'single'">Are you sure you want to delete this mission record?</span>
            <span v-else>Are you sure you want to delete the <strong>{{ selectedForDeletion.length }}</strong> selected mission records?</span>
            <br/>This action cannot be undone.
          </p>
        </div>
        
        <div class="p-4 bg-slate-50 flex justify-end gap-3 border-t border-slate-100">
          <button 
            @click="cancelDelete" 
            class="px-5 py-2.5 text-sm font-bold text-slate-500 hover:bg-slate-200 hover:text-slate-800 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button 
            @click="executeDelete" 
            class="px-5 py-2.5 bg-red-600 hover:bg-red-700 text-white text-sm font-bold rounded-lg shadow-sm transition-colors flex items-center gap-2"
          >
            Yes, Delete
          </button>
        </div>
      </div>
    </div>

  </div>
</template>