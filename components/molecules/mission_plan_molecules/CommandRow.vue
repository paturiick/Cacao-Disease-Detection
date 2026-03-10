<script setup>
import BaseInput from '~/components/atoms/BaseInput.vue';
import IconButton from '~/components/atoms/IconButton.vue';

const props = defineProps({
  command: { type: Object, required: true },
  index: { type: Number, required: true }
});
const emit = defineEmits(['update-command', 'remove-command']);

const updateField = (field, value) => {
  emit('update-command', props.index, { ...props.command, [field]: value });
};
</script>

<template>
  <div class="command-row">
    <span class="step-number">{{ index + 1 }}</span>
    <BaseInput 
      label="Dist (m)" 
      :modelValue="command.distance" 
      @update:modelValue="updateField('distance', $event)" 
    />
    <BaseInput 
      label="Deg (°)" 
      :modelValue="command.degrees" 
      @update:modelValue="updateField('degrees', $event)" 
    />
    <div class="action-wrap">
      <IconButton @click="$emit('remove-command', index)">✕</IconButton>
    </div>
  </div>
</template>

<style scoped>
.command-row {
  display: flex; gap: 12px; align-items: center;
  padding: 12px 0; border-bottom: 1px solid #eee;
}
.step-number { font-weight: bold; color: #40623F; width: 20px; }
.action-wrap { margin-top: 18px; }
</style>