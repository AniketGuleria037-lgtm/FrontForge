import chromadb
from pathlib import Path

def chunk_text(text, chunk_size=500):
    n=0
    chunks=[]
    while(n<len(text)):
        chunks.append(text[n:n+500])
        n+=chunk_size
    return chunks

def load_docs():
    docs=[]
    for file in Path("docs").glob("*.txt"):
        content=file.read_text(encoding="utf-8")
        docs.append((file.stem, content))
    return docs

def build_index():
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection("frontend-docs")
    docs=load_docs()
    for file, content in docs:
        chunks=chunk_text(content)
        for i, chunk in enumerate(chunks):
            collection.add(documents=[chunk], ids=[f"{file}-{i}"])
        print(f"Added chunks from {file}")

if __name__ == "__main__":
    build_index()
    print("Index built successfully")