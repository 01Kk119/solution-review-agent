---
type: effort-baseline
status: draft-for-review
version: "0.1"
updated: 2026-07-29
unit: person-hour
---

# Effort Estimation Baseline

> [!warning] Draft baseline
> 本表是方案评审阶段的初步人时估算基线，不是报价或排期承诺。正式使用前，应由研发、实施和 TPM 根据历史项目校准。

## Estimation Rules

1. 仅估算已经形成明确交付项、具有稳定事项 ID 的工作。
2. 每项使用“低 / 最可能 / 高”三点估算。
3. 推荐估算值采用 PERT：`(Low + 4 × Most Likely + High) / 6`。
4. 多车型、多站点、多接口或多套环境应使用复杂度系数。
5. 资料不足时标记 `not_estimable`，不得填写 0。
6. 客户施工、采购等待、运输和审批等待时间不计入研发人时。

## Complexity Multipliers

| Complexity | Typical condition | Multiplier |
|---|---|---:|
| Simple | 单车型、单区域、使用标准接口、无新增算法 | 1.0 |
| Moderate | 多区域或多接口，需要配置调整和联合调试 | 1.5 |
| Complex | 多车型、复杂异常流程、新增算法或跨系统联调 | 2.0 |
| High uncertainty | 需求或接口尚未冻结，只能做预估 | 2.5 |

## Work Item Baseline

| Work item | Primary role | Low | Most likely | High | Deliverable / closure condition |
|---|---|---:|---:|---:|---|
| 需求澄清与技术评审 | TPM / Product | 4 | 8 | 16 | 需求、边界、责任人与验收口径冻结 |
| 标准参数与配置调整 | Software / Deployment | 2 | 4 | 8 | 配置文件完成并通过基本验证 |
| 地图制作与导航参数调试 | Navigation / Deployment | 8 | 16 | 32 | 地图、定位和路径测试通过 |
| 新增导航或控制逻辑 | Navigation / Software | 24 | 48 | 96 | 代码、单元测试和场景验证完成 |
| RCS 任务流程配置 | RCS / Software | 8 | 16 | 32 | 标准任务流程及异常分支验证完成 |
| RCS 非标流程开发 | RCS / Software | 24 | 48 | 120 | 开发、接口联调和回归测试完成 |
| 单个外部系统接口适配 | Software / Integration | 16 | 32 | 80 | 协议、点表、联调记录和异常处理完成 |
| HMI 页面或状态展示调整 | Frontend / RCS | 8 | 16 | 40 | 页面、权限和状态同步测试完成 |
| 车体或传感器配置适配 | Hardware / Controls | 8 | 24 | 56 | BOM、接线、参数和功能验证完成 |
| 机械或属具非标设计 | Mechanical | 24 | 48 | 120 | 图纸、评审、样件及验证完成 |
| 明眸标准场景部署 | Brighteyes / Deployment | 12 | 24 | 48 | 相机、网络、模型配置和基础验收完成 |
| 明眸数据采集与模型适配 | Brighteyes / Algorithm | 24 | 56 | 120 | 数据集、标注、模型和指标验证完成 |
| 单专业测试用例与回归 | QA / Domain engineer | 8 | 16 | 40 | 测试记录和缺陷关闭 |
| 多系统现场联合调试 | TPM / Integration / Deployment | 16 | 32 | 80 | 联调问题关闭并形成调试记录 |
| FAT/SAT 支持 | TPM / QA / Deployment | 8 | 24 | 56 | 验收用例执行并完成问题闭环 |
| 技术文档和交付说明 | TPM / Domain engineer | 4 | 8 | 20 | 文档评审通过并进入交付包 |

## Calculation Template

| Item ID | Work item | Role | Quantity | Complexity | Low | Most likely | High | PERT recommendation | Confidence | Evidence |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| Example-01 | 单个外部系统接口适配 | Software / Integration | 1 | 1.5 | 24 | 48 | 120 | 56 | Low | 待补接口协议和点表 |

计算方式：

```text
Adjusted Low = Baseline Low × Quantity × Complexity
Adjusted Most Likely = Baseline Most Likely × Quantity × Complexity
Adjusted High = Baseline High × Quantity × Complexity
PERT = (Adjusted Low + 4 × Adjusted Most Likely + Adjusted High) / 6
```

## Exclusions

以下内容需要单独估算，不直接套用本表：

- 新车型或新控制器平台研发
- 安全认证和法规认证
- 大规模算法研究或全新模型架构
- 客户基础设施施工
- 长周期硬件采购和供应链等待
- 尚未形成明确需求和验收标准的事项
