<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';
import LabeledInput from '~/components/molecules/LabeledInput.vue';
import Button from '~/components/atoms/Button.vue';
</script>

<template>
  <BaseCard>
    <h3 class="font-bold text-gray-700 mb-4 font-poppins">Mission Commands</h3>
    
    <div class="space-y-4">
      <LabeledInput label="Command Type" />
      
      <div class="flex space-x-2">
         <Button class="flex-1 bg-[#7CB342] hover:bg-[#689F38] text-white py-2 rounded text-sm font-bold flex items-center justify-center gap-2">
            Save Mission
         </Button>

         <Button class="px-4 py-2 border border-gray-300 rounded text-sm font-bold text-gray-600 hover:bg-gray-50 bg-white shadow-none">
            Cancel
         </Button>
      </div>
    </div>
  </BaseCard>
</template>