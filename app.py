import streamlit as st
from pathlib import Path
import chromadb

from ingest import ingest_file
from answer import get_answer


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="RAG Document Chatbot",
    page_icon="📄",
    layout="centered"
)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("🤖 RAG Chatbot")

    st.write(
        "AI-powered document question answering "
        "using Retrieval-Augmented Generation."
    )

    st.divider()

    st.subheader("🛠️ Technology")

    st.write("🐍 Python")
    st.write("🧠 DeepSeek-R1")
    st.write("🔎 Sentence Transformers")
    st.write("🗄️ ChromaDB")
    st.write("🎨 Streamlit")

    st.divider()

    st.caption(
        "Upload → Process → Retrieve → Ask"
    )

    # =====================================================
    # CLEAR CHAT
    # =====================================================

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


    # =====================================================
    # CLEAR KNOWLEDGE BASE
    # =====================================================

    if st.button(
        "🗑️ Clear Knowledge Base",
        use_container_width=True
    ):

        try:

            client = chromadb.PersistentClient(
                path="chroma_db"
            )

            try:

                client.delete_collection(
                    name="documents"
                )

                st.success(
                    "✅ Knowledge base cleared!"
                )

            except Exception:

                st.info(
                    "Knowledge base was already empty."
                )

        except Exception as e:

            st.error(
                f"Could not clear knowledge base: {e}"
            )

        st.rerun()


# =========================================================
# MAIN TITLE
# =========================================================

st.title("📄 RAG Document Chatbot")

st.write(
    "Upload documents and ask questions about "
    "their contents."
)


# =========================================================
# CURRENT UPLOAD
# =========================================================

st.subheader("📤 Upload Documents")

uploaded_files = st.file_uploader(

    "Select PDF, DOCX, or TXT files",

    type=[
        "pdf",
        "docx",
        "txt"
    ],

    accept_multiple_files=True
)


if uploaded_files:

    st.success(
        f"📄 {len(uploaded_files)} document(s) "
        f"currently selected."
    )

    st.write(
        "**Currently selected files:**"
    )

    for file in uploaded_files:

        st.write(
            f"📄 {file.name}"
        )

else:

    st.info(
        "📭 No documents currently selected."
    )


# =========================================================
# PROCESS DOCUMENTS
# =========================================================

if uploaded_files:

    if st.button(
        "⚙️ Process Documents",
        use_container_width=True
    ):

        documents_folder = Path(
            "documents"
        )

        documents_folder.mkdir(
            exist_ok=True
        )

        total_chunks = 0

        failed_files = []

        with st.spinner(
            "Processing documents..."
        ):

            for file in uploaded_files:

                try:

                    file_path = (
                        documents_folder
                        / file.name
                    )

                    with open(
                        file_path,
                        "wb"
                    ) as f:

                        f.write(
                            file.getbuffer()
                        )


                    chunks = ingest_file(
                        file_path
                    )

                    total_chunks += chunks


                except Exception as e:

                    failed_files.append(
                        f"{file.name}: {e}"
                    )


        if failed_files:

            st.warning(
                "Some documents could not be processed:"
            )

            for error in failed_files:

                st.write(
                    f"⚠️ {error}"
                )


        if total_chunks > 0:

            st.success(
                f"✅ Documents processed successfully! "
                f"Created {total_chunks} chunk(s)."
            )

        else:

            st.error(
                "❌ No document chunks were created."
            )

        st.rerun()


# =========================================================
# KNOWLEDGE BASE
# =========================================================

st.divider()

st.subheader("🗄️ Knowledge Base")


try:

    client = chromadb.PersistentClient(
        path="chroma_db"
    )

    collection = client.get_collection(
        name="documents"
    )

    total_chunks = collection.count()


    if total_chunks > 0:

        data = collection.get(
            include=["metadatas"]
        )

        processed_documents = set()


        for metadata in data["metadatas"]:

            if metadata:

                source = metadata.get(
                    "source"
                )

                if source:

                    processed_documents.add(
                        source
                    )


        total_documents = len(
            processed_documents
        )


        # -------------------------------------------------
        # METRICS
        # -------------------------------------------------

        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "📄 Documents",
                total_documents
            )


        with col2:

            st.metric(
                "🧩 Chunks",
                total_chunks
            )


        with col3:

            st.metric(
                "✅ Database",
                "Ready"
            )


        # -------------------------------------------------
        # DOCUMENT LIST
        # -------------------------------------------------

        st.write(
            "**Documents in knowledge base:**"
        )


        for document in sorted(
            processed_documents
        ):

            st.write(
                f"📄 {document}"
            )


    else:

        st.info(
            "📭 Knowledge base is empty. "
            "Upload and process a document to begin."
        )


except Exception:

    st.info(
        "📭 Knowledge base is not initialized yet."
    )


# =========================================================
# CHAT HISTORY
# =========================================================

for message_index, message in enumerate(
    st.session_state.messages
):

    with st.chat_message(
        message["role"]
    ):

        st.write(
            message["content"]
        )


        # -------------------------------------------------
        # SOURCES
        # -------------------------------------------------

        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):

            with st.expander(
                "📚 Sources"
            ):

                for source in message["sources"]:

                    source_name = source.get(
                        "source"
                    )

                    page = source.get(
                        "page"
                    )


                    if page:

                        st.write(
                            f"📄 {source_name} "
                            f"— Page {page}"
                        )

                    else:

                        st.write(
                            f"📄 {source_name}"
                        )


        # -------------------------------------------------
        # RETRIEVED CONTEXT
        # -------------------------------------------------

        if (
            message["role"] == "assistant"
            and message.get(
                "retrieved_context"
            )
        ):

            with st.expander(
                "🔎 Retrieved Context"
            ):

                for context_index, item in enumerate(
                    message["retrieved_context"]
                ):

                    st.write(
                        f"### Retrieved Chunk "
                        f"{context_index + 1}"
                    )


                    st.write(
                        f"📄 **Source:** "
                        f"{item['source']}"
                    )


                    if item["page"]:

                        st.write(
                            f"📑 **Page:** "
                            f"{item['page']}"
                        )


                    if item["distance"] is not None:

                        st.write(
                            f"📏 **Retrieval distance:** "
                            f"{item['distance']:.4f}"
                        )


                    st.text_area(

                        "Retrieved text",

                        item["content"],

                        height=150,

                        key=(
                            f"history_context_"
                            f"{message_index}_"
                            f"{context_index}"
                        )

                    )


# =========================================================
# CHAT INPUT
# =========================================================

question = st.chat_input(
    "Ask a question about your documents..."
)


if question:

    # -----------------------------------------------------
    # USER MESSAGE
    # -----------------------------------------------------

    with st.chat_message(
        "user"
    ):

        st.write(
            question
        )


    st.session_state.messages.append(

        {
            "role": "user",
            "content": question
        }

    )


    # -----------------------------------------------------
    # ASSISTANT RESPONSE
    # -----------------------------------------------------

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "🔎 Searching documents..."
        ):

            try:

                result = get_answer(
                    question
                )


                answer = result.get(

                    "answer",

                    "Information not found "
                    "in the uploaded documents."

                )


                sources = result.get(
                    "sources",
                    []
                )


                retrieved_context = result.get(

                    "retrieved_context",

                    []

                )


                # -----------------------------------------
                # ANSWER
                # -----------------------------------------

                st.write(
                    answer
                )


                # -----------------------------------------
                # SOURCES
                # -----------------------------------------

                if sources:

                    with st.expander(
                        "📚 Sources"
                    ):

                        for source in sources:

                            source_name = source.get(
                                "source"
                            )

                            page = source.get(
                                "page"
                            )


                            if page:

                                st.write(
                                    f"📄 {source_name} "
                                    f"— Page {page}"
                                )

                            else:

                                st.write(
                                    f"📄 {source_name}"
                                )


                # -----------------------------------------
                # RETRIEVED CONTEXT
                # -----------------------------------------

                if retrieved_context:

                    with st.expander(
                        "🔎 Retrieved Context"
                    ):

                        for context_index, item in enumerate(

                            retrieved_context

                        ):

                            st.write(

                                f"### Retrieved Chunk "
                                f"{context_index + 1}"

                            )


                            st.write(

                                f"📄 **Source:** "
                                f"{item['source']}"

                            )


                            if item["page"]:

                                st.write(

                                    f"📑 **Page:** "
                                    f"{item['page']}"

                                )


                            if item["distance"] is not None:

                                st.write(

                                    f"📏 **Retrieval distance:** "
                                    f"{item['distance']:.4f}"

                                )


                            st.text_area(

                                "Retrieved text",

                                item["content"],

                                height=150,

                                key=(
                                    f"current_context_"
                                    f"{context_index}"
                                )

                            )


                # -----------------------------------------
                # SAVE ASSISTANT MESSAGE
                # -----------------------------------------

                st.session_state.messages.append(

                    {
                        "role": "assistant",

                        "content": answer,

                        "sources": sources,

                        "retrieved_context":
                            retrieved_context

                    }

                )


            except Exception as e:

                error_message = (
                    f"Something went wrong: {e}"
                )

                st.error(
                    error_message
                )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "RAG Document Chatbot • "
    "Python + Sentence Transformers + "
    "ChromaDB + DeepSeek-R1"
)