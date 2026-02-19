from typing import List, Dict, Any
from langchain_community.vectorstores import FAISS
from langchain.schema import Document


class DocumentRetriever:

    def __init__(self, vectorstore: FAISS, k: int = 4):
        self.vectorstore = vectorstore
        self.k = k

    def search(self, query: str, k: int = None) -> List[Document]:
        search_k = k if k else self.k
        docs = self.vectorstore.similarity_search(query, k=search_k)
        return docs

    def search_with_scores(self, query: str, k: int = None) -> List[tuple]:
        search_k = k if k else self.k
        docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=search_k)
        return docs_with_scores

    def get_context(self, query: str, k: int = None) -> Dict[str, Any]:
        docs_with_scores = self.search_with_scores(query, k)

        if not docs_with_scores:
            return {"context": "", "sources": [], "num_results": 0}

        contexts = [doc.page_content for doc, _ in docs_with_scores]
        combined_context = "\n\n---\n\n".join(contexts)

        sources = [
            {
                "source": doc.metadata.get("source", "Unknown"),
                "chunk_id": doc.metadata.get("chunk_id", -1),
                "score": float(score)
            }
            for doc, score in docs_with_scores
        ]

        return {
            "context": combined_context,
            "sources": sources,
            "num_results": len(docs_with_scores)
        }