import re
import requests
import chromadb
from sentence_transformers import SentenceTransformer


# =========================================================
# CONFIGURATION
# =========================================================

MODEL_NAME = "all-MiniLM-L6-v2"

OLLAMA_MODEL = "deepseek-r1:8b"
OLLAMA_URL = "http://localhost:11434/api/generate"

DATABASE_PATH = "chroma_db"
COLLECTION_NAME = "documents"

# Retrieve multiple candidates
TOP_K = 4

# Relevance settings
MIN_KEYWORD_COVERAGE = 0.30
SEMANTIC_DISTANCE_THRESHOLD = 0.90


# =========================================================
# LOAD EMBEDDING MODEL
# =========================================================

print("Loading embedding model...")

model = SentenceTransformer(
    MODEL_NAME
)

print("Embedding model loaded!")


# =========================================================
# STOP WORDS
# =========================================================

STOP_WORDS = {
    "what",
    "is",
    "are",
    "the",
    "a",
    "an",
    "of",
    "in",
    "on",
    "to",
    "for",
    "and",
    "or",
    "which",
    "when",
    "where",
    "who",
    "how",
    "does",
    "do",
    "did",
    "will",
    "be",
    "was",
    "were",
    "this",
    "that",
    "these",
    "those",
    "can",
    "could",
    "would",
    "should",
    "about",
    "from",
    "with",
    "your",
    "their",
    "it",
    "its",
    "my",
    "me",
    "please"
}


# =========================================================
# EXTRACT KEYWORDS
# =========================================================

def get_keywords(text):

    words = re.findall(
        r"\b[a-zA-Z0-9]+\b",
        text.lower()
    )

    keywords = {
        word
        for word in words
        if word not in STOP_WORDS
        and len(word) > 2
    }

    return keywords


# =========================================================
# KEYWORD COVERAGE
# =========================================================

def keyword_coverage(question, document):

    question_keywords = get_keywords(
        question
    )

    document_keywords = get_keywords(
        document
    )

    if not question_keywords:
        return 0.0

    matched_keywords = (
        question_keywords
        & document_keywords
    )

    coverage = (
        len(matched_keywords)
        / len(question_keywords)
    )

    return coverage


# =========================================================
# NOT FOUND RESPONSE
# =========================================================

def not_found_response():

    return {
        "answer": (
            "Information not found in "
            "the uploaded documents."
        ),
        "sources": [],
        "retrieved_context": []
    }


# =========================================================
# MAIN RAG FUNCTION
# =========================================================

def get_answer(question):

    # -----------------------------------------------------
    # CONNECT TO CHROMADB
    # -----------------------------------------------------

    try:

        client = chromadb.PersistentClient(
            path=DATABASE_PATH
        )

        collection = client.get_collection(
            name=COLLECTION_NAME
        )

    except Exception:

        return not_found_response()


    # -----------------------------------------------------
    # CHECK DATABASE
    # -----------------------------------------------------

    if collection.count() == 0:

        return not_found_response()


    # -----------------------------------------------------
    # CREATE QUESTION EMBEDDING
    # -----------------------------------------------------

    question_embedding = model.encode(
        question
    ).tolist()


    # -----------------------------------------------------
    # RETRIEVE TOP CANDIDATES
    # -----------------------------------------------------

    results = collection.query(

        query_embeddings=[
            question_embedding
        ],

        n_results=TOP_K,

        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )


    if (
        not results
        or not results.get("documents")
        or not results["documents"][0]
    ):

        return not_found_response()


    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    distances = results.get(
        "distances",
        [[]]
    )[0]


    # =====================================================
    # RELEVANCE FILTER
    # =====================================================

    relevant_documents = []
    relevant_metadatas = []
    relevant_distances = []


    for index, document in enumerate(
        documents
    ):

        metadata = metadatas[index]

        distance = (
            distances[index]
            if index < len(distances)
            else None
        )


        coverage = keyword_coverage(
            question,
            document
        )


        # -------------------------------------------------
        # ACCEPT IF:
        #
        # 1. Enough question keywords match
        #
        # OR
        #
        # 2. Semantic distance is very close
        # -------------------------------------------------

        is_relevant = (

            coverage >=
            MIN_KEYWORD_COVERAGE

            or

            (
                distance is not None
                and
                distance <=
                SEMANTIC_DISTANCE_THRESHOLD
            )
        )


        if is_relevant:

            relevant_documents.append(
                document
            )

            relevant_metadatas.append(
                metadata
            )

            relevant_distances.append(
                distance
            )


    # -----------------------------------------------------
    # NO RELEVANT DOCUMENT
    # -----------------------------------------------------

    if not relevant_documents:

        return not_found_response()


    # =====================================================
    # BUILD CONTEXT
    # =====================================================

    context_parts = []

    retrieved_context = []


    for index, (
        document,
        metadata,
        distance
    ) in enumerate(
        zip(
            relevant_documents,
            relevant_metadatas,
            relevant_distances
        ),
        start=1
    ):

        source = metadata.get(
            "source"
        )

        page = metadata.get(
            "page"
        )


        context_parts.append(
            f"""
Document {index}

Source: {source}

Page: {page}

Content:
{document}
"""
        )


        retrieved_context.append(
            {
                "source": source,
                "page": page,
                "content": document,
                "distance": distance
            }
        )


    context = "\n".join(
        context_parts
    )


    # =====================================================
    # DEEPSEEK PROMPT
    # =====================================================

    prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the information
provided in the document context.

RULES:

1. Use only the provided context.
2. Do not use outside knowledge.
3. Do not guess.
4. Do not invent information.
5. If the answer is present in the context, answer it.
6. If the answer is not present, respond exactly:

Information not found in the uploaded documents.

7. If multiple documents contain useful information,
   combine them when necessary.
8. Give a clear and concise answer.
9. Do not mention retrieval, embeddings, chunks,
   similarity, or the RAG system.
10. Do not provide reasoning.

DOCUMENT CONTEXT:

{context}

USER QUESTION:

{question}

FINAL ANSWER:
"""


    # =====================================================
    # CALL DEEPSEEK
    # =====================================================

    try:

        response = requests.post(

            OLLAMA_URL,

            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },

            timeout=180
        )

        response.raise_for_status()

        data = response.json()

        answer = data.get(
            "response",
            ""
        ).strip()


    except requests.exceptions.ConnectionError:

        answer = (
            "Unable to connect to DeepSeek. "
            "Please make sure Ollama is running."
        )


    except requests.exceptions.Timeout:

        answer = (
            "DeepSeek took too long to respond. "
            "Please try again."
        )


    except Exception as e:

        answer = (
            f"An error occurred while generating "
            f"the answer: {e}"
        )


    # =====================================================
    # COLLECT SOURCES
    # =====================================================

    sources = []


    for metadata in relevant_metadatas:

        source_info = {
            "source": metadata.get(
                "source"
            ),
            "page": metadata.get(
                "page"
            )
        }


        if source_info not in sources:

            sources.append(
                source_info
            )


    # =====================================================
    # RETURN RESULT
    # =====================================================

    return {

        "answer": answer,

        "sources": sources,

        "retrieved_context":
            retrieved_context

    }