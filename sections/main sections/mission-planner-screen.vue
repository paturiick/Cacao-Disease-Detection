<template>
  <div class="min-h-screen bg-slate-800 font-inter"> 
    
    <NavBar active-page="mission-planner" />

    <main class="p-4 md:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 max-w-[1600px] mx-auto h-[calc(100vh-80px)]">
      
      <div class="lg:col-span-3 space-y-6 flex flex-col">
        <FlightParametersCard />
        <MissionCommandsCard />
      </div>

      <div class="lg:col-span-3 ">
        <MissionHistoryCard />
      </div>

      <div class="lg:col-span-6 h-min">
         <ControlPanel />
      </div>

    </main>
  </div>
</template>

<script setup>
import NavBar from '~/components/organisms/NavBar.vue';
import FlightParametersCard from '~/components/organisms/mission_planner_organism/FlightParametersCard.vue';
import MissionCommandsCard from '~/components/organisms/mission_planner_organism/MissionCommandsCard.vue';
import MissionHistoryCard from '~/components/organisms/mission_planner_organism/MissionHistoryCard.vue';
import ControlPanel from '~/components/organisms/mission_planner_organism/ControlPanel.vue';
</script>