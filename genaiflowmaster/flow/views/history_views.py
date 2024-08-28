
from django.shortcuts import render, get_object_or_404
from ..models import FlowRun, NodeRunLog
from ..models import Flow
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json

def flow_result(request, flow_uuid, flow_run_id):
    flow_run = get_object_or_404(FlowRun, id=flow_run_id)
    flow = flow_run.flow
    node_run_logs = NodeRunLog.objects.filter(flow_run=flow_run).order_by('sequence')

    flow_data = flow_run.get_flow_data_snapshot()  # スナップショットからフローデータを取得

    node_run_logs_data = [
        {
            "node_id": log.get_node_data_snapshot()['df_id'],
            "node_name": log.get_node_data_snapshot()['name'],
            "sequence": log.get_node_data_snapshot()['sequence'],
            "status": log.status,
            "input_data": log.input_data,
            "output_data": log.output_data,
        } for log in node_run_logs
    ]

    context = {
        "flow": flow,
        "flow_run": flow_run,
        "flow_data": json.dumps(flow_data),
        "node_run_logs": json.dumps(node_run_logs_data),
    }

    return render(request, 'flow/flow_result.html', context)

def flow_run_history(request, flow_uuid):
    flow = get_object_or_404(Flow, uuid=flow_uuid)
    flow_runs = FlowRun.objects.filter(flow=flow).order_by('-started_at')
    context = {
        'flow': flow,
        'flow_runs': flow_runs
    }
    return render(request, 'flow/flow_run_history.html', context)


@require_POST
def delete_flow_run(request, run_id):
    run = get_object_or_404(FlowRun, id=run_id)
    try:
        run.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

    