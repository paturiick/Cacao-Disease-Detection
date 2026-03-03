<script setup lang="ts">
const handleGetStarted = () => {
  navigateTo('/login');
}
</script>

<template>
  <div class="h-screen overflow-hidden flex flex-col items-center justify-center relative font-poppins">

    <!-- Background image -->
    <div
      class="absolute inset-0 bg-cover bg-center z-0"
      style="background-image: url('https://images.unsplash.com/photo-1542601906990-24d4c16c3b6d?q=80&w=2670&auto=format&fit=crop');"
    ></div>

    <!-- Layered gradient overlay -->
    <div class="absolute inset-0 bg-gradient-to-b from-black/75 via-black/55 to-black/80 z-10"></div>

    <!-- Hero content -->
    <div class="relative z-20 flex flex-col items-center justify-center text-center px-6 max-w-2xl w-full">

      <!-- Logo badge -->
      <div class="mb-7 inline-flex items-center gap-3 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full px-5 py-2 shadow-lg">
        <img src="@/assets/icons/Logo.jpg" alt="LUPAD" class="w-10 h-6 object-contain" />
        <span class="text-white/75 text-sm font-medium tracking-widest uppercase">LUPAD System</span>
      </div>

      <!-- Main title -->
      <h1 class="text-5xl md:text-6xl font-bold text-white mb-3 leading-tight tracking-tight">
        Cacao Disease
      </h1>
      <h2 class="text-5xl md:text-6xl font-bold mb-6 leading-tight tracking-tight text-[#95C13E]">
        Detection
      </h2>

      <!-- Subtitle -->
      <p class="text-base md:text-lg text-white/60 mb-8 max-w-lg font-light leading-relaxed">
        AI-powered autonomous drone surveillance for early disease identification, flight planning, and real-time geotagged reporting.
      </p>

      <!-- Feature chips -->
      <div class="flex flex-wrap gap-2.5 justify-center mb-10">
        <span class="flex items-center gap-1.5 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full px-4 py-1.5 text-white/70 text-xs font-medium">
          <svg class="w-3.5 h-3.5 text-[#95C13E]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/></svg>
          Autonomous Flight
        </span>
        <span class="flex items-center gap-1.5 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full px-4 py-1.5 text-white/70 text-xs font-medium">
          <svg class="w-3.5 h-3.5 text-[#95C13E]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
          AI Detection
        </span>
        <span class="flex items-center gap-1.5 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full px-4 py-1.5 text-white/70 text-xs font-medium">
          <svg class="w-3.5 h-3.5 text-[#95C13E]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/></svg>
          Geotagged Reports
        </span>
      </div>

      <!-- CTA button -->
      <button
        @click="handleGetStarted"
        class="bg-[#658D1B] hover:bg-[#557516] text-white font-bold py-4 px-14 rounded-xl shadow-2xl text-sm uppercase tracking-widest transition-all duration-200 hover:scale-[1.03] focus:outline-none focus:ring-2 focus:ring-[#658D1B]/50"
      >
        Get Started
      </button>
    </div>

    <!-- Bottom branding -->
    <p class="absolute bottom-5 z-20 text-white/25 text-xs tracking-widest uppercase">
      Powered by YOLOv8 &middot; Built for Cacao Farmers
    </p>
  </div>
</template>