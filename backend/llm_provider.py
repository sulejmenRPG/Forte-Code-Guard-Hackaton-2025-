"""
LLM Provider abstraction layer
Supports multiple AI providers: OpenAI, Gemini, Claude
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import json
import logging

from backend.config import settings

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def analyze_code(self, prompt: str) -> Dict[str, Any]:
        """Analyze code using LLM"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self):
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = "gpt-4o-mini"  # Cost-effective model
            logger.info(f"✅ OpenAI provider initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI: {str(e)}")
            raise
    
    async def analyze_code(self, prompt: str) -> Dict[str, Any]:
        """Analyze code using OpenAI GPT"""
        try:
            logger.info("🤖 Calling OpenAI API...")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Ты опытный code reviewer. Отвечай ТОЛЬКО валидным JSON без дополнительного текста."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            logger.info(f"✅ OpenAI analysis complete. Score: {result.get('score', 'N/A')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ OpenAI API error: {str(e)}")
            raise


class GeminiProvider(LLMProvider):
    """Google Gemini provider"""
    
    def __init__(self):
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("✅ Gemini provider initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {str(e)}")
            raise
    
    async def analyze_code(self, prompt: str) -> Dict[str, Any]:
        """Analyze code using Gemini"""
        try:
            logger.info("🤖 Calling Gemini API...")
            logger.info(f"📝 Prompt length: {len(prompt)} chars")
            
            response = self.model.generate_content(prompt)
            content = response.text
            
            # Log raw response
            logger.info(f"📦 Raw Gemini response (first 500 chars): {content[:500]}")
            
            # Try to extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            logger.info(f"📦 Extracted JSON (first 300 chars): {content[:300]}")
            
            result = json.loads(content)
            
            logger.info(f"✅ Gemini analysis complete. Score: {result.get('score', 'N/A')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Gemini API error: {str(e)}")
            raise


class ClaudeProvider(LLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self):
        try:
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = "claude-3-haiku-20240307"  # Fast and cost-effective
            logger.info(f"✅ Claude provider initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Claude: {str(e)}")
            raise
    
    async def analyze_code(self, prompt: str) -> Dict[str, Any]:
        """Analyze code using Claude"""
        try:
            logger.info("🤖 Calling Claude API...")
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            content = response.content[0].text
            
            # Try to extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            
            logger.info(f"✅ Claude analysis complete. Score: {result.get('score', 'N/A')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Claude API error: {str(e)}")
            raise


def get_llm_provider() -> LLMProvider:
    """Factory function to get the configured LLM provider"""
    
    provider_name = settings.LLM_PROVIDER.lower()
    
    if provider_name == "openai":
        return OpenAIProvider()
    elif provider_name == "gemini":
        return GeminiProvider()
    elif provider_name == "claude":
        return ClaudeProvider()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")
