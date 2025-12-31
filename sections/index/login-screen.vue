<template>
  <div class="min-h-screen w-full flex items-center justify-center bg-gray-900 relative">
    
    <div 
      class="absolute inset-0 z-0 bg-cover bg-center"
      style="background-image: url('https://images.unsplash.com/photo-1542601906990-24d4c16c3b6d?q=80&w=2670&auto=format&fit=crop'); opacity: 0.6;"
    ></div>

    <div class="absolute inset-0 z-0 bg-black/40"></div>

    <div class="z-10 w-full max-w-md px-4">
      <LoginForm />
    </div>

  </div>
</template>

<script setup>
import LoginForm from '~/components/organisms/login/LoginForm.vue';

definePageMeta({
  layout: 'empty'
})
</script>