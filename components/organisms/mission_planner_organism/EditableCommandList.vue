<script setup>
import CommandRow from '~/components/molecules/mission_plan_molecules/CommandRow.vue';

const props = defineProps({ commands: { type: Array, required: true } });
const emit = defineEmits(['update-commands']);

const handleUpdate = (index, updatedCommand) => {
  const newCommands = [...props.commands];
  newCommands[index] = updatedCommand;
  emit('update-commands', newCommands);
};

const handleRemove = (index) => {
  const newCommands = [...props.commands];
  newCommands.splice(index, 1);
  emit('update-commands', newCommands);
};
</script>

<template>
  <div class="space-y-3">
    <div v-for="(item, idx) in queue" :key="item.id" 
      class="relative group"
      @dblclick="$emit('edit', idx)"
    >
      <MissionListItem 
        :index="idx" 
        v-bind="item" 
        :isActive="activeIndex === idx + 1" 
        :isRunning="isRunning" 
        @remove="$emit('remove', idx)" 
      />
    </div>
  </div>
</template>

<style scoped>
.command-list-card {
  background: white; padding: 24px; border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05); width: 320px;
}
.empty { color: #888; font-size: 0.9rem; }
.list-scroll { max-height: 400px; overflow-y: auto; }
</style>