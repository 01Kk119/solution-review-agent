---
type: knowledge-governance
domain: pick_place
status: proposal
created: 2026-07-29
updated: 2026-07-29
---

# 取放TPM知识库结构优化建议

## 1. 推荐目录

```text
03_knowledge/
├─ risk_indexes/
│  └─ pick_place_development_risk_index.md
├─ capability_specs/
│  ├─ pick_place_knowledge/
│  │  ├─ pick_and_place_review_master_guide.md
│  │  ├─ pick_and_place_version_boundary_matrix.md
│  │  └─ pick_and_place_knowledge_governance.md
│  ├─ pick_and_place_capability_spec.md
│  ├─ load_carrier_capability_spec.md
│  └─ sources/
└─ evidence/
   └─ pick_place/
      ├─ meeting_transcripts/
      ├─ screenshots/
      └─ test_reports/
```

职责：

- `risk_index`：Agent默认读取的短索引，只保留评审顺序、关键边界和回查路由。
- `master_guide`：唯一总入口，包含完整方法、判断逻辑、非标分类和向下引用。
- `version_boundary_matrix`：只存版本差异和参数，禁止混入解释性长文。
- `capability_spec`：原始规格表的结构化导出。
- `sources`：不可直接改写的原始资料，仅用于追溯，不进入日常阅读路径。
- `evidence`：会议、截图、测试报告等证据。

## 2. 推荐数据结构

每项能力建议采用唯一ID：

```yaml
capability_id: PP-RACK-SHUTTLE-CLOSED_LOOP
domain: pick_place
scene: rack
rack_type: shuttle
action: place
mode: closed_loop
version:
  5.2.2: unsupported
  5.3.2: supported
vehicle_models: []
hardware_requirements: []
parameter_boundaries: []
exceptions: []
evidence:
  - source: meeting_transcript
    location: "01:21:33-01:24:24"
verification_status: needs_parameter_spec
owner: pick_place_tpm
```

参数不要写在大段描述中，建议拆成：

```yaml
- parameter: lateral_clearance
  operator: ">="
  value: 210
  unit: mm
  condition:
    version: 5.2.2
    rack_type: beam
    lift_height_max: 3
    lift_height_unit: m
  source: pick_and_place_capability_spec
```

## 3. 版本结构

版本表建议至少包含：

- 产品版本；
- 取放能力代号；
- 车型；
- 场景；
- 功能状态：支持/不支持/条件支持/未验证/资料不足；
- 硬件要求；
- 参数边界；
- 测试状态；
- 发布状态；
- 来源和时间；
- 责任人。

不要在同一单元格中混放“计划、开发、合并、测试、发布”状态。

## 4. 引用关系

推荐关系：

```text
项目需求
→ capability_id
→ 版本能力
→ 参数边界
→ 原始规格表单元格/会议时间戳/测试报告
→ 风险结论
→ 非标项或验证项
```

每条非标结论必须能回溯到：

- 客户需求证据；
- 标准能力证据；
- 两者差异；
- 责任人；
- 关闭证据。

## 5. 当前需要修订的源数据

1. 将260430主版本号从源表中的5.3.1按确认口径修订为5.3.2。
2. 在源表中明确标注`251230＝5.3.1独立版本`，并禁止将该列继承到5.3.2。
3. 把“高位货架闭环”拆成：
   - 横梁式货架闭环；
   - 穿梭式货架闭环；
   - 其他货架闭环。
4. 在每个场景工作表增加明确的“产品版本”列，避免借用其他版本列。
5. 为站台闭环补充5.3.2是否支持的正式结论。
6. 为穿梭式货架闭环补充车型、硬件、尺寸、净空、精度、效率、成功率和异常恢复。
7. 统一单位为`mm、m、s、%、μm、°`，禁止在转写摘要中二次换算。
8. 缠膜能力拆成纯激光和视觉两条，并分别记录膜厚、颜色、透光、相机和训练要求。
9. 将“理论可以”“应该支持”“没测过”等表述改成正式状态字段。
10. 为参数增加生效条件，避免P/E、SL/L/R、双叉、四叉互相套用。
11. 给每次规格更新增加变更记录和审批人。

## 6. 建议的质量门禁

- 缺版本、车型、单位、来源或适用条件的能力不得进入“标准支持”状态。
- 自动转写数值不得直接进入参数库。
- 汇总表与场景明细冲突时阻止发布。
- “支持”但没有参数或测试证据时自动降级为“条件支持/待验证”。
- Agent输出非标结论前必须引用能力ID和差异字段。
