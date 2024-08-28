from django.db import models
import json
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Flow(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict, blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def __str__(self):
        return self.name

    def set_data(self, data):
        if isinstance(data, str):
            self.data = json.loads(data)
        else:
            self.data = data
            
    def get_data(self):
        if isinstance(self.data, str):
            return json.loads(self.data)
        return self.data


class AIModel(models.Model):
    MODEL_TYPES = [
        ('OpenAI', 'OpenAI'),
        ('AzureOpenAI', 'Azure OpenAI'),
        ('Claude', 'Claude'),
    ]
    name = models.CharField(max_length=200)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    api_key = models.CharField(max_length=200, blank=True, null=True)
    api_version = models.CharField(max_length=50, blank=True, null=True)
    endpoint = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.model_type} - {self.name}"
  
    
class Node(models.Model):
    flow = models.ForeignKey(Flow, on_delete=models.CASCADE, related_name='nodes')
    name = models.CharField(max_length=200)
    system_prompt = models.TextField(blank=True)
    instruction = models.TextField(blank=True)
    sequence = models.IntegerField(default=1)
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)
    ai_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True)
    df_id = models.PositiveIntegerField(null=True, blank=True)
    temperature = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    def __str__(self):
        return f"{self.flow.name} - {self.name}"
    

class FlowRun(models.Model):
    flow = models.ForeignKey(Flow, on_delete=models.CASCADE, related_name='runs')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='RUNNING')
    flow_data_snapshot = models.JSONField(default=dict)  # フロー実行時のフローデータのスナップショット

    def __str__(self):
        return f"Run of {self.flow.name} at {self.started_at}"

    def set_flow_data_snapshot(self, data):
        self.flow_data_snapshot = json.dumps(data)

    def get_flow_data_snapshot(self):
        return json.loads(self.flow_data_snapshot)

class NodeRunLog(models.Model):
    class NodeStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        RUNNING = 'RUNNING', 'Running'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    flow_run = models.ForeignKey('FlowRun', on_delete=models.CASCADE, related_name='node_logs')
    node = models.ForeignKey('Node', on_delete=models.CASCADE)
    sequence = models.IntegerField(default=1)
    input_data = models.JSONField(default=dict, blank=True)
    output_data = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=NodeStatus.choices,
        default=NodeStatus.PENDING,
    )
    node_data_snapshot = models.JSONField(default=dict)  # 新しいフィールド

    def set_running(self):
        self.status = self.NodeStatus.RUNNING
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])

    def set_completed(self):
        self.status = self.NodeStatus.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])

    def set_failed(self):
        self.status = self.NodeStatus.FAILED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])

    def set_node_data_snapshot(self, data):
        self.node_data_snapshot = json.dumps(data)

    def get_node_data_snapshot(self):
        return json.loads(self.node_data_snapshot)

    @property
    def is_running(self):
        return self.status == self.NodeStatus.RUNNING

    def __str__(self):
        return f"Log of {self.node.name} in {self.flow_run} - Status: {self.status}"

    class Meta:
        ordering = ['sequence']