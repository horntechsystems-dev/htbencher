import { frappeRequest } from "frappe-ui"

export default {
	get(url, params = {}) {
		console.log("api.get called with:", url, params)
		return frappeRequest({
			url,
			method: "GET",
			params,
		})
	},
	post(url, data = {}) {
		console.log("api.post called with:", url, data)
		return frappeRequest({
			url,
			method: "POST",
			params: data, // Frappe RPC expects params, not body
		})
	},
	patch(url, data = {}) {
		return frappeRequest({
			url,
			method: "PATCH",
			body: data,
		})
	},
	delete(url, params = {}) {
		return frappeRequest({
			url,
			method: "DELETE",
			params,
		})
	},
}
