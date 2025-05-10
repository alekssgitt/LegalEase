from typing import List, Dict
import PyPDF2
from io import BytesIO
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
    def extract_text(self, file_content: bytes, file_type: str) -> str:
        if file_type == "application/pdf":
            return self._process_pdf(BytesIO(file_content))
        return file_content.decode()
    
    def _process_pdf(self, file_obj: BytesIO) -> str:
        pdf_reader = PyPDF2.PdfReader(file_obj)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    
    def create_vector_store(self, text: str) -> FAISS:
        chunks = self.text_splitter.split_text(text)
        return FAISS.from_texts(
            texts=chunks,
            embedding=self.embeddings
        )
    
    def retrieve_relevant_context(self, vector_store: FAISS, query: str, k: int = 3) -> List[str]:
        results = vector_store.similarity_search(query, k=k)
        return [doc.page_content for doc in results]
