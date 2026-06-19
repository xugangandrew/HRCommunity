# 深蓝信息 · HR 社群网站

> 为 HR 从业者打造的专属社群网站，支持邮箱注册登录，登录后可浏览管理员发布的信息资讯、实用资料与效率工具。

## 功能特性

| 模块 | 说明 |
|------|------|
| 邮箱注册 | 用户通过邮箱+密码注册账号，密码经 werkzeug 哈希存储，安全可靠 |
| 邮箱登录 | 邮箱+密码登录，支持登录态保持 |
| 演示账号 | 提供 4 个预设演示账号（含管理员），登录页可一键填充，方便快速体验 |
| 信息资讯 | 图文信息发布与浏览，支持置顶、草稿 |
| 实用资料 | 资料文档上传与下载（支持 PDF/Word/Excel/PPT/压缩包等，≤50MB） |
| 效率工具 | 工具外链展示，直达外部工具 |
| 管理后台 | 管理员可发布/编辑/删除内容、管理成员角色 |
| 权限控制 | 普通成员仅可浏览；管理员可管理内容；未登录不可查看正文 |
| 响应式 | 适配桌面与移动端 |

## 技术栈

- **后端**：Python 3.11 + Flask 3.x
- **数据库**：SQLite（零配置，单文件）
- **前端**：原生 HTML/CSS/JS（无框架依赖，易定制）
- **认证**：邮箱+密码（werkzeug.security 密码哈希）

## 快速开始

```bash
# 1. 安装依赖（沙箱已预装，本地环境需执行）
pip install flask requests

# 2. 初始化数据库（建表 + 写入示例数据 + 生成示例文件）
python3.11 models.py

# 3. 启动服务
python3.11 run.py

# 4. 浏览器访问
#    http://127.0.0.1:8000
```

启动后即可使用邮箱注册登录。登录页提供演示账号一键填充：

| 邮箱 | 密码 | 角色 | 说明 |
|------|------|------|------|
| admin@shenlan.community | admin123 | 管理员 | 可进入后台发布/管理内容（推荐先用此账号体验） |
| helen@demo.com | demo123 | 普通成员 | 招聘HR视角 |
| david@demo.com | demo123 | 普通成员 | 培训HR视角 |
| wendy@demo.com | demo123 | 普通成员 | HRBP视角 |

## 项目结构

```
深蓝信息/
├── app.py                # 主应用（全部路由）
├── config.py             # 配置（站点信息、上传限制等）
├── models.py             # 数据库模型 + 初始化 + 示例数据/文件
├── run.py                # 生产启动入口（0.0.0.0:8000）
├── requirements.txt      # 依赖
├── shenlan.db            # SQLite 数据库（运行后自动生成）
├── static/
│   ├── css/style.css     # 深蓝主题样式
│   ├── js/main.js        # 前端交互
│   └── uploads/          # 上传的资料文件
└── templates/
    ├── base.html         # 基础模板（导航/页脚/消息）
    ├── index.html        # 首页（Hero + 三类内容分区）
    ├── login.html        # 登录页（邮箱密码 + 演示账号）
    ├── register.html     # 注册页
    ├── content.html      # 内容列表页
    ├── detail.html       # 内容详情页
    ├── admin.html        # 管理后台
    ├── admin_edit.html   # 发布/编辑表单
    └── error.html        # 错误页
```

## 部署上线

开发服务器仅用于本地预览，生产环境建议使用 **Gunicorn + Nginx**：

```bash
# 1. 安装 Gunicorn
pip install gunicorn

# 2. 启动（4 个 worker，监听 8000 端口）
gunicorn -w 4 -b 127.0.0.1:8000 app:app

# 3. Nginx 反向代理（将 80/443 转发到 8000）
```

## 常见问题

**Q：如何重置数据？**
删除 `shenlan.db` 文件后重新运行 `python3.11 models.py`。

**Q：如何修改站点名称、标语？**
编辑 `config.py` 中的 `SITE_NAME`、`SITE_SLOGAN`、`SITE_DESC`。

**Q：上传的文件存在哪里？**
`static/uploads/` 目录，文件名加时间戳前缀防重名。

**Q：如何提升某用户为管理员？**
管理员登录后台，在「社群成员」区点击「设为管理员」。

**Q：密码安全吗？**
密码使用 werkzeug.security 的 PBKDF2 算法哈希存储，数据库中不保存明文。

---

© 深蓝信息 · HR 专业社群
