  <script setup>
  import { ref, reactive, computed } from 'vue';
  import BaseCard from '~/components/atoms/BaseCard.vue';
  import SectionHeader from '~/components/atoms/SectionHeader.vue';

  import MissionListEmpty from '~/components/molecules/mission_plan_molecules/MissionListEmpty.vue';
  import MissionListItem from '~/components/molecules/mission_plan_molecules/MissionListItem.vue';
  import MissionStatusBadge from '~/components/molecules/mission_plan_molecules/MissionStatusBadge.vue';

  import VisualBoard from '~/components/organisms/mission_planner_organism/VisualBoard.vue';

  const props = defineProps({
    queue: { type: Array, default: () => [] },
    isRunning: { type: Boolean, default: false },
    activeIndex: { type: Number, default: -1 },
    flightParams: { type: Object, default: () => ({}) },
    commandOptions: { type: Array, default: () => [] },
    mode: { type: String, default: 'plan' },
    allowDelete: { type: Boolean, default: true},
    allowEdit: { type: Boolean, default: false }
  });

  const emit = defineEmits(['remove', 'reorder', 'edit', 'update:mode', 'send-rc', 'save-to-plan', 'duplicate']);

  const draggedIndex = ref(null);
  const dragOverIndex = ref(null);

  const handleDragStart = (index, event) => { if (props.isRunning) return; draggedIndex.value = index; event.dataTransfer.effectAllowed = 'move'; event.dataTransfer.setData('text/plain', index); };
  const handleDragOver = (index, event) => { event.preventDefault(); if (props.isRunning || draggedIndex.value === null) return; dragOverIndex.value = index; };
  const handleDrop = (index, event) => { event.preventDefault(); if (props.isRunning || draggedIndex.value === null) return; if (draggedIndex.value !== index) emit('reorder', { from: draggedIndex.value, to: index }); draggedIndex.value = null; dragOverIndex.value = null; };
  const handleDragEnd = () => { draggedIndex.value = null; dragOverIndex.value = null; };

  const showEditModal = ref(false);
  const editErrorMessage = ref('');
  const editIndex = ref(-1);

  const editForm = reactive({ type: '', val: '', speed: 30 });
  const editGoParams = reactive({ x: 0, y: 0, z: 0 });
  const editRcParams = reactive({ a: 0, b: 0, c: 0, d: 0, duration: 1 });

  const currentEditCmdDetails = computed(() => props.commandOptions?.find(c => c.value === editForm.type) || { unit: '' });

  const openEditModal = (idx) => {
    if (props.isRunning) return;
    editErrorMessage.value = '';
    const item = props.queue[idx];
    editIndex.value = idx;
    editForm.type = item.type;
    
    editForm.speed = item.speed || props.flightParams.speed || 30;
    
    if (item.type === 'go') { 
      const parts = String(item.val).split(' '); 
      editGoParams.x = parseInt(parts[0]) || 0; 
      editGoParams.y = parseInt(parts[1]) || 0; 
      editGoParams.z = parseInt(parts[2]) || 0; 
      if (parts[3]) editForm.speed = parseInt(parts[3]);
    } 
    else if (item.type === 'rc') {
      const parts = String(item.val).split(' ');
      editRcParams.a = parseInt(parts[0]) || 0;
      editRcParams.b = parseInt(parts[1]) || 0;
      editRcParams.c = parseInt(parts[2]) || 0;
      editRcParams.d = parseInt(parts[3]) || 0;
      editRcParams.duration = parseInt(parts[4]) || 1; 
    }
    else { 
      editForm.val = item.val; 
    }
    showEditModal.value = true;
  };

  const saveEdit = () => {
    editErrorMessage.value = '';
    if (!editForm.type) { editErrorMessage.value = "Please select a command type."; return; }
    
    if (editForm.speed < 10 || editForm.speed > 100) {
      editErrorMessage.value = "Safety Error: Speed must be between 10 and 100 cm/s.";
      return;
    }

    let finalVal = editForm.val;
    
    if (editForm.type === 'go') {
      const { x, y, z } = editGoParams;
      if (x < -500 || x > 500 || y < -500 || y > 500 || z < -500 || z > 500) { editErrorMessage.value = "Safety Error: Coordinates must be between -500 and 500."; return; }
      if (x > -20 && x < 20 && y > -20 && y < 20 && z > -20 && z < 20) { editErrorMessage.value = "Safety Error: X, Y, and Z cannot all be between -20 and 20 at the same time."; return; }
      finalVal = `${x} ${y} ${z} ${editForm.speed}`;
    } 
    else if (editForm.type === 'rc') {
      const { a, b, c, d, duration } = editRcParams;
      if ([a, b, c, d].some(val => val < -100 || val > 100)) { editErrorMessage.value = "Safety Error: All RC forces must be between -100 and 100."; return; }
      if (duration <= 0) { editErrorMessage.value = "Safety Error: Duration must be at least 1 second."; return; }
      finalVal = `${a} ${b} ${c} ${d} ${duration}`;
    }
    else if (!editForm.val) { editErrorMessage.value = "Please enter a valid duration or value."; return; }
    
    emit('edit', { 
      index: editIndex.value, 
      type: editForm.type, 
      val: finalVal, 
      speed: editForm.speed 
    });
    showEditModal.value = false;
  };

  const getFormattedValue = (item) => {
    if (item.type === 'rc') {
      const p = String(item.val).split(' ');
      return `Roll: ${p[0]} | Pitch: ${p[1]} | Thr: ${p[2]} | Yaw: ${p[3]} — ${p[4]}s`;
    }
    if (item.type === 'go') {
      const p = String(item.val).split(' ');
      return `X: ${p[0]}, Y: ${p[1]}, Z: ${p[2]}`;
    }
    return item.val;
  };

  const getFormattedUnit = (item) => {
    if (item.type === 'rc' || item.type === 'go') return ''; 
    return item.unit;
  };
  </script>

  <template>
    <BaseCard class="h-full flex flex-col bg-white/95 backdrop-blur-sm relative overflow-hidden">
      
      <div class="flex justify-between items-center mb-4 border-b border-gray-100 pb-4 shrink-0 px-2 pt-2">
        <div class="flex items-center gap-4">
          <span class="text-sm font-bold text-slate-800 uppercase tracking-widest px-2">Mission History</span>
        </div>
        
        <div class="flex gap-3 items-center">
          <MissionStatusBadge :isActive="props.isRunning" />
        </div>
      </div>

      <div class="flex-1 flex flex-col lg:flex-row min-h-0 overflow-hidden border border-gray-100 rounded-lg">
        <div class="flex flex-col h-full bg-white z-10 shadow-[4px_0_15px_-3px_rgba(0,0,0,0.05)] relative transition-all duration-300 w-full lg:w-1/2 border-r border-gray-100">
          <div class="flex-1 overflow-y-auto p-4 scrollbar-thin scrollbar-thumb-gray-300">
            
            <MissionListItem :isConfig="true" label="Initial Configuration" :isActive="props.activeIndex === 0" :isRunning="props.isRunning" class="shrink-0 mb-4">
              <template #details>
                <div class="mt-2 flex">
                  <div class="bg-white rounded border border-gray-200 px-4 py-1.5 text-center shadow-sm w-fit min-w-[70px]">
                    <span class="block text-slate-400 font-bold text-[10px] uppercase tracking-wider mb-0.5">SPD</span>
                    <span class="text-sm font-medium text-slate-800">{{ flightParams.speed || 0 }}cm/s</span>
                  </div>
                </div>
              </template>
            </MissionListItem>

            <div v-if="props.queue.length === 0" class="flex-1 flex items-center justify-center py-16 opacity-70">
              <MissionListEmpty />
            </div>

            <div v-else class="space-y-3 pb-8">
              <div 
                v-for="(item, idx) in props.queue" 
                :key="item.id" 
                :draggable="!props.isRunning" 
                @dragstart="handleDragStart(idx, $event)" 
                @dragover="handleDragOver(idx, $event)" 
                @dragenter.prevent 
                @drop="handleDrop(idx, $event)" 
                @dragend="handleDragEnd" 
                class="transition-all duration-200 ease-in-out relative group" 
                :class="[
                  {'cursor-grab active:cursor-grabbing': !props.isRunning, 'opacity-40 scale-[0.98]': draggedIndex === idx},
                  !props.allowDelete ? 'hide-delete-btn' : ''
                ]"
              >
                
                <div v-if="!props.isRunning && props.allowEdit" class="absolute right-12 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 z-20 flex gap-0.5 bg-white p-1 rounded-lg shadow-md border border-gray-200 transition-opacity">
                  <button v-if="props.allowEdit" @click.stop="openEditModal(idx)" class="text-[#658D1B] p-1.5 rounded hover:bg-gray-50 transition-colors" title="Edit Step">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                  </button>

                  <div v-if="props.allowEdit" class="w-px bg-gray-200 my-1"></div>
                  <button @click.stop="$emit('duplicate', idx)" class="text-blue-500 p-1.5 rounded hover:bg-blue-50 transition-colors" title="Duplicate Step">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" stroke-width="2.5"></rect>
                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></path>
                    </svg>
                  </button>
                </div>
                
                <MissionListItem 
                  :index="idx" 
                  :label="item.label" 
                  :value="getFormattedValue(item)" 
                  :unit="getFormattedUnit(item)" 
                  :icon="item.icon" 
                  :isActive="props.activeIndex === idx + 1" 
                  :isRunning="props.isRunning"
                  :allowDelete="props.allowDelete"
                  @remove="props.allowDelete ? $emit('remove', idx) : null"
                >
                  <template #footer v-if="item.speed">
                    <div class="text-[9px] font-bold text-gray-400 uppercase mt-1 flex items-center gap-1">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                      Custom Speed: {{ item.speed }} cm/s
                    </div>
                  </template>
                </MissionListItem>
              </div>
            </div>
          </div>
        </div>  

        <VisualBoard class="w-full lg:w-1/2" :queue="props.queue" :active-index="props.activeIndex" :is-running="props.isRunning" :mode="props.mode" />
      </div>

      <div v-if="showEditModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-sm overflow-hidden flex flex-col" @click.stop>
          <div class="bg-gray-50 px-5 py-4 border-b border-gray-100 flex justify-between items-center">
            <h3 class="font-bold text-gray-800 flex items-center gap-2">
              <svg class="w-4 h-4 text-[#658D1B]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
              Edit Command Step {{ editIndex + 1 }}
            </h3>
            <button @click="showEditModal = false" class="text-gray-400 hover:text-gray-600"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button>
          </div>
          
          <div class="p-5 space-y-4 max-h-[70vh] overflow-y-auto custom-scrollbar">
            <div class="flex flex-col">
              <label class="text-gray-600 text-xs font-bold mb-1.5 uppercase tracking-wide">Command Type</label>
              <select v-model="editForm.type" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm bg-white outline-none focus:ring-1 focus:ring-[#658D1B]">
                <option v-for="opt in props.commandOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
            </div>
            
            <div v-if="editForm.type !== 'rc'" class="flex flex-col p-3 bg-blue-50/50 border border-blue-100 rounded-md">
              <div class="flex justify-between items-center mb-1">
                <label class="text-[#2563EB] text-[10px] font-black uppercase tracking-widest">Command Speed</label>
                <span class="text-xs font-mono font-bold text-blue-600">{{ editForm.speed }} cm/s</span>
              </div>
              <input type="range" v-model.number="editForm.speed" min="10" max="100" step="1" class="w-full h-1.5 bg-blue-200 rounded-lg appearance-none cursor-pointer accent-[#2563EB]" />
              <div class="flex justify-between text-[8px] text-blue-400 font-bold mt-1">
                <span>MIN (10)</span>
                <span>MAX (100)</span>
              </div>
            </div>

            <div v-if="editForm.type === 'go'" class="grid grid-cols-2 gap-3 p-3 bg-gray-50 border border-gray-200 rounded-md">
              <div class="flex flex-col"><label class="text-[10px] text-gray-500 font-bold uppercase mb-1">X (-500 to 500)</label><input type="number" v-model="editGoParams.x" class="border border-gray-300 rounded px-2 py-1.5 text-sm focus:ring-1 focus:ring-[#658D1B]" /></div>
              <div class="flex flex-col"><label class="text-[10px] text-gray-500 font-bold uppercase mb-1">Y (-500 to 500)</label><input type="number" v-model="editGoParams.y" class="border border-gray-300 rounded px-2 py-1.5 text-sm focus:ring-1 focus:ring-[#658D1B]" /></div>
              <div class="flex flex-col col-span-2"><label class="text-[10px] text-gray-500 font-bold uppercase mb-1">Z (-500 to 500)</label><input type="number" v-model="editGoParams.z" class="border border-gray-300 rounded px-2 py-1.5 text-sm focus:ring-1 focus:ring-[#658D1B]" /></div>
            </div>
            
            <div v-else-if="editForm.type === 'rc'" class="grid grid-cols-2 gap-3 p-3 bg-gray-50 border border-gray-200 rounded-md">
              <div class="col-span-2 text-xs font-bold text-gray-500 uppercase mb-1">RC Override Forces</div>
              <div class="flex flex-col"><label class="text-[10px] font-bold text-gray-600 mb-1">ROLL (a)</label><input type="number" v-model="editRcParams.a" class="border border-gray-300 rounded px-3 py-2 text-sm focus:ring-1 focus:ring-[#658D1B]" /></div>
              <div class="flex flex-col"><label class="text-[10px] font-bold text-gray-600 mb-1">PITCH (b)</label><input type="number" v-model="editRcParams.b" class="border border-gray-300 rounded px-3 py-2 text-sm focus:ring-1 focus:ring-[#658D1B]" /></div>
              <div class="flex flex-col"><label class="text-[10px] font-bold text-gray-600 mb-1">THROTTLE (c)</label><input type="number" v-model="editRcParams.c" class="border border-gray-300 rounded px-3 py-2 text-sm focus:ring-1 focus:ring-[#658D1B]" /></div>
              <div class="flex flex-col"><label class="text-[10px] font-bold text-gray-600 mb-1">YAW (d)</label><input type="number" v-model="editRcParams.d" class="border border-gray-300 rounded px-3 py-2 text-sm focus:ring-1 focus:ring-[#658D1B]" /></div>
              <div class="flex flex-col col-span-2 mt-1"><label class="text-[10px] font-bold text-[#658D1B] mb-1">DURATION (Seconds)</label><input type="number" v-model="editRcParams.duration" class="border border-gray-300 rounded px-3 py-2 text-sm focus:ring-1 focus:ring-[#658D1B]" /></div>
            </div>

            <div v-else class="flex flex-col">
              <label class="text-gray-600 text-xs font-bold mb-1.5 uppercase tracking-wide">Value ({{ currentEditCmdDetails.unit }})</label>
              <div class="flex relative">
                <input type="number" v-model="editForm.val" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-1 focus:ring-[#658D1B]" />
                <div class="absolute right-0 top-0 bottom-0 px-3 flex items-center bg-gray-100 border-l border-gray-300 rounded-r-md text-gray-500 text-xs font-bold">{{ currentEditCmdDetails.unit }}</div>
              </div>
            </div>

            <div v-if="editErrorMessage" class="text-red-600 bg-red-50 p-2 rounded border border-red-200 text-xs font-medium">{{ editErrorMessage }}</div>
          </div>
          
          <div class="bg-gray-50 px-5 py-3 border-t border-gray-100 flex justify-end gap-2">
            <button @click="showEditModal = false" class="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-md">Cancel</button>
            <button @click="saveEdit" class="px-4 py-2 text-sm font-bold text-white bg-[#658D1B] hover:bg-[#557516] rounded-md shadow-sm">Save Changes</button>
          </div>
        </div>
      </div>

    </BaseCard>
  </template>

  <style scoped>
  /* Deep fallback to safely hide the 'X' button inside MissionListItem 
    when allowDelete is explicitly set to false. 
  */
  .hide-delete-btn :deep(button[title="Remove"]),
  .hide-delete-btn :deep(button[title="Edit Step"]),
  .hide-delete-btn :deep(button[title*="Delete"]),
  .hide-delete-btn :deep(button:has(svg path[d*="M6 18L18 6"])),
  .hide-delete-btn :deep(button:has(svg path[d*="6 18L18 6M6 6l12 12"])),
  .hide-delete-btn :deep(button.text-gray-300:hover\:text-red-500),
  .hide-delete-btn :deep(button.text-slate-300:hover\:text-red-500) {
    display: none !important;
    pointer-events: none !important;
  }

  /* Fallback to hide common nested flex icon wrappers typically used for standard X close buttons */
  .hide-delete-btn :deep(.flex > button:last-child > svg:only-child) {
    display: none !important;
  }
  </style>