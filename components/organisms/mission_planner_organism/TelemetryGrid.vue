<script setup>
import TelemetryItem from '~/components/molecules/mission_plan_molecules/TelemetryItem.vue';
</script>

<template>
  <div class="grid grid-cols-2 md:grid-cols-3 gap-3 md:gap-6 shrink-0">
    <TelemetryItem label="GPS Signal" value="---" />
    <TelemetryItem label="Speed" value="---" />
    <TelemetryItem label="Altitude" value="---" />
    <TelemetryItem label="Battery" value="---" />
    <TelemetryItem label="Roll" value="---" />
    <TelemetryItem label="Pitch" value="---" />
  </div>
</template>