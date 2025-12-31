<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';
import LabeledInput from '~/components/molecules/LabeledInput.vue';
import Button from '~/components/atoms/Button.vue';
import SaveIcon from '~/components/atoms/SaveIcon.vue';
</script>

<template>
  <BaseCard>
    <h3 class="font-bold text-gray-700 mb-4 font-poppins">Mission Commands</h3>
    
    <div class="space-y-4">
      <LabeledInput label="Command Type" />
      
      <div class="flex space-x-2">
         <Button class="hover:scale-105 w-full hover:bg-[#557516] text-white py-4 rounded font-bold shadow flex items-center justify-center gap-2 text-sm font-poppins transition">
           <SaveIcon /> Save Mission
         </Button>

         <Button class="hover:scale-105 px-4 py-2 border border-gray-300 rounded text-sm font-bold text-gray-600 hover:bg-gray-50 bg-white shadow-none transition">
           Cancel
         </Button>
      </div>
    </div>
  </BaseCard>
</template>