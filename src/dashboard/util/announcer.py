import os, requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class ComfyAnnouncer():
    def __init__(self):
        self.jobs_endpoint = os.getenv("COMFY_JOBS_ENDPOINT")
        self.jobs_key = os.getenv("COMFY_JOBS_KEY")
        self.jobs_server = os.getenv("COMFY_JOBS_SERVER")
        self.enabled = self.jobs_endpoint != None and self.jobs_endpoint != ""

    def announce(self, dashboard):
        data = { "adminKey": self.jobs_key, "server": self.jobs_server, "jobs": [] }
        addJob = lambda job, status: data["jobs"].append({
            "type": job.jobType,
            "name": job.jobName,
            "status": status,
            "progress": job.jobProgress,
            "details": job.jobDetails
        })
        for jobCollection in dashboard.jobCollections:
            if jobCollection.currentJob != None:
                addJob(jobCollection.currentJob, "in progress")
            for job in jobCollection.jobs:
                addJob(job, "waiting")

        x = requests.post(f'{self.jobs_endpoint}/v1/jobs/set', json = data, verify=False)
