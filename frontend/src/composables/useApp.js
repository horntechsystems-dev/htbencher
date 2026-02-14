import { apps } from "@/services/htbencherApi"
import { createResource } from "frappe-ui"

export function useApp() {
    const appList = createResource({
        url: 'htbencher.api.get_apps',
        auto: true,
    })

    return {
        appList,
    }
}
