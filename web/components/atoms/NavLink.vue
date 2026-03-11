<template>
  <NuxtLink 
    :to="to" 
    class="text-white font-poppins font-semibold text-lg hover:text-green-200 transition-colors"
  >
        {{ label }}
    </NuxtLink>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  to: string
}>()
</script>