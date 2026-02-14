<template>
  <header
    class="sticky top-0 z-40 flex h-16 items-center justify-between border-b border-gray-200 bg-white/80 px-6 backdrop-blur-xl transition-all dark:border-gray-800 dark:bg-gray-900/80"
    :class="[collapsed ? 'pl-26' : 'pl-70']"
  >
    <div class="flex items-center gap-4">
      <button
        @click="$emit('toggle-sidebar')"
        class="rounded-lg p-1.5 text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
      >
        <Menu class="h-5 w-5" />
      </button>
      
      <div class="h-6 w-px bg-gray-200 dark:bg-gray-800"></div>

      <nav class="flex items-center text-sm font-medium text-gray-500 dark:text-gray-400">
        <span class="hover:text-gray-900 dark:hover:text-white cursor-default">
          {{ route.name }}
        </span>
      </nav>
    </div>

    <div class="flex items-center gap-4">
      <button
        @click="toggleTheme"
        class="rounded-lg p-2 text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
        title="Toggle Theme"
      >
        <Sun v-if="isDark" class="h-5 w-5" />
        <Moon v-else class="h-5 w-5" />
      </button>

      <div class="flex items-center gap-3 pl-4 border-l border-gray-200 dark:border-gray-800">
        <div class="text-right hidden sm:block">
          <p class="text-sm font-medium text-gray-900 dark:text-white">{{ user?.full_name || user?.name }}</p>
          <p class="text-xs text-gray-500 dark:text-gray-400">{{ user?.email }}</p>
        </div>
        <div class="h-8 w-8 rounded-full bg-gradient-to-tr from-gray-900 to-gray-700 dark:from-white dark:to-gray-300"></div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useAuth } from "@/composables/useAuth"
import { useTheme } from "@/composables/useTheme"
import { Menu, Moon, Sun } from "lucide-vue-next"
import { useRoute } from "vue-router"

defineProps({
  collapsed: Boolean,
})

defineEmits(['toggle-sidebar'])

const route = useRoute()
const { user } = useAuth()
const { isDark, toggleTheme } = useTheme()
</script>
