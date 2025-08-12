<template>
    <nav class="flex gap-6 ">
        <NavLink v-for="link in links" :key="link.href" :href="link.href" :label="link.label" />
    </nav>
</template>

<script setup lang="ts">
import NavLink from '~/components/atoms/NavLink.vue'

const links = [
    { href: '/', label: '' },
    { href: '/log-in', label: 'Login' },
    { href: '/sign-up', label: 'Sign-up' }
]
</script>
