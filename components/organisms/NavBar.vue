<template>
    <header class="flex items-center justify-between py-4 px-8 bg-primary shadow">
        <Logo />
        <NavMenu />
    </header>
</template>

<script setup lang="ts">
import Logo from '~/components/atoms/Logo.vue'
import NavMenu from '~/components/molecules/NavMenu.vue'
</script>