<script setup>
import { ref } from 'vue';

const props = defineProps({
  presets: Array,
  activePresetId: Number
});

const emit = defineEmits(['select', 'create', 'edit', 'delete']);

// --- CUSTOM MODAL STATE ---
const showDeleteModal = ref(false);
const presetToDelete = ref(null);

const promptDelete = (preset) => {
  presetToDelete.value = preset;
  showDeleteModal.value = true;
};

const confirmDelete = () => {
  if (presetToDelete.value) {
    emit('delete', presetToDelete.value);
  }
  showDeleteModal.value = false;
  presetToDelete.value = null;
};

const cancelDelete = () => {
  showDeleteModal.value = false;
  presetToDelete.value = null;
};
</script>

<template>
  <div class="w-full flex flex-col gap-4">
    
    <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-5">
      <h2 class="text-lg font-bold text-slate-800 flex items-center gap-2">
        <svg class="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
        Mission Presets
      </h2>
      <p class="text-xs text-slate-500 mt-1">Select a saved flight plan to load it into the Mission History.</p>
    </div>

    <div class="flex flex-col gap-3">
      <div 
        v-for="preset in presets" 
        :key="preset.id"
        @click="$emit('select', preset)"
        :class="[
          'bg-white rounded-2xl p-4 border transition-all cursor-pointer group',
          activePresetId === preset.id 
            ? 'border-[#486732] shadow-md ring-1 ring-[#486732]' 
            : 'border-slate-100 shadow-sm hover:border-slate-300 hover:shadow'
        ]"
      >
        <div class="flex justify-between items-start">
          <div>
            <h3 class="font-bold text-slate-800">{{ preset.name }}</h3>
            <div class="flex items-center gap-3 mt-1.5 text-xs text-slate-500 font-medium">
              <span class="flex items-center gap-1">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                SPD: {{ preset.speed }}cm/s
              </span>
              <span class="flex items-center gap-1">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path></svg>
                {{ preset.steps.length }} Steps
              </span>
            </div>
          </div>
          
          <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button 
              @click.stop="$emit('edit', preset)" 
              class="text-slate-300 hover:text-[#486732] p-1 transition-colors"
              title="Edit Preset"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
            </button>

            <button 
              @click.stop="promptDelete(preset)" 
              class="text-slate-300 hover:text-red-500 p-1 transition-colors"
              title="Delete Preset"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
            </button>
          </div>

        </div>
      </div>
    </div>

    <button 
      @click="$emit('create')"
      class="mt-2 w-full py-3.5 font-bold text-white bg-[#486732] rounded-xl hover:bg-[#3f5a2b] transition-colors shadow-lg shadow-[#486732]/20 flex items-center justify-center gap-2"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
      Create Preset
    </button>

    <Teleport to="body">
      <div v-if="showDeleteModal" class="fixed inset-0 z-[9999] flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4" @click.stop>
        <div class="bg-white rounded-xl shadow-2xl max-w-sm w-full overflow-hidden transform transition-all" @click.stop>
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
              Are you sure you want to delete the preset <strong class="text-slate-800">"{{ presetToDelete?.name }}"</strong>?
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
              @click="confirmDelete" 
              class="px-5 py-2.5 bg-red-600 hover:bg-red-700 text-white text-sm font-bold rounded-lg shadow-sm transition-colors"
            >
              Yes, Delete
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>