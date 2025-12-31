<script setup>
defineProps({
  id: String,
  date: String
});
</script>

<template>
  <div class="bg-[#F1F8E9] p-2 rounded border border-gray-100 hover:border-[#AED581] transition cursor-pointer">
    <div class="text-xs text-gray-500 font-bold">{{ id }}</div>
    <div class="text-sm font-medium text-gray-800">{{ date }}</div>
  </div>
</template>