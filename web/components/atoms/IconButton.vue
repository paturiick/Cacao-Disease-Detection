<script setup>
defineEmits(['click']);
</script>

<template>
  <button class="icon-btn" @click="$emit('click')">
    <slot></slot>
  </button>
</template>

<style scoped>
.icon-btn {
  background: #ff4d4f; color: white; border: none;
  border-radius: 50%; width: 28px; height: 28px;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
}
.icon-btn:hover { background: #d9363e; }
</style>