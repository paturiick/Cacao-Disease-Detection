<script setup lang="ts">
import NavBar from '~/components/organisms/NavBar.vue';
</script>

<template>
  <div class="min-h-screen">
    <NavBar />
    <slot />
    <footer class="bg-primary text-white p-10 text-3xl"></footer>
  </div>
</template>
