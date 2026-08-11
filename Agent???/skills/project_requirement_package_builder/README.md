# 方案侧结构化资料包生成 Skill（project_requirement_package_builder）

> 对内口径：**项目订单原始资料包生成**。
> 注意：这里的"原始资料包"不是原始文件的堆放，而是 **AI 对方案侧资料做结构化转写后的资料包**——
> 尽可能完整保留原始信息 + 全程可追溯 + 明确标注不确定性，供第二阶段 TPM 做风险识别、
> 开发清单、版本规划与报价人天判断。本 Skill **不做**这些最终判断。

## 1. 这个 Skill 做什么

输入：一个项目的方案握手会资料文件夹（PPT / PDF / Excel / Word / Markdown / 会议 summary / 转写文本 / 图片 / 视频）。

输出（到指定输出目录）：

| 文件 | 说明 |
|---|---|
| `project_requirement_package.md` | 主资料包（0-13 章固定结构，中文，带证据引用） |
| `project_requirement_package.html` | 由 Markdown 渲染，带目录锚点，适合评审阅读 |
| `metadata.json` | 项目级元数据（schema 见 `schemas/metadata_schema.json`） |
| `evidence_index.json` | 证据索引：每条重要信息 → 源文件位置（可追溯） |
| `missing_info_checklist.md` | 缺失信息追问清单（分 A-G 类，可直接拿去开会） |
| `assets/` | 从各文件提取的图片、整页快照、表格资产 |
| `extracted/` | Stage-1 中间产物：`manifest.json` + 每文件的结构化单元 JSON |

## 2. 工作原理（三段式）

1. **Stage-1 确定性抽取（代码）**：`src/index.py extract` 递归解析输入目录所有文件 →
   带定位符（slide/page/sheet/段落/时间戳）的内容单元 JSON + 图片资产。
   纯图片 PDF 自动生成整页快照并标记 `needs_visual_reading`。
2. **Stage-2 结构化转写（AI，Claude 按 `SKILL.md` 执行）**：通读抽取结果、视觉读取关键图片、
   按 `knowledge/` + `基础知识库/` 做名词校准，写出四个输出文件。**这一步是 Skill 的核心，
   规则（证据、防幻觉、不做最终结论）都在 `SKILL.md`。**
3. **Stage-3 渲染与校验（代码）**：`render` 生成 HTML；`validate` 检查必需文件、章节完整性、
   metadata 字段、证据索引合法性、正文引用的证据编号与图片是否存在。

## 3. 输入目录怎么放

子目录结构**不强制**（递归扫描），推荐按类分目录：

```text
input_project/
  01_customer_ppt/  02_customer_pdf/  03_excel/  04_word_docs/
  05_meeting_summary/  06_transcripts/  07_images/  08_videos_optional/  09_other/
```

## 4. 怎么运行

推荐方式：在 Claude Code 中直接说——

> 用 project_requirement_package_builder 处理 `<资料目录>`，输出到 `<输出目录>`，项目名 XXX

Claude 会按 `SKILL.md` 完成全部三段。命令行方式（Stage-1/3）：

```bash
# 一步跑抽取 + 草稿（随后由 Claude 完成正文，再自动 render+validate）
python3 "skills/project_requirement_package_builder/src/index.py" run \
  --input ./input_project --output ./output_project --project-name "XXX项目" --language zh-CN

# 分步
python3 ".../src/index.py" extract  --input ./input_project --output ./output_project
python3 ".../src/index.py" scaffold --output ./output_project
python3 ".../src/index.py" render   --output ./output_project
python3 ".../src/index.py" validate --output ./output_project
```

依赖（Python 3.10+）：`pymupdf`、`python-pptx`、`python-docx`、`openpyxl`、`markdown`、`pyyaml`、
测试用 `pytest`。均为轻量稳定库：`pip install pymupdf python-pptx python-docx openpyxl markdown pyyaml`。

## 5. 如何添加 knowledge

- 本 Skill 的业务知识在 `knowledge/`（9 个文件：术语表、车型、场景、载具、取放、导航、调度、软件、硬件）。
- 公司级权威车型知识在 `基础知识库/`（`config.yaml` 的 `knowledge_dirs` 引用，排前者优先）。
- 直接新增/编辑 Markdown 即可，无需改代码。**知识库只用于解释/归类/名词规范化/提出待确认项，
  不允许据此编造项目事实**——新增知识时请保持这一纪律（文件头部注明）。

## 6. 如何处理解析失败

- 单文件解析失败**不会中断**整体流程：失败原因写入 `extracted/manifest.json` 和资料包第 13 章"AI 处理日志"。
- 常见处理：旧版 `.xls/.doc/.ppt` → 另存为新格式重跑；加密 PDF → 解密后重跑；
  损坏文件 → 找方案同事重新导出。
- 重跑只需再次执行 `extract`（输出目录内容会更新）。

## 7. 人工复核建议

资料包生成后，建议按顺序复核：
1. 第 13 章 AI 处理日志：解析失败/未视觉读取的图片/转写存疑项；
2. 第 0.3 节信息可信度说明 + 第 10 章待确认清单：逐条认领（方案/客户/TPM/现场/研发）;
3. 关键事实抽查：客户名、车型车数、效率数字、交付时间——对照 `evidence_index.json` 回源核对；
4. `missing_info_checklist.md` 交给项目经理跟踪补齐。

## 8. 当前能力边界与后续扩展点

| 能力 | 现状 | 扩展点 |
|---|---|---|
| 视频/音频 | 仅登记不解析（`extract_media.py` 预留接口） | 接转写服务后，把转写文本放入输入目录即可 |
| OCR | 不用本地 OCR；纯图片页生成快照由 Claude 视觉读取 | 需要批量离线 OCR 时可接 tesseract/云 OCR |
| 复杂 PDF 表格 | PyMuPDF find_tables 尽力而为，失败只记日志 | 可接 camelot/表格识别模型 |
| Excel 图表 | 不解析（记入日志） | 可加 chart XML 解析 |
| 旧版 Office（.xls/.doc/.ppt） | 登记为暂不支持并提示转存 | 可接 libreoffice 转换 |
| DOCX 浮动图片 | 段落内嵌图片可提取，个别浮动锚点图可能遗漏 | 可补 document.xml 全量 drawing 扫描 |
| 大图压缩 | 原图直存 | 可加缩略图生成 |

## 9. 测试

```bash
cd skills/project_requirement_package_builder && python3 -m pytest tests/ -q
```

8 个用例覆盖：目录读取、类型识别、损坏文件不中断、视频登记、快照与视觉标记、
表格与合并单元格、转写时间戳定位、草稿生成、处理日志、渲染、校验通过与校验报错。

## 10. 与第二阶段的衔接

第二阶段「TPM 风险识别与开发清单 Skill」直接读取本 Skill 输出的
`project_requirement_package.md` + `evidence_index.json`。因此：
- 第 9 章需求清单、第 10 章待确认、第 11 章资料侧风险提示必须按当前模板字段输出，尤其要保留 `依据类型` 字段；
- 证据编号 Exxx 是跨阶段追溯的主键。
