from django.shortcuts import render, get_object_or_404
from ..models import Flow, Node
from ..services.flow_service import extract_nodes_from_flow_data, get_updated_nodes_data
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Max
import traceback
import json
from django.http import HttpResponse


def help_page(request):
    return render(request, 'flow/help.html')


def index(request):
    return render(request, 'flow/index.html')


@csrf_exempt
@require_http_methods(["POST"])
def create_flow(request):
    try:
        name = request.POST.get('name')
        if not name:
            return JsonResponse({'error': 'Flow name is required'}, status=400)
        
        flow = Flow.objects.create(name=name)
        return JsonResponse({'id': flow.id, 'uuid': str(flow.uuid), 'name': flow.name}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def flow_editor(request, flow_uuid):
    try:
        flow = Flow.objects.get(uuid=flow_uuid)
        context = {
            'flow': flow,
            'flow_uuid': str(flow.uuid),  # UUIDを文字列に変換
        }
        return render(request, 'flow/flow_editor.html', context)
    except Flow.DoesNotExist:
        return JsonResponse({'error': 'Flow not found'}, status=404)

    
def list_flows(request):
    flows = Flow.objects.all().values('id', 'name', 'uuid')
    return JsonResponse({'flows': list(flows)})



@csrf_exempt
@require_http_methods(["POST"])
def save_flow(request, flow_uuid):
    try:
        with transaction.atomic():
            flow = get_object_or_404(Flow, uuid=flow_uuid)
            data = json.loads(request.body)
            flow.set_data(data)
            flow.save()
            
            nodes_data = extract_nodes_from_flow_data(data)
            
            # 既存のノードをdf_idでマッピング
            existing_nodes = {str(node.df_id): node for node in flow.nodes.all()}
            updated_or_created_df_ids = set()
            
            # 現在の最大sequence番号を取得
            max_sequence = flow.nodes.aggregate(Max('sequence'))['sequence__max'] or 0

            for node_data in nodes_data:
                df_id = str(node_data['id'])
                defaults = {
                    'name': node_data['name'],
                    'system_prompt': node_data.get('system_prompt', ''),
                    'instruction': node_data.get('instruction', ''),
                    'position_x': node_data['position_x'],
                    'position_y': node_data['position_y'],
                    'ai_model_id': node_data.get('ai_model_id'),
                    'temperature': node_data.get('temperature', 0.5),  # デフォルト値を0.5に設定
                }

                # 既存のノードかどうかをチェック
                if df_id not in existing_nodes:
                    # 新規ノードの場合、max_sequence + 1 を設定
                    max_sequence += 1
                    defaults['sequence'] = max_sequence
                else:
                    # 既存のノードの場合、提供されたsequenceを使用（または既存の値を維持）
                    defaults['sequence'] = node_data.get('sequence', existing_nodes[df_id].sequence)

                node, created = Node.objects.update_or_create(
                    flow=flow,
                    df_id=int(df_id),
                    defaults=defaults
                )
                updated_or_created_df_ids.add(df_id)
            
            # 削除されたノードを処理
            nodes_to_delete = set(existing_nodes.keys()) - updated_or_created_df_ids
            Node.objects.filter(flow=flow, df_id__in=nodes_to_delete).delete()
            
            updated_nodes = get_updated_nodes_data(flow)
            response_data = {
                'status': 'success',
                'nodes': updated_nodes,
                'flow_data': flow.get_data()
            }
            return JsonResponse(response_data)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)

def get_flow_data(request, flow_uuid):
    try:
        flow = Flow.objects.get(uuid=flow_uuid)
        flow_data = flow.get_data()
        
        if not flow_data or 'drawflow' not in flow_data or 'Home' not in flow_data['drawflow']:
            # フローデータが存在しない場合、空のフローデータを返す
            return JsonResponse({
                'drawflow': {
                    'Home': {
                        'data': {}
                    }
                }
            })
        
        nodes = Node.objects.filter(flow=flow).values(
            'id', 'df_id', 'name', 'system_prompt', 'instruction', 'sequence', 
            'position_x', 'position_y', 'ai_model_id', 'temperature',
        )
        for node in nodes:
            node_id = str(node['df_id'])
            if node_id in flow_data['drawflow']['Home']['data']:
                flow_data['drawflow']['Home']['data'][node_id]['data'] = node
        
        return JsonResponse(flow_data)
    except Flow.DoesNotExist:
        return JsonResponse({'error': 'Flow not found'}, status=404)  

def get_node_info(request, flow_id, node_id):
    flow = get_object_or_404(Flow, id=flow_id)
    node = get_object_or_404(Node, id=node_id, flow=flow)
    
    node_info = {
        'id': node.id,
        'name': node.name,
        'system_prompt': node.system_prompt,
        'instruction': node.instruction,
        'sequence': node.sequence,
        'ai_model_id': node.ai_model_id if node.ai_model else None
    }
    
    return JsonResponse(node_info)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_flow(request, flow_uuid):
    try:
        flow = Flow.objects.get(uuid=flow_uuid)
        flow.delete()
        return HttpResponse(status=204)
    except Flow.DoesNotExist:
        return JsonResponse({'error': 'Flow not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
