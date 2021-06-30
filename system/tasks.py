from constants import DOWNLOAD_STATUS
from system.models import DownloadJob
from system.download import get_download_handler
from settings.celery import app
import logging
logger = logging.getLogger(__name__)


@app.task
def execute_download(id):
    download_job = DownloadJob.objects.get(id=id)
    data = download_job.request_data
    data['download_id'] = download_job.id
    download_job.status = DOWNLOAD_STATUS.PROCESSING
    download_job.save()
    try:
        DownloadHandlerClass = get_download_handler(download_job.download_type)
        obj = DownloadHandlerClass()
        obj.request = data
        result = obj.process_data(data, download_job.created_by)
        download_job.files = result['file']
        download_job.status = DOWNLOAD_STATUS.PROCESSED
        download_job.complete_percentage = 100
        download_job.save()

    except Exception as e:
        download_job.status = DOWNLOAD_STATUS.FAILED
        download_job.error_message = f'{e}'
        download_job.save()
        return False
    return True
