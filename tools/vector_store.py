from langchain_community.vectorstores import FAISS

def create_vector_store(chunks, embeddings):
    return FAISS.from_texts(
        texts=chunks,
        embedding=embeddings
    )

def retrieve_relevant_context(vector_store, query, k=3):
    results = vector_store.similarity_search(query, k=k)
    return [doc.page_content for doc in results]
