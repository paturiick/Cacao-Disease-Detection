<template>
    <NuxtLink :to="href"
        class="text-background hover:underline font-poppins font-semibold text-lg 
        hover:scale-105 transition-all duration-300 ease-in-out transform">
        {{ label }}
    </NuxtLink>
</template>

<script setup lang="ts">
defineProps<{ href: string; label: string }>()
</script>