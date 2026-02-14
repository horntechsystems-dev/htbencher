<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
    <div class="w-full max-w-md space-y-8">
      <div class="text-center">
        <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-gray-900 to-gray-700 shadow-lg ring-1 ring-gray-900/10">
          <svg class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
        </div>
        <h2 class="mt-6 text-3xl font-bold tracking-tight text-gray-900">
          Welcome back
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          Sign in to your HTBencher account
        </p>
      </div>

      <div class="rounded-2xl bg-white p-8 shadow-xl ring-1 ring-gray-900/5 sm:p-10">
        <form class="space-y-6" @submit.prevent="handleLogin">
          <div>
            <label for="email" class="block text-sm font-medium leading-6 text-gray-900">Username or Email</label>
            <div class="relative mt-2 rounded-md shadow-sm">
              <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <UserIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
              </div>
              <input
                id="email"
                v-model="email"
                name="email"
                type="text"
                autocomplete="username"
                required
                class="block w-full rounded-md border-0 py-2.5 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-gray-900 sm:text-sm sm:leading-6 transition-all"
                placeholder="Administrator"
              />
            </div>
          </div>

          <div>
            <label for="password" class="block text-sm font-medium leading-6 text-gray-900">Password</label>
            <div class="relative mt-2 rounded-md shadow-sm">
              <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <LockIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
              </div>
              <input
                id="password"
                v-model="password"
                name="password"
                type="password"
                autocomplete="current-password"
                required
                class="block w-full rounded-md border-0 py-2.5 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-gray-900 sm:text-sm sm:leading-6 transition-all"
                placeholder="••••••••"
              />
            </div>
          </div>

          <div v-if="errorMessage" class="rounded-md bg-red-50 p-3">
            <div class="flex">
              <div class="flex-shrink-0">
                <AlertCircleIcon class="h-5 w-5 text-red-400" aria-hidden="true" />
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800">Login failed</h3>
                <div class="mt-1 text-sm text-red-700">
                  {{ errorMessage }}
                </div>
              </div>
            </div>
          </div>

          <div>
            <Button
              variant="solid"
              class="flex w-full justify-center rounded-md bg-gray-900 px-3 py-2.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-gray-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gray-900 transition-all active:scale-[0.98]"
              :loading="loginResource.loading"
              type="submit"
            >
              Sign in
            </Button>
          </div>
        </form>
      </div>
      
      <p class="text-center text-xs text-gray-500">
        &copy; {{ new Date().getFullYear() }} HTBencher. All rights reserved.
      </p>
    </div>
  </div>
</template>

<script setup>
import { useAuth } from "@/composables/useAuth"
import { AlertCircle as AlertCircleIcon, Lock as LockIcon, User as UserIcon } from "lucide-vue-next"
import { ref } from "vue"

const email = ref("")
const password = ref("")
const { login, loginResource } = useAuth()

const errorMessage = ref(null)

async function handleLogin() {
	errorMessage.value = null
	console.log('Attempting login with:', { email: email.value, password: password.value ? '****' : 'empty' })
	
	if (!email.value || !password.value) {
		errorMessage.value = "Please enter both username/email and password"
		return
	}

	try {
		await login(email.value, password.value)
	} catch (err) {
		console.error("Login failed:", err)
		errorMessage.value = err.messages?.[0] || err.message || "Invalid credentials. Please try again."
	}
}
</script>
