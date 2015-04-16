# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse
from django_ajax.decorators import ajax
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404

from manage.db_logger import DbLogger
from manage.models import StorageMap, Torrent, TorrentFile


def index(request):
    items = StorageMap.objects.all()
    if len(items) == 0:
        tabid = "id_local_storage"
    else:
        tabid = "id_%i" % items[0].id
    tabid = request.session.get('tabid', tabid)
    return render(request, 'manage/index.html',
                  {'items': items, 'load_tab': tabid})


@ajax
def torrent(request, id):
    storage_map = get_object_or_404(StorageMap, pk=id)
    header = storage_map.local_ptr.name + ":"
    request.session['tabid'] = "id_%i" % storage_map.id

    items = Torrent.objects.filter(storage_map_ptr=id)
    for it in items:
        it.files = TorrentFile.objects.filter(torent_ptr=it)
        it.url_delete = reverse('manage:torrent_delete', args=[it.id])
        it.url_delete_files = reverse('manage:torrent_delete_files',
                                      args=[it.id])

    return render(request, 'manage/torrent_view.html',
                  {'items': items, 'header': header})


def load_log(request, action, id):
    return HttpResponse(json.dumps(DbLogger(id).json_result()),
                        content_type="application/json")
