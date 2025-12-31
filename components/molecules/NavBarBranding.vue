<script setup>
import Logo from '~/components/atoms/Logo.vue';

defineProps({
  title: { type: String, default: 'LUPAD' },
  subtitle: { type: String, default: 'Welcome to LUPAD!' }
});

defineEmits(['click']);
</script>

<template>
  <button 
    @click="$emit('click')" 
    class="flex items-center space-x-4 hover:opacity-70 transition-opacity duration-200 text-left focus:outline-none"
    title="Return to Login"
  >
    <div class="w-16 h-12 flex items-center justify-center">
      <Logo />
    </div>
    <div class="flex flex-col">
      <h1 class="text-[#3E2723] font-bold text-xl leading-none tracking-wide font-poppins">{{ title }}</h1>
      <span class="text-gray-500 text-sm font-inter">{{ subtitle }}</span>
    </div>
  </button>
</template>