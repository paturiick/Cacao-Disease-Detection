<script setup>
import { computed } from 'vue';

const props = defineProps({
  position: { type: Object, required: true },
  options: { type: Array, required: true },
  command: { type: String, required: true },
  value: { type: [String, Number], required: true }
});

const emit = defineEmits(['update:command', 'update:value', 'save', 'cancel']);

const updateCommand = (e) => emit('update:command', e.target.value);
const updateValue = (e) => emit('update:value', e.target.value);

const currentUnit = computed(() => {
  return props.options.find(o => o.value === props.command)?.unit || '';
});
</script>

<template>
  <div 
    class="absolute bg-white/95 backdrop-blur-xl rounded-xl shadow-[0_8px_30px_rgb(0,0,0,0.12)] border border-gray-200/80 p-3 w-[200px] z-30 flex flex-col gap-3 transition-opacity"
    :style="position"
    @click.stop
  >
    <div class="flex items-center gap-2 px-1">
      <span class="relative flex h-2 w-2">
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#658D1B] opacity-75"></span>
        <span class="relative inline-flex rounded-full h-2 w-2 bg-[#658D1B]"></span>
      </span>
      <span class="text-[8px] font-bold text-gray-500 uppercase tracking-widest">Set Action</span>
    </div>

    <div class="relative">
      <select 
        :value="command"
        @change="updateCommand"
        class="w-full appearance-none text-[9px] border border-gray-200 rounded-lg px-3 py-2 bg-gray-50 hover:bg-gray-100/50 focus:bg-white focus:border-[#658D1B] focus:ring-2 focus:ring-[#658D1B]/20 outline-none text-gray-800 font-medium cursor-pointer transition-all"
      >
        <option value="" disabled>Select Action</option>
        <option v-for="opt in options" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>
      <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
        </svg>
      </div>
    </div>

    <div class="flex items-stretch border border-gray-200 rounded-lg bg-gray-50 focus-within:bg-white focus-within:border-[#658D1B] focus-within:ring-2 focus-within:ring-[#658D1B]/20 transition-all overflow-hidden shadow-sm">
      <input 
        type="number" 
        :value="value"
        @input="updateValue"
        placeholder="Enter Value" 
        class="w-full text-[9px] px-3 py-2 outline-none bg-transparent text-gray-800 font-medium placeholder:text-gray-400 placeholder:font-normal"
      />
      <div v-if="currentUnit" class="flex items-center justify-center px-3 bg-gray-100 border-l border-gray-200 text-[9px] font-bold text-gray-500 uppercase min-w-[40px]">
        {{ currentUnit }}
      </div>
    </div>

    <div class="grid grid-cols-2 gap-2 mt-1">
      <button 
        @click="$emit('cancel')" 
        class="flex items-center justify-center gap-1.5 py-2 rounded-lg text-[10px] font-bold text-gray-600 bg-white border border-gray-200 hover:bg-gray-50 hover:text-gray-800 transition-colors shadow-sm"
      >
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        Cancel
      </button>
      
      <button 
        @click="$emit('save')" 
        class="flex items-center justify-center gap-1.5 py-2 rounded-lg text-[10px] font-bold text-white bg-[#658D1B] hover:bg-[#527415] transition-colors shadow-sm"
      >
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"></path></svg>
        Save
      </button>
    </div>
  </div>
</template>