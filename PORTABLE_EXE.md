# Windows 便携版

1. 从 GitHub Releases 下载 `SolutionReviewAgent.exe`。
2. 把 EXE 放进一个可写文件夹后双击运行。
3. 首次启动时输入你自己的 DeepSeek API Key。
4. 浏览器会自动打开 `http://127.0.0.1:8765`。

程序会在 EXE 同目录创建 `方案评审数据`，项目资料、SQLite 数据库和评审结果均保存在该目录。API Key 只保存到当前使用者的 Windows 用户环境变量，不会写入 EXE、项目数据库或上传到 GitHub。

该便携版内置 Python 运行时、前端页面和 Agent 知识库，无需另行安装 Python。首次运行未签名 EXE 时，Windows SmartScreen 可能显示提醒；请仅从本仓库的 GitHub Release 下载，并核对 Release 中提供的 SHA-256。
