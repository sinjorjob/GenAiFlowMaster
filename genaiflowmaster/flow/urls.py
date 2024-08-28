from django.urls import path
from . import views
from .views import flow_views, model_views, execution_views, history_views, chat_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Flow views
    path('', flow_views.index, name='index'),
    path('create_flow/', flow_views.create_flow, name='create_flow'),
    path('<uuid:flow_uuid>/flow/', flow_views.flow_editor, name='flow_editor'),
    path('list_flows/', flow_views.list_flows, name='list_flows'),
    path('save_flow/<uuid:flow_uuid>/', flow_views.save_flow, name='save_flow'),
    path('get_flow_data/<uuid:flow_uuid>/', flow_views.get_flow_data, name='get_flow_data'),
    path('get_node_info/<int:flow_id>/<int:node_id>/', flow_views.get_node_info, name='get_node_info'),
    path('delete_flow/<uuid:flow_uuid>/', flow_views.delete_flow, name='delete_flow'),
    
    # Model views
    path('model_settings/', model_views.model_settings, name='model_settings'),
    path('get_ai_models/', model_views.get_ai_models, name='get_ai_models'),
    path('get_ai_model/', model_views.get_ai_model, name='get_ai_model'),
    path('save_or_update_model/', model_views.save_or_update_model, name='save_or_update_model'),
    
    # Execution views
    path('execute_flow/<int:flow_id>/', execution_views.execute_flow, name='execute_flow'),
    path('get_flow_status/<int:flow_run_id>/', execution_views.get_flow_status, name='get_flow_status'),
    path('get_flow_run_status/<int:flow_run_id>/', execution_views.get_flow_run_status, name='get_flow_run_status'),
    
    # History views
    path('<uuid:flow_uuid>/flow_result/<int:flow_run_id>/', history_views.flow_result, name='flow_result'),
    path('<uuid:flow_uuid>/flow_run_history/', history_views.flow_run_history, name='flow_run_history'),
    path('delete_flow_run/<int:run_id>/', history_views.delete_flow_run, name='delete_flow_run'),

    # Chat views
    path('<uuid:flow_uuid>/chat_input/', chat_views.chat_input, name='chat_input'),

    # ヘルプビューを追加
    path('help/', flow_views.help_page, name='help_page'),
  
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)