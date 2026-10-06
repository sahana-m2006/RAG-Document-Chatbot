import chromadb

client = chromadb.PersistentClient(
    path="chroma_db"
)

try:
    client.delete_collection(
        name="documents"
    )
    print("Old documents collection deleted!")

except Exception:
    print("Collection did not exist.")

print("Database reset completed.")