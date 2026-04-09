<script setup>
import { ref, computed } from 'vue';
import VisualBoard from '~/components/organisms/mission_planner_organism/VisualBoard.vue'; // Adjust path if needed

const props = defineProps({
  steps: { type: Array, default: () => [] },
  trees: { type: Array, default: () => [] }
});

// State to track which tab is active in the left column
const activeLeftTab = ref('commands'); // Options: 'commands' | 'visualization'

// Map the report data so the VisualBoard understands it
const mappedQueue = computed(() => {
  return props.steps.map(step => ({
    id: step.step_id,
    type: step.command,
    val: step.value
  }));
});
</script>

<template>
  <div class="grid grid-cols-2 gap-8 print:grid-cols-2">
    
    <section class="flex flex-col h-[calc(100vh-280px)] min-h-[400px] print:h-[500px]">
      
      <div class="flex items-center gap-6 mb-3 print:hidden">
        <button 
          @click="activeLeftTab = 'commands'" 
          class="text-xs font-bold uppercase tracking-widest pb-1 border-b-2 transition-colors duration-200"
          :class="activeLeftTab === 'commands' ? 'text-slate-700 border-[#658D1B]' : 'text-slate-400 border-transparent hover:text-slate-500'"
        >
          Command Sequence
        </button>
        <button 
          @click="activeLeftTab = 'visualization'" 
          class="text-xs font-bold uppercase tracking-widest pb-1 border-b-2 transition-colors duration-200"
          :class="activeLeftTab === 'visualization' ? 'text-slate-700 border-[#658D1B]' : 'text-slate-400 border-transparent hover:text-slate-500'"
        >
          Visualization
        </button>
      </div>
      
      <h3 class="hidden print:block text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">
        Command Sequence / Map
      </h3>

      <div class="bg-white border border-slate-200 rounded-xl shadow-sm flex-1 flex flex-col overflow-hidden print:shadow-none print:border-slate-300 print:rounded-none">
        
        <div v-show="activeLeftTab === 'commands'" class="flex-1 flex flex-col overflow-hidden">
          <div class="grid grid-cols-4 bg-slate-50 border-b border-slate-200 p-3 text-[10px] font-bold text-slate-500 uppercase tracking-wider shrink-0 print:bg-white print:border-black">
            <div class="col-span-1 text-center">Order</div>
            <div class="col-span-1">Step ID</div>
            <div class="col-span-1">Command</div>
            <div class="col-span-1 text-right">Value</div>
          </div>
          <div class="overflow-y-auto flex-1 p-1 print:overflow-visible custom-scrollbar">
            <div v-if="steps.length === 0" class="text-center p-6 text-slate-400 text-xs font-bold uppercase tracking-wider">No sequence data</div>
            <div v-for="step in steps" :key="step.step_id" class="grid grid-cols-4 p-2.5 border-b border-slate-50 last:border-0 hover:bg-slate-50 text-sm print:border-slate-200 print:py-1">
              <div class="col-span-1 text-center font-bold text-slate-400 print:text-black">{{ step.order }}</div>
              <div class="col-span-1 font-mono text-slate-500 print:text-black">{{ step.step_id }}</div>
              <div class="col-span-1 font-bold text-[#0F172A] uppercase text-xs">{{ step.command }}</div>
              <div class="col-span-1 text-right font-black text-[#658D1B] print:text-black">{{ step.value }}</div>
            </div>
          </div>
        </div>

        <div v-show="activeLeftTab === 'visualization'" class="flex-1 flex flex-col bg-[#F8FAFC]">
          <VisualBoard 
            :queue="mappedQueue" 
            :isRunning="false" 
            :activeIndex="-1"
            mode="report" 
            class="h-full w-full rounded-none border-0"
          />
        </div>

      </div>
    </section>

    <section class="flex flex-col h-[calc(100vh-280px)] min-h-[400px] print:h-[500px]">
      <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3 pb-1 border-b-2 border-transparent">
        Geotagged Database
      </h3>
      <div class="bg-white border border-slate-200 rounded-xl shadow-sm flex-1 flex flex-col overflow-hidden print:shadow-none print:border-slate-300 print:rounded-none">
        <div class="grid grid-cols-4 bg-slate-50 border-b border-slate-200 p-3 text-[10px] font-bold text-slate-500 uppercase tracking-wider shrink-0 print:bg-white print:border-black">
          <div class="col-span-1 text-center">Tree ID</div>
          <div class="col-span-1">Latitude</div>
          <div class="col-span-1">Longitude</div>
          <div class="col-span-1 text-right">Accuracy</div>
        </div>
        <div class="overflow-y-auto flex-1 p-1 print:overflow-visible custom-scrollbar">
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
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.3);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(101, 141, 27, 0.6);
}
</style>