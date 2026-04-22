<script setup>
import { reactive, ref, onMounted } from 'vue';
import Button from '~/components/atoms/Button.vue';
import Logo from '~/components/atoms/Logo.vue';
import InputField from '~/components/molecules/InputField.vue';
import InputPassword from '~/components/molecules/InputPassword.vue';
import ForgotPassword from '~/components/atoms/ForgotPassword.vue';

const form = reactive({
  email: '',
  password: '',
});

const errorMessage = ref('');
const isLoading = ref(false);

// --- NEW: Saved Emails State ---
const savedEmails = ref([]);
const isEmailFocused = ref(false);

// Load saved emails when the page opens
onMounted(() => {
  const storedEmails = localStorage.getItem('lupad_saved_emails');
  if (storedEmails) {
    savedEmails.value = JSON.parse(storedEmails);
  }
});

// Handle selecting an email from the dropdown
const selectEmail = (email) => {
  form.email = email;
  isEmailFocused.value = false;
  clearError();
};

const removeSavedEmail = (emailToRemove) => {
  savedEmails.value = savedEmails.value.filter(e => e !== emailToRemove);
  localStorage.setItem('lupad_saved_emails', JSON.stringify(savedEmails.value));
};
// -------------------------------

const validateForm = () => {
  if (!form.email || !form.password) {
    errorMessage.value = 'Please enter your email and password.';
    return false;
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(form.email)) {
    errorMessage.value = 'Please enter a valid email address.';
    return false;
  }
  
  return true;
};

const handleLogin = async () => {
  errorMessage.value = '';
  
  if (!validateForm()) return;

  isLoading.value = true;

  try {
    const response = await fetch('http://localhost:8000/api/auth/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: form.email,
        password: form.password
      })
    });

    const data = await response.json();

    if (response.ok) {
      // --- NEW: Save the successful email ---
      let emails = [...savedEmails.value];
      // If email isn't already in the list, add it to the top
      if (!emails.includes(form.email)) {
        emails.unshift(form.email);
        // Keep only the 5 most recent emails to prevent the list from getting too long
        if (emails.length > 5) emails.pop(); 
        localStorage.setItem('lupad_saved_emails', JSON.stringify(emails));
      }
      // ------------------------------------

      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      
      await navigateTo('/mission-planner'); 
    } else {
      if (response.status === 401) {
        errorMessage.value = 'Incorrect email or password. Please try again.';
      } else {
        errorMessage.value = data.detail || 'An error occurred during login. Please verify your credentials.';
      }
    }
  } catch (error) {
    errorMessage.value = 'Connection error. Please check your internet or ensure the server is running.';
    console.error('Login error:', error);
  } finally {
    isLoading.value = false;
  }
};

const clearError = () => {
  errorMessage.value = '';
};

// Delay hiding the dropdown slightly so clicks on the suggestions register first
const handleEmailBlur = () => {
  setTimeout(() => {
    isEmailFocused.value = false;
  }, 150);
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

    <div v-if="errorMessage" class="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded relative mb-4 text-sm font-inter">
      {{ errorMessage }}
    </div>

    <form @submit.prevent="handleLogin" class="space-y-4">
      
      <div class="relative">
        <div @focusin="isEmailFocused = true" @focusout="handleEmailBlur">
          <InputField 
            v-model="form.email" 
            label="Email Address" 
            placeholder="Enter email"
            autocomplete="off"
            @update:model-value="clearError"
          >
            <template #icon>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
              </svg>
            </template>
          </InputField>
        </div>

        <transition
          enter-active-class="transition duration-100 ease-out"
          enter-from-class="transform scale-95 opacity-0"
          enter-to-class="transform scale-100 opacity-100"
          leave-active-class="transition duration-75 ease-in"
          leave-from-class="transform scale-100 opacity-100"
          leave-to-class="transform scale-95 opacity-0"
        >
          <div 
            v-if="isEmailFocused && savedEmails.length > 0" 
            class="absolute z-50 w-full mt-1 bg-white border border-gray-100 rounded-md shadow-lg overflow-hidden font-inter"
          >
            <div class="px-3 py-2 bg-gray-50 border-b border-gray-100 text-[10px] font-bold text-gray-400 uppercase tracking-wider">
              Recent Accounts
            </div>
            <ul class="max-h-48 overflow-y-auto">
              <li 
                v-for="email in savedEmails" 
                :key="email"
                @mousedown.prevent="selectEmail(email)"
                class="px-4 py-3 text-sm text-gray-700 hover:bg-[#658D1B] hover:text-white cursor-pointer transition-colors flex items-center justify-between group"
              >
                <div class="flex items-center gap-2">
                  <svg class="w-4 h-4 opacity-50 group-hover:opacity-100 group-hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                  <span>{{ email }}</span>
                </div>
                
                <button 
                  @mousedown.stop.prevent="removeSavedEmail(email)" 
                  class="text-gray-400 hover:text-white opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-full hover:bg-black/20"
                  title="Remove from history"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
              </li>
            </ul>
          </div>
        </transition>
      </div>

      <div>
        <InputPassword 
          v-model="form.password" 
          placeholder="Enter password" 
          @update:model-value="clearError"
        />
        
        <ForgotPassword />
      </div>

      <div class="pt-2">
        <Button 
          type="submit" 
          :disabled="isLoading"
          class="w-full bg-[#658D1B] hover:bg-[#557516] disabled:bg-gray-400 text-white font-bold py-3 rounded shadow-sm transition font-poppins text-sm uppercase tracking-wide">
          {{ isLoading ? 'LOGGING IN...' : 'LOG IN' }}
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