import { io } from "socket.io-client"
import { socketio_port } from "../../../../sites/common_site_config.json"

let socket = null
export function initSocket() {
	let url = window.location.origin
	let options = {
		withCredentials: true,
		reconnectionAttempts: 5,
	}

	// Development configuration
	if (import.meta.env.DEV) {
		const port = socketio_port || 9000
		url = `${window.location.protocol}//${window.location.hostname}:${port}`
	}

	socket = io(url, options)

	socket.on("connect_error", (err) => {
		console.error("Socket Connection Error:", err)
	})

	return socket
}

export function useSocket() {
	return socket
}
