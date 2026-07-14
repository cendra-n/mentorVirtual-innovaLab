"""
core/ai_providers.py — Módulo unificado de proveedores de IA

Uso:
    from core.ai_providers import get_ai_provider, AIProvider

    # Usando el proveedor configurado en settings
    ai = get_ai_provider()
    response = ai.complete(system="Sos un tutor", prompt="¿Qué es Python?")

    # Especificando un proveedor
    ai = get_ai_provider('openai')
    response = ai.complete(system="Sos un tutor", prompt="¿Qué es Python?")

Variables de entorno requeridas según proveedor:
    AI_PROVIDER=anthropic|openai|deepseek|gemini|ollama  (obligatorio, sin default)
    ANTHROPIC_API_KEY=sk-ant-xxx
    OPENAI_API_KEY=sk-xxx
    DEEPSEEK_API_KEY=sk-xxx
    GEMINI_API_KEY=AIzaxxx
"""

import json
import logging
import urllib.request
from abc import ABC, abstractmethod

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


# ── Clase base ────────────────────────────────────────────────────────────────

class BaseAIProvider(ABC):
    """Interfaz común para todos los proveedores de IA."""

    @abstractmethod
    def complete(self, system: str, prompt: str, max_tokens: int = 1024) -> str:
        """
        Envía un prompt y devuelve el texto de respuesta.
        
        Args:
            system:     Prompt de sistema (instrucciones del rol)
            prompt:     Mensaje del usuario
            max_tokens: Máximo de tokens en la respuesta
            
        Returns:
            Texto de la respuesta del modelo
            
        Raises:
            Exception: Si la API devuelve un error
        """
        pass

    def _make_request(self, url: str, payload: dict, headers: dict) -> dict:
        """Helper para hacer requests HTTP."""
        data = json.dumps(payload).encode()
        req  = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())


# ── Anthropic (Claude) ────────────────────────────────────────────────────────

class AnthropicProvider(BaseAIProvider):
    """
    Claude API de Anthropic con soporte para Prompt Caching.
    Modelos: claude-sonnet-4-6, claude-opus-4-6, claude-haiku-4-5
    Docs: https://docs.anthropic.com/
    API Key: https://console.anthropic.com/
    Precio: ~$3/M tokens entrada, ~$15/M tokens salida (Sonnet)
    Con caching: 90% descuento en tokens cacheados
    """

    MODEL   = getattr(settings, 'ANTHROPIC_MODEL', 'claude-sonnet-4-6')
    API_URL = getattr(settings, 'ANTHROPIC_API_URL', 'https://api.anthropic.com/v1/messages')

    def complete(self, system: str, prompt: str, max_tokens: int = 1024,
                 use_cache: bool = True) -> str:

        api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY no configurada")

        # System con cache_control si use_cache=True
        system_payload = (
            [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
            if use_cache else system
        )

        payload = {
            "model":      self.MODEL,
            "max_tokens": max_tokens,
            "system":     system_payload,
            "messages":   [{"role": "user", "content": prompt}],
        }

        headers = {
            "Content-Type":    "application/json",
            "x-api-key":       api_key,
            "anthropic-version": "2023-06-01",
        }
        if use_cache:
            headers["anthropic-beta"] = "prompt-caching-2024-07-31"

        data = self._make_request(self.API_URL, payload, headers)

        # Log de uso de caché
        usage = data.get("usage", {})
        logger.info(
            "[Anthropic] input: %d, cache_read: %d, cache_creation: %d, output: %d",
            usage.get("input_tokens", 0),
            usage.get("cache_read_input_tokens", 0),
            usage.get("cache_creation_input_tokens", 0),
            usage.get("output_tokens", 0),
        )

        return data["content"][0]["text"]


# ── OpenAI (ChatGPT) ──────────────────────────────────────────────────────────

class OpenAIProvider(BaseAIProvider):
    """
    OpenAI API (ChatGPT).
    Modelos: gpt-4o, gpt-4o-mini, gpt-4-turbo
    Docs: https://platform.openai.com/docs/
    API Key: https://platform.openai.com/api-keys
    Precio: ~$2.5/M tokens entrada, ~$10/M tokens salida (GPT-4o)
    """

    MODEL   = getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')
    API_URL = getattr(settings, 'OPENAI_API_URL', 'https://api.openai.com/v1/chat/completions')

    def complete(self, system: str, prompt: str, max_tokens: int = 1024) -> str:

        api_key = getattr(settings, 'OPENAI_API_KEY', '')
        if not api_key:
            raise ValueError("OPENAI_API_KEY no configurada")

        payload = {
            "model":      self.MODEL,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system",  "content": system},
                {"role": "user",    "content": prompt},
            ],
        }

        headers = {
            "Content-Type":  "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        data = self._make_request(self.API_URL, payload, headers)

        usage = data.get("usage", {})
        logger.info(
            "[OpenAI] prompt_tokens: %d, completion_tokens: %d",
            usage.get("prompt_tokens", 0),
            usage.get("completion_tokens", 0),
        )

        return data["choices"][0]["message"]["content"]


# ── DeepSeek ──────────────────────────────────────────────────────────────────

class DeepSeekProvider(BaseAIProvider):
    """
    DeepSeek API — compatible con el formato de OpenAI.
    Modelos: deepseek-chat, deepseek-reasoner
    Docs: https://platform.deepseek.com/api-docs/
    API Key: https://platform.deepseek.com/api_keys
    Precio: ~$0.14/M tokens entrada (muy económico)
    """

    MODEL   = getattr(settings, 'DEEPSEEK_MODEL', 'deepseek-chat')
    API_URL = getattr(settings, 'DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')

    def complete(self, system: str, prompt: str, max_tokens: int = 1024) -> str:

        api_key = getattr(settings, 'DEEPSEEK_API_KEY', '')
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY no configurada")

        payload = {
            "model":      self.MODEL,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
        }

        headers = {
            "Content-Type":  "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        data = self._make_request(self.API_URL, payload, headers)

        usage = data.get("usage", {})
        logger.info(
            "[DeepSeek] prompt_tokens: %d, completion_tokens: %d",
            usage.get("prompt_tokens", 0),
            usage.get("completion_tokens", 0),
        )

        return data["choices"][0]["message"]["content"]


# ── Google Gemini ─────────────────────────────────────────────────────────────

class GeminiProvider(BaseAIProvider):
    """
    Google Gemini API.
    Modelos: gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash
    Docs: https://ai.google.dev/gemini-api/docs
    API Key: https://aistudio.google.com/apikey
    Precio: Gemini Flash es gratuito hasta 15 req/min
    """

    MODEL = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash')

    def complete(self, system: str, prompt: str, max_tokens: int = 1024) -> str:

        api_key = getattr(settings, 'GEMINI_API_KEY', '')
        if not api_key:
            raise ValueError("GEMINI_API_KEY no configurada")

        base = getattr(settings, 'GEMINI_API_BASE', 'https://generativelanguage.googleapis.com/v1beta/models')
        url = f"{base}/{self.MODEL}:generateContent?key={api_key}"

        payload = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens},
        }

        headers = {"Content-Type": "application/json"}

        data = self._make_request(url, payload, headers)

        usage = data.get("usageMetadata", {})
        logger.info(
            "[Gemini] prompt_tokens: %d, candidates_tokens: %d",
            usage.get("promptTokenCount", 0),
            usage.get("candidatesTokenCount", 0),
        )

        return data["candidates"][0]["content"]["parts"][0]["text"]


# ── Ollama (modelos locales) ──────────────────────────────────────────────────

class OllamaProvider(BaseAIProvider):
    """
    Ollama — modelos de IA corriendo localmente (sin costo).
    Modelos: llama3, mistral, phi3, gemma2, etc.
    Docs: https://ollama.com/
    Instalación: curl -fsSL https://ollama.com/install.sh | sh
    Precio: GRATIS (corre en tu hardware)
    Nota: Requiere Ollama corriendo en localhost:11434
    """

    MODEL   = getattr(settings, 'OLLAMA_MODEL', 'llama3')
    API_URL = getattr(settings, 'OLLAMA_URL', 'http://localhost:11434') + '/api/chat'

    def complete(self, system: str, prompt: str, max_tokens: int = 1024) -> str:

        payload = {
            "model":  self.MODEL,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
        }

        headers = {"Content-Type": "application/json"}

        data = self._make_request(self.API_URL, payload, headers)

        logger.info("[Ollama] model: %s", self.MODEL)

        return data["message"]["content"]


# ── Factory ───────────────────────────────────────────────────────────────────

PROVIDERS = {
    'anthropic': AnthropicProvider,
    'openai':    OpenAIProvider,
    'deepseek':  DeepSeekProvider,
    'gemini':    GeminiProvider,
    'ollama':    OllamaProvider,
}


def get_ai_provider(provider: str | None = None) -> BaseAIProvider:
    """
    Devuelve una instancia del proveedor de IA.
    
    Si no se especifica provider, usa settings.AI_PROVIDER (debe estar configurado en el .env).
    
    Uso:
        ai = get_ai_provider()              # usa settings.AI_PROVIDER
        ai = get_ai_provider('openai')      # fuerza OpenAI
        ai = get_ai_provider('deepseek')    # fuerza DeepSeek
        
        response = ai.complete(
            system="Sos un tutor educativo",
            prompt="¿Qué es una variable?",
            max_tokens=512,
        )
    """
    name = provider or getattr(settings, 'AI_PROVIDER', '')
    if not name:
        raise ImproperlyConfigured(
            "AI_PROVIDER no está configurado. Definila en el .env "
            f"con una de estas opciones: {list(PROVIDERS.keys())}"
        )

    if name not in PROVIDERS:
        raise ValueError(
            f"Proveedor '{name}' no soportado. Opciones: {list(PROVIDERS.keys())}"
        )

    logger.info("[AI] usando proveedor: %s", name)
    return PROVIDERS[name]()


# Alias para importación directa
AIProvider = BaseAIProvider
