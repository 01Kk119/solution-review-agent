---
type: spreadsheet-knowledge
source_file: "sources/pick_and_place_capability_spec.xlsx"
sheet_count: 12
conversion: "one-time Markdown export"
status: extracted
---

# 取放能力规格

> [!note] Source fidelity
> This Markdown is a one-time text/table export for Obsidian and Agent retrieval. The original Excel workbook remains authoritative for formatting, formulas, images, merged cells, and future updates.

## Workbook overview

- Source: `sources/pick_and_place_capability_spec.xlsx`
- Worksheets: 12
- Worksheet names: `说明`, `场景功能清单`, `料笼堆叠-P&E`, `料笼堆叠-SL&R`, `站台、输送线、旋转台、翻转台取放货-P&E`, `站台、输送线、旋转台、翻转台取放货-SL&L&R`, `板货堆叠-SL&L`, `板货堆叠-P&R&E`, `货柜车-双叉E`, `货柜车-四叉E`, `货柜车-ST`, `高位货架-R`

## Worksheet: 说明

- Extracted range size: 0 rows x 0 columns

_No non-empty cells._

## Worksheet: 场景功能清单

- Extracted range size: 35 rows x 7 columns

| A | B | C | D | E | F | G |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 功能 | 价值 | 160版 | 250930lite | 251230 | 260430 |
| 最初定义 |  |  | 2024年主版本 | 2025年产线版本 | 2025年最终合并版 | 2025年最终合并版 |
| 操作系统 |  | linux方便仿真验证 | win | linux | linux | linux |
| 网络安全 |  | 客户准入要求 | 不支持 | 支持 | 支持 | 支持 |
| VDA | VDA5050 | 对接第三方中控 | 不支持 | 支持 | 支持 | 支持 |
|  |  |  |  |  |  |  |
| 场景&功能 | 基础功能（基础导航、大地图、手持器、地面取放、<br>产线取放、货架取放、<br>单种料笼堆叠、板货堆拆、<br>e车装卸、st装车、立体防护） | 基础功能 | 支持 | 支持 | 支持 | 支持 |
|  | 多款大料笼堆叠 | 同时堆叠多种料笼 | 不支持 | 不支持 | 支持 | 支持 |
|  | 卡板箱堆叠 | 能堆卡板箱 | 不支持 | 不支持 | 不支持 | 支持 |
|  | 高位货架闭环 | 提升高位货架放货左右容差和安全 | 不支持 | 不支持 | 支持 | 支持 |
|  | 站台对接 | 能做115这类精确放货场景 | 不支持 | 不支持 | 支持 | 支持 |
|  | 4叉装车 | 4叉装车 | 不支持 | 不支持 | 不支持 | 支持 |
|  | 夹抱堆叠 | 夹抱场景 | 不支持 | 不支持 | 支持 | 支持 |
|  | ST卸车 | ST卸车订单需求 | 不支持 | 不支持 | 支持 | 支持 |
|  | 缠膜托盘、窄墩托盘 | 北美载具适配 | 不支持 | 不支持 | 支持 | 支持 |
|  |  |  |  |  |  |  |
| 硬件需求 | R车放货激光 | 用于高位货架闭环 | 不支持 | 不支持 | 支持 | 支持 |
|  | 智能货叉2.0 | 适配不完全入叉（2D激光、称重） | 不支持 | 不支持 | 支持 | 支持 |
|  | 语音播报 | / | 支持 | 支持 | 支持 | 支持 |
|  | 音响 | 便于更换音效、告警语音 | 不支持 | 支持 | 支持 | 支持 |
|  | 串口 | / | 支持 | 支持 | 支持 | 支持 |
|  | 嵌入式以太网协议 | 提高硬件可靠性、避免串口串扰导致的异常 | 不支持 | 不支持 | 不支持 | 不支持 |
|  |  |  |  |  |  |  |
| 版本号 |  | 主版本号 | 5.2.0 | 5.2.2 | 5.3.1 | 5.3.1 |
|  |  | 固件版本 | 5.2.0.14_260130_Hotfix_Yashi_US24160 | 5.2.2.16_251121_Hotfix_yjp |  |  |
|  |  | 定位版本 | 5.2.1_20250828_US24160_xjh | 5.2.2_3_251013_test |  |  |
|  |  | 感知版本 | E:5.2.0.11_250920_project_VN24160_chew<br>R:5.2.0.11_251001_project_VN24160_chew_R | 5.2.2.7_251114_release_zhewang |  |  |
|  |  | 控制版本 | 5.2.0.33_250917_lwj_hotfix5 | 5.2.2.10_251120_zr_test |  |  |
|  |  | robotune版本 | robotune_5.2.0_160_820_20260130-202204 | V5.3.0.13.20251120_release |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  | F |  |  |  |
|  | 0 |  | G |  |  |  |

## Worksheet: 料笼堆叠-P&E

- Extracted range size: 22 rows x 6 columns

| A | B | C | D | E | F |
| --- | --- | --- | --- | --- | --- |
| 料笼堆叠 - P&E |  |  |  |  |  |
| 类别 | 能力描述 | 图示 | 160版本能力 | 260430版本能力 | 风险提示 |
| Vehicle Body原车&属具 | Vehicle Model车型 | 81 | E&P | E&P |  |
|  | Fork 属具 | / | 双叉；<br>横移：±100mm | 双叉；<br>横移：±100mm |  |
|  | Sensor传感器 |  | 感知：<br>闭环堆叠 - 双M感知激光 | 感知：<br>闭环堆叠 - 双M感知激光 |  |
| Workflow Description 业务类型 | Depalletizing 拆垛 | / | 1. 支持层数和高度已知的拆垛 | 1. 支持层数和高度已知的拆垛 |  |
|  | Stacking 堆垛 | / | 堆叠闭环：<br>1. 支持一款料笼闭环（水平）；<br>2. 支持放货空间检测； | 堆叠闭环：<br>1. 同时支持多款料笼闭环；<br>2. 支持不完全入叉、俯仰堆叠；<br>3. 支持料笼混堆（料笼非同种，但料笼脚杯脚墩可以堆叠时）；<br>4. 支持感知半出叉堆叠确认；<br>5. 支持堆叠失败时放到其他库位尝试再次堆叠； |  |
| Stacking Requirement堆叠要求 | Maximum Cargo Placement Accuracy 堆叠容差 |  | ≥±7mm | ≥±7mm |  |
|  | Safety Distance Between the Highest Surface of the Goods and the Underside of the Beam抬升后离天花板高度预留值 |  | 1. 无俯仰堆叠：300mm | 1. 无俯仰堆叠：300mm<br>2. 带俯仰堆叠：500mm |  |
|  | Maximum Stacking Height 支持堆叠最大高度 |  | 4500mm（E车最大的门架高度 = 堆叠时，载具插孔的最高高度) | 4500mm（E车最大的门架高度 = 堆叠时，载具插孔的最高高度) |  |
|  | Lateral spacing 库位左右间距<br>L3：车比货宽时，车与旁边货物间距<br>L4：货比车宽时，货与旁边货物间距 |  | L3=300mm、L4=300mm | L3=300mm、L4=300mm |  |
|  | Front-to-back spacing 库位前后间距<br>D1: Minimum front/back safety distance of goods |  | 100mm | 100mm |  |
|  | Maximum Cargo Deviation 自主纠偏能力 |  | 下方料笼左右偏移100mm/5°能保证堆叠成功 | 下方料笼左右偏移100mm/5°能保证堆叠成功 |  |
| 检测特征指标 | Cage Outer Dimension W 料笼宽度 |  | P车最大可做料笼宽度1900mm内的料笼（受限于传感视野）<br>E车最大可做料笼宽度3800mm内的料笼 | P车最大可做料笼宽度1900mm内的料笼（受限于传感视野）<br>E车最大可做料笼宽度3800mm内的料笼 |  |
|  | Cage Bottom Requirement底面要求 | 81 | 容差≥20mm，没有要求；<br>容差＜20mm：<br>1、料笼下表面左右有支撑梁结构，梁深大于4cm<br>2、不可以为纯平面结构 | 容差≥20mm，没有要求；<br>容差＜20mm：<br>1. 下表面有支撑梁结构，梁深大于4cm<br>2. 不可以为纯平面结构 |  |
|  | 被堆叠料笼上表面要求 |  | 货物不能高于两侧横梁或露出10厘米的两侧立柱 | 货物不能高于两侧横梁或露出10厘米的两侧立柱 |  |
|  | Cage Deformation料笼变形 |  | ≤±5mm | ≤±5mm |  |
| 效率 | 取货效率（从到达检测高度开始，到抬起货叉结束） |  | 31s | 31s |  |
|  | 放货效率（从开始检测底部料笼开始，到完全出叉结束） |  | 水平堆叠：85s | 1. 水平堆叠：85s<br>2. 俯仰堆叠：107s |  |
| 成功率 | 解跺 |  | 0.99 | 0.99 |  |
|  | 堆叠（1次成功率，10mm容差） |  | 0.8 | 0.8 |  |
|  | 堆叠（3次成功率，10mm容差） |  | 0.99 | 0.99 |  |

## Worksheet: 料笼堆叠-SL&R

- Extracted range size: 19 rows x 6 columns

| A | B | C | D | E | F |
| --- | --- | --- | --- | --- | --- |
| 料笼堆叠 - SL&R |  |  |  |  |  |
| 类别 | 能力描述 | 图示 | 160版本能力 | 251230版本能力 | 风险提示 |
| Vehicle Body原车&属具 | Vehicle Model车型 | 81 | SL、L、R | SL、L、R |  |
|  | Fork 属具 |  | 双叉； | 双叉； |  |
|  | Sensor传感器 |  | 感知：<br>普通堆叠 - 单M感知激光 | 感知：<br>普通堆叠 - 单M感知激光 |  |
| Workflow Description 业务类型 | Depalletizing 拆垛 | / | 1. 支持层数和高度已知的拆垛 | 1. 支持层数和高度已知的拆垛 |  |
|  | Stacking 堆垛 | / | 支持普通伺服堆叠，不支持闭环 | 支持普通伺服堆叠，不支持闭环 |  |
| Stacking Requirement堆叠要求 | Maximum Cargo Placement Accuracy 堆叠容差 |  | 堆叠容差≥±20mm（举升<=3m）<br>堆叠容差≥±30mm（举升<=4.5m）<br>堆叠容差≥±40mm（举升<=6m） | 堆叠容差≥±20mm（举升<=3m）<br>堆叠容差≥±30mm（举升<=4.5m）<br>堆叠容差≥±40mm（举升<=6m） |  |
|  | Safety Distance Between the Highest Surface of the Goods and the Underside of the Beam抬升后离天花板高度预留值 |  | 无俯仰堆叠：300mm | 无俯仰堆叠：300mm |  |
|  | Maximum Stacking Height 支持堆叠最大高度 |  | 举升<=6m | 举升<=6m |  |
|  | Lateral spacing 库位左右间距<br>L3：车比货宽时，车与旁边货物间距<br>L4：货比车宽时，货与旁边货物间距 |  | L车：<br>L3=L4=200mm<br><br>R车：<br>L3=L4=300mm | L车：<br>L3=L4=200mm<br><br>R车：<br>L3=L4=300mm |  |
|  | Front-to-back spacing 库位前后间距<br>D1: Minimum front/back safety distance of goods |  | 100mm | 100mm |  |
|  | Maximum Cargo Deviation 自主纠偏能力 |  | 下方料笼左右偏移100mm/5°能保证堆叠成功 | 下方料笼左右偏移100mm/5°能保证堆叠成功 |  |
| 检测特征指标 | 料笼特征 |  | 同取货料笼特征 | 同取货料笼特征 |  |
|  | Cage Deformation料笼变形 |  | ≤±5mm | ≤±5mm |  |
| 效率 | 取货效率（从到达检测高度开始，到抬起货叉结束） |  | 31s | 31s |  |
|  | 放货效率（从开始检测底部料笼开始，到完全出叉结束） |  | 35s | 35s |  |
| 成功率 | 解跺 |  | 0.99 | 0.99 |  |
|  | 堆叠（容差≥±20mm） |  | 0.97 | 0.97 |  |

## Worksheet: 站台、输送线、旋转台、翻转台取放货-P&E

- Extracted range size: 22 rows x 6 columns

| A | B | C | D | E | F |
| --- | --- | --- | --- | --- | --- |
| 站台、输送线、旋转台、翻转台放货-P&E |  |  |  |  |  |
| 类别 | 能力描述 | 图示 | 160版本能力 | 251230版本能力 | 风险提示 |
| Vehicle Body原车&属具 | Vehicle Model车型 | 81 | E&P | E&P |  |
|  | Fork 属具 | / | 双叉 | 双叉 |  |
|  | Sensor传感器 |  | 感知：单M感知激光 | 感知：<br>闭环放货 - 双M感知激光 |  |
| Workflow Description 业务类型 | 取货 | / | 支持高度已知的取货 | 支持高度已知的取货 |  |
|  | 放货 | / | 支持普通放货，不支持放货闭环 | 放货闭环：<br>1. 支持不完全入叉；<br>2. 支持无横移闭环 |  |
| 放货要求 | 放货容差 |  | ≥±15mm | 普通放货：≥±15mm<br>放货闭环：≥±8mm |  |
|  | 货物与左右挡板距离 |  | ≥±300mm | 普通放货：≥±300mm<br>放货闭环：≥±200mm |  |
|  | Maximum Cargo Deviation 自主纠偏能力 |  | 下方料笼左右偏移100mm/5°能保证放货成功 | 下方料笼左右偏移100mm/5°能保证放货成功 |  |
| 检测特征指标 | 载具类型 |  | 托盘、料笼 | 普通放货：托盘、料笼<br>放货闭环：料笼 |  |
|  | Cage Outer Dimension W 载具宽度 |  | ≤3800mm | 普通放货：≤3800mm<br>放货闭环：<br>P车最大可做料笼宽度1900mm内的料笼（受限于传感视野）<br>E车最大可做料笼宽度3800mm内的料笼 |  |
|  | Cage Bottom Requirement底面要求 | 81 | 没有要求 | 容差 ≥ ±15mm，没有要求；<br>容差＜±15mm：<br>1. 下表面有支撑梁结构，梁深大于4cm<br>2. 不可以为纯平面结构 |  |
|  | 平台种类 |  | 站台、输送线、旋转台、翻转台 | 站台、输送线、旋转台、翻转台 |  |
|  | 平台识别特征 | 81 | 1. 放货容差 ≥ ±20mm，无要求<br>2. 放货容差 ≥ ±15~20mm：<br>2.1 平台有类墩特征，最小墩宽50mm，最小墩高65mm，墩间距≥100mm<br>2.2 若没有类墩特征，需要贴反光板：两张反光板（国四）对称张贴，尺寸最小为10*10cm；两张反光板高度齐平，且反光板间距≥5cm | 1. 放货容差 ≥ ±20mm，无要求<br>2. 放货容差 ≥ ±15~20mm：<br>2.1 平台有类墩特征，最小墩宽50mm，最小墩高65mm，墩间距≥100mm<br>2.2 若没有类墩特征，需要贴反光板：两张反光板（国四）对称张贴，尺寸最小为10*10cm；两张反光板高度齐平，且反光板间距≥5cm<br>3. 放货容差 ≥ ±8mm：<br>3.1 平台后侧挡板宽度≥25cm，用于粘贴反光板。两张反光板（国四）对称张贴，尺寸为10*15cm；两张反光板高度齐平，且反光板两侧无紧靠物体，反光板间距≥5cm<br>或者<br>3.2 站台四角有4个L型（俯视）的平整立柱面，且墩高≥70mm，墩宽≥50mm；平台宽度≤3800mm |  |
|  | 载具变形 |  | ≤±5mm | ≤±5mm |  |
| 效率 | 取货效率（从到达检测高度开始，到抬起货叉结束） |  | 31s | 31s |  |
|  | 放货效率（从开始检测平台开始，到完全出叉结束） |  | 35s | 普通放货：35s<br>放货闭环：52s |  |
| 成功率 | 取货 |  | 0.99 | 0.99 |  |
|  | 放货（容差≥±20mm） |  | 0.97 | 普通放货：97%<br>放货闭环：99% |  |
|  | 放货（1次成功率，±10mm容差） |  | / | 0.95 |  |
|  | 放货（3次成功率，±10mm容差） |  | / | 0.99 |  |

## Worksheet: 站台、输送线、旋转台、翻转台取放货-SL&L&R

- Extracted range size: 18 rows x 6 columns

| A | B | C | D | E | F |
| --- | --- | --- | --- | --- | --- |
| 站台、输送线、旋转台、翻转台放货-SL&L&R |  |  |  |  |  |
| 类别 | 能力描述 | 图示 | 160版本能力 | 251230版本能力 | 风险提示 |
| Vehicle Body原车&属具 | Vehicle Model车型 | 81 | SL、L、R | SL、L、R |  |
|  | Fork 属具 | / | 双叉； | 双叉； |  |
|  | Sensor传感器 |  | 感知：<br>普通放货 - 单M感知激光 | 感知：<br>普通放货 - 单M感知激光 |  |
| Workflow Description 业务类型 | 取货 | / | 支持高度已知的取货 | 支持高度已知的取货 |  |
|  | 放货 | / | 支持普通放货，不支持闭环 | 支持普通放货，不支持闭环 |  |
| Stacking Requirement放货要求 | 放货容差 |  | ≥±15mm | 普通放货：≥±15mm |  |
|  | 货物与左右挡板距离 |  | ≥±300mm | ≥±300mm |  |
|  | Maximum Cargo Deviation 自主纠偏能力 |  | 下方料笼左右偏移100mm/5°能保证放货成功 | 下方料笼左右偏移100mm/5°能保证放货成功 |  |
| 检测特征指标 | 载具类型 |  | 托盘、料笼 | 托盘、料笼 |  |
|  | 平台识别特征 | 81 | 1. 放货容差 ≥ ±20mm，无要求<br>2. 放货容差 ≥ ±15~20mm：<br>2.1 平台有类墩特征，最小墩宽50mm，最小墩高65mm，墩间距≥100mm<br>2.2 若没有类墩特征，需要贴反光板：两张反光板（国四）对称张贴，尺寸最小为10*10cm；两张反光板高度齐平，且反光板间距≥5cm | 1. 放货容差 ≥ ±20mm，无要求<br>2. 放货容差 ≥ ±15~20mm：<br>2.1 平台有类墩特征，最小墩宽50mm，最小墩高65mm，墩间距≥100mm<br>2.2 若没有类墩特征，需要贴反光板：两张反光板（国四）对称张贴，尺寸最小为10*10cm；两张反光板高度齐平，且反光板间距≥5cm |  |
|  | 平台种类 |  | 站台、输送线、旋转台、翻转台 | 站台、输送线、旋转台、翻转台 |  |
|  | Cage Deformation料笼变形 |  | ≤±5mm | ≤±5mm |  |
| 效率 | 取货效率（从到达检测高度开始，到抬起货叉结束） |  | 31s | 31s |  |
|  | 放货效率（从开始检测平台开始，到完全出叉结束） |  | 35s | 35s |  |
| 成功率 | 取货 |  | 0.99 | 0.99 |  |
|  | 放货（容差≥±20mm） |  | 0.97 | 0.97 |  |

## Worksheet: 板货堆叠-SL&L

- Extracted range size: 20 rows x 6 columns

| A | B | C | D | E | F |
| --- | --- | --- | --- | --- | --- |
| 板货堆叠-SL&L |  |  |  |  |  |
| 类别 | 能力描述 | 图示 | 160版本能力 | 251230版本能力 | 风险提示 |
| Vehicle Body原车&属具 | Vehicle Model 车型 |  | SLIM, L, | SLIM, L, |  |
|  | Fork 属具 |  | 双叉 | 双叉 |  |
| Workflow Description业务类型 | Depalletizing解垛 |  | 1. 支持层数未知的解垛（边降边扫）<br>2. 支持货物高度可变的解垛<br>3. 支持指定解垛高度的混合堆叠解垛（边降边扫不支持-1模式） | 1. 支持层数未知的解垛（边降边扫）<br>2. 支持货物高度可变的解垛<br>3. 支持指定解垛高度的混合堆叠解垛（边降边扫不支持-1模式） |  |
|  | Stacking 堆垛 |  | 1. 仅支持层数已知的堆垛<br>2. 支持货物高度变化量≤±300的堆垛<br>3. 不支持混合堆叠堆垛 | 1. 支持层数未知的堆垛<br>2. 不支持混合堆叠堆垛 |  |
| Line Storage Placement Requirement线库库位摆放 | Lateral Spacing 库位左右间距<br>L3：Distance between the outer width of AGV to the nearest goods<br>L4：Minimum left/right safety distance of goods |  | SLIM, L：L3=200mm、L4=200mm | SLIM, L：L3=200mm、L4=200mm |  |
|  | Front-to-back Spacing 库位前后间距<br>D1: Minimum front/back safety distance of goods |  | 100mm | 100mm |  |
|  | Maximum Cargo Deviation 自主纠偏能力 |  | 下方板货偏移100mm/5°能保证堆叠成功 | 下方板货偏移100mm/5°能保证堆叠成功 |  |
| Stacking Requirement堆叠要求 | Maximum  Stacking Height支持堆叠最大高度 |  | ≤3.4m(堆叠时，底部货物的最高高度) | ≤3.4m(堆叠时，底部货物的最高高度) |  |
|  | Column-based storage method堆叠方式 |  | 1堆1、1堆2、2堆2 | 1堆1、1堆2、2堆2 |  |
|  | 高度自适应范围 |  |  |  |  |
| Cargo Dimension Requirement板货尺寸要求 | Load’s Max-height 载具及货物总高：hc |  | ≤2500mm | ≤2500mm |  |
|  | Cargo Outer Dimension 货物尺寸 |  | 单侧超托量≤50mm | 单侧超托量≤50mm |  |
|  | Pallet Outer Dimension 托盘尺寸 |  | 跨入叉面≤2000mm<br><br>沿入叉面≤2000mm | 跨入叉面≤2000mm<br><br>沿入叉面≤2000mm |  |
| Cargo Type货物类型 | Material材质 |  | 1. 仅支持硬箱<br>2. 不支持软包 | 1. 仅支持硬箱<br>2. 不支持软包 |  |
| 效率 | 取货效率（从到达检测高度开始，到抬起货叉结束） |  | 1. 层数未知的解垛（边降边扫）：取决于层数高度，最大时长为预设高度/0.3+20s<br>2. 指定解垛高度的混合堆叠解垛：20s | 1. 层数未知的解垛（边降边扫）：取决于层数高度，最大时长为预设高度/0.3+20s<br>2. 指定解垛高度的混合堆叠解垛：20s |  |
|  | 放货效率（从开始检测底部托盘开始，到放下货物结束） |  | 1. 层数已知的堆垛：30s<br>2. 货物高度变化量≤±300的堆垛：45s | 1. 层数未知的堆垛：取决于层数高度：最大时长为预设高度/0.3+30s |  |
| 成功率 | 取货 |  | 0.99 | 0.99 |  |
|  | 放货 |  | 0.97 | 0.97 |  |

## Worksheet: 板货堆叠-P&R&E

- Extracted range size: 21 rows x 6 columns

| A | B | C | D | E | F |
| --- | --- | --- | --- | --- | --- |
| 板货堆叠-P&R&E |  |  |  |  |  |
| 类别 | 能力描述 | 图示 | 160版本能力 | 251230版本能力 | 风险提示 |
| Vehicle Body原车&属具 | Vehicle Model 车型 |  | P, R and E | P, R and E |  |
|  | Fork 属具 |  | 双叉，横移：±100mm、±200mm | 双叉，横移：±100mm、±200mm |  |
| Workflow Description业务类型 | Depalletizing解垛 |  | 1. 支持层数未知的解垛（边降边扫）<br>2. 支持货物高度可变的解垛<br>3. 支持指定解垛高度的混合堆叠解垛（边降边扫不支持-1模式） | 1. 支持层数未知的解垛（边降边扫）<br>2. 支持货物高度可变的解垛<br>3. 支持指定解垛高度的混合堆叠解垛（边降边扫不支持-1模式） |  |
|  | Stacking 堆垛 |  | 1. 仅支持层数已知的堆垛<br>2. 支持货物高度变化量≤±300的堆垛<br>3. 不支持混合堆叠堆垛 | 1. 支持层数未知的堆垛<br>2. 不支持混合堆叠堆垛 |  |
|  | 载具/货物类型 |  | 托盘、缠膜托盘<br>板货 |  |  |
| Line Storage Placement Requirement线库库位摆放 | Lateral Spacing 库位左右间距<br>L3：Distance between the outer width of AGV to the nearest goods<br>L4：Minimum left/right safety distance of goods |  | P, MR, R and E：L3=300mm、L4=300mm | P, MR, R and E：L3=300mm、L4=300mm |  |
|  | Front-to-back Spacing 库位前后间距<br>D1: Minimum front/back safety distance of goods |  | 100mm | 100mm |  |
|  | Maximum Cargo Deviation 自主纠偏能力 |  | 下方板货偏移100mm/5°能保证堆叠成功 | 下方板货偏移100mm/5°能保证堆叠成功 |  |
| Stacking Requirement堆叠要求 | Maximum  Stacking Height支持堆叠最大高度 |  | ≤3.4m(堆叠时，底部货物的最高高度) | ≤3.4m(堆叠时，底部货物的最高高度) |  |
|  | Column-based storage method堆叠方式 |  | 1堆1、1堆2、2堆2 | 1堆1、1堆2、2堆2 |  |
|  | 高度自适应能力 |  |  |  |  |
| Cargo Dimension Requirement板货尺寸要求 | Load’s Max-height 载具及货物总高：hc |  | ≤2500mm | ≤2500mm |  |
|  | Cargo Outer Dimension 货物尺寸 |  | 单侧超托量≤50mm | 单侧超托量≤50mm |  |
|  | Pallet Outer Dimension 托盘尺寸 |  | 跨入叉面≤2000mm<br><br>沿入叉面≤2000mm | 跨入叉面≤2000mm<br><br>沿入叉面≤2000mm |  |
| Cargo Type货物类型 | Material材质 |  | 1. 仅支持硬箱<br>2. 不支持软包 | 1. 仅支持硬箱<br>2. 不支持软包 |  |
| 效率 | 取货效率（从到达检测高度开始，到抬起货叉结束） |  | 1. 层数未知的解垛（边降边扫）：取决于层数高度，最大时长为预设高度/0.3+20s<br>2. 指定解垛高度的混合堆叠解垛：20s | 1. 层数未知的解垛（边降边扫）：取决于层数高度，最大时长为预设高度/0.3+20s<br>2. 指定解垛高度的混合堆叠解垛：20s |  |
|  | 放货效率（从开始检测底部托盘开始，到放下货物结束） |  | 1. 层数已知的堆垛：30s<br>2. 货物高度变化量≤±300的堆垛：45s | 1. 层数未知的堆垛：取决于层数高度：最大时长为预设高度/0.3+30s<br> |  |
| 成功率 | 取货 |  | 0.99 | 0.99 |  |
|  | 放货 |  | 0.97 | 0.97 |  |

## Worksheet: 货柜车-双叉E

- Extracted range size: 27 rows x 8 columns

| A | B | C | D | E | F | G | H |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 货柜车 - 双叉E |  |  |  |  |  |  |  |
| 类别 | 能力描述 | 图示 | 160版本能力 |  | 251230版本能力 |  | 风险提示 |
|  |  |  | 装车要求 | 卸车要求 | 装车要求 | 卸车要求 |  |
| Vehicle Body 原车&属具 | Vehicle Model车型 | 81 | E20、E30/35、E40 |  | E20、E30/35、E40 |  |  |
|  | Fork属具 | 81 | 双叉 |  | 双叉 |  |  |
|  | Pitch Range俯仰范围 |  | ±6° |  | ±6° |  |  |
|  | Offset Range侧移范围 |  | ±200mm |  | ±200mm |  |  |
|  | Sensor传感器 |  | 感知：单M感知激光 | 感知：单M感知激光 | 感知：单M感知激光 | 感知：单M感知激光 |  |
| Environment环境 | Protection against Rain月台区域覆盖雨棚 |  | 必须 |  | 必须 |  |  |
| Trailer Slope车厢坡度 | Angle deviation 内部角度偏差（β）俯仰角 |  | 小于1° |  | 小于1° |  |  |
|  | Floor slope 地板倾斜角度（γ）翻滚角 |  | 小于1° |  | 小于1° |  |  |
| Trailer Tailgate车厢尾门 | Tailgate Dimension尾门尺寸 |  | a≥AGV载货后的最大宽度*2+200mm；<br>h≥AGV货叉抬升300mm后门架的高度/+50mm |  | a≥AGV载货后的最大宽度*2+200mm；<br>h≥AGV货叉抬升300mm后门架的高度/+50mm |  |  |
| 车厢尺寸 | 长度 |  | 12000~16000 | 12000~16000 | 12000~16000 | 12000~16000 |  |
| Cargo Placement Requirement  inside Trailer车厢内货物摆放要求 | Front-to-back spacing 车箱内货物的前后距离（考虑超板） |  | d1≥30mm<br>d2≥30mm/理论上可以做到0mm<br>d3≥400 | d1≥0mm，无要求<br>d2≥0mm，无要求<br>d3≥50mm（能取到最后一排货） | d1≥30mm<br>d2≥30mm/理论上可以做到0mm<br>d3≥400 | d1≥0mm，无要求<br>d2≥0mm，无要求<br>d3≥50mm（能取到最后一排货） |  |
|  | Safety Distance Between the Highest Surface of the Goods and the Underside of the Trailer车厢内高度容差 |  | 1、AGV在车厢内举升0.3m后门架比车高，车厢内高度=AGV举升0.3m后的门架高度+H（0.15m）；<br>2、AGV在车厢内举升0.3m后货比门架高，车厢内高度=AGV举升0.3m后的货物高度+H（0.15m） |  | 1、AGV在车厢内举升0.3m后门架比车高，车厢内高度=AGV举升0.3m后的门架高度+H（0.15m）；<br>2、AGV在车厢内举升0.3m后货比门架高，车厢内高度=AGV举升0.3m后的货物高度+H（0.15m） |  |  |
|  | Lateral Spacing车箱内货物的左右距离（考虑超板） | 81 | 2*a1+a2≥100mm | 2*a1+a2≥100mm | 2*a1+a2≥100mm | 2*a1+a2≥100mm |  |
|  | Placement Method 车厢内货物摆放方式 |  | 同为长边/短边，一个车厢内同种规格货物 |  | 同为长边/短边，一个车厢内同种规格货物 |  |  |
| Boarding Bridge登车桥 | Maximum Angle Deviation Between Trailer and Boarding Bridge车厢与登车桥角度偏差 |  | β＜1°，理论上可以要求停正 |  | β＜1°，理论上可以要求停正 |  |  |
|  | Maximum Distance Between Trailer and Boarding Bridge(Central axis)车厢与登车桥中轴线的距离偏差 | 81 | ＜±10cm，另外需保证车厢不被门框遮挡 |  | ＜±10cm，另外需保证车厢不被门框遮挡 |  |  |
|  | Length长度 | 81 | 常见长度在1.5米~2米，长度会影响坡度，没有要求 |  | 常见长度在1.5米~2米，长度会影响坡度，没有要求 |  |  |
|  | Width宽度 |  | 至少要大于定向轮/车身宽度+0.2m | 应满足以下工况的最小物理宽度：<br>当货物紧贴车厢侧壁存放时，AGV通过最大横移补偿后对准货物，此时车体最外侧轮缘距离登车桥边缘应保持 100mm 的安全距离 | 至少要大于定向轮/车身宽度+0.2m | 应满足以下工况的最小物理宽度：<br>当货物紧贴车厢侧壁存放时，AGV通过最大横移补偿后对准货物，此时车体最外侧轮缘距离登车桥边缘应保持 100mm 的安全距离 |  |
|  | Slope坡度 |  | ≤3°，否则最后一排货物无法放货； |  | ≤3°，否则最后一排货物无法放货； |  |  |
| Bright Eye System明眸 | Fixed Bright Eye System固定式明眸 |  | 不需要（长度固定） | 不需要（长度固定） | 不需要（长度固定） | 不需要（长度固定） |  |
| Operation efficiency装卸效率 | 18 Pallet Operation Time18托盘装卸车耗时 |  | 52分钟 |  | 52分钟 |  |  |
|  | Single Operation Time单次装卸完成时间 |  | 约2分40s |  | 约2分40s |  | 老车：货叉不在0.4m附近时，速度小于0.6<br>新车：货叉不在0.2~0.4范围内时，速度小于0.6 |
| Goods type货物类型 | 板货、卡板箱、料笼 |  | 板货 |  | 板货 |  |  |
| 成功率 |  |  | 一车厢三次人工干预 | 一车厢三次人工干预 | 一车厢一次人工干预 | 一车厢一次人工干预 |  |

## Worksheet: 货柜车-四叉E

- Extracted range size: 27 rows x 8 columns

| A | B | C | D | E | F | G | H |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 货柜车 - 四叉E |  |  |  |  |  |  |  |
| 类别 | 能力描述 | 图示 | 160版本能力 |  | 251230版本能力 |  | 风险提示 |
|  |  |  | 装车要求 | 卸车要求 | 装车要求 | 卸车要求 |  |
| Vehicle Body 原车&属具 | Vehicle Model车型 | 81 | E20、E30/35、E40 | —— | E20、E30/35、E40 | —— |  |
|  | Fork属具 | 81 | 定制、固定式的四叉 | —— | 定制、固定式的四叉 | —— |  |
|  | Pitch Range俯仰范围 |  | ±6° | —— | ±6° | —— |  |
|  | Offset Range侧移范围 |  | ±200mm | —— | ±200mm | —— |  |
|  | Sensor传感器 |  | 感知：单M感知激光 | —— | 感知：单M感知激光 | —— |  |
| Environment环境 | Protection against Rain月台区域覆盖雨棚 |  | 必须 | —— | 必须 | —— |  |
| Trailer Slope车厢坡度 | Angle deviation 内部角度偏差（β） |  | 小于1° | —— | 小于1° | —— |  |
|  | Floor slope 地板倾斜角度（γ） |  | 小于1° | —— | 小于1° | —— |  |
| 车厢尺寸 | 长度 |  | 12000~16000 | —— | 12000~16000 | —— |  |
| Trailer Tailgate车厢尾门 | Tailgate Dimension尾门尺寸 |  | a≥AGV载货后的最大宽度+200mm；<br>h≥AGV货叉抬升300mm后门架的高度+50mm | —— | a≥AGV载货后的最大宽度+200mm；<br>h≥AGV货叉抬升300mm后门架的高度+50mm | —— |  |
| Cargo Placement Requirement  inside Trailer车厢内货物摆放要求 | Front-to-back spacing 车箱内货物的前后距离（考虑超板） |  | d1≥30mm<br>d2≥30mm/理论上可以做到0mm<br>d3≥400mm（规避门框和最后一排货能够放下，待测试） | —— | d1≥30mm<br>d2≥30mm/理论上可以做到0mm<br>d3≥400mm（规避门框和最后一排货能够放下，待测试） | —— |  |
|  | Safety Distance Between the Highest Surface of the Goods and the Underside of the Trailer车厢内高度容差 |  | 1、AGV在车厢内举升0.3m后门架比车高，车厢内高度=AGV举升0.3m后的门架高度+H（0.15m）；<br>2、AGV在车厢内举升0.3m后货比门架高，车厢内高度=AGV举升0.3m后的货物高度+H（0.15m） | —— | 1、AGV在车厢内举升0.3m后门架比车高，车厢内高度=AGV举升0.3m后的门架高度+H（0.15m）；<br>2、AGV在车厢内举升0.3m后货比门架高，车厢内高度=AGV举升0.3m后的货物高度+H（0.15m） | —— |  |
|  | Lateral Spacing车箱内货物的左右距离（考虑超板） | 81 | a1＞50mm；<br>a2可以为0或者取货时的固定间距 | —— | a1＞50mm；<br>a2可以为0或者取货时的固定间距 | —— |  |
|  | Placement Method 车厢内货物摆放方式 |  | 同为长边/短边，一个车厢内同种规格货物 | —— | 同为长边/短边，一个车厢内同种规格货物 | —— |  |
| Boarding Bridge登车桥 | Maximum Angle Deviation Between Trailer and Boarding Bridge车厢与登车桥角度偏差 |  | β＜1°，理论上可以要求停正 | —— | β＜1°，理论上可以要求停正 | —— |  |
|  | Maximum Distance Between Trailer and Boarding Bridge(Central axis)车厢与登车桥中轴线的距离偏差 | 81 | ＜±10cm，另外需保证车厢不被门框遮挡 | —— | ＜±10cm，另外需保证车厢不被门框遮挡 | —— |  |
|  | Length长度 | 81 | 常见长度在1.5米~2米，长度会影响坡度，没有要求 | —— | 常见长度在1.5米~2米，长度会影响坡度，没有要求 | —— |  |
|  | Width宽度 |  | ≥1.8m~2.2m，至少要大于车身宽度+0.4m | —— | ≥1.8m~2.2m，至少要大于车身宽度+0.4m | —— |  |
|  | Slope坡度 |  | ≤5°，否则最后一排货物无法放货； | —— | ≤5°，否则最后一排货物无法放货； | —— |  |
| Bright Eye System明眸 | Fixed Bright Eye System固定式明眸 |  | 不需要（长度固定） | —— | 不需要（长度固定） | —— |  |
| Operation efficiency装卸效率 | 18 Pallet Operation Time18托盘装卸车耗时 |  | 50分钟 | —— | 50分钟 | —— |  |
|  | Single Operation Time单次装卸完成时间 |  | 约3分钟 | —— | 约3分钟 | —— | 老车：货叉不在0.4m附近时，速度小于0.6<br>新车：货叉不在0.2~0.4范围内时，速度小于0.6 |
| Goods type货物类型 | 板货、卡板箱、料笼 |  | 板货 | —— | 板货 | —— |  |
| 成功率 |  |  | 一车厢2次人工干预 | —— | 一车厢一次人工干预 | —— |  |

## Worksheet: 货柜车-ST

- Extracted range size: 27 rows x 8 columns

| A | B | C | D | E | F | G | H |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 货柜车 - ST |  |  |  |  |  |  |  |
| 类别 | 能力描述 | 图示 | 160版本能力 |  | 251230版本能力 |  | 风险提示 |
|  |  |  | 装车要求 | 卸车要求 | 装车要求 | 卸车要求 |  |
| Vehicle Body 原车&属具 | Vehicle Model车型 |  | ST20-66 | —— | ST20-66 | ST20-66 |  |
|  | Fork属具 |  | 双叉 | —— | 双叉 | 双叉 |  |
|  | Pitch Range俯仰范围 |  | —— | —— | —— | —— |  |
|  | Offset Range侧移范围 |  | —— | —— | —— | —— |  |
|  | Sensor传感器 |  | 感知：单M感知激光 | —— | 感知：单M感知激光 | 感知：单M感知激光 |  |
| Environment环境 | Protection against Rain月台区域覆盖雨棚 |  | 必须 | —— | 必须 |  |  |
| Trailer Slope车厢坡度 | Angle deviation 内部角度偏差（β） |  | 小于1° | —— | 小于1° |  |  |
|  | Floor slope 地板倾斜角度（γ） |  | 小于1° | —— | 小于1° |  |  |
| Trailer Tailgate车厢尾门 | Tailgate Dimension尾门尺寸 |  | a≥AGV载货后的最大宽度+200mm； | —— | a≥AGV载货后的最大宽度+200mm； |  |  |
| 车厢尺寸 | 长度 |  | 12000~16000 | —— | 12000~16000 | —— |  |
| Cargo Placement Requirement  inside Trailer车厢内货物摆放要求 | Front-to-back spacing 车箱内货物的前后距离（考虑超板） |  | d1≥30mm<br>d2≥30mm/理论上可以做到0mm<br>d3≥300mm（规避门框和最后一排货能够放下） | —— | d1≥30mm<br>d2≥30mm/理论上可以做到0mm<br>d3≥300（规避门框和最后一排货能够放下） | d1≥0mm，无要求<br>d2≥0mm，无要求<br>d3≥50mm（能取到最后一排货） |  |
|  | Safety Distance Between the Highest Surface of the Goods and the Underside of the Trailer车厢内高度容差 |  | —— | —— | —— |  |  |
|  | Lateral Spacing车箱内货物的左右距离（考虑超板） | 81 | 2*a1+a2≥100mm | —— | 2*a1+a2≥100mm |  |  |
|  | Placement Method 车厢内货物摆放方式 |  | 同为长边/短边，一个车厢内同种规格货物 | —— | 同为长边/短边，一个车厢内同种规格货物 |  |  |
| Boarding Bridge登车桥 | Maximum Angle Deviation Between Trailer and Boarding Bridge车厢与登车桥角度偏差 |  | β＜1°，理论上可以要求停正 | —— | β＜1°，理论上可以要求停正 | β＜1°，理论上可以要求停正 |  |
|  | Maximum Distance Between Trailer and Boarding Bridge(Central axis)车厢与登车桥中轴线的距离偏差 | 81 | ＜±5cm，另外需保证车厢不被门框遮挡 | —— | ＜±10cm，另外需保证车厢不被门框遮挡 |  |  |
|  | Length长度 | 81 | 常见长度在1.5米~2米，长度会影响坡度，没有要求 | —— | 常见长度在1.5米~2米，长度会影响坡度，没有要求 |  |  |
|  | Width宽度 |  | ≥1800mm | —— | ≥1800mm | ≥1800mm |  |
|  | Slope坡度 |  | ≤3° | —— | ≤3° | ≤3° |  |
| Bright Eye System明眸 | Fixed Bright Eye System固定式明眸 |  | 不需要 | —— | 不需要 | 不需要 |  |
| Operation efficiency装卸效率 | 28 Pallet Operation Time28托盘（后两排单拖）装卸车耗时 |  | 84min | —— | 84min | 70min |  |
|  | Single Operation Time单次装卸完成时间 |  | 约3min | —— | 约3min | 约2min30s |  |
| Goods type货物类型 | 板货、卡板箱、料笼 |  | 板货 | —— | 板货 | 板货 |  |
| 成功率 |  |  | 28拖（后两排单拖）92% | —— | 28拖（后两排单拖）95% | 28拖（后两排单拖）92% |  |

## Worksheet: 高位货架-R

- Extracted range size: 21 rows x 6 columns

| A | B | C | D | E | F |
| --- | --- | --- | --- | --- | --- |
|  | 高位货架（横梁式）- R |  |  |  |  |
| 类别 | 能力描述 | 图示 | 160版本能力 | 251230版本能力 | 风险提示 |
| Vehicle Body 车体 | Vehicle Model车型 |  | VNR14/16/20/25系列 | VNR14/16/20/25系列 |  |
|  | Fork属具 |  | 双叉 | 双叉 |  |
|  | Offset Range侧移范围 |  | ±80mm | ±80mm、±120mm |  |
|  | Sensor感知传感器架构 |  | 单mid360，上仰20° | 感知：3M感知激光（门架两侧+货叉根部）- 只支持1&2拖货物 |  |
| Rack 货架 | Rack Form立柱形态 |  | 立柱为平面结构&带孔平面结构，孔面积占比小于50% | 立柱为平面结构&带孔平面结构，孔面积占比小于50% |  |
|  | Minimum Column Height立柱高度 |  | 有效立柱高度（不被防撞块遮挡）≥100mm | 有效立柱高度（不被防撞块遮挡）≥100mm |  |
|  | Minimum Column Width立柱宽度 |  | 立柱宽≥70mm | 立柱宽≥70mm |  |
|  | 横梁形态 |  | 前表面为光滑的平面，表面平整度小于1cm ，水平度<±1.5°。 上表面为光滑的平面或防跌网设计，最凸为1cm | 前表面为光滑的平面，表面平整度小于1cm ，长度需80cm以上，厚度需5cm以上，水平度<±1.5°。 上表面为光滑的平面或防跌网设计，最凸为1cm |  |
|  | Minimum Beam Height横梁高度 |  | ≥40mm | ≥40mm |  |
|  | 横梁的长度 |  | ≥80cm | ≥80cm |  |
|  | Maximum Rack Height货架高度 |  | ≤9m（放货出叉高度） | ≤9m（放货出叉高度） |  |
| Pallet Dimension Requirement载具要求 | Cargo Outer Dimension货物尺寸 |  | 两侧超托量：≤50mm<br>前侧超托量：≤60mm<br>货物高度：1300mm | 货物宽度(含托盘）：1200mm<br>货物高度：1800mm |  |
|  | 货物侧表面 |  | 无要求 | 侧表面平整<br>货物上下最大左右倾斜值 < 2cm |  |
| Cargo Placement Deviation货物摆放容差 | Minimum Safety Distance Between Goods货物左右净空值 | 81 | 举升高度=<3米，左右净空>=210mm（带横移180mm）<br>举升高度=<5米，左右净空>=280mm（带横移240mm）<br>举升高度=<7米，左右净空>=350mm（带横移300mm）<br>举升高度=<9米，左右净空>=450mm（带横移390mm） | 举升高度=<3米，左右净空>=120mm（均要横移）<br>举升高度=<5米，左右净空>=130mm（均要横移）<br>举升高度=<7米，左右净空>=160mm（均要横移）<br>举升高度=<9米，左右净空>=190mm（均要横移） |  |
|  | Minimum Safety Distance Between Goods and Upper Shelf货物高度净空值 |  | 高度净空>=150mm | 高度净空>=150mm |  |
|  | 货物最高离天花板的距离 |  | 150mm | 150mm |  |
|  | 货物背靠背距离 |  | 200mm | 100mm |  |
| 效率 | 放货效率（从抬升到指定高度开始，到放下货物结束） |  | 90s | 72s |  |
| 成功率 | 放货（举升高度=7米，左右净空=160mm） |  | 0.95 | 0.98 |  |
