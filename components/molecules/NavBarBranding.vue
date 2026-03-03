<script setup>
import { computed } from 'vue';

const props = defineProps({
  title: { type: String, default: 'LUPAD' },
  connectionStatus: { type: String, default: 'No Signal' }
});

defineEmits(['click']);

const isConnected = computed(() => {
  const status = props.connectionStatus?.toLowerCase() || '';
  return ['strong', 'connected', 'streaming', 'online'].includes(status);
});
</script>

<template>
  <div class="flex items-center gap-3 group shrink-0">
    <button
      @click="$emit('click')"
      class="flex items-center justify-center group-hover:opacity-75 transition-opacity focus:outline-none"
    >
      <img src="@/assets/icons/Logo.jpg" alt="LUPAD" class="w-11 h-7 object-contain" />
    </button>

    <div class="flex flex-col text-left">
      <button @click="$emit('click')" class="text-left group-hover:opacity-75 transition-opacity focus:outline-none leading-none">
        <span class="text-[#3E2723] font-bold text-lg tracking-wider font-poppins">{{ title }}</span>
      </button>
      <div class="flex items-center gap-1.5 mt-0.5">
        <span
          class="w-1.5 h-1.5 rounded-full transition-colors duration-300"
          :class="isConnected ? 'bg-green-500' : 'bg-red-400'"
        ></span>
        <span
          class="text-[10px] font-bold font-inter tracking-wide uppercase transition-colors duration-300"
          :class="isConnected ? 'text-green-600' : 'text-red-500'"
        >{{ connectionStatus }}</span>
      </div>
    </div>
  </div>
</template>