import os
import openai
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class LLMHelper:
    def __init__(self):
        self._initialized = False
        self.llm_type = None
        self.openai_api_key = None
        self.ollama_base_url = None
        self.ollama_model = None
    
    def _initialize(self):
        """Initialize the LLM helper with environment variables"""
        if self._initialized:
            return
            
        self.llm_type = os.getenv("LLM_TYPE", "openai").lower()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if self.llm_type == "openai":
            if not self.openai_api_key:
                logger.warning("OPENAI_API_KEY not set, LLM functionality will be disabled")
                return
            openai.api_key = self.openai_api_key
        elif self.llm_type == "ollama":
            self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            self.ollama_model = os.getenv("OLLAMA_MODEL", "llama2")
        
        self._initialized = True
    
    def generate_summary(self, content: str, max_tokens: int = 500) -> Optional[str]:
        """
        Generate a summary of the provided content using the configured LLM.
        
        Args:
            content: The content to summarize
            max_tokens: Maximum tokens for the response
            
        Returns:
            Summary text or None if failed
        """
        try:
            self._initialize()
            
            if not self._initialized:
                return "LLM not configured. Please set OPENAI_API_KEY or configure Ollama."
            
            if self.llm_type == "openai":
                return self._call_openai(content, max_tokens)
            elif self.llm_type == "ollama":
                return self._call_ollama(content, max_tokens)
            else:
                logger.error(f"Unsupported LLM type: {self.llm_type}")
                return None
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    def _call_openai(self, content: str, max_tokens: int) -> Optional[str]:
        """Call OpenAI API to generate summary"""
        try:
            prompt = f"""Please provide a concise summary of the following log content, highlighting any errors, warnings, or important events:

{content}

Summary:"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes log files."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    def _call_ollama(self, content: str, max_tokens: int) -> Optional[str]:
        """Call Ollama API to generate summary"""
        try:
            prompt = f"""Please provide a concise summary of the following log content, highlighting any errors, warnings, or important events:

{content}

Summary:"""
            
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.3
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return None 