# NCE2 Sentence Components

新概念英语第二册（NCE2）句子成分分析 + HTML 幻灯片演示工具。

## 功能

### P1（已完成）
- 从 `nce_txt/第二册/` 解析课文（96 课）
- 自动分句编号、缩写展开
- 导出单文件 HTML 幻灯片（每句一页，键盘 ← → 翻页）
- 有缩写句 5 行 / 无缩写句 4 行

### P2（已完成）
- 三栏 GUI：课文列表 · 句子列表 · 编辑器
- Token 表格编辑文本与成分（下拉 + 可自定义输入）
- 合并/拆分 token
- 编辑展开句（去缩写行）
- 幻灯片预览区
- 保存 JSON

### P3（已完成）
- **AI 预标注**：OpenAI 兼容 API（设置 → 标注本句/本课）
- **四册扩展接口**：`nce2_core/catalog.py`（当前仅启用第二册）

## AI 预标注配置

1. 复制 `config/ai.json.example` 为 `config/ai.json`
2. 填写 `api_base`、`api_key`、`model`，设 `"enabled": true`
3. 或在环境变量中设置：`NCE2_AI_API_KEY`、`NCE2_AI_API_BASE`、`NCE2_AI_MODEL`

GUI 中点击 **AI 设置** → **AI 标注本句** / **AI 标注本课**。标注结果可手工修改后保存。

## 安装

```powershell
cd D:\cursor_work\nce2_sentence_components
pip install -r requirements.txt
```

## 启动 GUI

```powershell
python -m nce2_gui.main
```

1. 左侧选课文 → 中间选句子
2. 编辑 token 成分 → 「保存本课」
3. 「导出 HTML」→ 「浏览器演示」（F11 全屏，← → 翻页）

## 测试

```powershell
python -m pytest tests/ -v
```

## 项目结构

```
nce2_core/     解析、分句、缩写、token 操作、JSON I/O
nce2_export/   HTML 幻灯片生成
nce2_gui/      PyQt6 桌面界面 + 预览组件
data/          titles.json + lessons/*.json
```

## 路线图

- **远期**：C++/Qt6 小 exe；启用第一/三/四册（已预留 catalog）

## 文档

- 设计规格：`docs/superpowers/specs/2026-06-19-nce2-sentence-components-design.md`
- P1 计划：`docs/superpowers/plans/2026-06-19-nce2-sentence-components-p1.md`
