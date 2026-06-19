# NCE2 Sentence Components — 设计规格

**日期：** 2026-06-19  
**项目路径：** `D:\cursor_work\nce2_sentence_components`  
**状态：** 已评审（brainstorming 阶段用户确认）

---

## 1. 项目目标

用 HTML 实现 PPT 式演示效果，针对**新概念英语第二册（NCE2）**：

1. 从本地 `nce_txt/第二册/` 读取课文原文
2. 自动分句并编号
3. 自动展开缩写（无缩写时省略缩写行）
4. 对每句进行句子成分划分（含定语、状语、补语、系动词、时间/地点状语等）
5. 每句生成一页 HTML 幻灯片，支持课堂全屏演示
6. PyQt6 GUI 支持成分手工编辑、预览、导出

**优先级：** 课堂全屏演示（A）> 备课编辑（B）> 自学（C）  
**远期：** 核心逻辑移植 C++/Qt6，打包为小 exe。

---

## 2. 已确认的需求决策

| 项 | 决定 |
|----|------|
| 课文来源 | 本地 `nce_txt/第二册/1.TXT`–`96.TXT` |
| 范围 | 仅 NCE2，96 课 |
| 成分划分 | 分阶段（D）：P1 占位 → P2 GUI 手工 → P3 可选 AI 预标注 |
| 成分标签 | 主语、谓语、宾语、表语、系动词、定语、状语、补语、时间状语、地点状语、方式状语、原因状语、目的状语、介词短语、从句、连词、同位语、呼语、独立成分 |
| 幻灯片展示 | 翻页后当前页所有行一次性显示（无逐步动画） |
| 动态行数 | 有缩写 → 5 行；无缩写 → 4 行（省略缩写行） |
| 技术栈 | 方案 1：分层核心库 + PyQt6 GUI + HTML 导出 |
| GUI | PyQt6 桌面应用，导出独立 HTML，浏览器全屏演示 |

---

## 3. 架构

### 3.1 方案选择

采用**分层核心库 + 薄 GUI**（方案 1），弃用单体 PyQt（难移植）和 Web 编辑器（偏离 C++ 路径）。

```
nce_txt/第二册/N.TXT
        │
        ▼
   nce2_core (纯 Python，无 Qt)
   ├── parser      读 txt、过滤 ID3/生词表/理解问句
   ├── splitter    分句 + 编号
   ├── contraction 缩写展开
   └── models      数据类 / JSON 序列化
        │
        ▼
   data/lessons/N.json  ← GUI 读写、成分编辑
        │
        ├── nce2_gui (PyQt6)     选课文、编辑、预览
        └── nce2_export          生成 output/lesson_N.html
                    │
                    ▼
              浏览器全屏演示 (← → 翻页, F11 全屏)
```

### 3.2 C++ 迁移预留

| Python 模块 | 将来 C++ 对应 |
|-------------|---------------|
| `nce2_core/*` | 静态库 `NceCore` |
| `data/lessons/*.json` | 格式不变 |
| `nce2_export/*` | `NceExport` 或模板引擎 |
| `nce2_gui/*` | Qt6 Widgets 重写 |

**约束：** `nce2_core` 与 `nce2_export` 禁止 import PyQt。

---

## 4. 目录结构

```
D:\cursor_work\nce2_sentence_components\
├── nce_txt/                 # 已有，四册课文（本项目只读第二册）
│   └── 第二册/1.TXT … 96.TXT
├── nce2_core/
│   ├── __init__.py
│   ├── parser.py
│   ├── splitter.py
│   ├── contraction.py
│   └── models.py
├── nce2_export/
│   ├── __init__.py
│   ├── generator.py
│   └── assets/              # CSS/JS 模板（导出时可内联）
├── nce2_gui/
│   ├── __init__.py
│   ├── main.py              # 入口
│   └── main_window.py
├── data/
│   ├── titles.json          # 96 课英文标题
│   └── lessons/             # 01.json … 96.json
├── output/                  # 导出的 HTML 幻灯片
├── tests/
│   ├── test_parser.py
│   ├── test_splitter.py
│   └── test_contraction.py
├── docs/superpowers/specs/  # 本文档
├── requirements.txt
└── README.md
```

---

## 5. 数据模型

### 5.1 课文标题 `data/titles.json`

```json
{
  "1": "A private conversation",
  "2": "Breakfast or lunch?",
  "96": "The dead return"
}
```

共 96 条，键为课号字符串。

### 5.2 课文 JSON `data/lessons/01.json`

```json
{
  "book": 2,
  "lesson": 1,
  "title": "A private conversation",
  "sentences": [
    {
      "id": 1,
      "original": "I'm late.",
      "expanded": "I am late.",
      "has_contraction": true,
      "tokens": [
        { "text": "I", "role": "主语" },
        { "text": "am", "role": "系动词" },
        { "text": "late.", "role": "表语" }
      ]
    },
    {
      "id": 2,
      "original": "Last week I went to the theatre.",
      "expanded": "Last week I went to the theatre.",
      "has_contraction": false,
      "tokens": [
        { "text": "Last week", "role": "时间状语" },
        { "text": "I", "role": "主语" },
        { "text": "went", "role": "谓语" },
        { "text": "to the theatre.", "role": "地点状语" }
      ]
    }
  ]
}
```

**字段说明：**

| 字段 | 说明 |
|------|------|
| `original` | 课文原句（含缩写） |
| `expanded` | 展开缩写后的句子 |
| `has_contraction` | `original != expanded`；控制幻灯片 4/5 行 |
| `tokens` | 基于 **expanded** 文本的分词/短语列表；驱动横线与成分行 |
| `tokens[].role` | 成分标签；P1 可为空字符串或 `"—"` |

**Token 划分原则：**

- 默认按空格分词，GUI 支持合并/拆分 token（如 `Last week` 合并为时间状语）
- 标点附着在前一个 token 末尾（如 `late.`、`theatre.`）
- 横线宽度与 `token.text` 字符宽度对齐（等宽字体 + CSS 微调）

---

## 6. 课文 txt 解析

### 6.1 文件特征

`nce_txt/第二册/N.TXT` 为 tinghere.com 资源格式：含 ID3 二进制头 + 嵌入英文课文 + 中文生词表。

### 6.2 解析步骤

1. 二进制读取，`latin-1` 解码（保留字节位置）
2. 过滤 ID3 等非文本区域
3. 提取 ASCII 英文行（字母占比 > 45%）
4. 遇到 `New words and expressions` 停止
5. **跳过**课文前理解问句（独立一行、以 `?` 结尾、位于正文之前）
6. 合并剩余段落为课文正文

### 6.3 分句规则

- 分隔符：`.` `?` `!`
- **不切分**的情况：
  - 常见缩写：`Mr.` `Mrs.` `Ms.` `Dr.` `St.` `etc.` `e.g.` `i.e.` `a.m.` `p.m.`
  - 小数点：`3.14`
- 保留引号对话为完整句子
- 分句后去除首尾空白，空句丢弃
- 全课连续编号 `(1)` `(2)` `(3)` …

### 6.4 批量预处理

提供 CLI（或 GUI 菜单）一次性处理 96 课：

```
python -m nce2_core.batch --book 2 --input nce_txt/第二册 --output data/lessons
```

生成 JSON，`tokens` 初始为空或按空格自动分词、`role` 为空。

---

## 7. 缩写展开

### 7.1 规则

内置缩写字典 + 正则，从 `original` 生成 `expanded`：

| 模式 | 展开 |
|------|------|
| `'m` | am |
| `'re` | are |
| `'ve` | have |
| `'ll` | will |
| `'d` | would / had（按上下文，默认可配置） |
| `'s` | is / has（按上下文） |
| `n't` | not |
| `won't` | will not |
| `can't` | can not |
| `I'm` | I am |
| `you'd` | you would |

- 保留大小写（句首大写）
- 展开后写入 `expanded`；若与 `original` 相同则 `has_contraction = false`

### 7.2 GUI 修正

用户可在 GUI 中手工编辑 `expanded`（非标准口语、特殊缩写）。

---

## 8. HTML 幻灯片

### 8.1 页面结构

每句一页，垂直居中，**一次性显示所有行**。

**5 行模式**（`has_contraction = true`）：

```
Line 1  Lesson 1: A private conversation
Line 2  (3) I'm late.
Line 3  (3) I am late.
Line 4       ___  __  ____          ← 横线，宽度对齐 expanded tokens
Line 5       主语 系动词 表语         ← 成分标签
```

**4 行模式**（`has_contraction = false`）：

```
Line 1  Lesson 1: A private conversation
Line 2  (1) Last week I went to the theatre.
Line 3       ─────────  ─   ────  ── ─── ────────
Line 4       时间状语   主语  谓语  …
```

### 8.2 对齐实现

- 使用等宽字体（如 `Consolas`, `Courier New`）显示 expanded 句与横线行
- 每个 token 为 `inline-block`，横线 `border-bottom` 宽度 = token 文本宽度
- token 间保留空格间隙

### 8.3 交互

| 按键 | 动作 |
|------|------|
| `→` / `↓` / `Space` | 下一句 |
| `←` / `↑` | 上一句 |
| `Home` | 第一句 |
| `End` | 最后一句 |
| `F11` | 浏览器全屏（用户操作） |

### 8.4 导出格式

- 单课导出：`output/lesson_01.html`
- CSS/JS 内联，无外部依赖，可拷贝至 U 盘
- 不引入 Reveal.js 等重型框架

---

## 9. PyQt6 GUI

### 9.1 主界面布局

```
┌─────────────────────────────────────────────────────────┐
│  文件  编辑  导出  演示                                    │
├──────────┬──────────────────────────────────────────────┤
│ 课文列表  │  句子列表                                     │
│ Lesson 1 │  ┌─ 句子编辑 ─────────────────────────────┐  │
│ Lesson 2 │  │ 序号 / 原文 / 展开句 / 含缩写 标记        │  │
│ …        │  ├─ Token 表格 ────────────────────────────┤  │
│ Lesson 96│  │ 文本 │ 成分（下拉框，可编辑）              │  │
│          │  ├─ 幻灯片预览（4 或 5 行模拟）──────────────┤  │
│          │  └──────────────────────────────────────────┘  │
│          │  [保存 JSON]  [导出 HTML]  [浏览器演示]          │
└──────────┴──────────────────────────────────────────────┘
```

### 9.2 功能

| 功能 | 阶段 |
|------|------|
| 选课文、查看句子列表 | P1 |
| 批量导入 txt → JSON | P1 |
| 导出 HTML + 浏览器演示 | P1 |
| Token 表格编辑成分 | P2 |
| Token 合并/拆分 | P2 |
| 编辑 expanded 句 | P2 |
| 幻灯片预览区 | P2 |
| AI 批量预标注 | P3（可选） |

### 9.3 成分下拉词表

主语、谓语、宾语、表语、系动词、定语、状语、补语、时间状语、地点状语、方式状语、原因状语、目的状语、介词短语、从句、连词、同位语、呼语、独立成分、（空）

---

## 10. 分阶段交付

### P1 — MVP（课堂演示）

- [ ] `nce2_core`：parser、splitter、contraction、models
- [ ] `data/titles.json`（96 课标题）
- [ ] 批量生成 96 课 JSON（tokens 自动分词，role 为空）
- [ ] `nce2_export`：HTML 生成（4/5 行动态）
- [ ] `nce2_gui` 最小版：选课文、导出、浏览器演示
- [ ] 单元测试：parser、splitter、contraction

**P1 完成标准：** 选任意一课 → 导出 HTML → 浏览器全屏逐句翻页，横线对齐，成分行显示占位符。

### P2 — 编辑

- [ ] GUI Token 表格 + 成分下拉
- [ ] Token 合并/拆分
- [ ] expanded 句手工编辑
- [ ] 幻灯片预览区
- [ ] 保存/加载 JSON

### P3 — 增强

- [ ] 可选 LLM API 批量预标注
- [ ] 四册扩展接口（UI 暂不开放）

---

## 11. 依赖

```
# requirements.txt（预期）
PyQt6>=6.5
```

P1 核心库无第三方依赖（标准库 `json`, `re`, `pathlib`, `dataclasses`）。

---

## 12. 测试策略

| 模块 | 测试重点 |
|------|----------|
| parser | Lesson 1/2/3 英文提取；跳过理解问句；截断生词表 |
| splitter | 缩写不切；引号对话完整；编号连续 |
| contraction | `I'm`→`I am`；无缩写时 `has_contraction=false` |
| export | 4/5 行切换；横线 token 数一致 |
| integration | Lesson 1 端到端：txt → JSON → HTML |

---

## 13. 风险与对策

| 风险 | 对策 |
|------|------|
| txt 格式不一致 | parser 容错 + 人工抽查前几课 |
| 分句误切 | 缩写白名单 + GUI P2 允许合并句子 |
| 横线对齐偏差 | 等宽字体 + 导出前预览 |
| 96 课标题维护 | 一次性录入 titles.json，可脚本校验条数 |
| C++ 移植范围过大 | 严格隔离 nce2_core，GUI 保持薄层 |

---

## 14. 附录：NCE2 第 1 课示例句子（解析后预期）

**Lesson 1: A private conversation**

1. Last week I went to the theatre.
2. I had a very good seat.
3. The play was very interesting.
4. I did not enjoy it.
5. A young man and a young woman were sitting behind me.
6. They were talking loudly.
7. I got very angry.
8. I could not hear the actors.
9. I turned round.
10. I looked at the man and the woman angrily.
11. They did not pay any attention.
12. In the end, I could not bear it.
13. I turned round again.
14. 'I can't hear a word!' I said angrily.
15. 'It's none of your business,' the young man said rudely.
16. 'This is a private conversation!'

（句 14–16 含缩写，显示 5 行；其余多为 4 行。）

---

*文档版本：v1.0 | 2026-06-19 | brainstorming 用户确认*
