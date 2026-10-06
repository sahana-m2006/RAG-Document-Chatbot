# 📄 RAG Document Chatbot

An AI-powered document question-answering chatbot built using **Retrieval-Augmented Generation (RAG)**.

The system allows users to upload **PDF, DOCX, and TXT documents** and ask questions in natural language. Instead of relying only on a language model's general knowledge, the application retrieves relevant information from the uploaded documents and uses it as context to generate grounded answers.

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
- ⚠️ Error handling
- 🔐 Environment-variable support for secrets

---

## 🎯 Project Objective

The objective of this project is to build a practical **document-grounded AI assistant** that can answer questions from user-provided documents.

The system uses Retrieval-Augmented Generation to retrieve relevant information from documents before generating an answer. This helps reduce unsupported or hallucinated responses and allows users to verify answers using source and page references.

---

## 🧠 What is RAG?

**Retrieval-Augmented Generation (RAG)** is a technique that combines information retrieval with language generation.

Instead of asking a language model to answer a question only from its pre-trained knowledge, the system:

1. Processes the user's documents.
2. Converts document content into embeddings.
3. Stores the embeddings in a vector database.
4. Retrieves relevant document chunks when a question is asked.
5. Passes the retrieved information to the language model.
6. Generates an answer based on the retrieved context.

This makes the chatbot more suitable for answering questions about private or user-provided documents.

---

## 🔄 RAG Pipeline

The application follows this pipeline:

```text
Documents
    │
    ▼
Document Processing
    │
    ├── PDF
    ├── DOCX
    ├── TXT
    └── OCR for Scanned PDFs
    │
    ▼
Text Chunking
    │
    ▼
Sentence Transformer
Embeddings
    │
    ▼
ChromaDB
Vector Database
    │
    │
    ▼
User Question
    │
    ▼
Question Embedding
    │
    ▼
Relevant Chunk Retrieval
    │
    ▼
Context + User Question
    │
    ▼
DeepSeek-R1
via Ollama
    │
    ▼
Grounded Answer
    │
    ▼
Source + Page Reference
    │
    ▼
Streamlit UI