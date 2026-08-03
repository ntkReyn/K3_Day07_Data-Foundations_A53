from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if results:
            context = "\n\n".join(
                f"[Nguồn {index}: {result['metadata'].get('doc_id', result['id'])}]\n"
                f"{result['content']}"
                for index, result in enumerate(results, start=1)
            )
        else:
            context = "Không tìm thấy đoạn tài liệu liên quan trong cơ sở tri thức."

        prompt = (
            "Bạn là trợ lý trả lời dựa trên cơ sở tri thức. "
            "Chỉ sử dụng thông tin trong phần Ngữ cảnh; nếu thiếu thông tin, hãy nói rõ điều đó.\n\n"
            f"Ngữ cảnh:\n{context}\n\n"
            f"Câu hỏi: {question}\n"
            "Trả lời:"
        )
        return self.llm_fn(prompt)
