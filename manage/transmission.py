import os
import shutil
import transmissionrpc

from manage.models import Torrent, TorrentFile, StorageMap, Setting


def _remove_file(path):
    if os.path.isfile(path):
        os.remove(path)


def _create_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    if not os.path.isdir(path):
        raise RuntimeError("can't create dir %s" % path)


def _copy_file(in_path, out_path):
    if not os.path.isfile(in_path):
        raise RuntimeError("can't find torrent path %s" % in_path)
    _remove_file(out_path)
    if os.path.isfile(out_path):
        raise RuntimeError("can't remove old file %s" % out_path)
    _create_dir(os.path.dirname(out_path))
    shutil.copy2(in_path, out_path)


class Transmission(object):
    def __init__(self, log):
        self.client = None
        self.log = log

    def get_setting(self, name):
        return str(Setting.objects.get(name__exact=name).value)

    def connect(self):
        if self.client is not None:
            return
        try:
            address = self.get_setting("SRV_IP")
            port = int(self.get_setting("SRV_PORT"))
            user = self.get_setting("SRV_USER")
            password = self.get_setting("SRV_PASS")
            msg = "conect to %s:%i (%s/%s)" % (address, port, user, password)
            self.log.write(msg)
            self.client = transmissionrpc.Client(address, port, user, password)
        except Exception, e:
            self.log.write("can't connect")
            raise e

    def find_torrent(self):
        self.connect()
        dir_map = {}
        srv_path = self.get_setting("SRV_PATH")
        for it in StorageMap.objects.all():
            remote = os.path.join(srv_path, it.remote_ptr.path)
            dir_map[remote] = it

        for torrent in self.client.get_torrents():
            storage_map = None
            for it in dir_map:
                if len(torrent.downloadDir) > 1 and it in torrent.downloadDir:
                    storage_map = dir_map[it]
                    break
            if storage_map is None:
                continue
            if torrent.uploadRatio < storage_map.min_ratio:
                continue
            is_valid = True
            for file_it in torrent.files().values():
                if file_it["selected"]:
                    if file_it["completed"] != file_it["size"]:
                        is_valid = False
                        break
            if not is_valid:
                continue
            if Torrent.objects.filter(idhash=torrent.hashString).exists():
                continue

            return torrent

        return None

    def _copy_file(self, in_path, out_path):
        try:
            self.log.write("start copy file from \"%s\" to \"%s\""
                           % (in_path, out_path))
            _copy_file(in_path, out_path)
            self.log.write("finish copy file from \"%s\" to \"%s\""
                           % (in_path, out_path))
        except Exception, e:
            self.log.write("can't copy file from \"%s\" to \"%s\""
                           % (in_path, out_path))
            raise e

    def _copy_files(self, files, in_dir, out_dir):
        write_files = []
        try:
            for it in files:
                in_path = os.path.join(in_dir, it["name"])
                out_path = os.path.join(out_dir, it["name"])
                self._copy_file(in_path, out_path)
                write_files.append(out_path)
            return write_files
        except Exception, e:
            for it in write_files:
                _remove_file(it)
            raise e

    def _unsafe_copy_torrent(self, torrent, src_path, trg_path):
        srv_path = self.get_setting("SRV_PATH")
        relpath = os.path.relpath(torrent.downloadDir, srv_path)
        in_dir = os.path.join(src_path, relpath)
        smap = None
        for it in StorageMap.objects.all():
            if(it.remote_ptr.path in torrent.downloadDir):
                smap = it
        if smap is None:
            raise RuntimeError("can't find %s in StorageMap" % torrent.downloadDir)
        out_dir = os.path.join(trg_path, smap.local_ptr.path)
        end_path = os.path.relpath(relpath, smap.remote_ptr.path)
        if end_path != ".":
            out_dir = os.path.join(out_dir, end_path)
        files = [it for it in torrent.files().values() if it["selected"]]
        write_files = self._copy_files(files, in_dir, out_dir)
        t = Torrent.objects.create(storage_map_ptr=smap,
                                   name=torrent.name,
                                   idhash=torrent.hashString)
        self.log.set_torrent(t)
        for it in write_files:
            TorrentFile.objects.create(torent_ptr=t, path=it)

    def copy_torrent(self, torrent):
        try:
            src_path = self.get_setting("LOC_SRC_PATH")
            trg_path = self.get_setting("LOC_TRG_PATH")
            self.log.write("start download torrent \"%s\"" % torrent.name)
            self._unsafe_copy_torrent(torrent, src_path, trg_path)
            self.log.write("finish download torrent \"%s\"" % torrent.name)
        except Exception, e:
            self.log.write("can't copy torrent")
            raise e

    def _remove_torrent_file(self, file_rec):
        try:
            self.log.write("start remove file \"%s\"" % file_rec.path)
            _remove_file(file_rec.path)
            file_rec.delete()
            self.log.write("finish remove file \"%s\"" % file_rec.path)
        except Exception, e:
            self.log.write("can't remove file")
            raise e

    def _remove_torrent_files(self, torrent_rec):
        try:
            self.log.write("start remove files for torrent \"%s\"" %
                           torrent_rec.name)
            for it in TorrentFile.objects.filter(torent_ptr=torrent_rec):
                self._remove_torrent_file(it)
            self.log.write("finish remove files for torrent \"%s\"" %
                           torrent_rec.name)
        except Exception, e:
            self.log.write("can't remove torrent files")
            raise e

    def _remove_torrent_srv(self, torrent_rec):
        try:
            self.log.write("start remove torrent \"%s\" from server" %
                           torrent_rec.name)
            self.connect()
            for torrent in self.client.get_torrents():
                if torrent.hashString == torrent_rec.idhash:
                    self.client.remove_torrent(torrent.id, True)
                    self.log.remove_torrent()
                    torrent_rec.delete()
                    break
            self.log.write("finish remove torrent \"%s\" from server" %
                           torrent_rec.name)
        except Exception, e:
            self.log.write("can't remove torrent from server")
            raise e

    def _remove_torrent(self, torrent_rec):
        try:
            self.log.write("start remove torrent \"%s\"" %
                           torrent_rec.name)
            self._remove_torrent_files(torrent_rec)
            self._remove_torrent_srv(torrent_rec)
            self.log.write("finish remove torrent \"%s\"" %
                           torrent_rec.name)
        except Exception, e:
            self.log.write("can't remove torrent")
            raise e

    def remove_torrent(self, torrent_rec, file_only):
        self.log.set_torrent(torrent_rec)
        if file_only:
            self._remove_torrent_files(torrent_rec)
        else:
            self._remove_torrent(torrent_rec)
