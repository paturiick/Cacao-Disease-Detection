<script setup>
defineProps({
  label: { type: String, required: true },
  colorClass: { type: String, required: true }
});
</script>

<template>
  <div
    class="inline-flex items-center gap-2 text-white px-5 py-2 rounded-lg shadow-sm select-none"
    :class="colorClass"
  >
    <div class="w-4 h-4 flex items-center justify-center invert mix-blend-screen shrink-0">
      <slot name="icon"></slot>
    </div>
    <span class="font-semibold text-sm font-poppins tracking-wide">{{ label }}</span>
  </div>
</template>