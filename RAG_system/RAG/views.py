import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .ai_system.ingest import ingest_pdf
from .ai_system.qa_chain import answer_question

logger = logging.getLogger(__name__)


def home(request):
    return render(request, 'RAG/home.html')


def upload(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('pdf_file')

        if not uploaded_file:
            return JsonResponse({'error': 'No file selected.'}, status=400)
        if not uploaded_file.name.endswith('.pdf'):
            return JsonResponse({'error': 'Please upload a PDF file.'}, status=400)

        collection_name = uploaded_file.name.lower().replace(' ', '_').replace('.', '_')

        try:
            num_chunks, num_pages = ingest_pdf(uploaded_file, collection_name)
            request.session['collection_name'] = collection_name
            request.session['pdf_name'] = uploaded_file.name
            request.session.modified = True

            return JsonResponse({
                'success': True,
                'pdf_name': uploaded_file.name,
                'num_pages': num_pages,
                'num_chunks': num_chunks,
            })
        except Exception as e:
            logger.exception('upload error')
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'RAG/home.html')


def chat(request):
    pdf_name = request.session.get('pdf_name', '')
    return render(request, 'RAG/home.html', {'pdf_name': pdf_name})


@csrf_exempt
def chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    question = payload.get('message', '').strip()
    history = payload.get('history', [])

    if not question:
        return JsonResponse({'error': 'No question provided'}, status=400)

    collection_name = request.session.get('collection_name')
    if not collection_name:
        return JsonResponse({'error': 'No PDF uploaded yet.'}, status=400)

    try:
        reply, docs = answer_question(question, collection_name, history)
        return JsonResponse({'reply': reply})  # docs excluded — not serializable
    except Exception as e:
        logger.exception('chat_api error')
        return JsonResponse({'error': str(e)}, status=500)