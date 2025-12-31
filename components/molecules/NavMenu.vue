<template>
    <nav class="flex gap-6 items-center">
        <NavLink 
            v-for="link in links" 
            :key="link.href" 
            :to="link.href" 
            :label="link.label" 
        />
    </nav>
</template>

<script setup lang="ts">
import NavLink from '~/components/atoms/NavLink.vue'

const links = [
    { href: '/login', label: 'Login' },
    { href: '/signup', label: 'Sign-up' }
]
</script>