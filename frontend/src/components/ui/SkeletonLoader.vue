<template>
  <div
    class="animate-pulse rounded bg-gray-200 dark:bg-gray-700"
    :class="[
      width ? '' : 'w-full',
      height ? '' : 'h-4',
    ]"
    :style="{
      width: width,
      height: height
    }"
  ></div>
</template>

<script setup>
defineProps({
  width: String,
  height: String,
})
</script>
