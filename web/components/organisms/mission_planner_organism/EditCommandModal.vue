<script setup>
import { reactive, computed, watch } from 'vue';

const props = defineProps({
  isOpen: Boolean,
  commandOptions: Array,
  editIndex: Number,
  initialData: Object
});

const emit = defineEmits(['close', 'save']);

const editErrorMessage = ref('');
const editForm = reactive({ type: '', val: '' });
const editGoParams = reactive({ x: 0, y: 0, z: 0 });

// Watch for when the modal opens to populate the data
watch(() => props.isOpen, (newVal) => {
  if (newVal && props.initialData) {
    editErrorMessage.value = '';
    editForm.type = props.initialData.type;
    
    if (props.initialData.type === 'go') {
      const parts = String(props.initialData.val).split(' ');
      editGoParams.x = parseInt(parts[0]) || 0;
      editGoParams.y = parseInt(parts[1]) || 0;
      editGoParams.z = parseInt(parts[2]) || 0;
    } else {
      editForm.val = props.initialData.val;
    }
  }
});

const currentEditCmdDetails = computed(() => {
  if (!props.commandOptions) return { unit: '' };
  return props.commandOptions.find(c => c.value === editForm.type) || { unit: '' };
});

const saveEdit = () => {
  editErrorMessage.value = '';

  if (!editForm.type) {
    editErrorMessage.value = "Please select a command type.";
    return;
  }

  let finalVal = editForm.val;

  if (editForm.type === 'go') {
    const { x, y, z } = editGoParams;
    if (x < -500 || x > 500 || y < -500 || y > 500 || z < -500 || z > 500) {
      editErrorMessage.value = "Safety Error: Coordinates must be between -500 and 500.";
      return;
    }
    if (x > -20 && x < 20 && y > -20 && y < 20 && z > -20 && z < 20) {
      editErrorMessage.value = "Safety Error: X, Y, and Z cannot all be between -20 and 20 at the same time.";
      return;
    }
    finalVal = `${x} ${y} ${z}`;
  } else if (!editForm.val) {
    editErrorMessage.value = "Please enter a valid duration or value.";
    return;
  }

  emit('save', { index: props.editIndex, type: editForm.type, val: finalVal });
};
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
    <div class="bg-white rounded-xl shadow-2xl w-full max-w-sm overflow-hidden flex flex-col" @click.stop>
      <div class="bg-gray-50 px-5 py-4 border-b border-gray-100 flex justify-between items-center">
        <h3 class="font-bold text-gray-800 flex items-center gap-2">
          <svg class="w-4 h-4 text-[#658D1B]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
          Edit Command Step {{ editIndex + 1 }}
        </h3>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button>
      </div>

      <div class="p-5 space-y-4">
        <div class="flex flex-col">
          <label class="text-gray-600 text-xs font-bold mb-1.5 uppercase tracking-wide">Command Type</label>
          <select v-model="editForm.type" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm bg-white focus:border-[#658D1B] focus:ring-1 outline-none">
            <option v-for="opt in commandOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>

        <div v-if="editForm.type === 'go'" class="grid grid-cols-2 gap-3 p-3 bg-gray-50 border border-gray-200 rounded-md">
          <div class="flex flex-col"><label class="text-[10px] text-gray-500 font-bold uppercase mb-1">X (-500 to 500)</label><input type="number" v-model="editGoParams.x" class="border border-gray-300 rounded px-2 py-1.5 text-sm outline-none focus:border-[#658D1B] focus:ring-1" /></div>
          <div class="flex flex-col"><label class="text-[10px] text-gray-500 font-bold uppercase mb-1">Y (-500 to 500)</label><input type="number" v-model="editGoParams.y" class="border border-gray-300 rounded px-2 py-1.5 text-sm outline-none focus:border-[#658D1B] focus:ring-1" /></div>
          <div class="flex flex-col col-span-2"><label class="text-[10px] text-gray-500 font-bold uppercase mb-1">Z (-500 to 500)</label><input type="number" v-model="editGoParams.z" class="border border-gray-300 rounded px-2 py-1.5 text-sm outline-none focus:border-[#658D1B] focus:ring-1" /></div>
        </div>

        <div v-else class="flex flex-col">
          <label class="text-gray-600 text-xs font-bold mb-1.5 uppercase tracking-wide">Value ({{ currentEditCmdDetails.unit }})</label>
          <div class="flex relative">
            <input type="number" v-model="editForm.val" min="1" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm outline-none focus:border-[#658D1B] focus:ring-1" />
            <div class="absolute right-0 top-0 bottom-0 px-3 flex items-center bg-gray-100 border-l border-gray-300 rounded-r-md text-gray-500 text-xs font-bold">{{ currentEditCmdDetails.unit }}</div>
          </div>
        </div>

        <div v-if="editErrorMessage" class="text-red-600 bg-red-50 p-2 rounded border border-red-200 text-xs font-medium flex items-center gap-2">
          <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
          {{ editErrorMessage }}
        </div>
      </div>

      <div class="bg-gray-50 px-5 py-3 border-t border-gray-100 flex justify-end gap-2">
        <button @click="$emit('close')" class="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-md transition-colors">Cancel</button>
        <button @click="saveEdit" class="px-4 py-2 text-sm font-bold text-white bg-[#658D1B] hover:bg-[#557516] rounded-md transition-colors shadow-sm">Save Changes</button>
      </div>
    </div>
  </div>
</template>