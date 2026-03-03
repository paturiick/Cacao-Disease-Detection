<script setup>
import { computed } from 'vue'

const props = defineProps({
  queue:       { type: Array,  default: () => [] },
  activeIndex: { type: Number, default: -1       }
})

const SVG_W   = 380
const SVG_H   = 260
const PADDING = 44
const NODE_R  = 11

// ---------------------------------------------------------------------------
// 1. Parse the command queue into world-space waypoints.
//    Heading convention: 0° = North (+Y), clockwise positive.
//    forward/back/left/right are relative to the current heading.
//    go x y z  →  x = drone-right, y = drone-forward  (heading-relative)
//    cw/ccw rotate the heading; hover/up/down add no XY waypoint.
// ---------------------------------------------------------------------------
const waypoints = computed(() => {
  const pts = [{ wx: 0, wy: 0, step: 0, type: 'start', label: 'Origin' }]
  let wx = 0, wy = 0, heading = 0 // heading in degrees, 0 = North

  props.queue.forEach((cmd, idx) => {
    const v   = parseFloat(cmd.val) || 0
    const rad = (heading * Math.PI) / 180
    // heading direction (world): (sin θ, cos θ)
    // right-of-heading  (world): (cos θ, −sin θ)
    const fwdX =  Math.sin(rad), fwdY =  Math.cos(rad)
    const rgtX =  Math.cos(rad), rgtY = -Math.sin(rad)

    switch (cmd.type) {
      case 'forward': wx += fwdX * v; wy += fwdY * v; break
      case 'back'   : wx -= fwdX * v; wy -= fwdY * v; break
      case 'right'  : wx += rgtX * v; wy += rgtY * v; break
      case 'left'   : wx -= rgtX * v; wy -= rgtY * v; break
      case 'go': {
        const p  = (cmd.val || '').split(' ')
        const dx = parseFloat(p[0]) || 0
        const dy = parseFloat(p[1]) || 0
        // dx = drone right, dy = drone forward
        wx += rgtX * dx + fwdX * dy
        wy += rgtY * dx + fwdY * dy
        break
      }
      case 'cw' : heading = (heading + v) % 360;               return
      case 'ccw': heading = ((heading - v) % 360 + 360) % 360; return
      default   : return   // hover, up, down – no XY change
    }

    pts.push({ wx, wy, step: idx + 1, type: cmd.type, label: cmd.label })
  })

  return pts
})

// ---------------------------------------------------------------------------
// 2. Scale world-space waypoints to SVG viewport coords.
// ---------------------------------------------------------------------------
const svgPoints = computed(() => {
  const pts = waypoints.value
  if (!pts.length) return []

  const xs = pts.map(p => p.wx), ys = pts.map(p => p.wy)
  const minX = Math.min(...xs), maxX = Math.max(...xs)
  const minY = Math.min(...ys), maxY = Math.max(...ys)

  // Keep a minimum range so origin-only path isn't tiny
  const range = Math.max(maxX - minX, maxY - minY, 60)
  const usable = Math.min(SVG_W, SVG_H) - PADDING * 2
  const scale  = usable / range

  const cx = (minX + maxX) / 2, cy = (minY + maxY) / 2

  return pts.map(p => ({
    ...p,
    x: (p.wx - cx) * scale + SVG_W / 2,
    y: -(p.wy - cy) * scale + SVG_H / 2  // flip Y: SVG grows downward
  }))
})

// ---------------------------------------------------------------------------
// 3. Helpers
// ---------------------------------------------------------------------------
const isStart  = s => s === 0
const isActive = s => props.activeIndex === s

// Compute mid-point & angle for an arrow glyph on a segment
const segmentArrow = (a, b) => {
  const dx = b.x - a.x, dy = b.y - a.y
  const len = Math.sqrt(dx * dx + dy * dy)
  if (len < 20) return null
  return {
    x    : (a.x + b.x) / 2,
    y    : (a.y + b.y) / 2,
    angle: Math.atan2(dy, dx) * 180 / Math.PI
  }
}
</script>

<template>
  <div class="w-full h-full flex flex-col select-none">
    <svg
      :viewBox="`0 0 ${SVG_W} ${SVG_H}`"
      class="w-full flex-1"
      xmlns="http://www.w3.org/2000/svg"
    >
      <!-- ── Defs ─────────────────────────────────────────────────── -->
      <defs>
        <!-- default arrowhead -->
        <marker id="fp-arrow" markerWidth="7" markerHeight="7"
                refX="5" refY="3.5" orient="auto">
          <polygon points="0 0, 7 3.5, 0 7" fill="#40623F" />
        </marker>
        <!-- active arrowhead -->
        <marker id="fp-arrow-active" markerWidth="7" markerHeight="7"
                refX="5" refY="3.5" orient="auto">
          <polygon points="0 0, 7 3.5, 0 7" fill="#F59E0B" />
        </marker>
        <!-- glow filter for active node -->
        <filter id="fp-glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="3" result="blur"/>
          <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
      </defs>

      <!-- ── Background ─────────────────────────────────────────── -->
      <rect x="0" y="0" :width="SVG_W" :height="SVG_H" fill="#F8FAF5" rx="8"/>

      <!-- ── Grid ───────────────────────────────────────────────── -->
      <g stroke="#D1D5DB" stroke-width="0.5" opacity="0.7">
        <line v-for="i in 9"  :key="`gx${i}`"
              :x1="i*SVG_W/10" y1="0" :x2="i*SVG_W/10" :y2="SVG_H"/>
        <line v-for="i in 7"  :key="`gy${i}`"
              x1="0" :y1="i*SVG_H/8" :x2="SVG_W" :y2="i*SVG_H/8"/>
      </g>

      <!-- ── Compass rose (top-left) ─────────────────────────────── -->
      <g transform="translate(20,20)" font-size="8" font-family="Inter,sans-serif" fill="#9CA3AF">
        <text x="0"  y="-6"  text-anchor="middle">N</text>
        <text x="0"  y="18"  text-anchor="middle">S</text>
        <text x="-8" y="5"   text-anchor="middle">W</text>
        <text x="8"  y="5"   text-anchor="middle">E</text>
        <line x1="0" y1="-4" x2="0" y2="14"  stroke="#D1D5DB" stroke-width="0.8"/>
        <line x1="-6" y1="5" x2="6" y2="5"  stroke="#D1D5DB" stroke-width="0.8"/>
      </g>

      <!-- ── Empty state ─────────────────────────────────────────── -->
      <g v-if="svgPoints.length <= 1" text-anchor="middle">
        <text :x="SVG_W/2" :y="SVG_H/2 - 10"
              fill="#9CA3AF" font-size="12" font-family="Inter,sans-serif">
          No path defined yet
        </text>
        <text :x="SVG_W/2" :y="SVG_H/2 + 8"
              fill="#C4CBA8" font-size="10" font-family="Inter,sans-serif">
          Add movement commands to visualise the route
        </text>
      </g>

      <!-- ── Segment lines ──────────────────────────────────────── -->
      <template v-for="(pt, i) in svgPoints" :key="`seg${i}`">
        <line
          v-if="i < svgPoints.length - 1"
          :x1="pt.x" :y1="pt.y"
          :x2="svgPoints[i+1].x" :y2="svgPoints[i+1].y"
          :stroke="isActive(svgPoints[i+1].step) ? '#F59E0B' : '#40623F'"
          stroke-width="2"
          stroke-linecap="round"
          :marker-end="isActive(svgPoints[i+1].step) ? 'url(#fp-arrow-active)' : 'url(#fp-arrow)'"
        />
      </template>

      <!-- ── Mid-segment direction triangles ───────────────────── -->
      <template v-for="(pt, i) in svgPoints" :key="`arr${i}`">
        <g
          v-if="i < svgPoints.length - 1 && segmentArrow(pt, svgPoints[i+1])"
          :transform="`translate(${segmentArrow(pt, svgPoints[i+1]).x},${segmentArrow(pt, svgPoints[i+1]).y}) rotate(${segmentArrow(pt, svgPoints[i+1]).angle})`"
        >
          <polygon
            points="-5,-4 5,0 -5,4"
            :fill="isActive(svgPoints[i+1].step) ? '#F59E0B' : '#40623F'"
            opacity="0.6"
          />
        </g>
      </template>

      <!-- ── Waypoint nodes ─────────────────────────────────────── -->
      <g v-for="(pt) in svgPoints" :key="`node${pt.step}`">
        <!-- Active pulse ring -->
        <circle
          v-if="isActive(pt.step)"
          :cx="pt.x" :cy="pt.y" :r="NODE_R + 6"
          fill="#F59E0B" opacity="0.18"
          filter="url(#fp-glow)"
        />
        <!-- Shadow for depth -->
        <circle
          :cx="pt.x + 1" :cy="pt.y + 1" :r="NODE_R"
          fill="rgba(0,0,0,0.1)"
        />
        <!-- Main circle -->
        <circle
          :cx="pt.x" :cy="pt.y" :r="NODE_R"
          :fill="isStart(pt.step)
                   ? '#40623F'
                   : isActive(pt.step)
                       ? '#F59E0B'
                       : 'white'"
          :stroke="isActive(pt.step) ? '#D97706' : '#40623F'"
          stroke-width="2"
        />
        <!-- Label -->
        <text
          :x="pt.x" :y="pt.y + 4"
          text-anchor="middle"
          font-size="9"
          font-weight="bold"
          font-family="Inter,sans-serif"
          :fill="(isStart(pt.step) || isActive(pt.step)) ? 'white' : '#40623F'"
        >{{ isStart(pt.step) ? 'S' : pt.step }}</text>
      </g>
    </svg>

    <!-- ── Legend ─────────────────────────────────────────────────── -->
    <div class="flex gap-4 items-center justify-center py-2 text-[10px] text-gray-500 border-t border-gray-100">
      <div class="flex items-center gap-1">
        <div class="w-2.5 h-2.5 rounded-full bg-[#40623F]"></div>
        <span>Start</span>
      </div>
      <div class="flex items-center gap-1">
        <div class="w-2.5 h-2.5 rounded-full bg-white border-2 border-[#40623F]"></div>
        <span>Waypoint</span>
      </div>
      <div class="flex items-center gap-1">
        <div class="w-2.5 h-2.5 rounded-full bg-amber-400"></div>
        <span>Active</span>
      </div>
      <div class="flex items-center gap-1">
        <div class="h-px w-5 bg-[#40623F]" style="position:relative;">
          <div class="absolute right-0 top-1/2 -translate-y-1/2 w-0 h-0"
               style="border-top:3px solid transparent;border-bottom:3px solid transparent;border-left:5px solid #40623F;"></div>
        </div>
        <span>Path</span>
      </div>
    </div>
  </div>
</template>
