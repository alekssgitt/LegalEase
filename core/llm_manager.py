import os
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate

class LLMManager:
    def __init__(self, model_name="LegalAI"):
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.llm = Ollama(model=model_name, base_url=base_url)

        self.analysis_prompt_template = PromptTemplate(
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

    def invokeLlm(self, prompt_text: str) -> str:
        try:
            response = self.llm.invoke(prompt_text)
            if hasattr(response, 'content'):
                return response.content
            return str(response)
        except Exception as e:
            print(f"Error during LLM invocation: {e}")
            raise

    def analyzeDocument(self, document_content: str, user_profile: dict) -> str:
        prompt_text = self.analysis_prompt_template.format(
            user_type=user_profile["type"],
            experience_level=user_profile["experience_level"],
            document_content=document_content
        )
        return self.invokeLlm(prompt_text)

llm_manager_qa = LLMManager(model_name="llama3.2")

llm_manager_analysis = LLMManager(model_name="LegalAI")
