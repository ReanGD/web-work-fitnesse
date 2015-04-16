import sys
import traceback
from manage.models import LoadLog


class DbLogger(object):
    def __init__(self, rec_id=None):
        if rec_id is None:
            self.rec = LoadLog.objects.create()
        else:
            self.rec = LoadLog.objects.get(pk=int(rec_id))

    def remove_torrent(self):
        if self.rec.torent_ptr is not None:
            for it in LoadLog.objects.filter(torent_ptr=self.rec.torent_ptr):
                it.torent_ptr = None
                it.save()

    def id(self):
        return self.rec.id

    def json_result(self):
        return {'result': self.rec.result, 'text': self.rec.text}

    def text(self):
        return self.rec.text

    def write(self, msg):
        self.rec.text += ("\n" + msg)
        self.rec.save()

    def set_result(self, result):
        self.rec.result = result
        self.rec.save()

    def set_torrent(self, t):
        self.torent_ptr = t
        self.rec.save()

    def exception(self):
        e_type, e_value, e_traceback = sys.exc_info()
        s = "\n".join(traceback.format_exception(e_type, e_value, e_traceback))
        self.write(s)
        self.set_result(LoadLog.RES_FAILED)
