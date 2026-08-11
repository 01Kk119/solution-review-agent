# 方案评审工作台

本地 Web 应用原型。浏览器负责项目操作，Python 后端负责 SQLite、原始文件、AI 产物和 Agent 运行记录。

## 启动

最简单的方法：返回上一级 `01_Agent程序与知识库` 文件夹，双击：

```text
打开方案评审工作台.cmd
```

它会在后台启动服务并自动打开浏览器，不需要操作 PowerShell。

也可以手动运行 `start.ps1`：

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

默认地址：`http://127.0.0.1:8765`

## 数据位置

- SQLite：`../02_项目资料与运行数据/工作台数据/review_console.db`
- 新上传的原始资料：`../02_项目资料与运行数据/工作台数据/uploads/<项目编号>/`
- 既有项目：从 `../02_项目资料与运行数据/项目记录/` 自动建立索引，不复制原文件。

数据库分开保存：

- `projects`：项目主数据
- `files`：原始附件元数据和哈希
- `runs`：每次评审任务
- `run_events`：Agent 阶段与状态摘要
- `artifacts`：文件解析结果、需求模型和 AI 评审产物
- `stage_cache`：按输入、知识版本和模型指纹缓存阶段结果，用于未变化资料的增量复评
- `ai_usage`：逐次记录模型输入字符、Token、缓存命中和调用用途
- `knowledge_feedback_tasks`：TPM 知识反馈的状态、目标知识库、文件路径、哈希和发布审计索引

## TPM 知识反馈

每个项目页底部提供“TPM 知识反馈”。使用顺序：

1. 填写结构化反馈，可选引用最多 3 份项目已有资料；引用不会复制文件。
2. 保存后生成不可由 AI 改写的原始反馈 Markdown。
3. 手动启动一次 DeepSeek 分析；模型只读取所选 Agent 的一份风险索引。
4. TPM 编辑并确认分析结果后，系统才把标记区间内的条目写入正式知识库。

反馈文件与正式 Agent 知识库分开保存：

```text
knowledge_feedback/
├─ 01_raw/
├─ 02_analysis/
├─ 03_confirmed/
└─ history/
```

发布前会校验知识库哈希并检查是否有评审正在运行。正式写入采用串行锁和原子替换，同时保存写入前、写入后及 diff 记录。保存反馈和发布知识均不会自动重新运行项目评审，也不会改变 Agent 架构和输出格式。

## 接入正式 AI 执行器

工作台已接入 DeepSeek 官方 Chat Completions：

- API 地址：`https://api.deepseek.com/chat/completions`
- 默认模型：`deepseek-v4-flash`
- 密钥环境变量：`DEEPSEEK_API_KEY`
- 可选环境变量：`DEEPSEEK_BASE_URL`、`DEEPSEEK_MODEL`

仍可双击项目根目录的 `设置智谱API.cmd` 配置密钥。启动脚本仅为迁移目的读取一次旧的 `SILICONFLOW_API_KEY`，请求地址和模型不会继承旧配置。

返回内容、模型、token 用量和请求 ID 会分别记录到任务和 Agent 事件中；不会保存模型的内部思维内容。

## 运行成本控制

- 领域 Agent 最多并发 2 个；每个请求独立超时和重试，单个失败不会阻塞其他领域。
- 需求建模只生成附件状态、关键字段、术语归一、REQ ID、证据、冲突和缺失项。
- 领域 Agent 默认只读 `agent/03_knowledge/risk_indexes/` 下的开发风险索引；高风险、证据冲突或索引缺口才定向回查源文件。
- 软件能力先检查 5.2.2；确认缺口后才加载 5.3.2 索引。
- 跨 Agent 问题由 Runner 直接路由，领域汇总由 Runner 直接拼装，不再调用协调或汇总模型。
- Evidence Critic 先执行规则检查；只有高风险无证据、冲突、错引、二进制证据缺口或领域失败时才执行定向语义复核。
- 交付决策按职责读取压缩输入，不再重复携带全量原始资料。
- 最终仅主报告调用一次汇总模型；版本、定制、非标和人时附件直接由上游结构化结果固化。
- HTTP 402、依赖产物缺失和决策链失败会立即停止，避免继续产生无效调用。

可通过环境变量调整保护阈值：

```powershell
$env:REVIEW_MAX_AI_CALLS = "18"
$env:REVIEW_MAX_PROMPT_TOKENS = "220000"
$env:REVIEW_MAX_CONTEXT_CHARS = "60000"
$env:REVIEW_CACHE_ENABLED = "1"
```

最简单的配置方法：双击上级目录的 `设置智谱API.cmd`，输入 API Key，然后重新启动工作台。API Key 保存为当前 Windows 用户环境变量，不写入前端、SQLite 或源码。

没有配置密钥时，工作台会显示“AI API 未配置”，启动评审会被阻止，不会再运行模拟流程。

## 自动发布到 Obsidian

每个 AI 阶段产物在保存到 `data/generated/` 和 SQLite 后，还会串行发布一份 Markdown 副本到 Obsidian。

默认 Obsidian 运行数据目录：

```text
../02_项目资料与运行数据/Obsidian运行数据
```

发布结构：

```text
review_outputs/<project_key>/
├─ project_output_index.md
├─ step1_requirements/
├─ step2_domain_review/
├─ step3_evidence_critique/
├─ step4_delivery_decisions/
└─ final/
   └─ <project_key>_final_review.md
```

最终报告使用固定 ASCII 名称。复评时，旧报告先移动到 `final/history/<timestamp>/`，再生成新的当前版本。

可以通过环境变量更改 Obsidian 运行数据路径：

```powershell
$env:OBSIDIAN_VAULT_PATH = "D:\MyObsidianVault"
```

如需临时关闭发布：

```powershell
$env:OBSIDIAN_PUBLISH_ENABLED = "0"
```

Obsidian 发布失败时，原运行产物仍会保留，并在 `run_events` 中记录 `Obsidian Publisher` 警告。
