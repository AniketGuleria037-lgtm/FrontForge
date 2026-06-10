import chromadb

def retrieve(query):
    client=chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection("frontend-docs")
    results = collection.query(
        query_texts=[query],
        n_results=3
    )
    return "\n\n".join(results["documents"][0])

if __name__=="__main__":
    result=retrieve("how to use useState in React")
    print(result)