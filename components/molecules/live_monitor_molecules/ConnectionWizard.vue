<script setup>
import { reactive } from 'vue';
import BaseCard from '~/components/atoms/BaseCard.vue';
import LabeledInput from '~/components/atoms/LabeledInput.vue';
import IconWifi from '~/components/atoms/IconWifi.vue'; // Assumes you created this in previous steps

const connection = reactive({
  ip: '192.168.1.100',
  port: '5760'
});
</script>

<template>
  <BaseCard class="h-auto">
    <div class="flex items-center gap-2 mb-4 border-b border-gray-100 pb-2">
      <div class="w-5 h-5">
         <IconWifi /> 
      </div>
      <h3 class="font-bold text-gray-700 font-poppins text-sm">UAV Connection Wizard</h3>
    </div>

    <div class="space-y-4">
      <LabeledInput 
        label="IP Address" 
        v-model="connection.ip" 
        placeholder="e.g. 192.168.1.100" 
      />
      
      <LabeledInput 
        label="Port" 
        v-model="connection.port" 
        placeholder="e.g. 5760" 
      />

      <button class="w-full bg-[#658D1B] hover:bg-[#557516] text-white py-3 rounded font-bold shadow flex items-center justify-center gap-2 text-sm font-poppins transition mt-6">
        <div class="w-4 h-4 brightness-0 invert">
           <IconWifi />
        </div>
        Connect to UAV
      </button>
    </div>
  </BaseCard>
</template>