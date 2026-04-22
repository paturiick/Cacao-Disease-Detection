<script setup lang="ts">
import { ref } from 'vue';
import Button from '~/components/atoms/Button.vue';

const isExiting = ref(false);

// Define the navigation action
const handleGetStarted = () => {
  // Trigger the exit animation
  isExiting.value = true;
  
  // Wait for the animation to complete before navigating
  setTimeout(() => {
    navigateTo('/login');
  }, 400); // 600ms matches our CSS transition duration
}
</script>

<template>
  <div class="h-screen overflow-hidden flex items-center justify-center bg-background font-poppins relative selection:bg-slate-200">
    
    <div class="absolute inset-0 z-0 pointer-events-none transition-opacity duration-700 ease-in-out"
         :class="isExiting ? 'opacity-0' : 'opacity-[0.04]'">
      <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="dot-pattern" width="32" height="32" patternUnits="userSpaceOnUse">
            <circle cx="2" cy="2" r="1.5" fill="currentColor" class="text-primary" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#dot-pattern)" />
      </svg>
    </div>

    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-[#658D1B] rounded-full blur-[150px] pointer-events-none z-0 animate-pulse-slow transition-opacity duration-700 ease-in-out"
         :class="isExiting ? 'opacity-0' : 'opacity-[0.06]'"></div>

    <div 
      class="relative z-10 text-center max-w-2xl px-6 py-12 flex flex-col items-center transition-all duration-700 ease-in-out"
      :class="isExiting ? 'opacity-0 scale-95 -translate-y-10 blur-sm pointer-events-none' : 'opacity-100'"
    >
      
      <div class="animate-fade-in-up delay-100 mb-10 group">
        <div class="animate-float">
          <img 
            src="~/assets/icons/Logo.png" 
            alt="Cacao Disease Detection Logo" 
            class="h-36 md:h-40 w-auto object-contain drop-shadow-2xl transition-all duration-500 group-hover:drop-shadow-[0_20px_25px_rgba(101,141,27,0.25)] group-hover:scale-105"
          />
        </div>
      </div>
      
      <h1 class="animate-fade-in-up delay-200 text-4xl md:text-5xl lg:text-6xl font-black text-primary mb-6 tracking-tight leading-[1.15]">
        Welcome to LUPAD<br class="hidden md:block"/>
      </h1>
      
      <p class="animate-fade-in-up delay-300 text-lg md:text-xl text-gray-600 mb-12 max-w-xl mx-auto leading-relaxed">
        Localized UAV-based Black Pod Rot (Phytophthora Palmivora) Automated Disease Detection in Cacao Pods
      </p>
      
      <div class="animate-fade-in-up delay-400">
        <Button 
          @click="handleGetStarted"
          class="group relative overflow-hidden inline-flex items-center gap-3 px-10 py-4 text-lg font-bold transition-all duration-300 active:scale-95 shadow-lg hover:shadow-xl hover:shadow-[#658D1B]/20 rounded-2xl"
        >
          <div class="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/20 to-transparent group-hover:animate-sweep"></div>
          
          <span class="relative z-10">Get Started</span>
          <svg class="relative z-10 w-5 h-5 transition-transform duration-300 group-hover:translate-x-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </Button>
      </div>

    </div>

  </div>
</template>

<style scoped>
/* 1. Staggered Entry Animations */
.animate-fade-in-up {
  opacity: 0;
  animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.delay-100 { animation-delay: 100ms; }
.delay-200 { animation-delay: 200ms; }
.delay-300 { animation-delay: 300ms; }
.delay-400 { animation-delay: 400ms; }

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(24px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 2. Continuous Float for the Drone Logo */
.animate-float {
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-12px); }
  100% { transform: translateY(0px); }
}

/* 3. Slow Breathing/Pulse for the Background Glow */
.animate-pulse-slow {
  animation: pulseGlow 4s ease-in-out infinite alternate;
}

@keyframes pulseGlow {
  0% { transform: scale(0.95) translate(-50%, -50%); transform-origin: top left; }
  100% { transform: scale(1.05) translate(-50%, -50%); transform-origin: top left; }
}

/* 4. Sweep effect inside the button on hover */
@keyframes sweep {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(200%); }
}
.animate-sweep {
  animation: sweep 1.5s ease-in-out infinite;
}
</style>