# 🚀 Space Research AI

**AI-powered Space Research Assistant** built using Django, RAG (Retrieval-Augmented Generation) architecture, and Generative AI to analyze satellite and space-related documents through intelligent question answering.

## 📋 Overview

Space Research AI is a web application that allows users to upload PDF mission reports and CSV satellite databases, then ask natural language questions about the content. The system uses advanced RAG techniques combined with LLM-powered question answering to provide accurate, context-grounded responses with real-time quality metrics.

## ✨ Key Features

- **📄 Multi-Format Document Support**: Upload PDF files or CSV databases
- **🔍 Intelligent Document Processing**: Automatic chunking and semantic embedding
- **💬 Conversational Q&A**: Ask questions and get context-grounded answers
- **📊 Real-Time Evaluation Metrics**:
  - **Relevance Score**: Measures keyword matching between query and retrieved documents
  - **Faithfulness Score**: Ensures answers are grounded in retrieved context
  - **Completeness Score**: Evaluates answer quality and informativeness
- **📈 Quality Dashboard**: Visual metrics panel displays evaluation scores for every answer
- **🎯 Chat History**: Maintains conversation context for improved multi-turn interactions
- **⚡ Fast Performance**: Optimized chunking with 1000-char chunks and 200-char overlap

## 🏗️ Architecture

```
Document Upload (PDF/CSV)
        ↓
Document Ingestion & Splitting (1000 char chunks)
        ↓
Semantic Embedding (HuggingFace all-MiniLM-L6-v2)
        ↓
Vector Storage (ChromaDB)
        ↓
Query Processing & Retrieval (Top-4 chunks)
        ↓
LLM Generation (Groq Llama 3.3 70B)
        ↓
Quality Evaluation (3 Metrics)
        ↓
Response + Metrics Display
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend Framework | Django 6.0.3 |
| Web Server | Django Development Server |
| LLM Provider | Groq (Llama 3.3 70B) |
| Vector Database | ChromaDB 1.5.5 |
| Embeddings | HuggingFace (all-MiniLM-L6-v2) |
| Document Loaders | LangChain |
| Frontend | HTML/CSS/JavaScript |
| Database | SQLite3 |
| Environment | Python 3.x |

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip package manager
- Git (optional)

### Step 1: Clone or Download the Project
```bash
cd space-research-ai
```

### Step 2: Create Virtual Environment
```bash
python -m venv .venv
```

### Step 3: Activate Virtual Environment

**Windows:**
```bash
.\.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Set Environment Variables
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.3-70b-versatile
```

Get your Groq API key from [console.groq.com](https://console.groq.com)

### Step 6: Run Server
```bash
cd RAG_system
python manage.py runserver
```

Access the application at `http://localhost:8000`

## 📁 Project Structure

```
space-research-ai/
├── RAG_system/                 # Django Project
│   ├── RAG/                   # Django App
│   │   ├── ai_system/         # AI Components
│   │   │   ├── ingest.py      # Document ingestion & embedding
│   │   │   ├── qa_chain.py    # Question answering pipeline
│   │   │   ├── evaluation.py  # RAG evaluation metrics
│   │   │   └── validator.py   # Data validation
│   │   ├── templates/         # HTML Templates
│   │   │   └── RAG/
│   │   │       ├── landing.html
│   │   │       └── home.html
│   │   ├── static/            # Frontend Assets
│   │   │   ├── CSS/
│   │   │   │   ├── home.css
│   │   │   │   └── landing.css
│   │   │   └── JS/
│   │   │       ├── home.js
│   │   │       └── landing.js
│   │   ├── views.py           # View handlers
│   │   ├── models.py          # Database models
│   │   └── admin.py           # Admin configuration
│   ├── chroma_db/             # Vector store (auto-generated)
│   ├── manage.py              # Django CLI
│   └── db.sqlite3             # SQLite database
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🚀 Usage

### 1. Landing Page
Navigate to `http://localhost:8000/` to see the landing page with project information.

### 2. Upload Document
- Click **"Home"** to go to the chat interface
- Upload a PDF file (mission reports) or CSV file (satellite data)
- System automatically processes and indexes the document

### 3. Ask Questions
- Type your question in the chat input
- Press Enter or click Send
- System retrieves relevant context and generates an answer
- Quality metrics display in real-time on the left panel

### 4. View Metrics
The metrics panel shows three key scores:
- **Relevance** (0.0-1.0): Percentage of retrieved chunks containing query keywords
- **Faithfulness** (0.0-1.0): Percentage of answer sentences grounded in retrieved context
- **Completeness** (0.0-1.0): Quality assessment based on answer length and content

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|------------|
| GET | `/` | Landing page |
| GET | `/home/` | Main chat interface |
| POST | `/upload-pdf/` | Upload PDF document |
| POST | `/upload-csv/` | Upload CSV document |
| POST | `/chat-api/` | Send question and get answer |
| GET | `/metrics/` | Get session evaluation metrics |

### Example Request: Ask a Question
```bash
curl -X POST http://localhost:8000/chat-api/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What satellites were launched in 2024?",
    "history": []
  }'
```

### Example Response
```json
{
  "reply": "Based on the satellite database...",
  "metrics": {
    "retrieval_relevance": 0.85,
    "faithfulness": 0.92,
    "completeness": 0.88,
    "overall": 0.88
  }
}
```

## 📊 Evaluation Metrics Explained

### 1. Retrieval Relevance
- **What**: Measures how well retrieved documents match the query
- **How**: Counts chunks containing keywords from the question (excluding stop words)
- **Formula**: `relevant_chunks / total_retrieved_chunks`

### 2. Faithfulness
- **What**: Ensures the answer is grounded in retrieved context
- **How**: Checks if answer sentences contain words from the context
- **Formula**: `grounded_sentences / total_sentences`

### 3. Completeness
- **What**: Evaluates answer quality and informativeness
- **How**: Penalizes short answers, refusal phrases, and missing information
- **Scoring**:
  - Complete answers (>25 words): 1.0
  - Medium answers (10-25 words): 0.7
  - Short answers (<10 words): 0.4
  - Refusal phrases: 0.3

## ⚙️ Configuration

### Document Processing
**File**: `RAG_system/RAG/ai_system/ingest.py`
- Chunk Size: 1000 characters
- Chunk Overlap: 200 characters
- Embedding Model: `sentence-transformers/all-MiniLM-L6-v2`

### RAG Pipeline
**File**: `RAG_system/RAG/ai_system/qa_chain.py`
- Retrieval K: Top 4 chunks
- LLM Model: Llama 3.3 70B (via Groq)
- Temperature: Default (0.7)

### Supported File Types
- PDF files (any size)
- CSV files (with automatic data cleaned)

## 🌐 Frontend Components

### Landing Page
- Project overview
- Feature highlights
- Call-to-action button

### Home/Chat Interface
- **Left Panel**: Real-time quality metrics with animated progress bars
- **Main Chat Area**: Message history and input field
- **Top Bar**: Active document display and upload button
- **Responsive Design**: Works on desktop, tablet, and mobile

## 🔒 Security Notes

- CSRF protection enabled on all forms
- Session-based authentication for document management
- SQLite database for local development
- `.env` file for sensitive credentials (not committed to git)

## 🚀 Future Enhancements

- [ ] Multi-document context support
- [ ] User authentication and profiles
- [ ] Search history and saved searches
- [ ] Custom evaluation metrics
- [ ] Export results to PDF/JSON
- [ ] Advanced prompt engineering UI
- [ ] Real-time collaborative chat
- [ ] Integration with more LLM providers
- [ ] Production-grade database (PostgreSQL)
- [ ] Docker containerization
- [ ] Cloud deployment options (AWS/Azure/GCP)

## 📝 Dependencies Overview

### Core AI/ML
- `langchain`: Unified interface for LLMs and embeddings
- `langchain-chroma`: ChromaDB integration
- `langchain-groq`: Groq API integration
- `chromadb`: Vector database
- `huggingface_hub`: HuggingFace model access

### Document Processing
- `PyPDF`: PDF parsing
- `pandas`: CSV handling

### Web Framework
- `Django`: Web framework
- `python-dotenv`: Environment variable management

### Utilities
- `httpx`: HTTP client
- `pydantic`: Data validation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License

This project is open source. See LICENSE file for details.

## 💡 Tips & Best Practices

1. **Optimize Uploads**: Use clear, well-structured documents for better retrieval
2. **Ask Specific Questions**: More specific queries yield better results
3. **Multi-turn Conversations**: The system maintains context from previous questions
4. **Monitor Metrics**: Low relevance? Your question might not match document keywords
5. **Batch Processing**: For large document sets, consider uploading them separately

## 🐛 Troubleshooting

### "No response" Error
- Check `.env` file has valid `GROQ_API_KEY`
- Verify internet connection (Groq is cloud-based)

### Low Quality Scores
- Upload documents with clearer structure
- Ask more specific, keyword-rich questions

### Slow Performance
- Consider splitting large PDFs into smaller documents
- Reduce chat history size

## 📞 Support

For issues or questions:
1. Check existing GitHub issues
2. Create a detailed bug report with steps to reproduce
3. Include relevant logs and screenshots
4. luitelbigyan344@gmail.com
5. +977 9840977554
6. https://www.linkedin.com/in/bigyan-luitel-b5245230b/

---

**Happy researching! 🌌**