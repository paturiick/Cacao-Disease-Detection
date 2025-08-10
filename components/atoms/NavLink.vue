<template>
    <NuxtLink :to="href" class="text-background hover:text-gray-400 transition-colors font-poppins text-lg">
        {{ label }}
    </NuxtLink>
</template>

<script setup lang="ts">
defineProps<{ href: string; label: string }>()
</script>