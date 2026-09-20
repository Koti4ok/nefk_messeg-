import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .chatbot import get_bot_answer


@require_POST
def chatbot_api(request):
    """AJAX endpoint: POST {message: "..."} → {answer: "..."}"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
    except Exception:
        message = request.POST.get('message', '').strip()

    if not message:
        return JsonResponse({'answer': 'Напиши своє питання! 😊'})

    answer = get_bot_answer(message)
    # Перетворюємо **bold** в <strong>
    import re
    answer_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', answer)
    # Переноси рядків → <br>
    answer_html = answer_html.replace('\n', '<br>')

    return JsonResponse({'answer': answer_html, 'raw': answer})
