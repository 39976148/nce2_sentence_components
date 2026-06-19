# NCE2 Sentence Components P1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 NCE2 课堂演示 MVP：从 `nce_txt/第二册/` 解析课文 → 分句编号 → 缩写展开 → 导出 HTML 幻灯片（4/5 行动态）→ PyQt6 最小 GUI 选课文并浏览器演示。

**Architecture:** 分层核心库 `nce2_core`（无 Qt 依赖）负责解析/分句/缩写/JSON 模型；`nce2_export` 生成自包含 HTML；`nce2_gui` 为薄 PyQt6 壳。数据持久化为 `data/lessons/NN.json`。

**Tech Stack:** Python 3.10+、标准库（core）、PyQt6（GUI）、pytest（测试）

**Spec:** `docs/superpowers/specs/2026-06-19-nce2-sentence-components-design.md`

**Project root:** `D:\cursor_work\nce2_sentence_components`

---

## File Map (P1)

| File | Responsibility |
|------|----------------|
| `nce2_core/models.py` | Token, Sentence, Lesson dataclasses + JSON 读写 |
| `nce2_core/contraction.py` | 缩写展开 |
| `nce2_core/splitter.py` | 正文分句 |
| `nce2_core/parser.py` | 读 tinghere TXT，提取英文正文 |
| `nce2_core/tokenizer.py` | expanded 句按空格分 token，role 初始为空 |
| `nce2_core/pipeline.py` | txt → Lesson 一站式 |
| `nce2_core/batch.py` | CLI 批量处理 96 课 |
| `nce2_export/generator.py` | Lesson JSON → 单文件 HTML |
| `nce2_export/assets/slide.css` | 幻灯片样式 |
| `nce2_export/assets/slide.js` | 键盘翻页 |
| `nce2_gui/main.py` | 应用入口 |
| `nce2_gui/main_window.py` | 课文列表 + 导出 + 浏览器演示 |
| `data/titles.json` | 96 课标题 |
| `scripts/gen_titles.py` | 生成 titles.json |
| `tests/test_*.py` | 单元/集成测试 |

---

### Task 0: 项目脚手架

**Files:**
- Create: `requirements.txt`, `README.md`, `pytest.ini`, 各包 `__init__.py`

- [ ] **Step 1: 创建目录与依赖文件**

`requirements.txt`:
```
PyQt6>=6.5
pytest>=7.0
```

`pytest.ini`:
```ini
[pytest]
testpaths = tests
pythonpath = .
```

创建空包：
```
nce2_core/__init__.py
nce2_export/__init__.py
nce2_gui/__init__.py
tests/__init__.py
data/lessons/.gitkeep
output/.gitkeep
```

- [ ] **Step 2: 初始化 git（可选）**

Run:
```powershell
cd D:\cursor_work\nce2_sentence_components
git init
git add requirements.txt pytest.ini README.md docs/
git commit -m "chore: scaffold nce2_sentence_components project"
```

---

### Task 1: 数据模型 `models.py`

**Files:**
- Create: `nce2_core/models.py`
- Test: `tests/test_models.py`

- [ ] **Step 1: Write the failing test**

`tests/test_models.py`:
```python
import json
from pathlib import Path

from nce2_core.models import Lesson, Sentence, Token, lesson_to_dict, lesson_from_dict


def test_lesson_roundtrip(tmp_path: Path):
    lesson = Lesson(
        book=2,
        lesson=1,
        title="A private conversation",
        sentences=[
            Sentence(
                id=1,
                original="I'm late.",
                expanded="I am late.",
                has_contraction=True,
                tokens=[
                    Token(text="I", role=""),
                    Token(text="am", role=""),
                    Token(text="late.", role=""),
                ],
            )
        ],
    )
    path = tmp_path / "01.json"
    path.write_text(
        json.dumps(lesson_to_dict(lesson), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    loaded = lesson_from_dict(json.loads(path.read_text(encoding="utf-8")))
    assert loaded.lesson == 1
    assert loaded.sentences[0].expanded == "I am late."
    assert loaded.sentences[0].has_contraction is True
    assert len(loaded.sentences[0].tokens) == 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd D:\cursor_work\nce2_sentence_components && python -m pytest tests/test_models.py -v`  
Expected: FAIL — `ModuleNotFoundError: nce2_core.models`

- [ ] **Step 3: Write minimal implementation**

`nce2_core/models.py`:
```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Token:
    text: str
    role: str = ""


@dataclass
class Sentence:
    id: int
    original: str
    expanded: str
    has_contraction: bool
    tokens: list[Token] = field(default_factory=list)


@dataclass
class Lesson:
    book: int
    lesson: int
    title: str
    sentences: list[Sentence] = field(default_factory=list)


def token_to_dict(token: Token) -> dict[str, Any]:
    return {"text": token.text, "role": token.role}


def token_from_dict(data: dict[str, Any]) -> Token:
    return Token(text=data["text"], role=data.get("role", ""))


def sentence_to_dict(sentence: Sentence) -> dict[str, Any]:
    return {
        "id": sentence.id,
        "original": sentence.original,
        "expanded": sentence.expanded,
        "has_contraction": sentence.has_contraction,
        "tokens": [token_to_dict(t) for t in sentence.tokens],
    }


def sentence_from_dict(data: dict[str, Any]) -> Sentence:
    return Sentence(
        id=data["id"],
        original=data["original"],
        expanded=data["expanded"],
        has_contraction=data["has_contraction"],
        tokens=[token_from_dict(t) for t in data.get("tokens", [])],
    )


def lesson_to_dict(lesson: Lesson) -> dict[str, Any]:
    return {
        "book": lesson.book,
        "lesson": lesson.lesson,
        "title": lesson.title,
        "sentences": [sentence_to_dict(s) for s in lesson.sentences],
    }


def lesson_from_dict(data: dict[str, Any]) -> Lesson:
    return Lesson(
        book=data["book"],
        lesson=data["lesson"],
        title=data["title"],
        sentences=[sentence_from_dict(s) for s in data.get("sentences", [])],
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_models.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add nce2_core/models.py tests/test_models.py
git commit -m "feat: add lesson data models with JSON serialization"
```

---

### Task 2: 缩写展开 `contraction.py`

**Files:**
- Create: `nce2_core/contraction.py`
- Test: `tests/test_contraction.py`

- [ ] **Step 1: Write the failing test**

`tests/test_contraction.py`:
```python
from nce2_core.contraction import expand_contractions, sentence_has_contraction


def test_im_expansion():
    assert expand_contractions("I'm late.") == "I am late."


def test_no_contraction():
    original = "Last week I went to the theatre."
    expanded = expand_contractions(original)
    assert expanded == original
    assert sentence_has_contraction(original, expanded) is False


def test_cant_and_wont():
    assert expand_contractions("I can't hear a word!") == "I can not hear a word!"
    assert expand_contractions("won't") == "will not"


def test_youd():
    assert expand_contractions("You'd better go.") == "You would better go."
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_contraction.py -v`  
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

`nce2_core/contraction.py`:
```python
from __future__ import annotations

import re

# Order matters: longer patterns first
_REPLACEMENTS: list[tuple[re.Pattern[str], str | callable]] = [
    (re.compile(r"\bwon't\b", re.I), "will not"),
    (re.compile(r"\bcan't\b", re.I), "can not"),
    (re.compile(r"\bshan't\b", re.I), "shall not"),
    (re.compile(r"\bn't\b", re.I), " not"),
    (re.compile(r"\bI'm\b"), "I am"),
    (re.compile(r"\bI've\b"), "I have"),
    (re.compile(r"\bI'll\b"), "I will"),
    (re.compile(r"\bI'd\b"), "I would"),
    (re.compile(r"\byou're\b", re.I), "you are"),
    (re.compile(r"\bYou're\b"), "You are"),
    (re.compile(r"\bwe're\b", re.I), "we are"),
    (re.compile(r"\bthey're\b", re.I), "they are"),
    (re.compile(r"\bhe's\b", re.I), "he is"),
    (re.compile(r"\bshe's\b", re.I), "she is"),
    (re.compile(r"\bit's\b", re.I), "it is"),
    (re.compile(r"\bIt's\b"), "It is"),
    (re.compile(r"\bthat's\b", re.I), "that is"),
    (re.compile(r"\bwhat's\b", re.I), "what is"),
    (re.compile(r"\bthere's\b", re.I), "there is"),
    (re.compile(r"\bhere's\b", re.I), "here is"),
    (re.compile(r"\b(\w+)'re\b"), lambda m: f"{m.group(1)} are"),
    (re.compile(r"\b(\w+)'ve\b"), lambda m: f"{m.group(1)} have"),
    (re.compile(r"\b(\w+)'ll\b"), lambda m: f"{m.group(1)} will"),
    (re.compile(r"\b(\w+)'d\b"), lambda m: f"{m.group(1)} would"),
    (re.compile(r"\b(\w+)'m\b"), lambda m: f"{m.group(1)} am"),
    (re.compile(r"\b(\w+)n't\b"), lambda m: f"{m.group(1)} not"),
]


def expand_contractions(text: str) -> str:
    result = text
    for pattern, repl in _REPLACEMENTS:
        if callable(repl):
            result = pattern.sub(repl, result)
        else:
            result = pattern.sub(repl, result)
    return result


def sentence_has_contraction(original: str, expanded: str) -> bool:
    return original != expanded
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_contraction.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add nce2_core/contraction.py tests/test_contraction.py
git commit -m "feat: add English contraction expansion"
```

---

### Task 3: 分句 `splitter.py`

**Files:**
- Create: `nce2_core/splitter.py`
- Test: `tests/test_splitter.py`

- [ ] **Step 1: Write the failing test**

`tests/test_splitter.py`:
```python
from nce2_core.splitter import split_sentences


def test_basic_periods():
    text = "I turned round. I looked at the man."
    assert split_sentences(text) == [
        "I turned round.",
        "I looked at the man.",
    ]


def test_abbreviation_mr():
    text = "Mr. Smith arrived. He sat down."
    assert split_sentences(text) == ["Mr. Smith arrived.", "He sat down."]


def test_quoted_dialogue():
    text = (
        "'It's none of your business,' the young man said rudely. "
        "'This is a private conversation!'"
    )
    result = split_sentences(text)
    assert len(result) == 2
    assert result[0].startswith("'It's none")
    assert result[1] == "'This is a private conversation!'"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_splitter.py -v`  
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

`nce2_core/splitter.py`:
```python
from __future__ import annotations

import re

_ABBREV = (
    r"Mr|Mrs|Ms|Dr|St|Prof|etc|e\.g|i\.e|a\.m|p\.m|No|Vol|Fig"
)
_ABBREV_DOT = re.compile(rf"\b(?:{_ABBREV})\.", re.I)
_DECIMAL = re.compile(r"\d+\.\d+")


def split_sentences(text: str) -> list[str]:
    """Split English text into sentences on . ? ! respecting abbreviations."""
    if not text.strip():
        return []

    # Protect abbreviations and decimals
    protected = text
    placeholders: dict[str, str] = {}

    def _protect(match: re.Match[str]) -> str:
        key = f"§{len(placeholders)}§"
        placeholders[key] = match.group(0)
        return key

    protected = _DECIMAL.sub(_protect, protected)
    protected = _ABBREV_DOT.sub(_protect, protected)

    parts = re.split(r"(?<=[.!?])\s+", protected)
    sentences: list[str] = []
    for part in parts:
        restored = part
        for key, val in placeholders.items():
            restored = restored.replace(key, val)
        restored = restored.strip()
        if restored:
            sentences.append(restored)
    return sentences
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_splitter.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add nce2_core/splitter.py tests/test_splitter.py
git commit -m "feat: add sentence splitter with abbreviation handling"
```

---

### Task 4: TXT 解析 `parser.py`

**Files:**
- Create: `nce2_core/parser.py`
- Test: `tests/test_parser.py`

- [ ] **Step 1: Write the failing test**

`tests/test_parser.py`:
```python
from pathlib import Path

from nce2_core.parser import extract_lesson_body

LESSON1 = Path(r"D:\cursor_work\nce2_sentence_components\nce_txt\第二册\1.TXT")


def test_lesson1_extracts_body():
    body = extract_lesson_body(LESSON1)
    assert "Last week I went to the theatre." in body
    assert "private conversation" in body
    assert "New words" not in body
    assert "Why did the writer complain" not in body


def test_lesson1_not_empty():
    body = extract_lesson_body(LESSON1)
    assert len(body) > 200
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_parser.py -v`  
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

`nce2_core/parser.py`:
```python
from __future__ import annotations

from pathlib import Path


def _is_english_line(line: str) -> bool:
    if len(line) < 15:
        return False
    alpha = sum(c.isascii() and c.isalpha() for c in line)
    return alpha > len(line) * 0.45


def extract_english_lines(raw: str) -> list[str]:
    lines: list[str] = []
    for line in raw.splitlines():
        s = line.strip()
        if not s:
            continue
        if "New words and expressions" in s:
            break
        if _is_english_line(s):
            lines.append(s)
    return lines


def extract_lesson_body(path: Path) -> str:
    data = path.read_bytes().decode("latin-1")
    lines = extract_english_lines(data)
    if not lines:
        return ""

    # Drop leading comprehension question (ends with ?)
    while lines and lines[0].rstrip().endswith("?"):
        lines.pop(0)

    return " ".join(lines)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_parser.py -v`  
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add nce2_core/parser.py tests/test_parser.py
git commit -m "feat: parse NCE tinghere TXT lesson body"
```

---

### Task 5: Tokenizer + Pipeline

**Files:**
- Create: `nce2_core/tokenizer.py`, `nce2_core/pipeline.py`
- Test: `tests/test_pipeline.py`

- [ ] **Step 1: Write the failing test**

`tests/test_pipeline.py`:
```python
from pathlib import Path

from nce2_core.pipeline import build_lesson_from_txt

LESSON1 = Path(r"D:\cursor_work\nce2_sentence_components\nce_txt\第二册\1.TXT")


def test_build_lesson1():
    lesson = build_lesson_from_txt(
        LESSON1, lesson_num=1, title="A private conversation"
    )
    assert lesson.lesson == 1
    assert len(lesson.sentences) >= 14
    assert lesson.sentences[0].original.startswith("Last week")
    assert lesson.sentences[0].has_contraction is False
    # sentence with contraction exists
    contracted = [s for s in lesson.sentences if s.has_contraction]
    assert len(contracted) >= 1
    for s in lesson.sentences:
        assert s.tokens, f"sentence {s.id} has no tokens"
        assert s.id >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_pipeline.py -v`  
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

`nce2_core/tokenizer.py`:
```python
from __future__ import annotations

from nce2_core.models import Token


def tokenize_expanded(expanded: str) -> list[Token]:
    words = expanded.split()
    if not words:
        return []
    return [Token(text=w, role="") for w in words]
```

`nce2_core/pipeline.py`:
```python
from __future__ import annotations

from pathlib import Path

from nce2_core.contraction import expand_contractions, sentence_has_contraction
from nce2_core.models import Lesson, Sentence
from nce2_core.parser import extract_lesson_body
from nce2_core.splitter import split_sentences
from nce2_core.tokenizer import tokenize_expanded


def build_lesson_from_txt(path: Path, lesson_num: int, title: str) -> Lesson:
    body = extract_lesson_body(path)
    raw_sentences = split_sentences(body)
    sentences: list[Sentence] = []
    for idx, original in enumerate(raw_sentences, start=1):
        expanded = expand_contractions(original)
        has_c = sentence_has_contraction(original, expanded)
        sentences.append(
            Sentence(
                id=idx,
                original=original,
                expanded=expanded,
                has_contraction=has_c,
                tokens=tokenize_expanded(expanded),
            )
        )
    return Lesson(book=2, lesson=lesson_num, title=title, sentences=sentences)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_pipeline.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add nce2_core/tokenizer.py nce2_core/pipeline.py tests/test_pipeline.py
git commit -m "feat: add txt-to-lesson pipeline"
```

---

### Task 6: 标题表 + 批量 CLI

**Files:**
- Create: `scripts/gen_titles.py`, `data/titles.json`, `nce2_core/batch.py`
- Test: `tests/test_batch.py`

- [ ] **Step 1: 生成 titles.json**

`scripts/gen_titles.py` — 运行一次写入 96 课标题：

```python
"""Generate data/titles.json for NCE2."""
import json
from pathlib import Path

TITLES = {
    "1": "A private conversation",
    "2": "Breakfast or lunch?",
    "3": "Please send me a card",
    "4": "An exciting trip",
    "5": "No wrong numbers",
    "6": "Percy Buttons",
    "7": "Too late",
    "8": "The best and the worst",
    "9": "A cold welcome",
    "10": "Not for jazz",
    "11": "One good turn deserves another",
    "12": "Goodbye and good luck",
    "13": "The Greenwood Boys",
    "14": "Do you speak English?",
    "15": "Good news",
    "16": "A polite request",
    "17": "Always young",
    "18": "He often does this!",
    "19": "Sold out",
    "20": "One man in a boat",
    "21": "Mad or not?",
    "22": "A glass envelope",
    "23": "A new house",
    "24": "It could be worse",
    "25": "Do the English speak English?",
    "26": "The best art critics",
    "27": "A wet night",
    "28": "No parking!",
    "29": "Taxi!",
    "30": "Football or polo?",
    "31": "Success story",
    "32": "Shopping made easy",
    "33": "Out of the darkness",
    "34": "Quick work",
    "35": "Stop thief!",
    "36": "Across the Channel",
    "37": "The Olympic Games",
    "38": "Everything except the weather",
    "39": "Am I all right?",
    "40": "Food and talk",
    "41": "Do you call that a hat?",
    "42": "Not very musical",
    "43": "Over the South Pole",
    "44": "Through the forest",
    "45": "A clear conscience",
    "46": "Expensive and uncomfortable",
    "47": "A thirsty ghost",
    "48": "Did you want to tell me something?",
    "49": "The end of a dream",
    "50": "Taken for a ride",
    "51": "Reward for virtue",
    "52": "A pretty carpet",
    "53": "Hot snake",
    "54": "Sticky fingers",
    "55": "Not a gold mine",
    "56": "Faster than sound!",
    "57": "Can I help you, madam?",
    "58": "A blessing in disguise?",
    "59": "In or out?",
    "60": "The future",
    "61": "Trouble with the Hubble",
    "62": "After the fire",
    "63": "She was not amused",
    "64": "The Channel Tunnel",
    "65": "Jumbo versus the police",
    "66": "Sweet as honey!",
    "67": "Volcanoes",
    "68": "Persistent",
    "69": "But not murder!",
    "70": "Red for danger",
    "71": "A famous clock",
    "72": "A car called Bluebird",
    "73": "The record-holder",
    "74": "Out of the limelight",
    "75": "SOS",
    "76": "April Fools' Day",
    "77": "A successful operation",
    "78": "The last one?",
    "79": "By air",
    "80": "The Crystal Palace",
    "81": "Escape",
    "82": "Monster or fish?",
    "83": "After the elections",
    "84": "On strike",
    "85": "Never too old to learn",
    "86": "Out of control",
    "87": "A perfect alibi",
    "88": "Trapped in a mine",
    "89": "A slip of the tongue",
    "90": "What's for supper?",
    "91": "Three men in a basket",
    "92": "Asking for trouble",
    "93": "A noble gift",
    "94": "Future champions",
    "95": "A fantasy",
    "96": "The dead return",
}

def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "data" / "titles.json"
    out.write_text(json.dumps(TITLES, ensure_ascii=False, indent=2), encoding="utf-8")
    assert len(TITLES) == 96
    print(f"Wrote {out} ({len(TITLES)} titles)")

if __name__ == "__main__":
    main()
```

Run: `python scripts/gen_titles.py`  
Expected: `Wrote ... data/titles.json (96 titles)`

- [ ] **Step 2: Write batch module + test**

`tests/test_batch.py`:
```python
import json
from pathlib import Path

from nce2_core.batch import batch_import_book2


def test_batch_import_lesson1(tmp_path: Path):
    root = Path(r"D:\cursor_work\nce2_sentence_components")
    titles_path = root / "data" / "titles.json"
    txt_dir = root / "nce_txt" / "第二册"
    out_dir = tmp_path / "lessons"
    batch_import_book2(txt_dir, titles_path, out_dir, lessons=[1])
    out_file = out_dir / "01.json"
    assert out_file.exists()
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["lesson"] == 1
    assert len(data["sentences"]) >= 14
```

`nce2_core/batch.py`:
```python
from __future__ import annotations

import json
from pathlib import Path

from nce2_core.models import lesson_to_dict
from nce2_core.pipeline import build_lesson_from_txt


def load_titles(path: Path) -> dict[str, str]:
    return json.loads(path.read_text(encoding="utf-8"))


def batch_import_book2(
    txt_dir: Path,
    titles_path: Path,
    out_dir: Path,
    lessons: list[int] | None = None,
) -> None:
    titles = load_titles(titles_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    nums = lessons or list(range(1, 97))
    for n in nums:
        title = titles[str(n)]
        txt_path = txt_dir / f"{n}.TXT"
        if not txt_path.exists():
            raise FileNotFoundError(txt_path)
        lesson = build_lesson_from_txt(txt_path, lesson_num=n, title=title)
        out_path = out_dir / f"{n:02d}.json"
        out_path.write_text(
            json.dumps(lesson_to_dict(lesson), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
```

- [ ] **Step 3: Run tests**

Run: `python -m pytest tests/test_batch.py -v`  
Expected: PASS

- [ ] **Step 4: 批量生成全部 96 课**

Run:
```powershell
cd D:\cursor_work\nce2_sentence_components
python -c "from pathlib import Path; from nce2_core.batch import batch_import_book2; batch_import_book2(Path('nce_txt/第二册'), Path('data/titles.json'), Path('data/lessons'))"
```
Expected: `data/lessons/01.json` … `96.json` 存在

- [ ] **Step 5: Commit**

```bash
git add scripts/gen_titles.py data/titles.json nce2_core/batch.py tests/test_batch.py data/lessons/
git commit -m "feat: add NCE2 titles and batch lesson import"
```

---

### Task 7: HTML 幻灯片导出

**Files:**
- Create: `nce2_export/assets/slide.css`, `nce2_export/assets/slide.js`, `nce2_export/generator.py`
- Test: `tests/test_export.py`

- [ ] **Step 1: Write the failing test**

`tests/test_export.py`:
```python
import json
from pathlib import Path

from nce2_core.models import lesson_from_dict
from nce2_export.generator import export_lesson_html

ROOT = Path(r"D:\cursor_work\nce2_sentence_components")


def test_export_lesson1_html(tmp_path: Path):
    lesson_data = json.loads(
        (ROOT / "data/lessons/01.json").read_text(encoding="utf-8")
    )
    lesson = lesson_from_dict(lesson_data)
    out = tmp_path / "lesson_01.html"
    export_lesson_html(lesson, out)
    html = out.read_text(encoding="utf-8")
    assert "Lesson 1: A private conversation" in html
    assert "slide active" in html
    assert "Last week I went to the theatre." in html
    # contraction sentence shows expanded line
    assert "I can not hear a word!" in html or "I am" in html
    assert "<style>" in html
    assert "<script>" in html
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_export.py -v`  
Expected: FAIL

- [ ] **Step 3: Create CSS/JS assets**

`nce2_export/assets/slide.css`:
```css
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; background: #1a1a2e; color: #eee; font-family: "Segoe UI", sans-serif; }
.deck { height: 100%; position: relative; }
.slide {
  display: none; height: 100%; flex-direction: column;
  justify-content: center; align-items: center; padding: 2rem;
}
.slide.active { display: flex; }
.line-title { font-size: 1.4rem; color: #a0c4ff; margin-bottom: 2rem; }
.line-original, .line-expanded {
  font-family: Consolas, "Courier New", monospace;
  font-size: 1.5rem; margin-bottom: 1.2rem;
}
.line-expanded { color: #ffd166; }
.analysis { font-family: Consolas, "Courier New", monospace; font-size: 1.5rem; margin-top: 0.5rem; }
.token-group { display: inline-block; text-align: center; margin-right: 0.6ch; vertical-align: top; }
.token-text { visibility: hidden; height: 0; overflow: hidden; }
.underline { border-bottom: 2px solid #06d6a0; min-width: 2ch; height: 1.6rem; margin: 0 auto; }
.role-label { font-size: 0.95rem; color: #06d6a0; margin-top: 0.3rem; min-height: 1.2rem; }
.hint { position: fixed; bottom: 1rem; right: 1rem; font-size: 0.85rem; color: #666; }
```

`nce2_export/assets/slide.js`:
```javascript
(function () {
  const slides = Array.from(document.querySelectorAll(".slide"));
  let index = 0;
  function show(i) {
    if (i < 0 || i >= slides.length) return;
    slides[index].classList.remove("active");
    index = i;
    slides[index].classList.add("active");
  }
  document.addEventListener("keydown", (e) => {
    if (["ArrowRight", "ArrowDown", " ", "PageDown"].includes(e.key)) {
      e.preventDefault(); show(index + 1);
    } else if (["ArrowLeft", "ArrowUp", "PageUp"].includes(e.key)) {
      e.preventDefault(); show(index - 1);
    } else if (e.key === "Home") {
      e.preventDefault(); show(0);
    } else if (e.key === "End") {
      e.preventDefault(); show(slides.length - 1);
    }
  });
})();
```

- [ ] **Step 4: Write generator**

`nce2_export/generator.py`:
```python
from __future__ import annotations

import html
from pathlib import Path

from nce2_core.models import Lesson, Sentence

_ASSETS = Path(__file__).resolve().parent / "assets"


def _render_token_row(sentence: Sentence) -> str:
    parts: list[str] = []
    for token in sentence.tokens:
        text = html.escape(token.text)
        role = html.escape(token.role) if token.role else "—"
        width = max(len(token.text), 2)
        parts.append(
            f'<span class="token-group">'
            f'<span class="token-text">{text}</span>'
            f'<div class="underline" style="width:{width}ch"></div>'
            f'<div class="role-label">{role}</div>'
            f"</span>"
        )
    return "".join(parts)


def _render_slide(lesson: Lesson, sentence: Sentence) -> str:
    title = html.escape(f"Lesson {lesson.lesson}: {lesson.title}")
    orig = html.escape(f"({sentence.id}) {sentence.original}")
    expanded_line = ""
    if sentence.has_contraction:
        exp = html.escape(f"({sentence.id}) {sentence.expanded}")
        expanded_line = f'<div class="line-expanded">{exp}</div>\n'
    analysis = _render_token_row(sentence)
    return (
        f'<section class="slide">\n'
        f'  <div class="line-title">{title}</div>\n'
        f'  <div class="line-original">{orig}</div>\n'
        f"{expanded_line}"
        f'  <div class="analysis">{analysis}</div>\n'
        f"</section>\n"
    )


def export_lesson_html(lesson: Lesson, out_path: Path) -> None:
    css = (_ASSETS / "slide.css").read_text(encoding="utf-8")
    js = (_ASSETS / "slide.js").read_text(encoding="utf-8")
    slides = "".join(_render_slide(lesson, s) for s in lesson.sentences)
    if lesson.sentences:
        slides = slides.replace('class="slide"', 'class="slide active"', 1)

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lesson {lesson.lesson}: {html.escape(lesson.title)}</title>
<style>{css}</style>
</head>
<body>
<div class="deck">
{slides}
</div>
<div class="hint">← → 翻页 · F11 全屏</div>
<script>{js}</script>
</body>
</html>
"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(doc, encoding="utf-8")
```

- [ ] **Step 5: Run test (requires data/lessons/01.json from Task 6)**

Run: `python -m pytest tests/test_export.py -v`  
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add nce2_export/ tests/test_export.py
git commit -m "feat: export self-contained HTML slides with 4/5 line layout"
```

---

### Task 8: PyQt6 最小 GUI

**Files:**
- Create: `nce2_gui/main.py`, `nce2_gui/main_window.py`

- [ ] **Step 1: 实现主窗口**

`nce2_gui/main_window.py`:
```python
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from nce2_core.batch import batch_import_book2
from nce2_core.models import lesson_from_dict
from nce2_export.generator import export_lesson_html

ROOT = Path(__file__).resolve().parents[1]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("NCE2 Sentence Components")
        self.resize(900, 600)
        self.lessons_dir = ROOT / "data" / "lessons"
        self.output_dir = ROOT / "output"
        self.titles_path = ROOT / "data" / "titles.json"
        self.txt_dir = ROOT / "nce_txt" / "第二册"

        self.list_widget = QListWidget()
        for n in range(1, 97):
            self.list_widget.addItem(f"Lesson {n:02d}")

        self.info_label = QLabel("选择课文，然后导出或演示。")
        self.info_label.setWordWrap(True)

        import_btn = QPushButton("导入 TXT → JSON（全部96课）")
        import_btn.clicked.connect(self.on_import_all)

        export_btn = QPushButton("导出 HTML")
        export_btn.clicked.connect(self.on_export)

        demo_btn = QPushButton("浏览器演示")
        demo_btn.clicked.connect(self.on_demo)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(import_btn)
        btn_layout.addWidget(export_btn)
        btn_layout.addWidget(demo_btn)

        right = QVBoxLayout()
        right.addWidget(self.info_label)
        right.addLayout(btn_layout)
        right.addStretch()

        layout = QHBoxLayout()
        layout.addWidget(self.list_widget, 1)
        layout.addLayout(right, 2)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _selected_lesson_num(self) -> int | None:
        row = self.list_widget.currentRow()
        if row < 0:
            return None
        return row + 1

    def on_import_all(self) -> None:
        try:
            batch_import_book2(self.txt_dir, self.titles_path, self.lessons_dir)
            QMessageBox.information(self, "完成", "已导入 96 课 JSON。")
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def on_export(self) -> None:
        n = self._selected_lesson_num()
        if n is None:
            QMessageBox.warning(self, "提示", "请先选择一课。")
            return
        json_path = self.lessons_dir / f"{n:02d}.json"
        if not json_path.exists():
            QMessageBox.warning(self, "提示", f"找不到 {json_path.name}，请先导入。")
            return
        lesson = lesson_from_dict(json.loads(json_path.read_text(encoding="utf-8")))
        out_path = self.output_dir / f"lesson_{n:02d}.html"
        export_lesson_html(lesson, out_path)
        self.info_label.setText(f"已导出: {out_path}\n共 {len(lesson.sentences)} 句")
        QMessageBox.information(self, "完成", f"已导出到\n{out_path}")

    def on_demo(self) -> None:
        n = self._selected_lesson_num()
        if n is None:
            QMessageBox.warning(self, "提示", "请先选择一课。")
            return
        html_path = self.output_dir / f"lesson_{n:02d}.html"
        if not html_path.exists():
            self.on_export()
            if not html_path.exists():
                return
        subprocess.Popen(["cmd", "/c", "start", "", str(html_path.resolve())], shell=False)


def main() -> None:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

`nce2_gui/main.py`:
```python
from nce2_gui.main_window import main

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 手动验证 GUI**

Run:
```powershell
cd D:\cursor_work\nce2_sentence_components
pip install -r requirements.txt
python -m nce2_gui.main
```
操作：选 Lesson 01 → 导入（若尚未导入）→ 导出 HTML → 浏览器演示 → 键盘 ← → 翻页

Expected: 浏览器打开幻灯片，每句一页，含/不含缩写行正确

- [ ] **Step 3: Commit**

```bash
git add nce2_gui/
git commit -m "feat: add minimal PyQt6 GUI for import export and demo"
```

---

### Task 9: 集成测试 + README

**Files:**
- Create: `tests/test_integration.py`, update `README.md`

- [ ] **Step 1: 集成测试**

`tests/test_integration.py`:
```python
import json
from pathlib import Path

from nce2_core.batch import batch_import_book2
from nce2_core.models import lesson_from_dict
from nce2_export.generator import export_lesson_html

ROOT = Path(r"D:\cursor_work\nce2_sentence_components")


def test_end_to_end_lesson1(tmp_path: Path):
    lessons_dir = tmp_path / "lessons"
    batch_import_book2(
        ROOT / "nce_txt" / "第二册",
        ROOT / "data" / "titles.json",
        lessons_dir,
        lessons=[1],
    )
    lesson = lesson_from_dict(
        json.loads((lessons_dir / "01.json").read_text(encoding="utf-8"))
    )
    html_path = tmp_path / "lesson_01.html"
    export_lesson_html(lesson, html_path)
    html = html_path.read_text(encoding="utf-8")
    assert html.count('class="slide"') == len(lesson.sentences)
    assert "private conversation" in html
```

Run: `python -m pytest tests/ -v`  
Expected: ALL PASS

- [ ] **Step 2: README**

`README.md` 包含：
- 项目简介
- 安装: `pip install -r requirements.txt`
- 启动 GUI: `python -m nce2_gui.main`
- 批量导入: `python -c "..."` 或 GUI 按钮
- 演示: 导出后在浏览器 F11 全屏
- P2 计划简述（成分编辑 GUI）

- [ ] **Step 3: Commit**

```bash
git add tests/test_integration.py README.md
git commit -m "docs: add integration test and README for P1 MVP"
```

---

## P1 完成标准（验收清单）

- [ ] `python -m pytest tests/ -v` 全部通过
- [ ] `data/lessons/` 含 01.json–96.json
- [ ] 导出 `output/lesson_01.html` 可在浏览器全屏演示
- [ ] 无缩写句 4 行（标题/原文/横线+成分）
- [ ] 有缩写句 5 行（多一行 expanded）
- [ ] GUI 可选课文、导入、导出、浏览器打开

---

## Spec Coverage Self-Review

| Spec 章节 | 对应 Task |
|-----------|-----------|
| 数据模型 §5 | Task 1 |
| txt 解析 §6 | Task 4 |
| 分句 §6.3 | Task 3 |
| 缩写 §7 | Task 2 |
| 4/5 行 HTML §8 | Task 7 |
| titles.json §5.1 | Task 6 |
| 批量预处理 §6.4 | Task 6 |
| PyQt6 GUI P1 §9.2 | Task 8 |
| 测试 §12 | Tasks 1–9 |
| C++ 隔离 §3.2 | nce2_core 无 PyQt |

**P2 不在本计划范围**（成分编辑 GUI）→ 后续 plan `...-p2.md`

---

## 后续计划预告

- **P2 Plan:** Token 表格编辑、成分下拉、预览区、合并/拆分 token
- **P3 Plan:** 可选 LLM 预标注、四册扩展
