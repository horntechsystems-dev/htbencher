<template>
  <div class="space-y-1.5">
    <label v-if="label" :for="id" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
      {{ label }} <span v-if="required" class="text-red-500">*</span>
    </label>
    <div class="relative">
      <select
        :id="id"
        :value="modelValue"
        :required="required"
        :disabled="disabled"
        class="block w-full appearance-none rounded-xl border-gray-200 bg-white/50 px-4 py-2.5 text-sm text-gray-900 shadow-sm ring-1 ring-inset ring-gray-200 transition-all focus:bg-white focus:ring-2 focus:ring-inset focus:ring-gray-900 disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500 disabled:ring-gray-200 dark:border-gray-700 dark:bg-gray-800/50 dark:text-white dark:ring-gray-700 dark:focus:bg-gray-800 dark:focus:ring-white"
        @change="$emit('update:modelValue', $event.target.value)"
      >
        <option value="" disabled selected>{{ placeholder || 'Select an option' }}</option>
        <option v-for="option in options" :key="option.value" :value="option.value">
          {{ option.label }}
        </option>
      </select>
      <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-gray-500">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
    <p v-if="error" class="text-xs text-red-600 dark:text-red-400">{{ error }}</p>
    <p v-if="hint" class="text-xs text-gray-500 dark:text-gray-400">{{ hint }}</p>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  modelValue: [String, Number],
  label: String,
  options: {
    type: Array, // [{ label: 'Option 1', value: 'opt1' }]
    default: () => [],
  },
  placeholder: String,
  required: Boolean,
  disabled: Boolean,
  error: String,
  hint: String,
})

const emit = defineEmits(["update:modelValue"])

const id = computed(() => `select-${Math.random().toString(36).substr(2, 9)}`)
</script>
