<template>
    <NuxtLink :to="href" class="text-background hover:text-gray-400 transition-colors font-inter font-semibold text-lg">
        {{ label }}
    </NuxtLink>
</template>

<script setup lang="ts">
defineProps<{ href: string; label: string }>()
</script>