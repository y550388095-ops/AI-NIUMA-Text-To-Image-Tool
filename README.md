[README.md](https://github.com/user-attachments/files/29325608/README.md)
# AI NIUMA - AI牛马图文自动化 🪄

> 政策文件一键转精美长图 | 文档上传 → AI 提炼 → 智能配图 → 高清下载

## ✨ 功能亮点

- 📄 **多格式支持** — 上传 PDF / DOCX 政策文件
- 🧠 **AI 智能提炼** — DeepSeek 大模型自动梳理要点、分板块结构化
- 🎨 **AI 智能配图** — 支持 DALL·E 3 / 通义万相自动生成配图，也支持本地上传
- 📸 **高清长图输出** — Playwright 无头浏览器精准渲染，一键下载 ZIP
- 🎬 **动态 Logo** — 品牌视频 Logo 循环播放
- 🌙 **暗色玻璃质感 UI** — 现代深色主题，磨砂玻璃风格

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| 前端框架 | Streamlit |
| AI 文本提炼 | DeepSeek（兼容 OpenAI SDK） |
| AI 图像生成 | DALL·E 3 / 通义万相 2.7 |
| 截图渲染 | Playwright (Chromium) |
| 文档解析 | pdfplumber + python-docx |

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/y550388095-ops/AI-NIUMA-Text-To-Image-Tool.git
cd AI-NIUMA-Text-To-Image-Tool
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. 启动应用

```bash
streamlit run app.py
```

浏览器打开 `http://localhost:8501` 即可使用。

### 4. 获取 API Key

- **DeepSeek API Key**：前往 [platform.deepseek.com](https://platform.deepseek.com) 注册获取
- **DALL·E 3**：前往 [platform.openai.com](https://platform.openai.com) 获取 OpenAI API Key
- **通义万相**：前往阿里云百炼平台获取

所有 Key 在应用侧边栏输入，不会保存到服务器。

## ☁️ Streamlit Cloud 部署

本项目已适配 Streamlit Community Cloud（免费托管）：

[![Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

1. Fork 本仓库
2. 在 [share.streamlit.io](https://share.streamlit.io) 关联仓库
3. Main file path 填 `app.py`，点击 Deploy

首次部署会自动安装 Playwright Chromium 浏览器（2-3 分钟）。

## 📁 项目结构

```
├── app.py                          # 主应用入口
├── requirements.txt                # Python 依赖
├── packages.txt                    # Linux 系统依赖（Cloud 用）
├── logo.mp4                        # 品牌动态 Logo
├── 图标 logo/                      # Logo 及图标资源
└── policy_to_infographic_mvp.py    # 核心功能模块
```

## 📝 使用流程

1. **上传提炼** — 上传政策文件，AI 自动提取关键信息
2. **内容确认** — 修改文案，选择配图风格，上传本地图片
3. **预览下载** — 一键生成高清长图，支持 ZIP 打包下载

## ⚠️ 注意事项

- API Key 请妥善保管，不要在公开场合泄露
- 本地运行需安装 Playwright 浏览器：`playwright install chromium`
- 大文件上传和 AI 配图可能需要较长时间，请耐心等待

---

Made with ❤️ by AI NIUMA
