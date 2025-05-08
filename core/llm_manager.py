from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

class LLMManager:
    def __init__(self, model_name="LegalAI"):
        self.llm = Ollama(model=model_name, base_url="http://localhost:11434")
        self.memory = ConversationBufferMemory()
        
        self.base_prompt = PromptTemplate(
            input_variables=["user_type", "experience_level", "document_content"],
            template="""As a legal document analyzer, help explain the following document in plain language.
            The explanation should be tailored for a {user_type} with {experience_level} legal experience.
            
            Document content:
            {document_content}
            
            Please provide:
            1. A clear summary
            2. Key points and obligations
            3. Potential risks or hidden clauses
            4. Recommended actions"""
        )
        
    def analyze_document(self, document_content: str, user_profile: dict) -> str:

        prompt = self.base_prompt.format(
            user_type=user_profile["type"],
            experience_level=user_profile["experience_level"],
            document_content=document_content
        )
        
        chain = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=True
        )
        
        return chain.run(prompt)
