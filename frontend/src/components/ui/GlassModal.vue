<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm transition-opacity" @click="close"></div>

        <!-- Modal Content -->
        <div class="relative w-full max-w-lg overflow-hidden rounded-2xl bg-white/90 p-6 shadow-2xl ring-1 ring-gray-900/5 backdrop-blur-xl transition-all dark:bg-gray-900/90 dark:ring-white/10">
          <!-- Header -->
          <div class="mb-6 flex items-center justify-between">
            <h3 class="text-xl font-bold text-gray-900 dark:text-white">{{ title }}</h3>
            <button
              @click="close"
              class="rounded-lg p-1 text-gray-500 hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200"
            >
              <X class="h-5 w-5" />
            </button>
          </div>

          <!-- Body -->
          <div class="space-y-4">
            <slot />
          </div>

          <!-- Footer -->
          <div v-if="$slots.actions" class="mt-8 flex justify-end gap-3">
            <slot name="actions" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { X } from "lucide-vue-next"

const props = defineProps({
  modelValue: Boolean,
  title: {
    type: String,
    default: "",
  },
})

const emit = defineEmits(["update:modelValue", "close"])

function close() {
  emit("update:modelValue", false)
  emit("close")
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

.modal-enter-to,
.modal-leave-from {
  opacity: 1;
  transform: scale(1);
}
</style>
