<script setup>
defineProps({
  modelValue: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false }
});
defineEmits(['update:modelValue']);
</script>

<template>
  <div class="switch-wrapper" :class="{ 'opacity-50 pointer-events-none': disabled }">
    <input 
      type="checkbox" role="switch" class="simple-switch" 
      :checked="modelValue"
      @change="$emit('update:modelValue', $event.target.checked)"
      :disabled="disabled"
    />
  </div>
</template>

<style scoped>
.switch-wrapper { display: inline-flex; }
.simple-switch {
  appearance: none; width: 40px; height: 24px; border-radius: 24px;
  position: relative; cursor: pointer; margin: 0; outline: none;
  background-color: #4F4F4F; transition: background-color 0.3s ease;
}
.simple-switch::before {
  content: ""; position: absolute; top: 3px; left: 3px;
  width: 18px; height: 18px; background-color: #E4EDD2;
  border-radius: 50%; transition: transform 0.3s ease;
}
.simple-switch:checked { background-color: #40623F; }
.simple-switch:checked::before { transform: translateX(16px); }
</style>