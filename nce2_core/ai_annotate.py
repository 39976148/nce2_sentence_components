from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Callable

from nce2_core.ai_config import AiConfig
from nce2_core.models import Sentence, Token
from nce2_core.roles import ROLE_LABELS

ROLE_LIST_TEXT = "、".join(r for r in ROLE_LABELS if r)


def build_annotation_prompt(sentence: Sentence) -> str:
    token_texts = [t.text for t in sentence.tokens]
    return f"""你是英语语法分析助手。请对下列句子进行成分划分。

展开句：{sentence.expanded}
原句：{sentence.original}

当前分词：{json.dumps(token_texts, ensure_ascii=False)}

可选成分标签：{ROLE_LIST_TEXT}

要求：
1. 返回 JSON，格式为 {{"tokens": [{{"text": "...", "role": "..."}}, ...]}}
2. tokens 按顺序覆盖整个展开句，拼接 text 后与展开句一致（忽略多余空格）
3. role 必须从可选标签中选择；可合并相邻词为一个 token（如 "Last week" 作时间状语）
4. 只输出 JSON，不要其他文字"""


def extract_json_object(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("AI response does not contain JSON object")
    return json.loads(text[start : end + 1])


def parse_annotation_response(raw: str, sentence: Sentence) -> list[Token]:
    data = extract_json_object(raw)
    items = data.get("tokens") or data.get("annotations")
    if not isinstance(items, list) or not items:
        raise ValueError("AI JSON missing tokens array")

    tokens: list[Token] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        text = str(item.get("text", "")).strip()
        role = str(item.get("role", "")).strip()
        if text:
            tokens.append(Token(text=text, role=role))

    if not tokens:
        raise ValueError("AI returned no valid tokens")

    joined = " ".join(t.text for t in tokens)
    normalized_exp = " ".join(sentence.expanded.split())
    normalized_got = " ".join(joined.split())
    if normalized_got != normalized_exp:
        raise ValueError(
            f"AI tokens do not match expanded sentence: got {normalized_got!r}"
        )
    return tokens


def chat_completion(
    cfg: AiConfig,
    prompt: str,
    *,
    http_post: Callable[..., bytes] | None = None,
) -> str:
    if not cfg.is_ready():
        raise RuntimeError("AI 未配置：请在 config/ai.json 中设置 api_key 并启用")

    url = f"{cfg.api_base}/chat/completions"
    body = json.dumps(
        {
            "model": cfg.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
    ).encode("utf-8")

    if http_post is None:
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {cfg.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"AI API HTTP {e.code}: {detail}") from e
    else:
        raw = http_post(url, body, cfg.api_key)
        payload = json.loads(raw.decode("utf-8"))

    choices = payload.get("choices") or []
    if not choices:
        raise RuntimeError("AI API returned empty choices")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if not content:
        raise RuntimeError("AI API returned empty content")
    return str(content)


def annotate_sentence(
    sentence: Sentence,
    cfg: AiConfig,
    *,
    http_post: Callable[..., bytes] | None = None,
) -> Sentence:
    prompt = build_annotation_prompt(sentence)
    raw = chat_completion(cfg, prompt, http_post=http_post)
    sentence.tokens = parse_annotation_response(raw, sentence)
    return sentence
