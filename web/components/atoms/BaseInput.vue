<script setup>
defineProps({
  modelValue: { type: [String, Number], required: true },
  label: { type: String, required: true }
});
defineEmits(['update:modelValue']);
</script>

<template>
  <div class="base-input">
    <label>{{ label }}</label>
    <input 
      type="number" 
      :value="modelValue" 
      @input="$emit('update:modelValue', Number($event.target.value))" 
    />
  </div>
</template>

<style scoped>
.base-input { display: flex; flex-direction: column; }
.base-input label { font-size: 0.75rem; color: #666; margin-bottom: 4px; }
.base-input input { width: 70px; padding: 6px; border: 1px solid #ccc; border-radius: 4px; }
</style>