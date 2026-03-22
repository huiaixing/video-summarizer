# B 站视频总结器 🎬

输入 B 站视频链接，自动提取字幕并生成结构化学习笔记。

## 功能特点

- ✅ 支持 B 站 CC 字幕和自动生成字幕
- ✅ 使用 LLM 生成结构化笔记（核心要点、详细内容、关键概念）
- ✅ 简洁的 Web 界面
- ✅ 支持复制和下载 Markdown 笔记
- ✅ 本地运行，隐私安全

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 设置 API Key（二选一）

**方式 A：环境变量（推荐）**
```bash
export DASHSCOPE_API_KEY="your-api-key-here"
```

**方式 B：网页输入**
启动后在网页的 API Key 输入框中填写

> 获取 API Key: https://dashscope.console.aliyun.com/

### 3. 启动服务

```bash
cd backend
python app.py
```

### 4. 打开浏览器

访问：http://localhost:5000

## 使用示例

1. 复制 B 站视频链接（如：`https://www.bilibili.com/video/BV1xx411c7mD`）
2. 粘贴到输入框
3. （可选）填写 API Key
4. 点击"开始总结"
5. 等待几秒，获取结构化笔记
6. 复制或下载 Markdown 文件

## 项目结构

```
bilibili-summarizer/
├── backend/
│   ├── app.py                 # Flask 后端服务
│   ├── subtitle_extractor.py  # 字幕提取模块
│   ├── summarizer.py          # 内容总结模块
│   └── requirements.txt       # Python 依赖
├── frontend/
│   └── index.html             # 前端页面
└── README.md
```

## 注意事项

- 仅支持有字幕的视频（CC 字幕或自动生成字幕）
- 硬编码字幕（长在画面上的）暂不支持
- 视频时长建议不超过 2 小时（避免 token 超限）

## 技术栈

- **后端**: Python + Flask
- **前端**: 原生 HTML/CSS/JS
- **字幕提取**: B 站 API
- **内容总结**: 阿里百炼 Qwen 模型

---

Made with 🎭 by 小 D
