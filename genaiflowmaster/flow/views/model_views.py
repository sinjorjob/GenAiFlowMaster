
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ..models import Flow, Node, AIModel
from django.http import JsonResponse
import json

@csrf_exempt
@require_http_methods(["POST"])
def model_settings(request):
    try:
        data = json.loads(request.body)
        model_type = data.get('model_type')
        name = data.get('name')
        api_key = data.get('api_key')
        api_version = data.get('api_version')
        endpoint = data.get('endpoint')

        model = AIModel.objects.create(
            model_type=model_type,
            name=name,
            api_key=api_key,
            api_version=api_version,
            endpoint=endpoint
        )
        return JsonResponse({'status': 'success', 'id': model.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    


def get_ai_models(request):
    models = AIModel.objects.all().values('id', 'name', 'model_type')
    return JsonResponse({'models': list(models)})


@require_http_methods(["GET"])
def get_ai_model(request):
    model_type = request.GET.get('model_type', 'OpenAI')
    try:
        model = AIModel.objects.filter(model_type=model_type).first()
        if model:
            return JsonResponse({
                'id': model.id,
                'model_type': model.model_type,
                'name': model.name,
                'api_key': model.api_key,
                'api_version': model.api_version,
                'endpoint': model.endpoint
            })
        else:
            return JsonResponse({}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def save_or_update_model(request):
    try:
        data = json.loads(request.body)
        model, created = AIModel.objects.update_or_create(
            model_type=data.get('model_type'),
            defaults={
                'name': data.get('name'),
                'api_key': data.get('api_key'),
                'api_version': data.get('api_version', ''),
                'endpoint': data.get('endpoint', '')
            }
        )
        return JsonResponse({'status': 'success', 'id': model.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    