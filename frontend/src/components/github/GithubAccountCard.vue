<template>
  <GlassCard class="relative overflow-hidden transition-all hover:-translate-y-1 hover:shadow-2xl">
    <div class="absolute top-0 right-0 p-4">
      <StatusIndicator :status="account.status" />
    </div>

    <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gray-900 text-white shadow-lg dark:bg-white dark:text-gray-900">
      <Github class="h-6 w-6" />
    </div>

    <h3 class="text-lg font-bold text-gray-900 dark:text-white">{{ account.account_name }}</h3>
    <p class="text-sm text-gray-500 dark:text-gray-400">GitHub SSH Account</p>

    <div class="mt-6 flex gap-2">
      <Button
        variant="subtle"
        class="flex-1"
        @click="$emit('copy-public-key', account)"
      >
        Public Key
      </Button>
      <Button
        variant="solid"
        class="flex-1 bg-gray-900 text-white hover:bg-gray-800 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-100"
        @click="$emit('edit', account)"
      >
        Edit
      </Button>
    </div>
  </GlassCard>
</template>

<script setup>
import GlassCard from "@/components/ui/GlassCard.vue"
import StatusIndicator from "@/components/ui/StatusIndicator.vue"
import { Github } from "lucide-vue-next"

defineProps({
  account: {
    type: Object,
    required: true
  }
})

defineEmits(['copy-public-key', 'edit'])
</script>
