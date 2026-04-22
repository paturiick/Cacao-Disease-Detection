<script setup>
import LoginForm from '~/components/organisms/login/LoginForm.vue';

definePageMeta({
  layout: 'empty'
})
</script>

<template>
  <div class="min-h-screen w-full flex items-center justify-center relative overflow-hidden bg-slate-900 font-inter">
    
    <div 
      class="absolute inset-0 z-0 bg-cover bg-center opacity-40 transition-transform duration-[30s] ease-in-out hover:scale-110"
      style="background-image: url('https://images.unsplash.com/photo-1542601906990-24d4c16c3b6d?q=80&w=2670&auto=format&fit=crop');"
    ></div>

    <div class="absolute inset-0 z-0 bg-slate-900/60 backdrop-blur-[8px]"></div>

    <div class="absolute top-[-10%] left-[-5%] w-[500px] h-[500px] bg-[#658D1B]/30 rounded-full mix-blend-screen filter blur-[100px] opacity-60 z-0"></div>
    <div class="absolute bottom-[-10%] right-[-5%] w-[400px] h-[400px] bg-emerald-600/20 rounded-full mix-blend-screen filter blur-[100px] opacity-60 z-0"></div>

    <div class="z-10 w-full max-w-[420px] px-4 py-8 transform transition-all duration-700 ease-out translate-y-0 opacity-100 flex justify-center">
      <LoginForm />
    </div>

    <div class="absolute bottom-6 text-center z-10 w-full">
      <p class="text-slate-400 text-2xl tracking-widest uppercase font-semibold">LUPAD</p>
    </div>

  </div>
</template>