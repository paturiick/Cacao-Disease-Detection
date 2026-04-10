<script setup>
/**
 * DroneModel Atom
 * Renders the top-down view of the UAV with animations, specifically modeled after the Robomaster Tello TT.
 * Designed to be used inside an SVG coordinate system.
 */
const props = defineProps({
  isRunning: { type: Boolean, default: false },
  scale: { type: Number, default: 7 } 
});

// Tello specific colors
const TelloMainRed = '#DC2626'; // Main body, arms, propellers
const TelloGray = '#94A3B8'; // Motor bases, camera housing
const TelloLogoWhite = '#FFFFFF'; // Logo and text
const TelloRidgeRed = '#991B1B'; // Darker red for ridges
</script>

<template>
  <g class="transition-transform duration-[1200ms] ease-in-out pointer-events-none">
    
    <template v-if="isRunning">
      <circle cx="-13" cy="-13" r="8.5" fill="#CBD5E1" opacity="0.3" class="animate-spin origin-[-13px_-13px]" />
      <circle cx="13" cy="-13" r="8.5" fill="#CBD5E1" opacity="0.3" class="animate-spin origin-[13px_-13px]" />
      <circle cx="-13" cy="13" r="8.5" fill="#CBD5E1" opacity="0.3" class="animate-spin origin-[-13px_13px]" />
      <circle cx="13" cy="13" r="8.5" fill="#CBD5E1" opacity="0.3" class="animate-spin origin-[13px_13px]" />
    </template>

    <g v-if="!isRunning" :stroke="TelloMainRed" stroke-width="2" stroke-linecap="round">
      <path d="M-19,-19 L-7,-7" />
      <path d="M19,-19 L7,-7" />
      <path d="M-19,19 L-7,7" />
      <path d="M19,19 L7,7" />
    </g>
    
    <g :stroke="TelloMainRed" stroke-width="1.5" stroke-linecap="round">
      <path d="M-11,-11 L-3,-4" />
      <path d="M11,-11 L3,-4" />
      <path d="M-11,11 L-3,4" />
      <path d="M11,11 L3,4" />
      <circle cx="-13" cy="-13" r="9" fill="none" stroke-width="1" />
      <circle cx="13" cy="-13" r="9" fill="none" stroke-width="1" />
      <circle cx="-13" cy="13" r="9" fill="none" stroke-width="1" />
      <circle cx="13" cy="13" r="9" fill="none" stroke-width="1" />
    </g>
    
    <g :fill="TelloGray" :stroke="TelloGray" stroke-width="1">
      <circle cx="-13" cy="-13" r="5" />
      <circle cx="13" cy="-13" r="5" />
      <circle cx="-13" cy="13" r="5" />
      <circle cx="13" cy="13" r="5" />
    </g>
    
    <rect x="-7" y="-12" width="14" height="24" rx="4" :fill="TelloMainRed" :stroke="TelloMainRed" stroke-width="1" />
    
    <g :stroke="TelloRidgeRed" stroke-width="1">
      <line x1="-4" y1="-8" x2="-4" y2="7" />
      <line x1="-1.5" y1="-8" x2="-1.5" y2="7" />
      <line x1="1.5" y1="-8" x2="1.5" y2="7" />
      <line x1="4" y1="-8" x2="4" y2="7" />
    </g>
    
    <g :fill="TelloLogoWhite">
      <path d="M -1.5,-7 L 0,-5.5 L 1.5,-7 L 1.5,-4.5 L 0,-3 L -1.5,-4.5 Z" />
      <text x="0" y="1.5" font-size="1.8" font-weight="bold" text-anchor="middle" font-family="Arial, sans-serif">TELLO</text>
      <text x="0" y="4.5" font-size="1.2" text-anchor="middle" font-family="Arial, sans-serif">Talent</text>
    </g>
    
    <rect x="-5" y="-14" width="10" height="6" rx="2" :fill="TelloGray" />
    <circle cx="-2" cy="-11" r="1.2" fill="#38BDF8" />
    
    <circle 
      cx="0" cy="8.5" r="1.5" 
      :fill="isRunning ? '#84CC16' : '#F1F5F9'" 
      :class="{ 'animate-pulse': isRunning }" 
      stroke="#E2E8F0" 
      stroke-width="0.5" 
    />
  </g>
</template>

<style scoped>
/* Ensure the propeller spin blurs spin around their new origin points */
.animate-spin {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>