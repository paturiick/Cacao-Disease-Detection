<script setup>
defineProps({
  label: { type: String, required: true },
  colorClass: { type: String, required: true }
});

defineEmits(['click']);
</script>

<template>
  <button
    @click="$emit('click')"
    class="h-9 px-3 rounded-lg flex items-center justify-center gap-2 hover:opacity-90 active:scale-95 transition-all shadow-sm text-white text-[11px] font-semibold tracking-wide"
    :class="colorClass"
    :title="label"
  >
    <div class="w-4 h-4 flex items-center justify-center brightness-0 invert shrink-0">
      <slot name="icon"></slot>
    </div>
    <span class="hidden md:inline truncate max-w-[90px]">{{ label }}</span>
  </button>
</template>