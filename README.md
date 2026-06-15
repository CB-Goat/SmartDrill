# 智练通 - 学科复习与强化训练工具

## 项目结构

```
smartdrill.handy.xin/
├── frontend/          # Vue3前端项目
│   ├── src/
│   │   ├── api/       # API接口
│   │   ├── router/    # 路由配置
│   │   ├── stores/    # Pinia状态管理
│   │   ├── views/     # 页面组件
│   │   └── styles/    # 样式文件
│   ├── public/        # 静态资源
│   └── Dockerfile
├── backend/           # Python后端项目
│   ├── app/
│   │   ├── api/       # API路由
│   │   ├── models/    # 数据库模型
│   │   ├── schemas/   # Pydantic模型
│   │   ├── services/  # 业务逻辑
│   │   └── utils/     # 工具函数
│   ├── main.py        # 应用入口
│   └── Dockerfile
├── docker-compose.yml
├── nginx.conf
└── .env.example
```

## 技术栈

### 前端
- Vue 3 + TypeScript
- Vite 构建工具
- Vant 4 UI组件库（移动端优化）
- Pinia 状态管理
- PWA + Service Worker

### 后端
- Python 3.11
- FastAPI 异步框架
- SQLAlchemy ORM
- MySQL 数据库
- python-docx 文档生成

## 本地开发

### 前端
```bash
cd frontend
npm install
npm run dev
```

### 后端
```bash
cd backend
pip install -r requirements.txt
python init_db.py
python main.py
```

## 部署

### Docker部署
```bash
cp .env.example .env
# 编辑.env配置数据库信息
docker-compose up -d
```

### 宝塔面板部署
1. 将nginx.conf内容添加到宝塔网站配置
2. 运行docker-compose up -d
3. 确保数据库已创建

## 功能说明

### 用户功能
- 注册/登录
- 充值积分（1元=100积分）
- 获取复习资料（10积分/单元）
- 获取练习题（1积分/题）
- 下载Word文档

### 管理后台
- 用户管理
- 充值记录
- 订单管理
- 知识点维护
- 题库维护

## 默认管理员账号
- 用户名: admin
- 密码: admin123