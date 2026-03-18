from django.shortcuts import render

# Create your views here.
def home(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('pdf_file')

        if not uploaded_file:
            return render(request, 'RAG/home.html', {'error': 'No file selected.'})

        if not uploaded_file.name.endswith('.pdf'):
            return render(request, 'RAG/home.html', {'error': 'Please upload a PDF file.'})

        collection_name = uploaded_file.name.lower().replace(' ', '_').replace('.', '_')

        try:
            num_chunks, num_pages = ingest_pdf(uploaded_file, collection_name)

            request.session['collection_name'] = collection_name
            request.session['pdf_name'] = uploaded_file.name
            request.session.modified = True

            return render(request, 'RAG/home.html', {
                'success': True,
                'num_chunks': num_chunks,
                'num_pages': num_pages,
                'pdf_name': uploaded_file.name,
            })

        except Exception as e:
            return render(request, 'RAG/home.html', {'error': f'Failed to process PDF: {str(e)}'})

    return render(request, 'RAG/home.html')

from .ai_system.qa_chain import answer_question
from .ai_system.ingest import ingest_pdf

def upload_pdf(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['pdf_file']
        collection_name = request.POST.get('collection_name', 'default_collection')
        num_chunks, num_pages = ingest_pdf(uploaded_file, collection_name)
        return render(request, 'RAG/upload_success.html', {
            'num_chunks': num_chunks,
            'num_pages': num_pages,
            'collection_name': collection_name
        })
    return render(request, 'RAG/home.html')
