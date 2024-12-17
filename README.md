这是大创项目的项目目录结构
project-root/
│
├── frontend/                     # 前端文件夹
│   ├── css/                      # CSS样式文件夹
│   │   ├── style.css             # 全局样式文件
│   │   ├── prediction.css         # 水库流量预测页面特定样式
│   │   └── chat.css              # AI助手聊天界面样式
│   │
│   ├── js/                       # JavaScript文件夹
│   │   ├── prediction.js          # 水库流量预测页面的交互逻辑
│   │   ├── flowAnalysis.js        # 流量分析相关的JavaScript逻辑
│   │   └── chat.js               # AI助手聊天界面的交互逻辑
│   │
│   ├── index.html                # 首页HTML文件
│   └── prediction.html           # 水库流量预测页面HTML文件
│
├── backend/                      # 后端文件夹
│   ├── tool_register.py          # 工具注册功能，允许模型调用各种工具
│   ├── app.py                    # 主应用程序文件，处理API请求和路由
│   ├── models.py                 # 数据模型定义，包含数据库模型和数据处理逻辑
│   ├── routes.py                 # 路由定义，处理不同API端点的请求
│   ├── utils.py                  # 工具函数，包含通用的辅助函数
│   ├── config.py                 # 配置文件，存储应用程序的配置参数
│   ├── requirements.txt          # Python依赖包列表
│   └── reservoir_data.csv        # 训练lightgbm模型的数据（一共是30天）
│
└── README.md                     # 项目说明文件
