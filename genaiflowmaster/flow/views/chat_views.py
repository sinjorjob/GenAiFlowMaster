from django.shortcuts import render, get_object_or_404
from ..models import Flow

    

def chat_input(request,flow_uuid):
    flow = get_object_or_404(Flow,uuid=flow_uuid)
    return render(request, 'flow/chat_input.html', {'flow': flow})
