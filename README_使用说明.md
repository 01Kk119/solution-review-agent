# 方案评审 Agent：迁移与使用说明

本系统已经按用途拆分为两个同级目录：

```text
方案评审Skill/
├─ 01_Agent程序与知识库/       # 适合放入私有 Git 仓库
└─ 02_项目资料与运行数据/       # 适合放入公司网盘或加密云盘
```

两个目录必须放在同一个父目录下。目录可以整体移动或改父目录位置，不依赖当前 Windows 用户名或桌面路径。

## 第 1 份：程序与知识库

- `review-console/`：本地 Python Web 工作台
- `Agent工作区/skills/`：方案评审及各专业 Agent Skill
- `Agent工作区/scripts/`：抽取、渲染、导出、登记脚本
- `Agent工作区/基础知识库/`：基础知识
- `Agent知识库/agent/03_knowledge/`：工作台使用的专业风险知识库
- `打开方案评审工作台.cmd`：启动入口
- `设置智谱API.cmd`：API Key 配置入口（当前实际配置 DeepSeek）

这个目录不得保存 API Key。建议同步到私有 GitHub 仓库。

## 第 2 份：项目资料与运行数据

- `项目记录/`：客户原始项目资料及项目评估结果
- `工作台数据/`：SQLite、上传文件和工作台生成产物
- `Agent运行数据/projects_input/`：Agent 原始输入
- `Agent运行数据/output/`：Agent 工作输出和 trace
- `Agent运行数据/项目汇总包/`：跨项目索引
- `Obsidian运行数据/`：Obsidian 发布结果和知识反馈记录
- `临时与历史/`：缓存、临时转换和历史导出

其中包含客户资料，不能放入公开 Git 仓库或公开网站。建议使用公司 OneDrive、SharePoint、NAS 或加密云盘。

## 新设备恢复

1. 将两个目录下载到同一个父目录。
2. 安装 Python 3.10 或更高版本，并勾选 `Add Python to PATH`。
3. 在第 1 份目录运行 `新设备初始化.ps1` 安装依赖并检查目录。
4. 双击 `设置智谱API.cmd`，在新设备重新输入 API Key。
5. 双击 `打开方案评审工作台.cmd`。

API Key 只保存在当前 Windows 用户环境变量中，不会随文件迁移。

## 可选路径覆盖

默认采用两个同级目录。确需把数据放到其他磁盘时，可设置：

```powershell
$env:REVIEW_CONSOLE_DATA_PATH = "D:\ReviewData\工作台数据"
$env:REVIEW_PROJECTS_PATH = "D:\ReviewData\项目记录"
$env:REVIEW_AGENT_RUNTIME_PATH = "D:\ReviewData\Agent运行数据"
$env:OBSIDIAN_VAULT_PATH = "D:\ReviewData\Obsidian运行数据"
$env:REVIEW_KNOWLEDGE_BASE_PATH = "D:\ReviewCode\Agent知识库\agent\03_knowledge"
```

不设置时全部使用可移植的相对位置。

## 命令行工作流

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ".\Agent工作区\scripts\Run-ExtractProject.ps1" `
  -InputDir "..\02_项目资料与运行数据\Agent运行数据\projects_input\项目编号" `
  -ProjectKey "项目编号" `
  -ProjectName "项目名称"
```

默认输出到 `../02_项目资料与运行数据/Agent运行数据/output/<ProjectKey>/`。

## 同步规则

- 第 1 份：提交前运行测试，再推送私有 Git。
- 第 2 份：工作台关闭后再同步，避免复制正在写入的 SQLite WAL 文件。
- 不要同时在两台设备上修改同一份 SQLite 数据库。
- 每次换设备前，确认云盘已经完成同步。

