<script setup>
import { reactive, ref } from 'vue';
import Button from '~/components/atoms/Button.vue';
import Logo from '~/components/atoms/Logo.vue';
import InputField from '~/components/molecules/InputField.vue';
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
  errors.confirmPassword = '';
  errors.general = '';
};

const validateForm = () => {
  // 1. Check for empty fields
  if (!form.fullName || !form.email || !form.password || !form.confirmPassword) {
    errors.general = "All fields are required.";
    return false;
  }

  // 2. Validate email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(form.email)) {
    errors.general = "Please enter a valid email address.";
    return false;
  }

  // 3. Validate password length
  if (form.password.length < 8) {
    errors.general = "Password must be at least 8 characters long.";
    return false;
  }

  // 4. Validate password match
  if (form.password !== form.confirmPassword) {
    errors.confirmPassword = "Passwords do not match.";
    return false;
  }

  return true;
};

const handleSignup = async () => {
  clearError();
  
  // Run client-side validation first
  if (!validateForm()) return;
  
  isLoading.value = true;
  
  try {
    const response = await fetch('http://localhost:8000/api/auth/register/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        full_name: form.fullName,
        email: form.email,
        password: form.password,
        confirm_password: form.confirmPassword
      })
    });

    const data = await response.json();

    if (response.ok) {
      // Success! Send them to the login screen
      await navigateTo('/login'); 
    } else {
      // Handle specific Django REST Framework validation errors
      if (data.email) {
        errors.general = `Email Error: ${data.email[0]}`;
      } else if (data.password) {
        errors.general = `Password Error: ${data.password[0]}`;
      } else if (data.full_name) {
        errors.general = `Name Error: ${data.full_name[0]}`;
      } else if (data.non_field_errors) {
        errors.general = data.non_field_errors[0];
      } else {
        // Fallback for any other unexpected error keys
        const errorKey = Object.keys(data)[0];
        errors.general = `${errorKey}: ${data[errorKey][0]}`;
      }
    }
  } catch (err) {
    errors.general = "Connection error. Please check your internet or ensure the server is running.";
    console.error('Signup error:', err);
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

    <div v-if="errors.general" class="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded relative mb-4 text-sm font-inter leading-tight">
      {{ errors.general }}
    </div>

    <form @submit.prevent="handleSignup" class="space-y-4">
      
      <InputField 
        v-model="form.fullName" 
        label="Full Name" 
        placeholder="Enter full name"
        @update:model-value="clearError"
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
        @update:model-value="clearError"
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