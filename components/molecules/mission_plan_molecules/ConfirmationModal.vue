<script setup>
import { onMounted, onUnmounted } from 'vue';
import Button from '~/components/atoms/Button.vue';

const props = defineProps({
  isOpen: Boolean,
  title: String,
  message: String,
  confirmText: { type: String, default: 'Confirm' },
  cancelText: { type: String, default: 'Cancel' },
  // isWarning: red styling, blocking error icon (X), single 'Close' button
  isWarning: { type: Boolean, default: false },
  // NEW: isSuccess: green styling, success icon (checkmark), single 'OK' button
  isSuccess: { type: Boolean, default: false }
});

const emit = defineEmits(['confirm', 'cancel']);

// --- Close on Escape Key ---
const handleEscape = (e) => {
  if (e.key === 'Escape' && props.isOpen) {
    emit('cancel');
  }
};

onMounted(() => document.addEventListener('keydown', handleEscape));
onUnmounted(() => document.removeEventListener('keydown', handleEscape));
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 overflow-y-auto" role="dialog" aria-modal="true">
        
        <div class="fixed inset-0 bg-black/40 backdrop-blur-sm" aria-hidden="true" @click="$emit('cancel')"></div>

        <Transition
          enter-active-class="transition duration-300 ease-out"
          enter-from-class="opacity-0 scale-95 translate-y-4"
          enter-to-class="opacity-100 scale-100 translate-y-0"
          leave-active-class="transition duration-200 ease-in"
          leave-from-class="opacity-100 scale-100 translate-y-0"
          leave-to-class="opacity-0 scale-95 translate-y-4"
        >
          <div v-if="isOpen" class="relative bg-white/95 backdrop-blur-md rounded-xl shadow-2xl w-full max-w-sm overflow-hidden border border-white/20 z-10">
            
            <div class="p-4 border-b border-gray-100/50 flex items-center gap-3" 
              :class="{
                'bg-red-50/50': isWarning,
                'bg-green-50/50': isSuccess,
                'bg-yellow-50/50': !isWarning && !isSuccess
              }">
               <div class="w-10 h-10 rounded-full flex items-center justify-center shrink-0 shadow-sm border border-white/50" 
                 :class="{
                   'bg-red-100 text-red-600': isWarning,
                   'bg-green-100 text-green-600': isSuccess,
                   'bg-yellow-100 text-yellow-600': !isWarning && !isSuccess
                 }">
                 
                 <svg v-if="isWarning" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
                   <path fill-rule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25zm-1.72 6.97a.75.75 0 10-1.06 1.06L10.94 12l-1.72 1.72a.75.75 0 101.06 1.06L12 13.06l1.72 1.72a.75.75 0 101.06-1.06L13.06 12l1.72-1.72a.75.75 0 10-1.06-1.06L12 10.94l-1.72-1.72z" clip-rule="evenodd" />
                 </svg>

                 <svg v-else-if="isSuccess" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
                   <path fill-rule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm13.36-1.814a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z" clip-rule="evenodd" />
                 </svg>

                 <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
                   <path fill-rule="evenodd" d="M9.401 3.003c1.155-2 4.043-2 5.197 0l7.355 12.748c1.154 2-.29 4.5-2.599 4.5H4.645c-2.309 0-3.752-2.5-2.598-4.5L9.4 3.003zM12 8.25a.75.75 0 01.75.75v3.75a.75.75 0 01-1.5 0V9a.75.75 0 01.75-.75zm0 8.25a.75.75 0 100-1.5.75.75 0 000 1.5z" clip-rule="evenodd" />
                 </svg>
               </div>
               <h3 class="text-lg font-bold text-gray-800 leading-tight">{{ title }}</h3>
            </div>

            <div class="p-6">
              <p class="text-sm text-gray-600 leading-relaxed">{{ message }}</p>
            </div>

            <div class="p-4 bg-gray-50/80 border-t border-gray-100/50 flex justify-end gap-3">
              
              <button 
                v-if="isWarning || isSuccess"
                @click="$emit('cancel')" 
                class="px-4 py-2 text-sm font-bold text-white rounded-md shadow-sm transition-colors"
                :class="isWarning ? 'bg-[#d32f2f] hover:bg-[#b71c1c]' : 'bg-green-600 hover:bg-green-700'"
              >
                {{ isWarning ? 'Close' : 'OK' }}
              </button>

              <template v-else>
                <button 
                  @click="$emit('cancel')" 
                  class="px-4 py-2 text-sm font-bold text-gray-700 hover:bg-gray-200/70 rounded-md transition-colors border border-gray-300/50"
                >
                  {{ cancelText }}
                </button>
                
                <Button 
                  @click="$emit('confirm')" 
                  class="px-4 py-2 text-sm font-bold text-white bg-[#d32f2f] hover:bg-[#b71c1c] rounded-md shadow-sm transition-colors"
                >
                  {{ confirmText }}
                </Button>
              </template>

            </div>

          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>