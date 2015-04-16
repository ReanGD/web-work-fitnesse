from django.contrib import admin
from manage.models import LocalStorage, RemoteStorage, StorageMap, Torrent, TorrentFile, Setting, LoadLog


admin.site.register(LocalStorage)
admin.site.register(RemoteStorage)
admin.site.register(StorageMap)
admin.site.register(Torrent)
admin.site.register(TorrentFile)
admin.site.register(Setting)
admin.site.register(LoadLog)
