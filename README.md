
## 详细说明

### 前端文件夹 (`frontend/`)
- **CSS 样式文件夹 (`css/`)**
  - `style.css`: 全局样式文件，定义整个项目的通用样式。
  - `prediction.css`: 水库流量预测页面的特定样式。
  - `chat.css`: AI 助手聊天界面的样式。

- **JavaScript 文件夹 (`js/`)**
  - `prediction.js`: 水库流量预测页面的交互逻辑。
  - `flowAnalysis.js`: 流量分析相关的 JavaScript 逻辑。
  - `chat.js`: AI 助手聊天界面的交互逻辑。

- **HTML 文件**
  - `index.html`: 项目的首页。
  - `prediction.html`: 水库流量预测页面的 HTML 文件。

### 后端文件夹 (`backend/`)
- **核心功能文件**
  - `tool_register.py`: 工具注册功能，允许模型调用各种工具。
  - `app.py`: 主应用程序文件，处理 API 请求和路由。
  - `models.py`: 数据模型定义，包含数据库模型和数据处理逻辑。
  - `routes.py`: 路由定义，处理不同 API 端点的请求。
  - `utils.py`: 工具函数，包含通用的辅助函数。
  - `config.py`: 配置文件，存储应用程序的配置参数。

- **其他文件**
  - `requirements.txt`: Python 依赖包列表。
  - `reservoir_data.csv`: 训练 LightGBM 模型的数据（共 30 天）。

### 项目说明文件
- `README.md`: 项目的说明文件，包含项目的概述、安装指南、使用说明等。
