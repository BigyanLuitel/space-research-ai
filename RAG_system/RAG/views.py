import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .ai_system.ingest import ingest_pdf, ingest_csv
from .ai_system.qa_chain import answer_question


logger = logging.getLogger(__name__)

def landing(request):
    return render(request, 'RAG/landing.html')
def home(request):
    return render(request, 'RAG/home.html')


def upload_pdf(request):
    if request.method != 'POST':
        return render(request, 'RAG/home.html')

    uploaded_file = request.FILES.get('pdf_file')

    if not uploaded_file:
        return JsonResponse({'error': 'No file selected.'}, status=400)
    if not uploaded_file.name.lower().endswith('.pdf'):
        return JsonResponse({'error': 'Please upload a PDF file.'}, status=400)

    collection_name = uploaded_file.name.lower().replace(' ', '_').replace('.', '_')

    try:
        num_chunks, num_pages = ingest_pdf(uploaded_file, collection_name)
        request.session['collection_name'] = collection_name
        request.session['file_name'] = uploaded_file.name
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'file_name': uploaded_file.name,
            'num_pages': num_pages,
            'num_chunks': num_chunks,
        })
    except Exception as e:
        logger.exception('upload_pdf error')
        return JsonResponse({'error': str(e)}, status=500)


def upload_csv(request):
    if request.method != 'POST':
        return render(request, 'RAG/home.html')

    uploaded_file = request.FILES.get('csv_file')

    if not uploaded_file:
        return JsonResponse({'error': 'No file selected.'}, status=400)
    if not uploaded_file.name.lower().endswith('.csv'):
        return JsonResponse({'error': 'Please upload a CSV file.'}, status=400)

    collection_name = uploaded_file.name.lower().replace(' ', '_').replace('.', '_')

    try:
        # cleaning happens inside ingest_csv
        num_chunks, num_rows = ingest_csv(uploaded_file, collection_name)
        request.session['collection_name'] = collection_name
        request.session['file_name'] = uploaded_file.name
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'file_name': uploaded_file.name,
            'num_rows': num_rows,
            'num_chunks': num_chunks,
        })
    except Exception as e:
        logger.exception('upload_csv error')
        return JsonResponse({'error': str(e)}, status=500)


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
        return JsonResponse({'error': 'No file uploaded yet.'}, status=400)

    try:
        reply, docs, metrics = answer_question(question, collection_name, history)
        return JsonResponse({'reply': reply, 'metrics': metrics})
    except Exception as e:
        logger.exception('chat_api error')
        return JsonResponse({'error': str(e)}, status=500)

def metrics_dashboard(request):
    """
    GET /metrics/ — returns aggregate scores for the session.
    Useful for checking quality after a demo.
    """
    eval_log = request.session.get('eval_log', [])
    if not eval_log:
        return JsonResponse({'message': 'No evaluations yet.'})

    count = len(eval_log)
    return JsonResponse({
        'total_queries':      count,
        'avg_retrieval':      round(sum(m['retrieval_relevance'] for m in eval_log) / count, 2),
        'avg_faithfulness':   round(sum(m['faithfulness']        for m in eval_log) / count, 2),
        'avg_completeness':   round(sum(m['completeness']        for m in eval_log) / count, 2),
        'avg_overall':        round(sum(m['overall']             for m in eval_log) / count, 2),
        'recent':             eval_log[-5:],
    })