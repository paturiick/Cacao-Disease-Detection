<script setup>
import { reactive } from 'vue';
import Button from '~/components/atoms/Button.vue';
import InputField from '~/components/molecules/InputField.vue';
import InputPassword from '~/components/molecules/InputPassword.vue';
import ForgotPassword from '~/components/atoms/ForgotPassword.vue';

const form = reactive({
  username: '',
  password: '',
});

const handleLogin = async () => {
  await navigateTo('/mission-planner');
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
        Welcome to <span class="text-[#95C13E]">LUPAD</span>
      </h2>
      <p class="text-white/55 text-xs mt-1 font-inter">Log in to access the system</p>
    </div>

    <!-- Form body -->
    <div class="px-8 py-7">
      <form @submit.prevent="handleLogin" class="space-y-4">

        <InputField
          v-model="form.username"
          label="Username"
          placeholder="Enter username"
        >
          <template #icon>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
          </template>
        </InputField>

        <div>
          <InputPassword v-model="form.password" placeholder="Enter password" />
          <ForgotPassword />
        </div>

        <div class="pt-2">
          <Button
            type="submit"
            class="w-full bg-[#658D1B] hover:bg-[#557516] text-white font-bold py-3 rounded-lg shadow-sm transition font-poppins text-sm uppercase tracking-wide"
          >
            Log In
          </Button>
        </div>

        <div class="text-center text-xs text-gray-400 font-inter pt-1">
          Don't have an account?
          <NuxtLink to="/signup" class="font-bold text-[#658D1B] hover:underline ml-1">
            Sign up here
          </NuxtLink>
        </div>

      </form>
    </div>
  </div>
</template>