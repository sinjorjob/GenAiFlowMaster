from django.contrib import admin
from django.utils.html import format_html
from .models import Flow, Node, AIModel, FlowRun, NodeRunLog
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse
from django.db import models
from django import forms  

class TemperatureRangeInput(forms.NumberInput):
    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        attrs.update({
            'type': 'range',
            'step': '0.1',
            'min': '0',
            'max': '1',
        })
        return super().render(name, value, attrs, renderer)
    
class NodeInline(admin.TabularInline):
    model = Node
    extra = 1
   
@admin.register(Flow)
class FlowAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    inlines = [NodeInline]

@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'flow', 'sequence', 'ai_model', 'temperature')
    list_filter = ('flow', 'ai_model')
    search_fields = ('name', 'flow__name', 'ai_model__name')
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'temperature':
            kwargs['widget'] = TemperatureRangeInput()
        return super().formfield_for_dbfield(db_field, request, **kwargs)
@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'model_type', 'api_version', 'endpoint')
    list_filter = ('model_type',)
    search_fields = ('name', 'model_type')

class NodeRunLogInline(admin.TabularInline):
    model = NodeRunLog
    extra = 0
    readonly_fields = ('id', 'node', 'started_at', 'completed_at', 'status')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(NodeRunLog)
class NodeRunLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'node', 'flow_run', 'started_at', 'completed_at', 'status', 'delete_button')
    list_filter = ('flow_run__flow', 'status')
    search_fields = ('node__name', 'flow_run__flow__name')
    readonly_fields = ('id', 'flow_run', 'node', 'input_data', 'output_data', 'started_at', 'completed_at')
    actions = ['delete_selected_node_run_logs']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('node', 'flow_run__flow')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def delete_button(self, obj):
        url = reverse('admin:flow_noderunlog_delete', args=[obj.pk])
        return format_html('<a class="button" href="{}">削除</a>', url)
    delete_button.short_description = '操作'

    def delete_model(self, request, obj):
        flow_run = obj.flow_run
        super().delete_model(request, obj)
        self._update_flow_run_status(flow_run)

    def delete_queryset(self, request, queryset):
        flow_runs = set(queryset.values_list('flow_run', flat=True))
        super().delete_queryset(request, queryset)
        for flow_run_id in flow_runs:
            self._update_flow_run_status(FlowRun.objects.get(id=flow_run_id))

    def _update_flow_run_status(self, flow_run):
        # FlowRunのステータスを更新するロジック
        if flow_run.node_logs.count() == 0:
            flow_run.status = 'DELETED'
        else:
            # 他のステータス更新ロジックをここに追加
            pass
        flow_run.save()

    @admin.action(description="選択したNode Run Logsを削除")
    def delete_selected_node_run_logs(self, request, queryset):
        if request.POST.get('post'):
            flow_runs = set(queryset.values_list('flow_run', flat=True))
            deleted_count = queryset.count()
            queryset.delete()
            
            for flow_run_id in flow_runs:
                self._update_flow_run_status(FlowRun.objects.get(id=flow_run_id))
            
            self.message_user(request, f"{deleted_count}個のNode Run Logが削除されました。", messages.SUCCESS)
        else:
            return self.delete_selected_confirmation(request, queryset)

    def delete_selected_confirmation(self, request, queryset):
        return render(request, 'admin/custom_delete_selected_confirmation.html', {
            'queryset': queryset,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        })

@admin.register(FlowRun)
class FlowRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'flow', 'status', 'started_at', 'completed_at')
    # 他の既存の設定

    def delete_model(self, request, obj):
        obj.node_logs.all().delete()
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.node_logs.all().delete()
        queryset.delete()