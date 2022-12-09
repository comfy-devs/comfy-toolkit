from job.types.upload_local import UploadLocalJob
from job.types.upload import UploadJob

def stepUpload(dashboard, opt_id, i=None):
    selection = input("> Method of upload? (remote/local/local-move) [remote]: ")
    selection = "remote" if selection == "" else selection
    if selection == "remote":
        return UploadJob(dashboard, opt_id, i)
    elif selection == "local":
        return UploadLocalJob(dashboard, opt_id, i, False)
    elif selection == "local-move":
        return UploadLocalJob(dashboard, opt_id, i, True)