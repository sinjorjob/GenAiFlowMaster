from ..models import Node


def extract_nodes_from_flow_data(data):
    nodes = []
    for node_id, node_data in data['drawflow']['Home']['data'].items():
        nodes.append({
            'id': int(node_id),
            'name': node_data['data'].get('name', ''),
            'system_prompt': node_data['data'].get('system_prompt', ''),
            'instruction': node_data['data'].get('instruction', ''),
            'sequence': node_data['data'].get('sequence') or 0,  # デフォルト値を0に設定
            'position_x': node_data['pos_x'],
            'position_y': node_data['pos_y'],
            'ai_model_id': node_data['data'].get('ai_model_id'),
            'temperature': node_data['data'].get('temperature', 0.5),
        })
    return nodes


def update_or_create_nodes(flow, nodes_data):
    existing_nodes = {str(node.id): node for node in flow.nodes.all()}
    created_or_updated_nodes = []
    for node_data in nodes_data:
        node_id = str(node_data['id'])
        if node_id in existing_nodes:
            # 既存のノードを更新
            node = existing_nodes[node_id]
            for key, value in node_data.items():
                setattr(node, key, value)
            node.save()
        else:
            # 新しいノードを作成（IDを指定しない）
            node = Node.objects.create(
                flow=flow,
                name=node_data['name'],
                system_prompt=node_data['system_prompt'],
                instruction=node_data['instruction'],
                sequence=node_data['sequence'],
                position_x=node_data['position_x'],
                position_y=node_data['position_y'],
                ai_model_id=node_data['ai_model_id'],
            )
        created_or_updated_nodes.append(node)
    return created_or_updated_nodes


def get_updated_nodes_data(flow):
    return list(flow.nodes.values(
        'id', 'df_id', 'name', 'system_prompt', 'instruction', 'sequence', 
        'position_x', 'position_y', 'ai_model_id', 'temperature'
    ))

def assign_sequence_numbers(nodes_data):
    def get_sort_key(node):
        sequence = node.get('sequence')
        if sequence is None or sequence == '':
            return float('inf'), node['id']
        try:
            return int(sequence), node['id']
        except ValueError:
            return float('inf'), node['id']

    sorted_nodes = sorted(nodes_data, key=get_sort_key)
    
    next_sequence = 1  # 1から始まるように変更

    for node in sorted_nodes:
        node['sequence'] = next_sequence
        next_sequence += 1

    return sorted_nodes
