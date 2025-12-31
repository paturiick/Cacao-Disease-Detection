<script setup lang="ts">
import Button from '~/components/atoms/Button.vue';

// Define the navigation action
const handleGetStarted = () => {
    navigateTo('/login');
}
</script>

<template>
    <div class="h-screen overflow-hidden flex items-center justify-center bg-background font-poppins">
        <div class="text-center max-w-md px-4">
            <h1 class="text-4xl font-semibold text-primary mb-4">
                Welcome to Cacao Disease Detection
            </h1>
            <p class="text-gray-600 mb-6">
                Helping you identify and manage cacao diseases with AI precision.
            </p>
            
            <Button @click="handleGetStarted">
                Get Started
            </Button>
        </div>
    </div>
</template>