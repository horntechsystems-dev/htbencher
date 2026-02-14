<template>
  <header class="flex h-16 items-center justify-between border-b bg-surface-white px-6">
    <div class="flex items-center gap-4">
      <h1 class="text-lg font-semibold text-ink-gray-9">{{ pageTitle }}</h1>
    </div>

    <div class="flex items-center gap-4">
      <div v-if="user" class="flex items-center gap-2 text-sm mr-2">
        <div class="h-8 w-8 rounded-full bg-surface-gray-2 flex items-center justify-center text-ink-gray-7 border">
          {{ user[0]?.toUpperCase() }}
        </div>
        <span class="font-medium text-ink-gray-8">{{ user }}</span>
      </div>
      
      <Button
        variant="subtle"
        size="sm"
        @click="logout"
        :loading="logoutResource.loading"
      >
        Logout
      </Button>
    </div>
  </header>
</template>

<script setup>
import { useAuth } from "@/composables/useAuth"
import { computed } from "vue"
import { useRoute } from "vue-router"

const route = useRoute()
const { user, logout, logoutResource } = useAuth()

const pageTitle = computed(() => {
	return route.name || "Dashboard"
})
</script>
