"""LLM client abstraction for multiple providers."""

from abc import ABC, abstractmethod
from typing import Optional
import json

from .config import LLMConfig


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def chat(self, messages: list[dict], **kwargs) -> str:
        """Send chat messages and get response."""
        pass


class OpenAIClient(LLMClient):
    """OpenAI API client."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=config.api_key,
                base_url=config.base_url,
            )
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def chat(self, messages: list[dict], **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
        )
        return response.choices[0].message.content or ""


class AnthropicClient(LLMClient):
    """Anthropic API client."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=config.api_key)
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    def chat(self, messages: list[dict], **kwargs) -> str:
        # Convert messages format
        system = ""
        chat_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                chat_messages.append(msg)
        
        response = self.client.messages.create(
            model=self.config.model,
            system=system,
            messages=chat_messages,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
        )
        return response.content[0].text


class OllamaClient(LLMClient):
    """Ollama local model client."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.base_url = config.base_url or "http://localhost:11434"
    
    def chat(self, messages: list[dict], **kwargs) -> str:
        try:
            import ollama
            response = ollama.chat(
                model=self.config.model,
                messages=messages,
            )
            return response["message"]["content"]
        except ImportError:
            # Fallback to requests
            import requests
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.config.model,
                    "messages": messages,
                    "stream": False,
                },
            )
            response.raise_for_status()
            return response.json()["message"]["content"]


def create_llm_client(config: LLMConfig) -> LLMClient:
    """Factory function to create appropriate LLM client."""
    provider = config.provider.lower()
    
    if provider == "openai":
        return OpenAIClient(config)
    elif provider == "anthropic":
        return AnthropicClient(config)
    elif provider == "ollama":
        return OllamaClient(config)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
