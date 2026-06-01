# AGENTS.md

## 项目约定

- 应用 Python 代码统一放在 `src/`。
- Prompt 模板统一放在 `prompts/`。
- Skill 文档统一放在 `skills/`。
- 知识库 JSON 统一放在 `kb/`。
- 续写、审校、修订等生成结果统一放在 `data/outputs/`。
- 原始小说 txt 放在 `data/raw/`。
- 中间处理产物放在 `data/processed/`。
- 向量库文件和检索缓存放在 `vector_store/`。

## 技术要求

- Python 版本为 3.11+。
- 依赖管理优先使用 `requirements.txt`。
- CLI 使用 `typer`。
- 终端输出使用 `rich`。
- 数据结构和配置模型使用 `pydantic`。
- 环境变量使用 `.env` 和 `python-dotenv`。
- 测试框架使用 `pytest`。

## 质量要求

- 新增核心逻辑必须添加 pytest 测试。
- 测试应覆盖正常流、边界值和异常流。

## 实现边界

- 当前阶段只维护最小可运行骨架。
- 不在 `src/` 外编写应用运行代码。
- 不把大体积小说原文、生成结果、向量索引提交到版本库。
