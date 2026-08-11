---
name: project-requirement-package-builder
description: 方案侧结构化资料包生成（项目订单原始资料包）。当用户要把某个项目的方案握手会资料（PPT/PDF/Excel/Word/会议纪要/转写/图片）整理成结构化的订单原始资料包，或提到"资料包生成/方案资料结构化/握手会资料整理"时使用。输入为项目资料文件夹，输出 project_requirement_package.md/html + metadata.json + evidence_index.json + missing_info_checklist.md。
---

# 方案侧结构化资料包生成 Skill（project_requirement_package_builder）

## When to use this skill

- 方案握手会后，把散落的方案侧资料（PPT / PDF / Excel / Word / Markdown / 会议 summary / 转写文本 / 图片 / 视频）整理成**一个结构化、可追溯的项目订单原始资料包**。
- 为第二阶段「TPM 风险识别与开发清单 Skill」准备高质量输入。
- **不要**用本 Skill 做：最终风险评审、非标判定、版本排期、人天报价——这些是第二阶段的事。

## Inputs

- 一个项目资料文件夹（任意子目录结构，递归扫描）。支持：`.pptx .pdf .xlsx .docx .md .txt .html` 与常见图片；视频/音频仅登记（预留接口，请提供转写文本）。
- 本 Skill 目录下的 `knowledge/`（9 个业务知识文件）与 `../../基础知识库/`（权威车型场景知识）。
- `config.yaml`（抽取阈值与输出文件名）。

## Workflow（严格按顺序执行）

### Step 1 — Stage-1 确定性抽取（跑脚本，不要手工读原始文件）

```bash
python3 "<skill_dir>/src/index.py" extract \
  --input "<输入资料目录>" --output "<输出目录>" --project-name "<项目名>"
python3 "<skill_dir>/src/index.py" scaffold --output "<输出目录>" --project-name "<项目名>"
```

产物：`extracted/manifest.json`、`extracted/F*.json`（带定位符的内容单元）、`assets/`（图片与页面快照）、两个 `.draft.md` 草稿。

### Step 2 — 通读抽取结果

1. 读 `extracted/manifest.json`：确认每个文件的解析状态；失败/跳过的文件记入第 13 章 AI 处理日志。
2. 逐个读 `extracted/F*.json` 的全部单元。**大文件也必须通读**（可分段 Read），不允许只看开头。
3. 对 `needs_visual_reading: true` 的资产：用 Read 工具**逐张视觉读取**关键图片（布局图、载具照片、选配单快照、流程图、现场照片），为每张图写一句"图片说明 + 分类（layout/载具/现场/流程图/货架/托盘/设备/截图）"。数量太多时优先级：整页快照 > layout > 载具/现场照片 > 表格截图 > 装饰图；未读的图片在第 13 章声明"未逐张视觉读取"。

### Step 3 — 名词校准与信息交叉

1. 读 `knowledge/terminology_glossary.md`（含 ASR 转写噪声纠偏指引）和其余 knowledge 文件、`基础知识库/02_VisionNav_车型产品场景知识库.md`。
2. 统一中英文术语；主表达中文，关键英文原词保留在括号中。
3. 转写噪声纠偏：**只有在书面资料交叉印证时才纠偏**，并标注"转写纠偏"；无法印证的保留原词 + "转写存疑，需确认"。
4. 同一事实多处出现且数值冲突时：**两个值都列出**，标记冲突，进待确认清单。

### Step 4 — 写四个输出文件

在草稿基础上产出（模板：`templates/`；schema：`schemas/`）：

1. `project_requirement_package.md` —— 严格按模板 0-13 章结构，一级/二级标题不得增删。
2. `metadata.json` —— 按 `schemas/metadata_schema.json`。
3. `evidence_index.json` —— 按 `schemas/evidence_schema.json`；正文中引用的每个 Exxx 必须在索引中存在。
4. `missing_info_checklist.md` —— 按模板分 A-G 类，可直接拿去开会追问。

完成后删除正文中的 AI 指导注释与草稿文件（`*.draft.md`）。

### Step 5 — Stage-3 渲染与校验（必须跑，必须通过）

```bash
python3 "<skill_dir>/src/index.py" render   --output "<输出目录>"
python3 "<skill_dir>/src/index.py" validate --output "<输出目录>"
```

validate 报错必须修复后重跑；最后向用户汇报：输出位置、解析失败清单、需人工复核项。

## Output format

- 中文为主；结构清晰；**尽量完整，不过度摘要**；图片/表格插入对应章节；每条重要结论带来源。
- 证据引用格式：`（来源：<文件> / <定位>；证据 E001）`，定位如 `slide 12`、`page 7`、`sheet 装卸车（Truck）`、`00:12:35`、`段落 35`。
- 需求清单（第 9 章）与风险提示（第 11 章）用规定表格字段。
- 在正文表格中显式标注 `依据类型`。允许值：`原文明确` / `会议口头信息` / `AI归类` / `AI推断待确认` / `条件性推断` / `无原文依据-不列为当前风险`。
- `条件性推断` 只能用于范围变更提醒，例如“如果客户后续要求某功能，则可能形成非标/算法适配风险”；不得写成当前项目已存在风险。
- 没有项目资料原文支撑的内容不得进入当前需求清单或当前风险提示；如用户追问，明确写 `无原文依据-不列为当前风险`。

## Evidence rules（证据规则）

1. 每条重要结论尽量带来源；无法定位来源的信息不写入正文。
2. 证据可信度四级：`原文明确` / `会议口头信息` / `AI归类` / `AI推断待确认`——在 evidence_index 的 confidence 字段标注。
3. 转写中的数值默认"会议口头信息"；与书面资料冲突时双值并列。
4. 图片证据给 asset_path，说明文字注明出自哪个文件哪一页/哪个 sheet。
5. 正文中的 `依据类型` 必须和 evidence_index 的 confidence 保持一致；若正文是进一步推导，标 `AI推断待确认`，并写明待确认条件。

## Hallucination prevention rules（防幻觉规则）

1. **知识库只能用于解释、归类、命名规范化和提出待确认项**；凡资料中没有明确出现的信息，必须写：`未在资料中明确提供` / `需方案确认` / `基于资料推断，需人工确认`。
2. 不得凭车型型号推断参数；不得脑补尺寸、数量、流程；不得把"可能"写成"确定"。
3. 不做最终研发结论：禁止输出"一定能做 / 不能做 / 一定属于非标 / 排某版本 / 人天 X 天"；允许输出"资料显示可能涉及非标，需 TPM 判断"。
4. 客户设备与我方设备严格分开（客户的 tugger/输送线/扫码枪 ≠ 我方交付物）。
5. 宁可多列待确认项，不可编造确定性。

## Human review requirements（人工复核要求）

输出末尾（第 13 章）必须列出：
- 解析失败/跳过的文件（需人工提供或转换格式）；
- 未逐张视觉读取的图片清单；
- 所有"转写存疑"与"数值冲突"条目；
- 建议由方案同事复核的关键事实（客户名、车数、效率指标、交付时间）。
