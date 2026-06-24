import json
import subprocess
import importlib.util
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class LLMConfig:
    backend: str = "ollama"
    model: str = "llama3.2:3b"
    temperature: float = 0.7
    max_tokens: int = 512
    ollama_host: str = "http://localhost:11434"
    hf_model: str = "microsoft/Phi-3-mini-4k-instruct"
    device: str = "cpu"
    hf_quantize: bool = True


class LLMBackend(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        ...

    @abstractmethod
    def chat(self, messages: list[dict]) -> str:
        ...


class OllamaBackend(LLMBackend):
    def __init__(self, config: LLMConfig):
        self.config = config
        self.base_url = config.ollama_host.rstrip("/")

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        import urllib.request

        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens,
            },
        }
        if system_prompt:
            payload["system"] = system_prompt

        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())["response"]

    def chat(self, messages: list[dict]) -> str:
        import urllib.request

        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens,
            },
        }

        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())["message"]["content"]


class HFFastBackend(LLMBackend):
    def __init__(self, config: LLMConfig):
        self.config = config
        self._pipe = None

    def _load(self):
        if self._pipe is not None:
            return
        from transformers import pipeline

        kwargs = {"model": self.config.hf_model, "device": self.config.device}
        if self.config.hf_quantize:
            try:
                import torch

                if self.config.device == "cpu":
                    kwargs["torch_dtype"] = torch.float32
                kwargs["model_kwargs"] = {"load_in_8bit": False}
            except ImportError:
                pass
        self._pipe = pipeline("text-generation", **kwargs)

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        self._load()
        full = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        result = self._pipe(
            full,
            max_new_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            do_sample=True,
        )
        return result[0]["generated_text"][len(full):].strip()

    def chat(self, messages: list[dict]) -> str:
        self._load()
        prompt = self._format_chat(messages)
        return self.generate(prompt)

    def _format_chat(self, messages: list[dict]) -> str:
        lines = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                lines.append(f"System: {content}")
            elif role == "user":
                lines.append(f"User: {content}")
            elif role == "assistant":
                lines.append(f"Assistant: {content}")
        lines.append("Assistant: ")
        return "\n".join(lines)


def create_llm(config: LLMConfig | None = None) -> LLMBackend:
    cfg = config or LLMConfig()

    if cfg.backend == "ollama":
        return OllamaBackend(cfg)
    elif cfg.backend == "huggingface":
        return HFFastBackend(cfg)
    else:
        raise ValueError(f"Unknown backend: {cfg.backend}")


def check_ollama() -> bool:
    try:
        import urllib.request

        req = urllib.request.Request("http://localhost:11434/api/tags")
        urllib.request.urlopen(req, timeout=2)
        return True
    except Exception:
        return False


def auto_detect_backend() -> str:
    if check_ollama():
        return "ollama"
    try:
        import transformers
        return "huggingface"
    except ImportError:
        return "none"
