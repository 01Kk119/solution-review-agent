# 20260430-5.x 版本说明

# 一、260430主版本 特性概要

**20260430-5.x版本是继251230年度基线版本发布后的首个重大迭代版本**。

在此之前，251230版本完成了核心能力的统一收敛与稳定输出，确立了年度交付的技术基础 。

260430版本在保持基线版本稳定性的基础上，进一步聚焦于 “**复杂场景深水区攻坚**” 与 “**生产运维工具体验升级**”。在业务场景侧，重点突破了E车大料笼堆叠、线库动态搜索以及高难度感知场景（如缠膜、插环、细立柱），显著拓宽了非标场景的适应能力；在工具侧，通过AgvHub数据校验、Robotune交互优化及维保数据维度的扩展，进一步提升了现场部署效率与设备运维的精细度。

**相较于251230版本，20260430-5.x版本主要整合并新增了以下特性：**

*   E车大料笼堆叠能力（含半驶离确认、空间检测及优雅降级策略）
    
*   线库动态搜索取放（支持无库位动态感知搜索）
    
*   复杂视觉感知增强（视觉缠膜检测、料笼插环）
    
*   四叉属具装车适配 
    
*   Robotune 交互体验优化（通讯稳定性优化、任务失败提醒优化）
    
*   维保与工具链升级（支持里程/循环计数、AgvHub导出校验）
    

# 二、版本开发与测试时间

*   版本规划： 2025-12-01 
    
*   设计截止： 2026-01-30 
    
*   开发时间： 2026-01-01 ～ 2026-03-31 
    
*   联调时间： 2026-04-01 ~ 2026-04-30 
    
*   准入时间： 2026-04-30 
    
*   测试时间： 2026-04-30 ～ 2026-06-30 
    
*   **发布时间：** 2026-07-15 
    

# 三、260430主版本 增量说明

**1、规划特性**

| **编号** | **范畴** | **特性** | **细分特性** | **产品经理&技术SE** | **相关职能组** | **参与研发&文档** |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **场景解决方案升级** | E40-07大料笼堆叠 | 半驶离确认 | $\color{#0089FF}{@段鹏飞}$ | 应用、感知 | $\color{#0089FF}{@王琛(Blayton王琛)}$  $\color{#0089FF}{@石永安(TaylorShi石永安)}$ <br>[《VN24168-VNE-实施方案说明(固件&控制)》](https://alidocs.dingtalk.com/i/nodes/Qnp9zOoBVBe6N3PnTEdzX3bpW1DK0g6l?utm_scene=team_space)<br>[《称重+半出叉感知 料笼堆叠确认新方案》](https://alidocs.dingtalk.com/i/nodes/Y1OQX0akWml6pDGwCAEy6Yyy8GlDd3mE?utm_scene=team_space)<br>[《【VN24168】出叉确认感知部署文档——参数配置》](https://alidocs.dingtalk.com/i/nodes/vy20BglGWOMrbn9qCaGLanr2JA7depqY?utm_scene=team_space) |
| 2 |  |  | 堆叠失败优雅降级 | $\color{#0089FF}{@段鹏飞}$ | 应用、RCS | $\color{#0089FF}{@石永安(TaylorShi石永安)}$ <br>[《VN24168-VNE-实施方案说明(固件&控制)》](https://alidocs.dingtalk.com/i/nodes/Qnp9zOoBVBe6N3PnTEdzX3bpW1DK0g6l?utm_scene=team_space) |
|  |  |  | 补充：带智能货叉2.0的料笼堆叠闭环 $\color{#0089FF}{@谭海东}$ | $\color{#0089FF}{@段鹏飞}$ | 应用、感知 | $\color{#0089FF}{@王琛(Blayton王琛)}$  $\color{#0089FF}{@石永安(TaylorShi石永安)}$  $\color{#0089FF}{@吴庭威}$ [《通用料笼堆叠闭环-VN24191/168/178》](https://alidocs.dingtalk.com/i/nodes/QG53mjyd80yrqn7lfpYwE1RKW6zbX04v?doc_type=wiki_doc&utm_medium=main_vertical&utm_scene=team_space&utm_source=search)<br>[《不完全入叉堆叠闭环+不完全入叉到位判断+料笼堆叠确认+空间检测VN24168&VN24178》](https://alidocs.dingtalk.com/i/nodes/XPwkYGxZV3yzE51vfEoR0YBQ8AgozOKL?doc_type=wiki_doc&utm_medium=main_vertical&utm_scene=team_space&utm_source=search) |
| 6 |  | P15-66卡板箱堆拆 | 卡板箱闭环检测 | $\color{#0089FF}{@段鹏飞}$ | 应用、感知 | $\color{#0089FF}{@王琛(Blayton王琛)}$ [《卡板箱堆叠闭环流程和接口设计-JPN24151/VN24205》](https://alidocs.dingtalk.com/i/nodes/YMyQA2dXW7rnd57MFEmX5nE48zlwrZgb?utm_scene=team_space)[《【CAN24030】感知现场部署参考文档》](https://alidocs.dingtalk.com/i/nodes/Gl6Pm2Db8De6XqPRTGYEnb43WxLq0Ee4?utm_scene=team_space)[《伺服卡板箱堆叠标准闭环优化(固件)》](https://alidocs.dingtalk.com/i/nodes/QOG9lyrgJPjBYeDrIngvaavjWzN67Mw4?utm_scene=team_space) |
| 8 |  |  | 卡板箱堆叠策略（横移+前后） | $\color{#0089FF}{@段鹏飞}$ | 应用、感知 | $\color{#0089FF}{@王琛(Blayton王琛)}$  $\color{#0089FF}{@石永安(TaylorShi石永安)}$ <br>[《JPN24151/VN24205卡板箱堆叠闭环-需求说明文档》](https://alidocs.dingtalk.com/i/nodes/vy20BglGWOMrbn9qCEBopzx5JA7depqY?utm_scene=team_space)[《伺服卡板箱堆叠标准闭环优化(固件)》](https://alidocs.dingtalk.com/i/nodes/QOG9lyrgJPjBYeDrIngvaavjWzN67Mw4?utm_scene=team_space)[《卡板箱堆叠闭环流程和接口设计-JPN24151/VN24205》](https://alidocs.dingtalk.com/i/nodes/YMyQA2dXW7rnd57MFEmX5nE48zlwrZgb?utm_scene=team_space) |
| 12 | **车型适配和硬件功能升级** | 标定房1期适配 | 适配P15-66车 | $\color{#0089FF}{@李滨(Levi 李滨)}$ | 感知 | 补文档 |
| 13 |  | 标定 | 叉端雷达标定校验 | $\color{#0089FF}{@李滨(Levi 李滨)}$ | 感知 | $\color{#0089FF}{@吴庭威}$ |
| 14 |  | 多雷达库 | 多雷达库上报激光异常错误码 | $\color{#0089FF}{@陈伟键(Nick陈伟键)}$ | 仿真、应用 | $\color{#0089FF}{@曾令彬}$  $\color{#0089FF}{@陈泽鹏}$ <br>[《【5.x】多雷达库上报激光异常错误码(TPD)》](https://alidocs.dingtalk.com/i/nodes/93NwLYZXWyb93GKNCkDyR5B9VkyEqBQm?utm_scene=team_space) |
| 16 | **取放特性** | P15-66视觉缠膜 | RGBD感知检测 | $\color{#0089FF}{@黄莉莎(lisa黄莉莎)}$ | 感知 | $\color{#0089FF}{@王震辉}$ [《缠膜托盘检测-需求说明书》](https://alidocs.dingtalk.com/api/doc/transit?dentryUuid=ZX6GRezwJly6X9GPfkZnKPyl8dqbropQ&queryString=utm_medium%3Ddingdoc_doc_plugin_card%26utm_source%3Ddingdoc_doc) |
| 17 |  |  | 缠膜托盘自动标注软件 | $\color{#0089FF}{@黄莉莎(lisa黄莉莎)}$ | 感知 | $\color{#0089FF}{@王震辉}$ [《自动标注与数据管理方案及现场对接工作流说明》](https://alidocs.dingtalk.com/api/doc/transit?dentryUuid=Obva6QBXJw64bdGMIRok1b50Vn4qY5Pr&queryString=utm_medium%3Ddingdoc_doc_plugin_card%26utm_source%3Ddingdoc_doc) |
| 18 |  | 插环检测 | 插环检测 | $\color{#0089FF}{@段鹏飞}$ | 感知 | $\color{#0089FF}{@林浈超}$ <br>[《VN25028、VN25099插环检测需求说明书》](https://alidocs.dingtalk.com/i/nodes/Y1OQX0akWml6pDGwCY7qpR1Q8GlDd3mE?utm_scene=team_space)<br>[《【VN25028 & 099】感知部署文档——料笼插孔/插环检测》](https://alidocs.dingtalk.com/i/nodes/20eMKjyp81Opl67KHdXrod5wVxAZB1Gv?utm_scene=team_space) |
| 22 | **导航特性** | 定位优化 | 重定位彩色方案<br>库位与路径、彩色PNG、黑白滤去地面法向量 | $\color{#0089FF}{@吴頔(woody 吴頔)}$ | 定位、工具 | $\color{#0089FF}{@岑庆威}$  $\color{#0089FF}{@王振宇}$  $\color{#0089FF}{@赵岐源}$  $\color{#0089FF}{@SUNGWOO KIM(Sungwoo Kim / 金圣祐)}$ <br>[《260430，重定位彩色升级（5.X），PRD》](https://alidocs.dingtalk.com/i/nodes/YMyQA2dXW7rnd57MFkL3P5OL8zlwrZgb?doc_type=wiki_doc&iframeQuery=utm_source=portal&utm_medium=portal_recent&rnd=0.5709024375357064) |
| 23 |  |  | last pose 数据库优化 | $\color{#0089FF}{@张研宇(Yanyu Zhang / 张研宇)}$ | 定位 | $\color{#0089FF}{@王朋朋}$ <br>[《5.3.1定位lastagvpose模块测试报告》](https://alidocs.dingtalk.com/i/nodes/YMyQA2dXW7rnd57MFk3ob2AX8zlwrZgb?doc_type=wiki_doc&utm_scene=team_space) |
| 24 | **软件特性** | 生产工具体验优化 | 通参工具箱导出前数据校验 | $\color{#0089FF}{@石永安(TaylorShi石永安)}$ | 应用 | $\color{#0089FF}{@刘海}$ <br>[《【5.x】AgvHub工具箱通参Json导出前数据自我校验(TPD)》](https://alidocs.dingtalk.com/i/nodes/qnYMoO1rWxbvYOGjC0Z2eDamJ47Z3je9?utm_scene=team_space) |
| 25 |  | Robotune交互体验优化 | Robotune界面出厂语言为英语 | $\color{#0089FF}{@罗哲瑞(Jerry罗哲瑞)}$ | 工具 | $\color{#0089FF}{@岑庆威}$  $\color{#0089FF}{@赵岐源}$ <br>[《【5.x】Robotune界面出厂语言为英语(TPD)》](https://alidocs.dingtalk.com/i/nodes/ZX6GRezwJly6X9GPfRQ5RqdY8dqbropQ?utm_scene=team_space) |
| 26 |  |  | Robotune通讯连接稳定性优化，避免任务状态异常<br>(WebSocket性能优化) | $\color{#0089FF}{@胡凯}$ | 工具 | $\color{#0089FF}{@岑庆威}$ <br>[《Robotune通讯连接(WebSocket)优化》](https://alidocs.dingtalk.com/i/nodes/vy20BglGWOMrbn9qCYnz44RoJA7depqY?utm_scene=team_space) |
| 27 |  |  | Robotune任务失败提醒优化（弹窗提示任务失败的原因，告诉用户哪个搬运方案配错了） | $\color{#0089FF}{@石永安(TaylorShi石永安)}$ | 应用 | $\color{#0089FF}{@苏得冠(苏德冠)}$ <br>[《【5.x】Robotune任务失败提醒优化(TPD)》](https://alidocs.dingtalk.com/i/nodes/mExel2BLV5yaG5YDfj7GgODBVgk9rpMq?utm_scene=team_space) |
| 28 |  | 维保优化 | 维保任务支持行驶里程和电池循环计数<br>(仅适配DCU板车型，已验证E/P/R，<br>未验证Q/SL/L) | $\color{#0089FF}{@石永安(TaylorShi石永安)}$ | 应用、嵌入式、工具 | $\color{#0089FF}{@赵岐源}$  $\color{#0089FF}{@岑庆威}$  $\color{#0089FF}{@刘海}$ <br>[《AGV维保计划需求V2.1》](https://alidocs.dingtalk.com/i/nodes/AR4GpnMqJzYDyn4ksDdoBRqZVKe0xjE3?utm_scene=team_space) |

**2、增补特性：**

| **编号** | **范畴** | **特性** | **细分特性** | **产品经理&技术SE** | **相关职能组** | **参与研发&文档** |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **导航特性** | 控制优化 | 长路径窗口滚动下发 | $\color{#0089FF}{@郑魁松}$ | 控制 | $\color{#0089FF}{@李文杰}$ [《控制长路径滚动窗口下发功能说明文档》](https://alidocs.dingtalk.com/i/nodes/G1DKw2zgV2y2B574fBQa6k1OWB5r9YAn?doc_type=wiki_doc&iframeQuery=utm_source=portal&utm_medium=portal_main_colum_create&rnd=0.6803670344294568) |
| 2 |  |  | double s 速度规划优化 | $\color{#0089FF}{@郑魁松}$ | 控制 | $\color{#0089FF}{@李文杰}$ [《double S 速度规划说明与测试文档》](https://alidocs.dingtalk.com/i/nodes/QG53mjyd80yrqn7lfbaR1zDBW6zbX04v?doc_type=wiki_doc&iframeQuery=utm_source=portal&utm_medium=Portal_Home_MixFolders&rnd=0.9178023883595083) |
| 6 |  | 定位优化 | ver1算法自适应降采样优化 | $\color{#0089FF}{@张锋(Finn张锋)}$ | 定位 | $\color{#0089FF}{@张锋(Finn张锋)}$ <br>[《自适应降采样延迟体素变化》](https://alidocs.dingtalk.com/i/nodes/MNDoBb60VL967nKPFzvvlokXJlemrZQ3?doc_type=wiki_doc) |
| 8 |  |  | MPE，抠图效果选择易读 | $\color{#0089FF}{@张研宇(Yanyu Zhang / 张研宇)}$ | 定位 | $\color{#0089FF}{@SUNGWOO KIM(Sungwoo Kim / 金圣祐)}$ |
|  |  |  | 分核/优先级/内存三大linux系统优化 | $\color{#0089FF}{@张研宇(Yanyu Zhang / 张研宇)}$ | 定位 | $\color{#0089FF}{@王朋朋}$  $\color{#0089FF}{@蓝贤停}$ |
| 9 |  |  |  |  |  |  |
| 10 |  |  |  |  |  |  |
|  | **取放特性** | 算力库升级 | openvino版本升级适配 | $\color{#0089FF}{@杨思琪(Skylar杨思琪)}$ | 感知 | $\color{#0089FF}{@林浈超}$ <br>[《24VINO-YOLO 通参部署文档》](https://alidocs.dingtalk.com/i/nodes/XPwkYGxZV3yzE51vfgKA0daL8AgozOKL?utm_scene=team_space)[《研发特性自测测试报告\_24VINO\_相关接口测试》](https://alidocs.dingtalk.com/i/nodes/6LeBq413JAeQjbPmTR7X62eOJDOnGvpb?utm_scene=team_space) |
|  |  |  | 智能货叉2.0 半入叉分二级优先级配置功能（任务特性参数下发优先于通过pallectTypeID查询载具库参数设置） | $\color{#0089FF}{@段鹏飞(Kason段鹏飞)}$ | 固件 | $\color{#0089FF}{@杨泽腾}$  $\color{#0089FF}{@陈泽鹏}$ <br>[《智能货叉2.0需求说明文档-第一批功能》](https://alidocs.dingtalk.com/i/nodes/Gl6Pm2Db8De6XqPRTqvXOmYgWxLq0Ee4?doc_type=wiki_doc&utm_medium=dingdoc_doc_splitview&utm_scene=team_space&utm_source=dingdoc_doc)<br>[《智能货叉2.0-半入叉实施方案说明》](https://alidocs.dingtalk.com/i/nodes/QG53mjyd80yrqn7lfgOGkNmAW6zbX04v?doc_type=wiki_doc&utm_medium=dingdoc_doc_splitview&utm_scene=team_space&utm_source=dingdoc_doc) |
|  |  |  |  |  |  |  |
|  | **软件特性** |  | 分核 |  | 软件 | $\color{#0089FF}{@蓝贤停}$ |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |

通参整合：[《260430，5.3.2，通用参数确认》](https://alidocs.dingtalk.com/i/nodes/Obva6QBXJw64bdGMIQ05LkBNVn4qY5Pr?doc_type=wiki_doc&iframeQuery=utm_source=portal&utm_medium=portal_space_create)