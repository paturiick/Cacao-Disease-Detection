<script setup>
defineProps({
  steps: { type: Array, default: () => [] },
  trees: { type: Array, default: () => [] }
});
</script>

<template>
  <div class="grid grid-cols-2 gap-8 print:grid-cols-2">
    
    <section class="flex flex-col h-[400px] print:h-auto print:block">
      <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Command Sequence</h3>
      <div class="bg-white border border-slate-200 rounded-xl shadow-sm flex-1 flex flex-col overflow-hidden print:shadow-none print:border-slate-300 print:rounded-none">
        <div class="grid grid-cols-4 bg-slate-50 border-b border-slate-200 p-3 text-[10px] font-bold text-slate-500 uppercase tracking-wider shrink-0 print:bg-white print:border-black">
          <div class="col-span-1 text-center">Order</div>
          <div class="col-span-1">Step ID</div>
          <div class="col-span-1">Command</div>
          <div class="col-span-1 text-right">Value</div>
        </div>
        <div class="overflow-y-auto flex-1 p-1 print:overflow-visible">
          <div v-if="steps.length === 0" class="text-center p-6 text-slate-400 text-xs font-bold uppercase tracking-wider">No sequence data</div>
          <div v-for="step in steps" :key="step.step_id" class="grid grid-cols-4 p-2.5 border-b border-slate-50 last:border-0 hover:bg-slate-50 text-sm print:border-slate-200 print:py-1">
            <div class="col-span-1 text-center font-bold text-slate-400 print:text-black">{{ step.order }}</div>
            <div class="col-span-1 font-mono text-slate-500 print:text-black">{{ step.step_id }}</div>
            <div class="col-span-1 font-bold text-[#0F172A] uppercase text-xs">{{ step.command }}</div>
            <div class="col-span-1 text-right font-black text-[#658D1B] print:text-black">{{ step.value }}</div>
          </div>
        </div>
      </div>
    </section>

<<<<<<< HEAD:web/components/molecules/report_molecules/MissionSummaryCard.vue
    <div class="grid grid-cols-2 gap-6">
      <DataLabelValue label="Mission ID" :value="data.id" />
      <DataLabelValue label="Duration" :value="data.duration">
      </DataLabelValue>
      <DataLabelValue label="Start Time" :value="data.startTime" />
      <DataLabelValue label="End Time" :value="data.endTime" />
    </div>
  </BaseCard>
=======
    <section class="flex flex-col h-[400px] print:h-auto print:block">
      <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Geotagged Database</h3>
      <div class="bg-white border border-slate-200 rounded-xl shadow-sm flex-1 flex flex-col overflow-hidden print:shadow-none print:border-slate-300 print:rounded-none">
        <div class="grid grid-cols-4 bg-slate-50 border-b border-slate-200 p-3 text-[10px] font-bold text-slate-500 uppercase tracking-wider shrink-0 print:bg-white print:border-black">
          <div class="col-span-1 text-center">Tree ID</div>
          <div class="col-span-1">Latitude</div>
          <div class="col-span-1">Longitude</div>
          <div class="col-span-1 text-right">Accuracy</div>
        </div>
        <div class="overflow-y-auto flex-1 p-1 print:overflow-visible">
          <div v-if="trees.length === 0" class="text-center p-6 text-slate-400 text-xs font-bold uppercase tracking-wider">No trees mapped</div>
          <div v-for="tree in trees" :key="tree.tree_id" class="grid grid-cols-4 p-2.5 border-b border-slate-50 last:border-0 hover:bg-slate-50 text-sm print:border-slate-200 print:py-1">
            <div class="col-span-1 text-center font-bold text-slate-400 print:text-black">{{ tree.tree_id }}</div>
            <div class="col-span-1 font-mono text-[#0F172A]">{{ tree.lat }}</div>
            <div class="col-span-1 font-mono text-[#0F172A]">{{ tree.lon }}</div>
            <div class="col-span-1 text-right font-black text-[#0F172A]">{{ tree.accuracy }}<span class="text-xs text-slate-400 font-normal ml-0.5">%</span></div>
          </div>
        </div>
      </div>
    </section>

  </div>
>>>>>>> origin/main:components/molecules/report_molecules/MissionSummaryCard.vue
</template>