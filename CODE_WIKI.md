# 智练通 (SmartDrill) Code Wiki

## 1. 项目概述

智练通是一个面向中小学学科复习与强化训练的工具系统，支持知识点复习资料获取、练习题下载、积分充值等功能。系统采用前后端分离架构，前端使用Vue3 + TypeScript，后端使用Python FastAPI。

---

## 2. 技术栈

### 前端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.4+ | 核心框架 |
| TypeScript | 5.6+ | 类型支持 |
| Vite | 5.0+ | 构建工具 |
| Vant | 4.8+ | 移动端UI组件库 |
| Pinia | 2.1+ | 状态管理 |
| Vue Router | 4.2+ | 路由管理 |
| Axios | 1.6+ | HTTP请求 |
| docx-preview | 0.3+ | Word文档预览 |
| PWA | - | 渐进式Web应用支持 |

### 后端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11 | 运行环境 |
| FastAPI | 0.109+ | Web框架 |
| SQLAlchemy | 2.0+ | ORM |
| Pydantic | 2.5+ | 数据验证 |
| python-jose | 3.3+ | JWT令牌处理 |
| passlib | 1.7+ | 密码加密 |
| python-docx | 1.1+ | Word文档生成 |
| openpyxl | 3.1+ | Excel文件处理 |
| MySQL | - | 数据库 |
| Uvicorn | 0.27+ | ASGI服务器 |

---

## 3. 项目架构

```
smartdrill/
├── backend/                    # Python后端项目
│   ├── app/
│   │   ├── api/               # API路由模块
│   │   ├── models/            # 数据库模型
│   │   ├── schemas/           # Pydantic请求/响应模型
│   │   ├── services/          # 业务逻辑层
│   │   ├── utils/             # 工具函数
│   │   ├── config.py          # 配置管理
│   │   └── database.py        # 数据库连接
│   ├── migrations/            # 数据库迁移脚本
│   ├── main.py               # 应用入口
│   ├── init_db.py            # 数据库初始化
│   ├── requirements.txt      # Python依赖
│   └── Dockerfile
├── frontend/                  # Vue3前端项目
│   ├── src/
│   │   ├── api/              # API接口封装
│   │   ├── router/           # 路由配置
│   │   ├── stores/           # Pinia状态管理
│   │   ├── views/            # 页面组件
│   │   ├── styles/           # 样式文件
│   │   ├── App.vue           # 根组件
│   │   └── main.ts           # 应用入口
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── Dockerfile
├── docker-compose.yml         # Docker编排配置
├── nginx.conf                 # Nginx配置
└── .env.example               # 环境变量示例
```

---

## 4. 后端模块详解

### 4.1 应用入口 (main.py)

**文件路径**: [backend/main.py](file:///workspace/backend/main.py)

FastAPI应用初始化和路由注册中心。

**核心功能**:
- 创建FastAPI应用实例
- 配置CORS中间件
- 注册所有API路由
- 健康检查端点

**路由前缀**: `/api`

**注册的路由模块**:
| 模块 | 路由前缀 | 功能 |
|------|----------|------|
| auth | /api/auth | 用户注册、登录 |
| user | /api/user | 用户信息、充值、订单 |
| subjects | /api/subjects | 学科、年级、学期、单元查询 |
| materials | /api/materials | 复习资料、练习题获取 |
| admin | /api/admin | 管理后台CRUD |
| admin_auth | /api/admin/auth | 管理员登录 |
| knowledge_import | /api/admin | 知识考点导入管理 |
| user_home | /api/user | 用户首页数据 |

---

### 4.2 数据库模型 (models.py)

**文件路径**: [backend/app/models/models.py](file:///workspace/backend/app/models/models.py)

#### 数据模型关系图

```
Version (版本)
    └── Grade (年级)
            └── Subject (科目)
                    └── Semester (学期)
                            └── Unit (单元)
                                    ├── KnowledgePoint (知识点)
                                    └── ExamPoint (考点)
                                            └── Question (题目)
```

#### 模型说明

**User (用户)**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| username | String(50) | 用户名，唯一 |
| password | String(255) | 密码哈希 |
| phone | String(20) | 手机号 |
| points | Integer | 积分余额，默认0 |
| child_grade_id | Integer | 孩子年级ID，外键 |
| child_grade_set_at | DateTime | 孩子年级设置时间 |
| created_at | DateTime | 创建时间 |

**AdminUser (管理员)**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| username | String(50) | 用户名，唯一 |
| password | String(255) | 密码哈希 |
| created_at | DateTime | 创建时间 |

**Recharge (充值记录)**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 用户ID，外键 |
| amount | Integer | 充值金额(元) |
| points | Integer | 充值积分 |
| created_at | DateTime | 创建时间 |

**Order (订单)**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 用户ID，外键 |
| title | String(255) | 订单标题 |
| order_type | String(50) | 订单类型: review/practice/knowledge |
| points | Integer | 消耗积分 |
| file_path | String(255) | 文件路径 |
| created_at | DateTime | 创建时间 |

**Version (版本)**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(100) | 版本名称，如"人教版" |

**Grade (年级)**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| version_id | Integer | 版本ID，外键 |
| name | String(50) | 年级名称 |

**Subject (科目)**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| grade_id | Integer | 年级ID，外键 |
| name | String(100) | 科目名称 |

**Semester (学期)**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| subject_id | Integer | 科目ID，外键 |
| name | String(100) | 学期名称，如"上册"、"下册" |

**Unit (单元)**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| semester_id | Integer | 学期ID，外键 |
| unit_number | Integer | 单元序号 |
| name | String(100) | 单元名称 |

**KnowledgePoint (知识点)**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| unit_id | Integer | 单元ID，外键 |
| title | String(255) | 知识点标题 |
| content | Text | 知识点内容 |
| created_at | DateTime | 创建时间 |

**ExamPoint (考点)**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| unit_id | Integer | 单元ID，外键 |
| title | String(255) | 考点标题 |
| content | Text | 考点内容 |
| exam_types | String(255) | 考试题型 |
| exam_frequency | Enum | 考试频率: 少考/常考/必考 |
| created_at | DateTime | 创建时间 |

**Question (题目)**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| version_id | Integer | 版本ID，外键 |
| grade_id | Integer | 年级ID，外键 |
| subject_id | Integer | 科目ID，外键 |
| semester_id | Integer | 学期ID，外键 |
| unit_id | Integer | 单元ID，外键 |
| knowledge_point_id | Integer | 知识点ID，外键 |
| exam_point_id | Integer | 考点ID，外键 |
| question_type_id | Integer | 题型ID，外键 |
| difficulty_id | Integer | 难度ID，外键 |
| content | Text | 题目内容 |
| options | Text | 选项(如有) |
| answer | Text | 答案 |
| analysis | Text | 解析 |
| question_json | JSON | 题目JSON格式数据 |
| question_type | String(50) | 题型名称 |
| stem | Text | 题干 |
| created_at | DateTime | 创建时间 |

**QuestionType (题型)**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(50) | 题型名称 |

**Difficulty (难度)**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(50) | 难度名称 |

---

### 4.3 Pydantic Schemas (schemas.py)

**文件路径**: [backend/app/schemas/schemas.py](file:///workspace/backend/app/schemas/schemas.py)

#### 请求/响应模型

**UserCreate** - 用户注册请求
```python
username: str      # 用户名
password: str      # 密码
phone: str         # 手机号
```

**UserLogin** - 用户登录请求
```python
username: str      # 用户名
password: str      # 密码
```

**UserResponse** - 用户信息响应
```python
id: int           # 用户ID
username: str     # 用户名
phone: str        # 手机号
points: int       # 积分
```

**Token** - 登录令牌响应
```python
access_token: str  # JWT令牌
token_type: str    # 令牌类型
user: UserResponse # 用户信息
```

**RechargeRequest** - 充值请求
```python
amount: int        # 充值金额(元)
```

**ReviewRequest** - 复习资料请求
```python
subjectId: int     # 科目ID
semesterId: int    # 学期ID
unitId: int        # 单元ID
```

**PracticeRequest** - 练习题请求
```python
subjectId: int      # 科目ID
semesterId: int     # 学期ID
unitId: int         # 单元ID
examType: str       # 考试题型
difficulty: str     # 难度
questionCount: int  # 题目数量
```

**OrderResponse** - 订单响应
```python
id: int            # 订单ID
title: str         # 订单标题
points: int        # 消耗积分
created_at: datetime # 创建时间
```

---

### 4.4 API路由详解

#### 4.4.1 认证模块 (auth.py)

**文件路径**: [backend/app/api/auth.py](file:///workspace/backend/app/api/auth.py)

**路由前缀**: `/api/auth`

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| POST | /register | 用户注册 | UserCreate | `{message: "注册成功"}` |
| POST | /login | 用户登录 | UserLogin | Token |

**积分规则**: 1元 = 100积分

---

#### 4.4.2 用户模块 (user.py)

**文件路径**: [backend/app/api/user.py](file:///workspace/backend/app/api/user.py)

**路由前缀**: `/api/user`

| 方法 | 路径 | 说明 | 认证 | 请求体 | 响应 |
|------|------|------|------|--------|------|
| GET | /info | 获取用户信息 | 必须 | - | UserResponse |
| POST | /recharge | 充值积分 | 必须 | RechargeRequest | `{message, points}` |
| GET | /orders | 获取订单列表 | 必须 | - | OrderResponse[] |
| POST | /update-phone | 修改手机号 | 必须 | `{phone}` | `{message}` |
| POST | /update-password | 修改密码 | 必须 | `{old_password, new_password}` | `{message}` |

---

#### 4.4.3 学科模块 (subjects.py)

**文件路径**: [backend/app/api/subjects.py](file:///workspace/backend/app/api/subjects.py)

**路由前缀**: `/api/subjects`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | /grades | 获取年级列表 | 必须 |
| GET | / | 获取科目列表 | 必须 |
| GET | `/{subject_id}/semesters` | 获取学期列表 | 必须 |
| GET | `/{subject_id}/semesters/{semester_id}/units` | 获取单元列表 | 必须 |

---

#### 4.4.4 资料模块 (materials.py)

**文件路径**: [backend/app/api/materials.py](file:///workspace/backend/app/api/materials.py)

**路由前缀**: `/api/materials`

| 方法 | 路径 | 说明 | 认证 | 积分消耗 |
|------|------|------|------|----------|
| POST | /review | 获取复习资料 | 必须 | 10积分/单元 |
| POST | /practice | 获取练习题 | 必须 | 1积分/题 |
| GET | /orders/{order_id}/download | 下载订单文件 | 必须 | - |

---

#### 4.4.5 管理员认证模块 (admin_auth.py)

**文件路径**: [backend/app/api/admin_auth.py](file:///workspace/backend/app/api/admin_auth.py)

**路由前缀**: `/api/admin/auth`

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| POST | /login | 管理员登录 | `{username, password}` | Token |
| GET | /info | 获取管理员信息 | - | `{id, username}` |

---

#### 4.4.6 管理后台模块 (admin.py)

**文件路径**: [backend/app/api/admin.py](file:///workspace/backend/app/api/admin.py)

**路由前缀**: `/api/admin`

**用户管理**
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /users | 获取用户列表 |
| GET | /recharges | 获取充值记录 |
| GET | /orders | 获取订单列表 |

**版本/年级/科目/学期/单元管理 (CRUD)**
| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | /versions | 版本列表/创建 |
| DELETE | /versions/{id} | 删除版本 |
| GET/POST | /grades | 年级列表/创建 |
| DELETE | /grades/{id} | 删除年级 |
| GET/POST | /subjects | 科目列表/创建 |
| DELETE | /subjects/{id} | 删除科目 |
| GET/POST | /semesters | 学期列表/创建 |
| DELETE | /semesters/{id} | 删除学期 |
| GET/POST | /units | 单元列表/创建 |
| DELETE | /units/{id} | 删除单元 |

**知识考点管理**
| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | /knowledge | 知识点列表/创建 |
| GET/POST | /exam-points | 考点列表/创建 |
| GET | /question-types | 题型列表 |
| GET | /difficulties | 难度列表 |
| GET/POST | /questions | 题目列表/创建 |

---

#### 4.4.7 知识导入模块 (knowledge_import.py)

**文件路径**: [backend/app/api/knowledge_import.py](file:///workspace/backend/app/api/knowledge_import.py)

**路由前缀**: `/api/admin`

| 方法 | 路径 | 说明 | 功能 |
|------|------|------|------|
| GET | /knowledge-exam-points | 获取单元知识点和考点 | - |
| POST | /knowledge-exam-points | 保存知识点和考点 | 支持批量 |
| POST | /import-knowledge-exam-points | Excel导入知识点考点 | 导入数据 |
| POST | /import-knowledge | Excel导入知识点 | 导入数据 |
| POST | /import-exam-points | Excel导入考点 | 导入数据 |
| POST | /import-units | Excel导入单元 | 导入数据 |
| POST | /clear-knowledge | 清除知识点 | 按条件清除 |
| POST | /clear-exam-points | 清除考点 | 按条件清除 |
| POST | /clean-duplicate-exam-points | 清理重复考点 | - |
| DELETE | /unit-knowledge/{unit_id} | 删除单元知识点 | - |
| POST | /clean-exam-content | 清理考点内容格式 | - |
| POST | /import-questions | Excel导入题目 | 导入题库 |
| GET | /query-units | 查询单元 | 按条件查询 |
| GET | /unit-detail/{unit_id} | 获取单元详情 | - |
| GET | /unit-word/{unit_id} | 导出单元Word | 下载文件 |

---

#### 4.4.8 用户首页模块 (user_home.py)

**文件路径**: [backend/app/api/user_home.py](file:///workspace/backend/app/api/user_home.py)

**路由前缀**: `/api/user`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | /home-data | 获取首页数据 | 必须 |
| GET | /unit-word/{unit_id} | 下载单元Word | 必须 |
| POST | /download-unit/{unit_id} | 扣费下载单元 | 必须 |
| POST | /set-child-grade | 设置孩子年级 | 必须 |

---

### 4.5 工具函数 (utils/auth.py)

**文件路径**: [backend/app/utils/auth.py](file:///workspace/backend/app/utils/auth.py)

#### 认证函数

**verify_password(plain_password, hashed_password)**
- 验证密码是否正确
- 参数: plain_password(明文密码), hashed_password(哈希密码)
- 返回: Boolean

**get_password_hash(password)**
- 生成密码哈希
- 参数: password(明文密码)
- 返回: String(哈希密码)

**create_access_token(data: dict)**
- 创建JWT访问令牌
- 参数: data(包含sub和type的字典)
- 返回: String(JWT令牌)
- 默认过期时间: 1440分钟(24小时)

**get_current_user(token, db)**
- 获取当前登录用户
- 参数: token(JWT令牌), db(数据库会话)
- 返回: User对象
- 依赖: OAuth2PasswordBearer

**get_current_admin(token, db)**
- 获取当前登录管理员
- 参数: token(JWT令牌), db(数据库会话)
- 返回: AdminUser对象

---

### 4.6 文档服务 (services/document.py)

**文件路径**: [backend/app/services/document.py](file:///workspace/backend/app/services/document.py)

#### 文档生成函数

**ensure_upload_dir()**
- 确保上传目录存在
- 返回: `/app/uploads`

**generate_review_document(knowledge_points, user_id)**
- 生成复习资料Word文档
- 参数: knowledge_points(知识点列表), user_id(用户ID)
- 返回: 文件保存路径
- 文档包含: 标题、生成时间、知识点内容、考试频率、考试题型

**generate_practice_document(questions, user_id)**
- 生成练习题Word文档
- 参数: questions(题目列表), user_id(用户ID)
- 返回: 文件保存路径
- 文档包含: 题目、题型、难度、参考答案

---

### 4.7 配置管理 (config.py)

**文件路径**: [backend/app/config.py](file:///workspace/backend/app/config.py)

```python
class Settings(BaseSettings):
    app_name: str = "智练通"
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    database_url: str = "mysql+pymysql://root:password@localhost:3306/smartdrill"
    upload_dir: str = "/app/uploads"
```

环境变量配置(.env):
```
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=smartdrill
SECRET_KEY=your-secret-key-change-in-production
```

---

### 4.8 数据库配置 (database.py)

**文件路径**: [backend/app/database.py](file:///workspace/backend/app/database.py)

```python
engine = create_engine(settings.database_url, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- `pool_pre_ping=True`: 连接池连接前ping测试
- `pool_recycle=3600`: 3600秒后回收连接

---

## 5. 前端模块详解

### 5.1 API接口封装 (api/index.ts)

**文件路径**: [frontend/src/api/index.ts](file:///workspace/frontend/src/api/index.ts)

#### request - 用户请求拦截器

- 基础URL: `/api`
- 超时: 10000ms
- 自动携带Token
- 401响应自动登出

#### adminRequest - 管理员请求拦截器

- 基础URL: `/api`
- Token来源: localStorage.admin_token
- 401响应自动跳转登录页

#### 用户API接口
```typescript
api.login(username, password)           // 用户登录
api.register(data)                       // 用户注册
api.getUserInfo()                       // 获取用户信息
api.recharge(amount)                    // 充值
api.getSubjects()                       // 获取科目
api.getSemesters(subjectId)             // 获取学期
api.getUnits(subjectId, semesterId)     // 获取单元
api.getReviewMaterials(data)            // 获取复习资料
api.getPracticeQuestions(data)          // 获取练习题
api.getOrders()                         // 获取订单
api.downloadOrder(orderId)              // 下载订单
```

#### 管理员API接口 (api.admin.*)
```typescript
// 用户管理
api.admin.getUsers()                     // 用户列表
api.admin.updateUser(id, data)           // 更新用户
api.admin.getRecharges()                 // 充值记录
api.admin.getOrders()                    // 订单列表

// 基础数据CRUD
api.admin.getVersions()                  // 版本列表
api.admin.saveVersion(data)              // 保存版本
api.admin.deleteVersion(id)              // 删除版本
api.admin.getGrades(versionId)           // 年级列表
api.admin.saveGrade(data)                // 保存年级
api.admin.deleteGrade(id)                // 删除年级
api.admin.getSubjects(gradeId)           // 科目列表
api.admin.saveSubject(data)              // 保存科目
api.admin.deleteSubject(id)              // 删除科目
api.admin.getSemesters(subjectId)        // 学期列表
api.admin.saveSemester(data)             // 保存学期
api.admin.deleteSemester(id)             // 删除学期
api.admin.getUnits(semesterId)           // 单元列表
api.admin.saveUnit(data)                 // 保存单元
api.admin.deleteUnit(id)                 // 删除单元

// 知识考点
api.admin.getKnowledge(unitId)          // 知识点列表
api.admin.saveKnowledge(data)           // 保存知识点
api.admin.getExamPoints()               // 考点列表
api.admin.saveExamPoint(data)           // 保存考点
api.admin.getKnowledgeExamPoints(unitId) // 知识点考点
api.admin.saveKnowledgeExamPoint(data)  // 保存知识点考点

// 题库
api.admin.getQuestionTypes()            // 题型列表
api.admin.getDifficulties()              // 难度列表
api.admin.getQuestions(unitId)          // 题目列表
api.admin.saveQuestion(data)            // 保存题目
```

---

### 5.2 状态管理 (stores/user.ts)

**文件路径**: [frontend/src/stores/user.ts](file:///workspace/frontend/src/stores/user.ts)

```typescript
const token = ref(localStorage.getItem('token') || '')
const userInfo = ref<any>(null)

const isLoggedIn = computed(() => !!token.value)
const isAdmin = computed(() => userInfo.value?.role === 'admin')

// 方法
login(username, password)        // 登录
fetchUserInfo()                  // 获取用户信息
logout()                         // 登出
```

---

### 5.3 路由配置 (router/index.ts)

**文件路径**: [frontend/src/router/index.ts](file:///workspace/frontend/src/router/index.ts)

#### 用户端路由

| 路径 | 组件 | 认证 | 说明 |
|------|------|------|------|
| / | Home.vue | 必须 | 首页 |
| /login | Login.vue | - | 登录页 |
| /register | Register.vue | - | 注册页 |
| /recharge | Recharge.vue | 必须 | 充值页 |
| /review | Review.vue | 必须 | 复习页 |
| /practice | Practice.vue | 必须 | 练习页 |
| /orders | Orders.vue | 必须 | 订单页 |
| /profile | Profile.vue | 必须 | 个人中心 |

#### 管理后台路由

| 路径 | 组件 | 说明 |
|------|------|------|
| /admin/login | admin/Login.vue | 管理员登录 |
| /admin | admin/Layout.vue | 管理后台布局 |
| /admin/users | admin/Users.vue | 用户管理 |
| /admin/recharges | admin/Recharges.vue | 充值记录 |
| /admin/orders | admin/Orders.vue | 订单管理 |
| /admin/versions | admin/Versions.vue | 版本管理 |
| /admin/grades | admin/Grades.vue | 年级管理 |
| /admin/subjects | admin/Subjects.vue | 科目管理 |
| /admin/semesters | admin/Semesters.vue | 学期管理 |
| /admin/units | admin/Units.vue | 单元管理 |
| /admin/knowledge-exam-points | admin/KnowledgeExamPoints.vue | 知识点考点管理 |
| /admin/questions | admin/Questions.vue | 题库管理 |

---

### 5.4 页面组件

**文件路径**: `frontend/src/views/`

#### 用户端页面

| 文件 | 说明 |
|------|------|
| Home.vue | 首页，显示科目和单元列表 |
| Login.vue | 用户登录 |
| Register.vue | 用户注册 |
| Recharge.vue | 积分充值 |
| Review.vue | 复习资料下载 |
| Practice.vue | 练习题下载 |
| Orders.vue | 订单历史 |
| Profile.vue | 个人中心 |

#### 管理后台页面

| 文件 | 说明 |
|------|------|
| admin/Layout.vue | 后台布局容器 |
| admin/Login.vue | 管理员登录 |
| admin/Dashboard.vue | 仪表盘 |
| admin/Users.vue | 用户管理 |
| admin/Recharges.vue | 充值记录 |
| admin/Orders.vue | 订单管理 |
| admin/Versions.vue | 版本管理 |
| admin/Grades.vue | 年级管理 |
| admin/Subjects.vue | 科目管理 |
| admin/Semesters.vue | 学期管理 |
| admin/Units.vue | 单元管理 |
| admin/KnowledgeExamPoints.vue | 知识点考点管理 |
| admin/Questions.vue | 题库管理 |

---

## 6. 依赖关系

### 6.1 后端依赖

```
fastapi==0.109.0          # Web框架
uvicorn[standard]==0.27.0 # ASGI服务器
sqlalchemy==2.0.25        # ORM
pymysql==1.1.0            # MySQL驱动
python-jose[cryptography]==3.3.0  # JWT
passlib[bcrypt]==1.7.4    # 密码加密
bcrypt==4.0.1             # bcrypt算法
python-multipart==0.0.6  # 文件上传
python-docx==1.1.0        # Word文档
pydantic==2.5.0           # 数据验证
pydantic-settings==2.1.0 # 设置管理
alembic==1.13.0           # 数据库迁移
openpyxl==3.1.2           # Excel处理
```

### 6.2 前端依赖

```
vue: ^3.4.0               # 核心框架
vue-router: ^4.2.5        # 路由
pinia: ^2.1.7             # 状态管理
vant: ^4.8.0              # UI组件库
axios: ^1.6.0             # HTTP请求
@vant/use: ^1.6.0         # Vant Hooks
docx-preview: ^0.3.0     # Word预览
```

---

## 7. 项目运行

### 7.1 本地开发

#### 前端
```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:10080
```

#### 后端
```bash
cd backend
pip install -r requirements.txt
python init_db.py  # 初始化数据库
python main.py     # 启动服务
# 服务运行在 http://localhost:8000
```

### 7.2 Docker部署

```bash
# 复制并配置环境变量
cp .env.example .env
# 编辑.env配置数据库信息

# 启动所有服务
docker-compose up -d
```

### 7.3 数据库初始化

运行 `python init_db.py` 会创建:
- 默认管理员账号: admin / admin123
- 人教版版本
- 年级数据(三年级~九年级)
- 各年级默认科目
- 上下册学期
- 每学期5个单元
- 题型(8种)和难度(3级)

---

## 8. 默认管理员账号

| 用户名 | 密码 | 说明 |
|--------|------|------|
| admin | admin123 | 系统管理员 |

---

## 9. 业务规则

### 9.1 积分规则
- 充值比例: 1元 = 100积分
- 复习资料: 10积分/单元
- 练习题: 1积分/题

### 9.2 考试频率枚举
- `seldom` (少考)
- `often` (常考)
- `must` (必考)

### 9.3 年级自动升级
系统根据用户设置的孩子入学时间和当前日期，自动计算当前所在年级。

---

## 10. 环境变量

**.env.example**
```bash
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=smartdrill
SECRET_KEY=your-secret-key-change-in-production
```

**注意**: 生产环境必须修改SECRET_KEY，使用以下命令生成:
```bash
openssl rand -hex 32
```
