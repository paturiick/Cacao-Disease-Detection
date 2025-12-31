<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';
import Button from '~/components/atoms/Button.vue';
</script>

<template>
  <BaseCard class="h-full flex flex-col justify-between">
    <SectionHeader>
      <template #icon>
        <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
        </svg>
      </template>
      Mission Control
    </SectionHeader>
    
    <div class="flex-1 flex items-center justify-center py-4">
      <Button class="w-full bg-[#AED581] hover:bg-[#9CCC65] text-white py-4 rounded font-bold shadow flex items-center justify-center gap-2 text-lg font-poppins transition">
        <svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        Run Mission Plan
      </Button>
    </div>
  </BaseCard>
</template>