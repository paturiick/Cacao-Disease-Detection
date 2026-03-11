<script setup>
const props = defineProps({
  mission: { type: Object, required: true }
});

const formatTime = (seconds) => {
  if (!seconds) return '0m 0s';
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}m ${s}s`;
};
</script>

<template>
  <section>
    <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Flight Metrics</h3>
    <div class="grid grid-cols-5 gap-3 print:grid-cols-5">
      
<<<<<<< HEAD:web/components/molecules/report_molecules/FlightStatisticsCard.vue
      <StatTile label="Altitude" :value="stats.altitude" color-class="bg-green-50 text-green-900" />
      <StatTile label="Speed" :value="stats.speed" color-class="bg-purple-50 text-purple-900" />
      <StatTile label="Waypoints Completed" :value="stats.waypoints" color-class="bg-orange-50 text-orange-900" />
      <StatTile label="Photos" :value="stats.photos" color-class="bg-pink-50 text-pink-900" />
      <StatTile label="Battery" :value="stats.battery" color-class="bg-yellow-50 text-yellow-900" />
=======
      <div class="bg-white border border-slate-200 rounded-lg p-4 flex flex-col items-center justify-center text-center shadow-sm print:shadow-none">
        <span class="text-[9px] font-bold text-slate-400 uppercase mb-1">Flight Mode</span>
        <span class="text-sm font-black text-[#658D1B] uppercase tracking-wide">{{ mission.mode }}</span>
      </div>
      
      <div class="bg-white border border-slate-200 rounded-lg p-4 flex flex-col items-center justify-center text-center shadow-sm print:shadow-none">
        <span class="text-[9px] font-bold text-slate-400 uppercase mb-1">Air Time</span>
        <span class="text-base font-black text-[#0F172A]">{{ formatTime(mission.telemetry?.flight_time) }}</span>
      </div>
      
      <div class="bg-white border border-slate-200 rounded-lg p-4 flex flex-col items-center justify-center text-center shadow-sm print:shadow-none">
        <span class="text-[9px] font-bold text-slate-400 uppercase mb-1">Max Altitude</span>
        <span class="text-base font-black text-[#0F172A]">{{ mission.telemetry?.max_altitude || 0 }} <span class="text-[10px] text-slate-400 font-normal">m</span></span>
      </div>
      
      <div class="bg-white border border-slate-200 rounded-lg p-4 flex flex-col items-center justify-center text-center shadow-sm print:shadow-none">
        <span class="text-[9px] font-bold text-slate-400 uppercase mb-1">Target Speed</span>
        <span class="text-base font-black text-[#0F172A]">{{ mission.speed || 0 }} <span class="text-[10px] text-slate-400 font-normal">cm/s</span></span>
      </div>
      
      <div class="bg-white border border-slate-200 rounded-lg p-4 flex flex-col items-center justify-center text-center shadow-sm print:shadow-none">
        <span class="text-[9px] font-bold text-slate-400 uppercase mb-1">End Battery</span>
        <span class="text-base font-black" :class="(mission.telemetry?.battery_end <= 30 && mission.telemetry?.battery_end > 0) ? 'text-[#C60C0C]' : 'text-[#0F172A]'">
          {{ mission.telemetry?.battery_end || 0 }}<span class="text-[10px] font-normal">%</span>
        </span>
      </div>

>>>>>>> origin/main:components/molecules/report_molecules/FlightStatisticsCard.vue
    </div>
  </section>
</template>