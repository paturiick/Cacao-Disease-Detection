<script setup lang="ts">
import NavBar from '~/components/organisms/NavBar.vue';
</script>

<template>
  <div class="min-h-screen">
    <NavBar />
    <slot />
  </div>
</template>
