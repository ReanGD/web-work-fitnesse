from django.conf.urls import patterns, url

from manage import views, forms, actions

urlpatterns = patterns('',
    url(r'^$', views.index,
        {}, 'index'),

    url(r'^run_sync_get/$', actions.run_sync_get,
        {}, 'run_sync_get'),

    url(r'^torrent/list/(?P<id>\d+)$', views.torrent,
        {}, 'torrent_list'),
    url(r'^torrent/delete/(?P<id>\d+)$', forms.torrent,
        {'action': 'delete'}, 'torrent_delete'),
    url(r'^torrent/delete_files/(?P<id>\d+)$', forms.torrent,
        {'action': 'delete_files'}, 'torrent_delete_files'),

    url(r'^local_storage/list/$', forms.local_storage,
        {'action': 'list'}, 'local_storage_list'),
    url(r'^local_storage/add/$', forms.local_storage,
        {'action': 'add'}, 'local_storage_add'),
    url(r'^local_storage/edit/(?P<id>\d+)$', forms.local_storage,
        {'action': 'edit'}, name='local_storage_edit'),
    url(r'^local_storage/delete/(?P<id>\d+)$', forms.local_storage,
        {'action': 'delete'}, name='local_storage_delete'),

    url(r'^remote_storage/list/$', forms.remote_storage,
        {'action': 'list'}, 'remote_storage_list'),
    url(r'^remote_storage/add/$', forms.remote_storage,
        {'action': 'add'}, 'remote_storage_add'),
    url(r'^remote_storage/edit/(?P<id>\d+)$', forms.remote_storage,
        {'action': 'edit'}, name='remote_storage_edit'),
    url(r'^remote_storage/delete/(?P<id>\d+)$', forms.remote_storage,
        {'action': 'delete'}, name='remote_storage_delete'),

    url(r'^storage_map/list/$', forms.storage_map,
        {'action': 'list'}, 'storage_map_list'),
    url(r'^storage_map/add/$', forms.storage_map,
        {'action': 'add'}, 'storage_map_add'),
    url(r'^storage_map/edit/(?P<id>\d+)$', forms.storage_map,
        {'action': 'edit'}, name='storage_map_edit'),
    url(r'^storage_map/delete/(?P<id>\d+)$', forms.storage_map,
        {'action': 'delete'}, name='storage_map_delete'),

    url(r'^setting/list/$', forms.setting,
        {'action': 'list'}, 'setting_list'),
    url(r'^setting/add/$', forms.setting,
        {'action': 'add'}, 'setting_add'),
    url(r'^setting/edit/(?P<id>\d+)$', forms.setting,
        {'action': 'edit'}, name='setting_edit'),
    url(r'^setting/delete/(?P<id>\d+)$', forms.setting,
        {'action': 'delete'}, name='setting_delete'),

    url(r'^load_log/get/(?P<id>\d+)$', views.load_log,
        {'action': 'get'}, 'load_log_get'),
)
