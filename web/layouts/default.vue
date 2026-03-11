<script setup lang="ts">
import bgImage from '~/assets/images/background.jpg';

const bgStyle = {
  backgroundImage: `url(${bgImage})`,
  backgroundSize: 'cover',
  backgroundPosition: 'center',
  backgroundRepeat: 'no-repeat',
};
</script>

<template>
  <div class="min-h-screen w-full relative">
    
    <div class="fixed inset-0 z-0" :style="bgStyle">
      <div class="absolute inset-0 bg-black/50 backdrop-blur-[2px]"></div>
    </div>

    <div class="relative z-10">
      <slot />
    </div>

  </div>
</template>