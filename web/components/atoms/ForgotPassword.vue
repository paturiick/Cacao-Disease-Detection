<template>
  <div class="flex justify-end mt-1 animate-fade-in">
    <NuxtLink 
      to="/forgot-password" 
      class="text-xs text-[#658D1B] hover:underline font-medium transition-opacity hover:opacity-80"
    >
      Forgot password?
    </NuxtLink>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.5s ease-out forwards;
  opacity: 0;
  animation-delay: 200ms;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>