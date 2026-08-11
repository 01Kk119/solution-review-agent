# 术语表（terminology_glossary）

> 用途：中英文术语统一、会议转写噪声纠偏、输出名词规范化。
> **硬约束：术语表只用于解释与命名规范化，不得据此编造资料中不存在的项目事实。**
> 权威车型知识见 `基础知识库/02_VisionNav_车型产品场景知识库.md`（本表不重复其内容）。

## 车型

| 原词 / 英文 | 规范中文表达 | 说明 |
|---|---|---|
| forklift / fork truck / AGV forklift | 无人叉车 | 泛指 |
| AGV | 无人搬运车（AGV） | 客户文档常用总称 |
| AMR | 自主移动机器人（AMR） | 对应 K 系列顶升车 |
| pallet truck / pallet jack | 搬运车 / 地牛类车型 | 对应 ST 系列 |
| VNA / Very Narrow Aisle | 窄巷道三向车（VNA） | 极窄巷道高位 |
| reach truck | 前移式高位货架车 | 对应 R 系列 |
| tugger / tow tractor / AGT (Automated Guided Tugger) | 牵引车 / 拖挂车 | 对应 Q 系列；AGT 指牵引车+拖挂小车系统 |
| counterbalance forklift | 平衡重叉车 | 对应 P（室内）/ E（室外重载） |
| VNE40-66 等 VNx 型号 | 按原型号保留 | VN+系列字母+数字为公司型号命名；具体数字含义（载重/门架等）以选配单为准，**不要凭型号推断参数** |

## 业务 / 场景

| 原词 | 规范中文表达 |
|---|---|
| workflow | 作业流（workflow） |
| dock / dock loading | 月台 / 月台装卸车 |
| dock leveler | 登车桥 |
| inbound / outbound | 入库 / 出库 |
| picking / placing | 取货 / 放货 |
| staging area | 暂存区 |
| conveyor / conveyor line | 输送线 |
| roller conveyor | 滚筒线 |
| rack / racking | 货架 |
| deep lane storage | 深巷道线库 / 地面深位存储 |
| floor storage | 线库 / 地面堆存 |
| cage | 料笼 |
| pallet | 托盘 |
| carrier | 载具 |
| stack / stacking / destacking | 堆叠 / 拆堆（拆垛） |
| stop sign | 停车标识点（现场交通规则点） |
| aisle | 通道 / 巷道 |
| mixed traffic | 人车混行 / 混行 |
| cycle time / takt | 节拍 |
| pallets per hour (PPH) | 托/小时（效率单位） |
| peak | 峰值 |
| simulation | 仿真 |
| GMA pallet | 北美 GMA 标准托盘（48×40 英寸 ≈ 1219×1016mm） |
| CHEP pallet | CHEP 租赁托盘（北美常见蓝色托盘） |
| stretch wrap / shrink wrap | 缠膜 / 缠绕膜 |

## 系统 / 软件

| 原词 | 规范中文表达 | 说明 |
|---|---|---|
| WMS | 仓储管理系统（WMS） | 客户侧 |
| WCS | 仓储控制系统（WCS） | 客户侧 |
| MES | 制造执行系统（MES） | 客户侧 |
| ERP | 企业资源计划（ERP） | 客户侧 |
| PLC | 可编程控制器（PLC） | 常作信号源（扫码、输送线、门） |
| VFS | 公司调度系统（VFS） | 我方产品 |
| RCS | 机器人中控系统（RCS） | 我方产品；与 VFS 是不同架构，项目用哪套必须确认 |
| IGV 软件版本 | 车端软件大版本（如 IGV 5.0 / 6.0） | 与调度架构（RCS/VFS）存在配套关系，烧录版本必须与中控匹配 |
| HMI | 人机交互界面（HMI） | 车端/现场 |
| 明眸 | 明眸（视觉监控系统） | 我方摄像头监控产品，按原名保留 |
| call button / PAD | 呼叫按钮 / 平板 | 现场交互 |

## 研发 / 项目

| 原词 | 规范中文表达 |
|---|---|
| 非标 | 项目非标开发 / 非标准产品能力 |
| 非标 | 非标准产品能力 |
| 主版本 / Release | 标准版本能力 / 版本发布 |
| TPM | 技术规划 / 技术产品管理 |
| PO | 采购订单（PO） |
| SOW / Scope of Work | 工作范围（SOW） |
| Program Success Criteria | 项目成功标准（客户验收框架文档） |
| Functional Spec | 功能规格书 |
| 选配 / 选配单 / 亮点单 | 车辆选型配置单 | 
| 二期 / phase 2 | 二期项目（承接一期） |

## 会议转写（ASR）噪声纠偏指引

> 中文会议转写常见错别字与英文名词误听。**纠偏只能在有其他资料交叉印证时进行**，
> 纠偏后的词要标注“转写纠偏”，无法印证时保留原词并标记“转写存疑，需确认”。

| 转写中可能出现 | 可能的本词 | 判断依据 |
|---|---|---|
| tager 车 / taker 车 / target 车 / Taskget | tugger 车（牵引车） | 项目上下文是否有牵引车/拖挂系统；书面资料（规格书/选配单）如何拼写 |
| prago / prego / proprogo | 某产品/货物/流程代号 | 以书面资料拼写为准；无书面印证则保留并标注存疑 |
| 二五幺九八 / 二五一九八 | 25198（项目编号口读） | 结合项目编号规则 |
| 菜托盘 | 待确认托盘类型（可能为某品牌/类型托盘的误听） | 必须以书面资料或图片印证，否则标“转写存疑” |
| 拍口托盘 / pico 托盘 | 同上，转写拼写不稳定 | 同上 |
| 货差 / 抚养 / 门价 | 货叉 / （规格话术误听）/ 门架 | 上下文为车辆配置时按叉车部件理解 |
| 明谋 / 明眸 | 明眸（视觉监控） | 我方产品名 |
| 德马赛克 / demaisike | Dematic（德马泰克）等厂商名误听 | 需人工确认，标注存疑 |
| 亮点单 / 量点单 | 选配单相关话术 | 需结合上下文确认 |

**处理规则：**
1. 数字、尺寸、单位在转写中极易出错（英尺/米/厘米混用、163↔125 等）——凡仅出现在转写中的关键数值，标注「会议口头信息」；与书面资料冲突时，两个数值都列出并标记冲突待确认。
2. 说话人身份从转写标注中保留（谁说的很重要：客户/方案/TPM/产品）。
3. 英文名词的最终拼写以书面资料（规格书、Excel、选配单）为准。
