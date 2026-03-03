<script setup>
import { reactive, ref } from 'vue';
import Button from '~/components/atoms/Button.vue';
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
  if (errors.confirmPassword) errors.confirmPassword = '';
  if (errors.general) errors.general = '';
};

const handleSignup = async () => {
  clearError();

  if (form.password !== form.confirmPassword) {
    errors.confirmPassword = "Passwords do not match";
    return;
  }

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
  <div class="bg-white rounded-2xl shadow-2xl overflow-hidden w-full max-w-[420px]">

    <!-- Colored header -->
    <div class="bg-[#40623F] px-8 pt-7 pb-6 flex flex-col items-center text-center">
      <div class="mb-3 p-2.5 bg-white/15 rounded-xl">
        <img src="@/assets/icons/Logo.jpg" alt="LUPAD" class="w-16 h-10 object-contain" />
      </div>
      <h2 class="text-white text-xl font-bold font-poppins tracking-wide uppercase">
        Create <span class="text-[#95C13E]">Account</span>
      </h2>
      <p class="text-white/55 text-xs mt-1 font-inter">Sign up to get started</p>
    </div>

    <!-- Form body -->
    <div class="px-8 py-7">

      <div v-if="errors.general" class="bg-red-50 border border-red-200 text-red-700 px-4 py-2.5 rounded-lg mb-4 text-sm font-inter flex items-center gap-2">
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
        {{ errors.general }}
      </div>

      <form @submit.prevent="handleSignup" class="space-y-4">

        <InputField
          v-model="form.fullName"
          label="Full Name"
          placeholder="Enter full name"
        >
          <template #icon>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
          </template>
        </InputField>

        <InputField
          v-model="form.email"
          label="Email Address"
          type="email"
          placeholder="Enter email address"
        >
          <template #icon>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
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
            class="w-full bg-[#658D1B] hover:bg-[#557516] disabled:bg-gray-400 text-white font-bold py-3 rounded-lg shadow-sm transition font-poppins text-sm uppercase tracking-wide"
          >
            {{ isLoading ? 'Creating...' : 'Sign Up' }}
          </Button>
        </div>

        <div class="text-center text-xs text-gray-400 font-inter pt-1">
          Already have an account?
          <NuxtLink to="/login" class="font-bold text-[#658D1B] hover:underline ml-1">
            Log in here
          </NuxtLink>
        </div>

      </form>
    </div>
  </div>
</template>