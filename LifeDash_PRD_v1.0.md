# 个人数字看板 (Personal Digital Dashboard) — 产品需求文档

**文档版本**: v1.0  
**创建日期**: 2026-06-16  
**产品名称**: LifeDash（暂定）  
**项目类型**: 全栈Web应用  
**预计周期**: 2-3周  
**技术复杂度**: ⭐⭐⭐☆☆（中等偏易，适合练手）

---

## 1. 产品概述

### 1.1 一句话描述
一个整合**时间、天气、待办、笔记、习惯追踪、财务记录**的个人数据看板，帮助用户在一个页面管理日常生活。

### 1.2 为什么选这个项目？
| 练习目标 | 本项目覆盖 |
|---------|-----------|
| 前端开发 | ✅ HTML/CSS/JS + 响应式布局 |
| 后端API | ✅ RESTful API 设计 |
| 数据库 | ✅ 增删改查 + 关联查询 |
| 第三方API | ✅ 天气API、新闻API |
| 用户认证 | ✅ 注册/登录/会话管理 |
| 数据可视化 | ✅ 图表展示 |
| 部署上线 | ✅ 云端部署 |

### 1.3 目标用户
- 想提升效率的大学生/职场新人
- 喜欢"All-in-One"工具的效率爱好者
- **最重要的用户：你自己**（ dogfood 原则）

---

## 2. 功能需求

### 2.1 功能总览

```
LifeDash
├── 模块1：用户系统（注册/登录/个人设置）
├── 模块2：仪表盘首页（时间/天气/概览）
├── 模块3：待办管理（Todo List）
├── 模块4：习惯追踪（Habit Tracker）
├── 模块5：快速笔记（Quick Notes）
├── 模块6：财务记录（Expense Tracker）
├── 模块7：数据看板（统计图表）
└── 模块8：设置中心
```

---

### 2.2 模块1：用户系统

#### 1.1 用户注册
- **功能描述**: 新用户创建账号
- **输入字段**:
  - 用户名（3-20字符，字母数字下划线）
  - 邮箱（格式校验，唯一）
  - 密码（8-20字符，至少1字母+1数字）
- **输出**: 注册成功提示，自动登录跳转仪表盘
- **错误处理**: 用户名已存在、邮箱已注册、格式不符

#### 1.2 用户登录
- **功能描述**: 已有用户登录系统
- **输入**: 邮箱 + 密码
- **输出**: JWT Token，跳转仪表盘
- **错误处理**: 邮箱不存在、密码错误
- **附加功能**: "记住我"选项（Token有效期7天 vs 1天）

#### 1.3 个人设置
- **功能描述**: 修改个人信息和偏好
- **可修改项**:
  - 用户名
  - 头像（上传图片）
  - 所在城市（用于天气显示）
  - 主题偏好（浅色/深色/跟随系统）
  - 时区设置

---

### 2.3 模块2：仪表盘首页

#### 2.1 实时时钟组件
- **功能描述**: 显示当前日期时间，每秒更新
- **显示内容**:
  - 大号时间（HH:MM）
  - 日期（YYYY年MM月DD日 星期X）
  - 问候语（根据时间变化：早上好/下午好/晚上好）

#### 2.2 天气组件
- **功能描述**: 显示用户所在城市实时天气
- **数据来源**: 第三方天气API（如OpenWeatherMap、和风天气）
- **显示内容**:
  - 当前温度
  - 天气状况（晴/阴/雨等 + 图标）
  - 最高/最低温度
  - 湿度、风速
  - 未来3天预报
- **交互**: 点击城市名可切换城市

#### 2.3 今日概览卡片
- **功能描述**: 一屏展示今日关键数据
- **卡片内容**:
  - 待办：今日待完成 / 已完成数量
  - 习惯：今日习惯完成率（百分比+进度条）
  - 财务：今日支出 / 本月总支出
  - 笔记：最近一条笔记预览

---

### 2.4 模块3：待办管理（Todo List）

#### 3.1 待办列表
- **功能描述**: 管理个人待办事项
- **字段**:
  - 标题（必填）
  - 描述（可选）
  - 优先级（高/中/低，默认中）
  - 截止日期（可选）
  - 标签（可选，如"学习""工作""生活"）
  - 完成状态（未完成/已完成）
  - 创建时间

#### 3.2 待办操作
- **新增**: 快速输入框 + 展开详细表单
- **编辑**: 点击待办项进入编辑模式
- **完成/取消**: 点击复选框切换状态
- **删除**: 删除按钮 + 确认弹窗
- **筛选**: 全部 / 进行中 / 已完成 / 已逾期
- **排序**: 按优先级 / 截止日期 / 创建时间

#### 3.3 今日待办
- **功能描述**: 仪表盘上只显示今日相关的待办
- **规则**: 截止日期为今天 或 无截止日期且未完成的待办

---

### 2.5 模块4：习惯追踪（Habit Tracker）

#### 4.1 习惯管理
- **功能描述**: 创建和追踪日常习惯
- **字段**:
  - 习惯名称（如"早起""喝水8杯""背单词"）
  - 图标/颜色标识
  - 频率（每天 / 每周X次 / 每周固定星期几）
  - 目标次数（如每天3次）
  - 提醒时间（可选）
  - 创建时间

#### 4.2 习惯打卡
- **功能描述**: 每日记录习惯完成情况
- **交互**:
  - 点击习惯卡片上的"+"号增加完成次数
  - 显示今日完成进度（如 2/3）
  - 完成目标后卡片高亮/动画庆祝

#### 4.3 习惯日历
- **功能描述**: 以日历形式展示习惯完成情况
- **展示方式**:
  - 月视图，每天一个小方块
  - 完成度用颜色深浅表示（GitHub贡献图风格）
  - 点击某天可查看当天所有习惯状态

#### 4.4 习惯统计
- **功能描述**: 展示习惯长期坚持情况
- **数据**:
  - 当前连续打卡天数（Streak）
  - 历史最长连续天数
  - 本月完成率
  - 总完成次数

---

### 2.6 模块5：快速笔记（Quick Notes）

#### 5.1 笔记列表
- **功能描述**: 简单的文本笔记管理
- **字段**:
  - 标题（可选，默认取正文前20字）
  - 正文（富文本或Markdown）
  - 标签（可选）
  - 创建时间 / 更新时间
  - 置顶标记

#### 5.2 笔记操作
- **新增**: 快速输入框，支持Markdown语法
- **编辑**: 点击笔记进入编辑
- **删除**: 删除按钮
- **搜索**: 按标题/内容关键词搜索
- **置顶**: 最多置顶3条笔记

#### 5.3 最近笔记
- **功能描述**: 仪表盘显示最近3条笔记预览
- **展示**: 标题 + 正文前50字 + 更新时间

---

### 2.7 模块6：财务记录（Expense Tracker）

#### 6.1 收支记录
- **功能描述**: 记录日常收入和支出
- **字段**:
  - 类型（收入 / 支出）
  - 金额（正数，保留2位小数）
  - 分类（餐饮/交通/购物/学习/娱乐/工资/其他）
  - 备注（可选）
  - 日期（默认今天，可修改）
  - 创建时间

#### 6.2 分类管理
- **功能描述**: 自定义收支分类
- **默认分类**:
  - 支出：餐饮、交通、购物、学习、娱乐、医疗、其他
  - 收入：工资、兼职、奖学金、理财、其他
- **可添加/编辑/删除自定义分类**

#### 6.3 财务统计
- **功能描述**: 可视化展示财务数据
- **图表类型**:
  - 本月支出饼图（按分类）
  - 近7天/30天支出趋势折线图
  - 本月收支对比柱状图
- **关键指标**:
  - 本月总支出 / 总收入 / 结余
  - 日均支出
  - 最大单笔支出

---

### 2.8 模块7：数据看板（统计中心）

#### 7.1 综合数据面板
- **功能描述**: 整合所有模块的统计数据
- **展示内容**:
  - 本周待办完成率趋势
  - 本周习惯打卡热力图
  - 本周财务支出分布
  - 笔记数量变化

#### 7.2 时间维度切换
- **功能描述**: 查看不同时间段的数据
- **选项**: 本周 / 本月 / 本年 / 自定义范围

---

### 2.9 模块8：设置中心

#### 8.1 账户设置
- 修改密码
- 绑定/解绑邮箱
- 注销账号（数据清除确认）

#### 8.2 应用设置
- 主题切换（浅色/深色/跟随系统）
- 语言切换（中文/英文）
- 数据导出（JSON格式下载所有个人数据）
- 数据清空（重置所有记录，保留账号）

---

## 3. 页面结构设计

### 3.1 页面清单

| 页面 | 路由 | 说明 |
|-----|------|------|
| 登录页 | /login | 注册/登录 |
| 仪表盘 | /dashboard | 首页，所有组件聚合 |
| 待办页 | /todos | 完整待办管理 |
| 习惯页 | /habits | 习惯追踪详情 |
| 笔记页 | /notes | 笔记管理 |
| 财务页 | /expenses | 财务记录与统计 |
| 统计页 | /stats | 综合数据看板 |
| 设置页 | /settings | 个人与应用设置 |

### 3.2 布局结构

```
┌─────────────────────────────────────────────┐
│  顶部导航栏 (Logo + 页面链接 + 用户头像下拉)   │
├──────────┬──────────────────────────────────┤
│          │                                  │
│  侧边栏   │         主内容区                  │
│ (快捷导航)│     (根据路由显示不同页面)         │
│          │                                  │
│ • 仪表盘  │                                  │
│ • 待办   │                                  │
│ • 习惯   │                                  │
│ • 笔记   │                                  │
│ • 财务   │                                  │
│ • 统计   │                                  │
│ • 设置   │                                  │
│          │                                  │
└──────────┴──────────────────────────────────┘
```

### 3.3 响应式设计

| 设备 | 布局调整 |
|-----|---------|
| 桌面端 (>1024px) | 侧边栏展开 + 主内容区 |
| 平板端 (768-1024px) | 侧边栏收起为图标 + 主内容区 |
| 手机端 (<768px) | 底部Tab导航 + 单栏内容 |

---

## 4. 数据库设计

### 4.1 实体关系图 (ERD)

```
User (1) ───< (N) Todo
     │
     ├──< (N) Habit ───< (N) HabitLog
     │
     ├──< (N) Note
     │
     ├──< (N) Expense ─── (N) Category
     │
     └──< (1) UserSetting
```

### 4.2 表结构

#### users 表
| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 用户ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| email | VARCHAR(100) | UNIQUE, NOT NULL | 邮箱 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希 |
| avatar_url | VARCHAR(255) | NULL | 头像URL |
| city | VARCHAR(50) | DEFAULT '北京' | 所在城市 |
| timezone | VARCHAR(50) | DEFAULT 'Asia/Shanghai' | 时区 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

#### todos 表
| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 待办ID |
| user_id | INT | FK → users.id, NOT NULL | 所属用户 |
| title | VARCHAR(200) | NOT NULL | 标题 |
| description | TEXT | NULL | 描述 |
| priority | ENUM('high','medium','low') | DEFAULT 'medium' | 优先级 |
| due_date | DATE | NULL | 截止日期 |
| tag | VARCHAR(50) | NULL | 标签 |
| is_completed | BOOLEAN | DEFAULT FALSE | 是否完成 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

#### habits 表
| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 习惯ID |
| user_id | INT | FK → users.id, NOT NULL | 所属用户 |
| name | VARCHAR(100) | NOT NULL | 习惯名称 |
| icon | VARCHAR(50) | DEFAULT 'star' | 图标标识 |
| color | VARCHAR(20) | DEFAULT '#3B82F6' | 颜色 |
| frequency_type | ENUM('daily','weekly','custom') | DEFAULT 'daily' | 频率类型 |
| frequency_value | INT | DEFAULT 1 | 频率值（每周几次/固定周几） |
| target_count | INT | DEFAULT 1 | 每日目标次数 |
| reminder_time | TIME | NULL | 提醒时间 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### habit_logs 表
| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 记录ID |
| habit_id | INT | FK → habits.id, NOT NULL | 所属习惯 |
| user_id | INT | FK → users.id, NOT NULL | 所属用户 |
| log_date | DATE | NOT NULL | 记录日期 |
| completed_count | INT | DEFAULT 0 | 当日完成次数 |
| note | VARCHAR(200) | NULL | 备注 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### notes 表
| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 笔记ID |
| user_id | INT | FK → users.id, NOT NULL | 所属用户 |
| title | VARCHAR(200) | NULL | 标题 |
| content | TEXT | NOT NULL | 正文 |
| tag | VARCHAR(50) | NULL | 标签 |
| is_pinned | BOOLEAN | DEFAULT FALSE | 是否置顶 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

#### expenses 表
| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 记录ID |
| user_id | INT | FK → users.id, NOT NULL | 所属用户 |
| type | ENUM('income','expense') | NOT NULL | 收支类型 |
| amount | DECIMAL(10,2) | NOT NULL | 金额 |
| category_id | INT | FK → categories.id, NOT NULL | 分类ID |
| note | VARCHAR(200) | NULL | 备注 |
| expense_date | DATE | NOT NULL | 发生日期 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### categories 表
| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 分类ID |
| user_id | INT | FK → users.id, NULL | NULL为系统默认分类 |
| name | VARCHAR(50) | NOT NULL | 分类名称 |
| type | ENUM('income','expense') | NOT NULL | 分类类型 |
| icon | VARCHAR(50) | DEFAULT 'circle' | 图标 |
| color | VARCHAR(20) | DEFAULT '#6B7280' | 颜色 |
| is_default | BOOLEAN | DEFAULT FALSE | 是否系统默认 |

---

## 5. API 接口设计

### 5.1 接口规范
- **Base URL**: `/api/v1`
- **认证方式**: Bearer Token (JWT)
- **响应格式**:
```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "timestamp": "2026-06-16T21:09:00Z"
}
```

### 5.2 接口清单

#### 认证模块
| 方法 | 路径 | 描述 | 认证 |
|-----|------|------|------|
| POST | /auth/register | 用户注册 | 否 |
| POST | /auth/login | 用户登录 | 否 |
| POST | /auth/refresh | 刷新Token | 是 |
| GET | /auth/me | 获取当前用户信息 | 是 |
| PUT | /auth/profile | 更新个人信息 | 是 |

#### 待办模块
| 方法 | 路径 | 描述 | 认证 |
|-----|------|------|------|
| GET | /todos | 获取待办列表（支持筛选排序） | 是 |
| POST | /todos | 创建待办 | 是 |
| GET | /todos/:id | 获取单个待办 | 是 |
| PUT | /todos/:id | 更新待办 | 是 |
| DELETE | /todos/:id | 删除待办 | 是 |
| PATCH | /todos/:id/toggle | 切换完成状态 | 是 |
| GET | /todos/today | 获取今日待办 | 是 |

#### 习惯模块
| 方法 | 路径 | 描述 | 认证 |
|-----|------|------|------|
| GET | /habits | 获取习惯列表 | 是 |
| POST | /habits | 创建习惯 | 是 |
| PUT | /habits/:id | 更新习惯 | 是 |
| DELETE | /habits/:id | 删除习惯 | 是 |
| POST | /habits/:id/log | 打卡记录 | 是 |
| GET | /habits/:id/logs | 获取习惯打卡记录 | 是 |
| GET | /habits/calendar | 获取习惯日历数据 | 是 |

#### 笔记模块
| 方法 | 路径 | 描述 | 认证 |
|-----|------|------|------|
| GET | /notes | 获取笔记列表 | 是 |
| POST | /notes | 创建笔记 | 是 |
| PUT | /notes/:id | 更新笔记 | 是 |
| DELETE | /notes/:id | 删除笔记 | 是 |
| PATCH | /notes/:id/pin | 置顶/取消置顶 | 是 |
| GET | /notes/search | 搜索笔记 | 是 |

#### 财务模块
| 方法 | 路径 | 描述 | 认证 |
|-----|------|------|------|
| GET | /expenses | 获取收支记录 | 是 |
| POST | /expenses | 创建记录 | 是 |
| PUT | /expenses/:id | 更新记录 | 是 |
| DELETE | /expenses/:id | 删除记录 | 是 |
| GET | /expenses/stats | 获取财务统计 | 是 |
| GET | /categories | 获取分类列表 | 是 |
| POST | /categories | 创建自定义分类 | 是 |

#### 天气模块
| 方法 | 路径 | 描述 | 认证 |
|-----|------|------|------|
| GET | /weather/current | 获取当前天气 | 是 |
| GET | /weather/forecast | 获取未来预报 | 是 |

---

## 6. 技术栈推荐

### 6.1 方案A：经典全栈（推荐）

| 层级 | 技术 | 说明 |
|-----|------|------|
| 前端 | **Vue 3 + Vite + Tailwind CSS** | 现代前端，响应式样式 |
| 图表 | **Chart.js / ECharts** | 数据可视化 |
| 后端 | **Python FastAPI** | 异步高性能 |
| 数据库 | **SQLite** (开发) → **PostgreSQL** (生产) | 轻量起步，后期迁移 |
| ORM | **SQLAlchemy** | Python数据库操作 |
| 认证 | **JWT (PyJWT)** | Token认证 |
| 部署 | **Vercel(前端) + Render/Railway(后端)** | 免费托管 |

### 6.2 方案B：更轻量（如果前端不熟）

| 层级 | 技术 | 说明 |
|-----|------|------|
| 前端 | **纯HTML/CSS/JS + Bootstrap** | 不用学框架 |
| 后端 | **Python Flask** | 比FastAPI更简单 |
| 数据库 | **SQLite** | 文件数据库，零配置 |
| 部署 | **PythonAnywhere** | 免费Python托管 |

---

## 7. 项目开发计划

### 7.1 里程碑

| 阶段 | 时间 | 目标 | 可演示内容 |
|-----|------|------|-----------|
| **Week 1** | 第1-7天 | 基础框架+用户系统 | 注册/登录页面，能创建账号 |
| **Week 2** | 第8-14天 | 核心功能 | 仪表盘+待办+笔记+天气 |
| **Week 3** | 第15-21天 | 完整功能+优化 | 习惯+财务+统计+部署上线 |

### 7.2 Week 1 逐日任务

| 天数 | 任务 | 产出 |
|-----|------|------|
| Day 1 | 搭建项目结构，配置开发环境 | 前后端项目能跑起来 |
| Day 2 | 设计数据库，创建表结构 | 能用SQL创建所有表 |
| Day 3 | 实现用户注册API | POST /auth/register 可用 |
| Day 4 | 实现用户登录API + JWT | POST /auth/login 返回Token |
| Day 5 | 做登录/注册前端页面 | 能填写表单，调用API |
| Day 6 | 做仪表盘布局（侧边栏+顶部栏） | 有基本的页面框架 |
| Day 7 | 整合测试，修复bug | 能注册→登录→看到仪表盘 |

### 7.3 Week 2 逐日任务

| 天数 | 任务 | 产出 |
|-----|------|------|
| Day 8 | 接入天气API，做天气组件 | 仪表盘显示实时天气 |
| Day 9 | 实现待办后端API（CRUD） | 待办增删改查可用 |
| Day 10 | 做待办前端页面 | 能添加、完成、删除待办 |
| Day 11 | 实现笔记后端API | 笔记CRUD可用 |
| Day 12 | 做笔记前端页面 | 能写笔记、搜索、置顶 |
| Day 13 | 做时钟组件+今日概览卡片 | 仪表盘信息丰富 |
| Day 14 | 整合测试 | 仪表盘+待办+笔记完整可用 |

### 7.4 Week 3 逐日任务

| 天数 | 任务 | 产出 |
|-----|------|------|
| Day 15 | 实现习惯后端API | 习惯CRUD+打卡可用 |
| Day 16 | 做习惯前端页面+日历 | 能打卡、看日历 |
| Day 17 | 实现财务后端API | 收支记录CRUD |
| Day 18 | 做财务前端+图表 | 能记账、看饼图 |
| Day 19 | 做统计页面（整合图表） | 数据可视化看板 |
| Day 20 | 做设置页面+主题切换 | 能改密码、换主题 |
| Day 21 | 部署上线+写README | 项目能在公网访问 |

---

## 8. 学习检查清单

做完这个项目，你将掌握：

### 前端技能
- [ ] HTML5 语义化标签
- [ ] CSS Flexbox / Grid 布局
- [ ] 响应式设计（媒体查询）
- [ ] JavaScript ES6+ 语法
- [ ] DOM 操作与事件处理
- [ ] Fetch API / Axios 请求
- [ ] Vue 3 组件化开发（如选方案A）
- [ ] 前端路由（Vue Router）

### 后端技能
- [ ] RESTful API 设计规范
- [ ] Python Web 框架（FastAPI/Flask）
- [ ] 数据库设计与 SQL 操作
- [ ] ORM 使用（SQLAlchemy）
- [ ] JWT 认证与权限控制
- [ ] 第三方 API 集成（天气）
- [ ] 错误处理与日志记录

### 通用技能
- [ ] Git 版本控制（分支、提交、推送）
- [ ] GitHub 项目管理（Issues、PR）
- [ ] 环境变量管理
- [ ] 项目部署（云服务器/托管平台）
- [ ] 写技术文档（README）

---

## 9. 扩展方向（做完基础版后）

| 功能 | 技术点 | 难度 |
|-----|-------|------|
| 数据同步（多端） | WebSocket / PWA | ⭐⭐⭐ |
| 邮件提醒 | Celery + Redis 定时任务 | ⭐⭐⭐ |
| AI智能建议 | 接入大模型API分析用户数据 | ⭐⭐⭐ |
| 语音输入 | Web Speech API | ⭐⭐ |
| 数据导入导出 | Excel/CSV处理 | ⭐⭐ |
| 暗黑模式 | CSS变量 + localStorage | ⭐ |
| 多语言 | i18n国际化 | ⭐⭐ |

---

## 10. 验收标准

项目完成的定义（Definition of Done）：

1. ✅ 用户能注册、登录、登出
2. ✅ 仪表盘显示实时时间、天气、今日概览
3. ✅ 能增删改查待办事项，支持筛选排序
4. ✅ 能创建习惯、每日打卡、查看日历
5. ✅ 能写笔记、搜索、置顶
6. ✅ 能记录收支、看统计图表
7. ✅ 支持浅色/深色主题切换
8. ✅ 部署到公网，能通过URL访问
9. ✅ GitHub仓库有完整的README文档
10. ✅ 录一个3分钟演示视频

---

**文档维护记录**

| 日期 | 版本 | 修改内容 | 修改人 |
|-----|------|---------|-------|
| 2026-06-16 | v1.0 | 初始版本创建 | [你的名字] |

---

*本文档为LifeDash项目需求文档。以项目驱动学习，边做边学，3周后你将拥有一个完整的全栈作品。*
