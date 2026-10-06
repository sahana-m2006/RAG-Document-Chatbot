from pathlib import Path

from sentence_transformers import SentenceTransformer
import chromadb

from document_processor import extract_text_from_file


CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

print("Loading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Embedding model loaded!")


def ingest_file(file_path):

    """
    Process one PDF, DOCX, or TXT file
    and store its chunks + metadata
    in ChromaDB.
    """

    file_path = Path(file_path)

    print(
        f"\nProcessing: {file_path.name}"
    )

    pages = extract_text_from_file(
        file_path
    )

    print(
        "Pages processed:",
        len(pages)
    )

    chunks = []

    for page in pages:

        text = page["text"]

        if not text.strip():
            continue

        start = 0

        while start < len(text):

            end = start + CHUNK_SIZE

            chunk_text = (
                text[start:end]
                .strip()
            )

            if chunk_text:

                chunks.append(
                    {
                        "text": chunk_text,
                        "source": page["source"],
                        "page": page["page"]
                    }
                )

            start += (
                CHUNK_SIZE -
                CHUNK_OVERLAP
            )

    print(
        "Chunks created:",
        len(chunks)
    )

    if not chunks:

        print(
            "No text found in document."
        )

        return 0


    # =====================================================
    # CHROMADB WITH COSINE DISTANCE
    # =====================================================

    client = chromadb.PersistentClient(
        path="chroma_db"
    )

    collection = client.get_or_create_collection(

        name="documents",

        metadata={
            "hnsw:space": "cosine"
        }

    )


    # =====================================================
    # CREATE EMBEDDINGS
    # =====================================================

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    print(
        "Creating embeddings..."
    )

    embeddings = model.encode(
        texts
    ).tolist()

    print(
        "Embeddings created!"
    )


    # =====================================================
    # CREATE IDS + METADATA
    # =====================================================

    ids = []

    metadatas = []


    for index, chunk in enumerate(
        chunks
    ):

        document_id = (

            f"{chunk['source']}_"
            f"page_{chunk['page']}_"
            f"chunk_{index}"

        )

        ids.append(
            document_id
        )


        metadatas.append(

            {
                "source": chunk["source"],
                "page": chunk["page"]
            }

        )


    # =====================================================
    # STORE IN CHROMADB
    # =====================================================

    collection.upsert(

        ids=ids,

        documents=texts,

        embeddings=embeddings,

        metadatas=metadatas

    )


    print(
        "Stored in ChromaDB!"
    )

    print(
        "Total chunks in database:",
        collection.count()
    )


    return len(chunks)


# =========================================================
# TEST ONE FILE
# =========================================================

if __name__ == "__main__":

    file_path = (
        "documents/sample.pdf"
    )

    total_chunks = ingest_file(
        file_path
    )

    print(
        f"\nSuccessfully ingested "
        f"{total_chunks} chunk(s)."
    )