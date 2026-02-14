// Disabled until HT Job doctype is created
/*
import { jobs } from "@/services/htbencherApi"
import { createResource } from "frappe-ui"

export function useJobs() {
    const jobList = createResource({
        url: 'htbencher.api.get_jobs',
        auto: true,
    })

    return {
        jobList,
    }
}
*/
export function useJobs() {
    // Placeholder until HT Job doctype is implemented
    return {
        jobList: { data: [], loading: false },
    }
}
