import { auth } from "@/services/htbencherApi"
import { createResource } from "frappe-ui"
import { computed, reactive } from "vue"
import { useRouter } from "vue-router"

const user = reactive({
	isLoggedIn: false,
	email: null,
	fullName: null,
})

export function useAuth() {
	const router = useRouter()

	const loginResource = createResource({
		url: "htbencher.api.login",
		onSuccess(data) {
			user.isLoggedIn = true
			user.email = data.email
			user.fullName = data.full_name
			router.push(data.default_route || "/")
		},
		onError(err) {
			console.error("Login failed", err)
		},
	})

	function login(email, password) {
		return loginResource.submit({ usr: email, pwd: password })
	}

	function logout() {
		user.isLoggedIn = false
		user.email = null
		user.fullName = null
		router.push("/login")
	}

	return {
		user,
		login,
		logout,
		loginResource,
		isLoggedIn: computed(() => user.isLoggedIn),
	}
}
