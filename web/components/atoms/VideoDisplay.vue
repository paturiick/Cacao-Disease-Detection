<script setup>
defineProps({
  src: { type: String, default: '' },
  poster: { type: String, default: '' },
  autoplay: { type: Boolean, default: true },
  muted: { type: Boolean, default: true }
});
</script>

<template>
  <video
    class="w-full h-full object-cover"
    :src="src"
    :poster="poster"
    :autoplay="autoplay"
    :muted="muted"
    playsinline
    controls
  >
    Your browser does not support the video tag.
  </video>
</template>