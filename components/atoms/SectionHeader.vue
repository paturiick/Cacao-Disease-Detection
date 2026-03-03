<template>
  <h3 class="font-semibold text-gray-800 mb-4 flex items-center gap-2.5 font-poppins text-sm">
    <span class="flex items-center justify-center w-6 h-6 rounded-md bg-[#40623F]/10 text-[#40623F] shrink-0">
      <slot name="icon"></slot>
    </span>
    <slot />
  </h3>
</template>