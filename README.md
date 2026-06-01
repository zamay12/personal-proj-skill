# novel-continuation-agent

`novel-continuation-agent` 是一个基于小说原文的续写 Agent 项目骨架。目标是支持小说 txt 导入、章节切分、章节摘要、人物/事件/设定/伏笔抽取、剧情规划、续写生成、一致性审校和自动修订。

当前版本只实现最小可运行骨架，不包含复杂 Agent 逻辑。

## 项目目标

- 导入小说原文 txt，并将原文沉淀到 `data/raw/`。
- 将章节切分和中间处理结果保存到 `data/processed/`。
- 将人物、事件、设定、伏笔等知识库 JSON 保存到 `kb/`。
- 将向量索引和检索缓存保存到 `vector_store/`。
- 将所有 prompt 模板集中放在 `prompts/`。
- 将所有 skill 文档集中放在 `skills/`。
- 将续写、审校和修订输出保存到 `data/outputs/`。

## 技术栈

- Python 3.11+
- pydantic
- typer
- rich
- python-dotenv
- chromadb
- openai
- streamlit
- pytest

## 安装方式

```powershell
cd novel-continuation-agent
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

如需配置 OpenAI API Key，可在项目根目录创建 `.env`：

```env
OPENAI_API_KEY=your_api_key_here
```

## 运行方式

查看 CLI 状态：

```powershell
$env:PYTHONPATH = "src"
python -m novel_continuation_agent status
```

导入 txt 并切分章节：

```powershell
python -m src.main ingest data/raw/novel.txt
```

处理结果会输出到：

```text
data/processed/chapters.json
```

生成章节摘要：

```powershell
python -m src.main summarize
```

抽取人物、事件、设定和伏笔知识库：

```powershell
python -m src.main extract
```

生成下一章续写闭环：

```powershell
python -m src.main continue-story --after-chapter 23 --direction "推进主角调查父亲失踪真相，不要立刻揭露黑袍人身份" --words 3000
```

续写闭环会按顺序生成：

```text
data/outputs/chapter_plan.json
data/outputs/chapter_draft.md
data/outputs/chapter_review.json
data/outputs/chapter_final.md
```

查看版本：

```powershell
$env:PYTHONPATH = "src"
python -m novel_continuation_agent version
```

启动 Streamlit 占位界面：

```powershell
$env:PYTHONPATH = "src"
streamlit run src/novel_continuation_agent/ui.py
```

运行测试：

```powershell
pytest
```

## 目录结构

```text
novel-continuation-agent/
├── data/
│   ├── raw/
│   ├── processed/
│   └── outputs/
├── kb/
├── vector_store/
├── skills/
├── prompts/
├── src/
│   └── novel_continuation_agent/
├── app/
├── tests/
├── requirements.txt
├── README.md
└── AGENTS.md
```

## 当前能力

- 提供 Typer CLI 入口。
- 提供 Streamlit 占位入口。
- 提供 pydantic 数据模型骨架。
- 支持 txt 导入，自动尝试 `utf-8`、`utf-8-sig`、`gbk` 编码。
- 支持中文和英文章节标题识别，并切分章节与段落。
- 支持章节摘要生成，并保存到 `kb/summaries.json`。
- 支持从章节正文和摘要中抽取人物、事件、设定和伏笔知识库。
- 支持续写闭环：剧情规划、正文起草、一致性审校和自动修订。
- 提供续写 Agent 流程阶段枚举和状态输出。
- 提供 pytest 基础测试。

## 后续路线

1. 实现 txt 导入和章节切分。
2. 实现章节摘要和知识抽取。
3. 实现知识库 JSON schema 和向量检索。
4. 实现剧情规划与续写生成。
5. 实现一致性审校和自动修订。
