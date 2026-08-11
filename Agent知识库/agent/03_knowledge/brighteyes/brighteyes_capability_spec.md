---
type: spreadsheet-knowledge
source_file: "sources/brighteyes_capability_spec.xlsx"
sheet_count: 1
conversion: "one-time Markdown export"
status: extracted
---

# 明眸能力规格

> [!note] Source fidelity
> This Markdown is a one-time text/table export for Obsidian and Agent retrieval. The original Excel workbook remains authoritative for formatting, formulas, images, merged cells, and future updates.

## Workbook overview

- Source: `sources/brighteyes_capability_spec.xlsx`
- Worksheets: 1
- Worksheet names: `明眸规格书`

## Worksheet: 明眸规格书

- Extracted range size: 16 rows x 6 columns

| A | B | C | D | E | F |
| --- | --- | --- | --- | --- | --- |
| 明眸规格书 |  |  |  |  |  |
| 类别 | 能力描述 | 图示 | 160版本能力 | 主版本能力 | 风险提示 |
| 库位监控 | 监控库位是否有货 | 9 | 无 | 1、垂直视角<br>2、斜视视角<br>3、结果上报RCS延迟，500ms<br>4、单层库位状态识别<br>5、料笼层数识别 |  |
| 安全监控 | 监控运行区域是否有人和车或者是同时有人和车 |  | 单车直连方案：<br>1、明眸到单车总时间：340ms<br>3、AGV停车时间：680ms | RCS中转方案：<br>1、明眸到RCS总时间：340ms<br>2、AGV停车时间：3s |  |
|  |  |  |  | 单车直连方案：<br>1、明眸到单车总时间：340ms<br>3、AGV停车时间：680ms |  |
| 相机信息 | 相机的品牌、分辨率、fov、协议等 | 9 | BOSH NVU-3702-F04<br>1、去畸变后fov: 82° * 50°<br>2、使用分辨率：1280 * 720<br>3、数据协议：rtsp<br>4、供电方式：POE | BOSH NVU-3702-F04<br>1、去畸变后fov: 82° * 50°<br>2、支持分辨率：1920*1080 、1280 * 720<br>3、数据协议：rtsp<br>4、供电方式：POE |  |
| 服务器信息 | cpu、gpu等硬件参数和带载能力 |  | 1、CPU：intel i7 12700<br>2、GPU：Nvidia RTX4070<br>3、内存：DDR4 16*2<br>4、硬盘：SSD 512G<br>5、电源：700W<br>6、带载能力：12台相机做推理 | 1、CPU：intel i7 12700<br>2、GPU：Nvidia RTX5070、Nvidia RTX 4070<br>3、内存：DDR4 16*2<br>4、硬盘：SSD 512G<br>5、电源：700W<br>6、带载能力：12台相机做推理 |  |
| 软件功能 | 支持的软件功能 |  | 1、web 界面<br>2、安全隐私功能(监控画面模糊处理)<br>3、相机断线检测、重连功能<br>4、视频回溯功能<br>5、安全异常一键关闭功能<br>6、进程异常自诊监控功能 | 1、web 界面<br>2、安全隐私功能(监控画面模糊处理)<br>3、相机断线检测、重连功能<br>4、视频回溯功能<br>5、安全异常一键关闭功能<br>6、进程异常自诊监控功能 |  |
| 网络情况 | 系统网络交互延迟、带宽 |  | web界面显示延迟：720p分辨率预览，平均延迟515.6ms | web界面显示延迟：720p分辨率预览，平均延迟515.6ms |  |
|  |  |  | 安全明眸总延迟(直连)：680ms | 安全明眸总延迟(RCS中转)：3s |  |
|  |  |  |  | 安全明眸总延迟(直连)：680ms |  |
|  |  |  | 12路并发请求接口响应延迟： | 多路并发请求接口响应延迟：90ms |  |
|  |  |  | 单客户端浏览12路相机网络带宽：105.5Mbps | 单客户端浏览12路相机网络带宽：105.5Mbps |  |
| 模型检测 | 模型版本、检测能力 |  | 基础模型：yolov5 n<br>检测目标：人、车<br> | 基础模型：yolov12 l<br>检测标签：货物、人、车 |  |
| 系统环境 |  |  | OS: ubuntu 20.04<br>driver: 535<br>cuda: 11.8<br>cudnn: 8.9.0<br>tensorrt: 8.6 | OS: ubuntu 20.04<br>driver: 535<br>cuda: 11.8<br>cudnn: 8.9.0<br>tensorrt: 8.6 |  |
|  |  |  |  | OS: ubuntu 24.04<br>driver: 575 <br>cuda: 12.8<br>cudnn: 9.8.0<br>tensorrt: 10.8 |  |
