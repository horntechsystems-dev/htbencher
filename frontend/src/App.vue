<template>
  <div class="antialiased">
    <MainLayout v-if="!isPublic">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </MainLayout>
    
    <router-view v-else />
  </div>
</template>

<script setup>
import MainLayout from "@/layouts/MainLayout.vue"
import { useTheme } from "@/composables/useTheme"
import { computed } from "vue"
import { useRoute } from "vue-router"

// Initialize theme globally
useTheme()

const route = useRoute()
const isPublic = computed(() => route.meta.isPublic)
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
