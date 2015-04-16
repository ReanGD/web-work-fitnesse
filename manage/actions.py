#!/usr/bin/python

import json
import db_logger
import transmission

from django.http import HttpResponse

from uwsgidecorators import spool
from manage.models import LoadLog


@spool
def run_sync_task(arguments):
    log = db_logger.DbLogger(arguments['log_id'])
    try:
        tr = transmission.Transmission(log)
        torrent = tr.find_torrent()
        if torrent is not None:
            tr.copy_torrent(torrent)
            log.set_result(LoadLog.RES_SUCCESS)
        else:
            log.write("not found torrent for download")
            log.set_result(LoadLog.RES_NOT_FOUND)
    except Exception:
        log.exception()


def run_sync_get(request):
    log = db_logger.DbLogger()
    log_id = str(log.id())
    run_sync_task.spool({'log_id': log_id})
    return HttpResponse(json.dumps({'id': log_id}),
                        content_type="application/json")


def delete_torrent(torrent_rec, file_only):
    log = db_logger.DbLogger()
    try:
        tr = transmission.Transmission(log)
        tr.remove_torrent(torrent_rec, file_only)
    except Exception:
        log.exception()
