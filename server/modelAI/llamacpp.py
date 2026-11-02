import json
import os
from collections.abc import Iterator
import httpx

LLM_URL = os.getenv("LLM_URL", "http://localhost:8888")
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "120"))
LLM_REASONING = os.getenv("LLM_REASONING", "medium") #temperatura do jarvis


def _corpo(prompt: str, sistema: str | None, temperatura: float, stream: bool) -> dict:
    mensagens = []
    if sistema:
        mensagens.append({"role": "system", "content": sistema})
    mensagens.append({"role": "user", "content": prompt})
    return {
        "messages": mensagens,
        "temperature": temperatura,
        "stream": stream,
        "chat_template_kwargs": {"reasoning_effort": LLM_REASONING},
    }

# fast api vai usar essa função
def perguntar_ia(prompt: str, sistema: str | None = None, temperatura: float = 0.3) -> str:
    
    resp = httpx.post(
        f"{LLM_URL}/v1/chat/completions",
        json=_corpo(prompt, sistema, temperatura, stream=False),
        timeout=LLM_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()

# vai usar essa tambem kkkkkkkkkkk
def perguntar_ia_stream(
    prompt: str, sistema: str | None = None, temperatura: float = 0.3
) -> Iterator[str]:
    # mim devolva pedaço por pedaço com um delay
    with httpx.stream(
        "POST",
        f"{LLM_URL}/v1/chat/completions",
        json=_corpo(prompt, sistema, temperatura, stream=True),
        timeout=LLM_TIMEOUT,
    ) as resp:
        resp.raise_for_status()
        for linha in resp.iter_lines():
            if not linha.startswith("data: "):
                continue
            dados = linha[6:]
            if dados == "[DONE]":
                break
            delta = json.loads(dados)["choices"][0]["delta"]
            # ignora o pensamento pensante interno e só entrega a resposta
            if delta.get("content"):
                yield delta["content"]
