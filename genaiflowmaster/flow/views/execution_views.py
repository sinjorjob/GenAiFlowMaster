from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from ..models import Flow, FlowRun, NodeRunLog
from ..ai_handlers import get_ai_handler

from django.db import transaction
from django.utils import timezone
import json
import threading


@csrf_exempt
@require_http_methods(["POST"])
def execute_flow(request, flow_id):
    flow = get_object_or_404(Flow, id=flow_id)
    data = json.loads(request.body)
    initial_input = data.get('input', '')

    with transaction.atomic():
        flow_run = FlowRun.objects.create(flow=flow)
        flow_run.set_flow_data_snapshot(flow.get_data())
        flow_run.save()
        
        nodes = flow.nodes.all().order_by('sequence')
        for node in nodes:
            node_run_log = NodeRunLog.objects.create(
                flow_run=flow_run,
                node=node,
                status=NodeRunLog.NodeStatus.PENDING
            )
            node_data_snapshot = {
                'id': node.id,
                'df_id': node.df_id,
                'name': node.name,
                'system_prompt': node.system_prompt,
                'instruction': node.instruction,
                'sequence': node.sequence,
                'position_x': node.position_x,
                'position_y': node.position_y,
                'ai_model_id': node.ai_model_id,
            }
            node_run_log.set_node_data_snapshot(node_data_snapshot)
            node_run_log.save()
    
    # バックグラウンドでフローを実行
    thread = threading.Thread(target=execute_flow_background, args=(flow_run.id, initial_input))
    thread.start()

    return JsonResponse({"status": "success", "flow_uuid": flow.uuid, "flow_run_id": flow_run.id})


def execute_flow_background(flow_run_id, initial_input):
    flow_run = FlowRun.objects.get(id=flow_run_id)
    nodes = flow_run.flow.nodes.all().order_by('sequence')
    previous_output = {"result": initial_input}

    for node in nodes:
        node_log = NodeRunLog.objects.get(flow_run=flow_run, node=node)
        node_log.set_running()

        try:
            ai_model = node.ai_model
            if not ai_model:
                raise ValueError(f"No AI model specified for node {node.name}")
            
            ai_handler = get_ai_handler(ai_model.model_type)
            
            replaced_instruction = replace_input_variable(node.instruction, previous_output["result"])

            input_data = {
                "previous_output": previous_output,
                "node_data": {
                    "name": node.name,
                    "system_prompt": node.system_prompt,
                    "instruction": replaced_instruction,
                }
            }
            node_log.input_data = input_data
            node_log.save()

            output_data = ai_handler.process_request(ai_model, input_data)
            
            # AIモデルからの応答を確実に記録
            node_log.output_data = output_data
            node_log.set_completed()
            node_log.save()

            previous_output = output_data

        except Exception as e:
            node_log.set_failed()
            node_log.output_data = {"error": str(e)}
            node_log.save()
            break

    flow_run.status = 'COMPLETED' if node_log.status == NodeRunLog.NodeStatus.COMPLETED else 'FAILED'
    flow_run.completed_at = timezone.now()
    flow_run.save()

def get_flow_status(request, flow_run_id):
    flow_run = get_object_or_404(FlowRun, id=flow_run_id)
    node_logs = NodeRunLog.objects.filter(flow_run=flow_run)

    node_statuses = []
    for log in node_logs:
        node_statuses.append({
            'node_id': log.node.id,
            'status': log.status,
            'is_running': log.is_running,
        })

    return JsonResponse({
        'flow_status': flow_run.status,
        'node_statuses': node_statuses,
    })
    
    
def get_flow_run_status(request, flow_run_id):
    flow_run = FlowRun.objects.get(id=flow_run_id)
    node_logs = NodeRunLog.objects.filter(flow_run=flow_run)

    node_data = []
    for log in node_logs:
        node_data.append({
            'node_id': log.node.df_id,
            'status': log.status,
            'input_data': log.input_data,
            'output_data': log.output_data,
        })

    return JsonResponse({
        'flow_status': flow_run.status,
        'node_data': node_data,
    })
    
    
def replace_input_variable(text, input_value):
    return text.replace('{{input}}', str(input_value))
    