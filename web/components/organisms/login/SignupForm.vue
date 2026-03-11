<script setup>
import { reactive, ref } from 'vue';
import Button from '~/components/atoms/Button.vue';
import Logo from '~/components/atoms/Logo.vue';

// 1. Import the Generic InputField
import InputField from '~/components/molecules/InputField.vue';

// Keep the password components separate (they have specific logic)
import InputPassword from '~/components/molecules/InputPassword.vue';
import InputConfirmPassword from '~/components/molecules/InputConfirmPassword.vue';

const form = reactive({
  fullName: '',
  email: '',
  password: '',
  confirmPassword: ''
});

const errors = reactive({
  confirmPassword: '',
  general: ''
});

const isLoading = ref(false);

const clearError = () => {
  if (errors.confirmPassword) errors.confirmPassword = '';
  if (errors.general) errors.general = '';
};

const handleSignup = async () => {
  clearError();
  
  if (form.password !== form.confirmPassword) {
    errors.confirmPassword = "Passwords do not match";
    return;
  }
  
  // Example Django Integration
  isLoading.value = true;
  try {
     const { data, error } = await useFetch('http://127.0.0.1:8000/api/signup/', {
      method: 'POST',
      body: {
        fullName: form.fullName,
        email: form.email,
        password: form.password
      }
    });

    if (error.value) {
      errors.general = error.value.data?.error || 'Signup failed.';
    } else {
      await navigateTo('/login'); 
    }
  } catch (err) {
    errors.general = "Connection error.";
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="bg-white rounded-lg shadow-2xl p-8 w-full max-w-[400px]">
    
    <div class="flex flex-col items-center mb-6">
      <Logo />
      <h2 class="text-xl text-[#3E2723] uppercase tracking-wide font-poppins mt-2">
        CREATE <span class="font-bold">ACCOUNT</span>
      </h2>
      <p class="text-gray-500 text-sm font-inter mt-1">
        Sign up to get started
      </p>
    </div>

    <div v-if="errors.general" class="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded relative mb-4 text-sm font-inter">
      {{ errors.general }}
    </div>

    <form @submit.prevent="handleSignup" class="space-y-4">
      
      <InputField 
        v-model="form.fullName" 
        label="Full Name" 
        placeholder="Enter full name"
      >
        <template #icon>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
        </template>
      </InputField>

      <InputField 
        v-model="form.email" 
        label="Email Address" 
        type="email"
        placeholder="Enter email address"
      >
        <template #icon>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
        </template>
      </InputField>

      <InputPassword 
        v-model="form.password" 
        placeholder="Create password"
        @update:model-value="clearError"
      />

      <InputConfirmPassword 
        v-model="form.confirmPassword" 
        :error="errors.confirmPassword"
        @update:model-value="clearError"
      />

      <div class="pt-2">
        <Button 
          type="submit" 
          :disabled="isLoading"
          class="w-full bg-[#658D1B] hover:bg-[#557516] disabled:bg-gray-400 text-white font-bold py-3 rounded shadow-sm transition font-poppins text-sm uppercase tracking-wide">
          {{ isLoading ? 'CREATING...' : 'SIGN UP' }}
        </Button>
      </div>

      <div class="text-center text-xs text-gray-500 mt-4 font-inter">
        Already have an account?
        <NuxtLink to="/login" class="font-bold text-[#658D1B] hover:underline ml-1">
          Log in here
        </NuxtLink>
      </div>

    </form>
  </div>
</template>