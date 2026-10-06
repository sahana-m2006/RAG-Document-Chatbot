# 📄 RAG Document Chatbot

An AI-powered document question-answering chatbot built using **Retrieval-Augmented Generation (RAG)**.

The system allows users to upload **PDF, DOCX, and TXT documents** and ask questions in natural language. The application retrieves relevant information from the uploaded documents and uses that information as context to generate grounded answers.

---

## ✨ Features

- 📄 Upload PDF, DOCX, and TXT documents
- 📚 Support for multiple documents
- 🔎 Semantic document retrieval
- 🧠 Sentence Transformer embeddings
- 🗄️ ChromaDB vector database
- 🤖 Local DeepSeek-R1 LLM using Ollama
- 📝 OCR support for scanned PDFs
- ✂️ Text chunking with overlap
- 📌 Source and page references
- 💬 Chat history
- 🚫 "Information not found" handling
- 🔍 Retrieved context inspection
- 🗑️ Clear chat functionality
- 🗑️ Clear knowledge base functionality
- 🎨 Streamlit web interface
- 🔐 Environment-variable support for secrets

---

## 🧠 How It Works

The application follows a Retrieval-Augmented Generation pipeline:

```text
                    User
                     │
                     ▼
             Upload Documents
                     │
                     ▼
          Document Processing
                     │
          ┌──────────┴──────────┐
          │                     │
       PDF/DOCX/TXT        Scanned PDF
          │                     │
          │                     ▼
          │                    OCR
          │                     │
          └──────────┬──────────┘
                     │
                     ▼
              Text Chunking
            500 chars / 100 overlap
                     │
                     ▼
          Sentence Transformer
              Embeddings
                     │
                     ▼
                 ChromaDB
           Vector Knowledge Base
                     │
                     ▼
              User Question
                     │
                     ▼
          Question Embedding
                     │
                     ▼
          Relevant Chunks
             Retrieved
                     │
                     ▼
       DeepSeek-R1 + Retrieved
               Context
                     │
                     ▼
              Final Answer
                     │
                     ▼
             Sources / Pages