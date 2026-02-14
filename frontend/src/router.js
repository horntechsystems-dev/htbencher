import { userResource } from "@/data/user"
import { createRouter, createWebHistory } from "vue-router"
import { session } from "./data/session"

const routes = [
	{
		path: "/",
		redirect: { name: "Dashboard" },
	},
	{
		path: "/account/login",
		redirect: { name: "Login" },
	},
	{
		path: "/login",
		name: "Login",
		component: () => import("@/pages/Login.vue"),
		meta: { isPublic: true },
	},
	{
		path: "/dashboard",
		name: "Dashboard",
		component: () => import("@/pages/Dashboard.vue"),
	},
	{
		path: "/benches",
		name: "Benches",
		component: () => import("@/pages/Benches.vue"),
	},
	{
		path: "/apps",
		name: "Apps",
		component: () => import("@/pages/Apps.vue"),
	},
	{
		path: "/sites",
		name: "Sites",
		component: () => import("@/pages/Sites.vue"),
	},
	{
		path: "/sites/:id",
		name: "SiteDetails",
		component: () => import("@/pages/SiteDetails.vue"),
	},
	{
		path: "/jobs",
		name: "Jobs",
		component: () => import("@/pages/Jobs.vue"),
	},
	{
		path: "/benches/:id",
		name: "BenchDetails",
		component: () => import("@/pages/BenchDetails.vue"),
	},
	{
		path: "/settings/github-accounts",
		name: "GithubAccounts",
		component: () => import("@/pages/Settings/GithubAccounts.vue"),
	},
]

const router = createRouter({
	history: createWebHistory("/frontend"),
	routes,
})

router.beforeEach(async (to, from, next) => {
	let isLoggedIn = !!session.user

	if (!isLoggedIn && !to.meta.isPublic) {
		try {
			await userResource.promise
			isLoggedIn = true
		} catch (error) {
			isLoggedIn = false
		}
	}

	if (to.name === "Login" && isLoggedIn) {
		next({ name: "Dashboard" })
	} else if (!to.meta.isPublic && !isLoggedIn) {
		next({ name: "Login" })
	} else {
		next()
	}
})

export default router
