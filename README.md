# 📄 RAG Document Chatbot

An AI-powered document question-answering system built using **Retrieval-Augmented Generation (RAG)**.

The chatbot allows users to upload **PDF, DOCX, and TXT documents**, retrieve relevant information from those documents, and ask questions in natural language.

Instead of relying only on the language model's general knowledge, the system retrieves relevant document content and uses it as context to generate grounded answers.

---

## 🚀 Features

- 📄 Upload PDF, DOCX, and TXT documents
- 📚 Support for multiple documents
- 🔎 Semantic document retrieval
- 🧠 Sentence Transformer embeddings
- 🗄️ ChromaDB vector database
- 🤖 Local DeepSeek-R1 language model
- 📝 OCR support for scanned PDFs
- ✂️ Text chunking with overlap
- 📌 Source and page references
- 💬 Chat history
- 🚫 "Information not found" handling
- 🔍 Retrieved context inspection
- 🗑️ Clear chat functionality
- 🗑️ Clear knowledge base functionality
- 🎨 Streamlit-based user interface
- 🔐 Environment-variable support for secrets

---

## 🧠 How the System Works

The project follows a Retrieval-Augmented Generation pipeline:

```text
                User
                 │
                 ▼
        Upload Documents
                 │
                 ▼
       Document Processing
                 │
        ┌────────┴────────┐
        │                 │
     PDF/DOCX/TXT      OCR for
        │             scanned PDFs
        └────────┬────────┘
                 │
                 ▼
          Text Chunking
                 │
                 ▼
       Sentence Transformers
          Embeddings
                 │
                 ▼
             ChromaDB
        Vector Knowledge Base
                 │
                 ▼
        User asks a question
                 │
                 ▼
        Question Embedding
                 │
                 ▼
        Relevant Chunks
          Retrieved
                 │
                 ▼
        DeepSeek-R1 + Context
                 │
                 ▼
          Final Answer