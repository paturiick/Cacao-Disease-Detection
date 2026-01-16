<script setup>
import { reactive } from 'vue';
import Button from '~/components/atoms/Button.vue';
import Logo from '~/components/atoms/Logo.vue';

// 1. Import the generic input field
import InputField from '~/components/molecules/InputField.vue';
import InputPassword from '~/components/molecules/InputPassword.vue';
import ForgotPassword from '~/components/atoms/ForgotPassword.vue';

const form = reactive({
  username: '',
  password: '',
});

const handleLogin = async () => {
  // Login Logic
  await navigateTo('/mission-planner'); 
};
</script>

<template>
  <div class="bg-white rounded-lg shadow-2xl p-8 w-full max-w-[400px]">
    
    <div class="flex flex-col items-center mb-6">
      <Logo />
      
      <h2 class="text-xl text-[#3E2723] uppercase tracking-wide font-poppins">
        WELCOME TO <span class="font-bold">LUPAD</span>!
      </h2>
      <p class="text-gray-500 text-sm font-inter mt-1">
        Log in to access the system
      </p>
    </div>

    <form @submit.prevent="handleLogin" class="space-y-4">
      
      <InputField 
        v-model="form.username" 
        label="Username" 
        placeholder="Enter username"
      >
        <template #icon>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
          </svg>
        </template>
      </InputField>

      <div>
        <InputPassword 
          v-model="form.password" 
          placeholder="Enter password" 
        />
        
        <ForgotPassword />
      </div>

      <div class="pt-2">
        <Button 
          type="submit" 
          class="w-full bg-[#658D1B] hover:bg-[#557516] text-white font-bold py-3 rounded shadow-sm transition font-poppins text-sm uppercase tracking-wide">
          Log In
        </Button>
      </div>

      <div class="text-center text-xs text-gray-500 mt-4 font-inter">
        Don't have an account?
        <NuxtLink to="/signup" class="font-bold text-[#658D1B] hover:underline ml-1">
          Sign up here
        </NuxtLink>
      </div>

    </form>
  </div>
</template>