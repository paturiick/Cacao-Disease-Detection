<template>
    <NuxtLink :to="href" class="text-background hover:underline font-poppins font-semibold text-lg">
        {{ label }}
    </NuxtLink>
</template>

<script setup lang="ts">
defineProps<{ href: string; label: string }>()
</script>