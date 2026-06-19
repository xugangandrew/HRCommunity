# 深蓝信息 · HR 社群网站

> 为 HR 从业者打造的专属社群网站，支持微信扫码登录，登录后可浏览管理员发布的信息资讯、实用资料与效率工具。

## 功能特性

| 模块 | 说明 |
|------|------|
| 微信登录 | 接入微信开放平台「网站应用」扫码登录（OAuth2.0）；未配置时自动进入演示模式 |
| 演示模式 | 提供 4 个预设账号（含管理员），可一键登录体验全部功能，方便本地预览 |
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
- **登录**：微信开放平台 OAuth2.0（snsapi_login）

## 快速开始

```bash
# 1. 安装依赖（沙箱已预装，本地环境需执行）
pip install flask requests

# 2. 初始化数据库（建表 + 写入示例数据 + 生成示例文件）
python3.11 models.py

# 3. 启动服务
python3.11 app.py

# 4. 浏览器访问
#    http://127.0.0.1:5000
```

启动后默认为**演示模式**，在登录页可选择演示账号一键登录：
- **深蓝管理员** —— 可进入后台发布/管理内容（推荐先用此账号体验）
- **Helen / David / Wendy** —— 普通成员视角

## 配置真实微信登录

当前演示模式下「微信扫码登录」按钮不可用。要启用真实微信登录，按以下步骤操作：

### 1. 注册微信开放平台

前往 [微信开放平台](https://open.weixin.qq.com/) 注册账号（需企业资质并通过开发者认证）。

### 2. 创建网站应用

- 在「管理中心 → 网站应用」创建应用，填写网站信息并提交审核
- 审核通过后获得 **AppID** 和 **AppSecret**
- 在应用详情中配置**授权回调域名**（必须是你已 ICP 备案的域名，不带 http://）

### 3. 填写配置

编辑 `config.py`（或通过环境变量注入）：

```python
WECHAT_APP_ID = "你的AppID"
WECHAT_APP_SECRET = "你的AppSecret"
WECHAT_REDIRECT_URI = "https://你的域名/wechat/callback"
```

或通过环境变量（推荐，避免泄露密钥）：

```bash
export WECHAT_APP_ID="你的AppID"
export WECHAT_APP_SECRET="你的AppSecret"
export WECHAT_REDIRECT_URI="https://你的域名/wechat/callback"
```

配置后 `WECHAT_DEMO_MODE` 会自动变为 `False`，登录页将显示真实的微信扫码按钮，演示账号区自动隐藏。

> 无需改动任何代码，OAuth 全流程（授权 → 换 token → 拉取用户信息 → 建立登录态）已在 `wechat_auth.py` 中实现。

## 项目结构

```
深蓝信息/
├── app.py                # 主应用（全部路由）
├── config.py             # 配置（微信凭证、站点信息等）
├── models.py             # 数据库模型 + 初始化 + 示例数据/文件
├── wechat_auth.py        # 微信 OAuth2.0 模块
├── requirements.txt      # 依赖
├── shenlan.db            # SQLite 数据库（运行后自动生成）
├── static/
│   ├── css/style.css     # 深蓝主题样式
│   ├── js/main.js        # 前端交互
│   └── uploads/          # 上传的资料文件
└── templates/
    ├── base.html         # 基础模板（导航/页脚/消息）
    ├── index.html        # 首页（Hero + 三类内容分区）
    ├── login.html        # 登录页（微信扫码 / 演示账号）
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

# 3. Nginx 反向代理（示例）
#    将 80/443 端口转发到 8000，并配置 SSL 证书
#    微信回调要求 https
```

Nginx 配置参考：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate     /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    client_max_body_size 50M;   # 与上传限制一致

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 常见问题

**Q：演示模式安全吗？**
演示模式仅用于本地预览。生产环境务必配置真实微信凭证（演示模式会自动关闭），并设置强随机的 `SECRET_KEY`。

**Q：如何重置数据？**
删除 `shenlan.db` 文件后重新运行 `python3.11 models.py`。

**Q：如何修改站点名称、标语？**
编辑 `config.py` 中的 `SITE_NAME`、`SITE_SLOGAN`、`SITE_DESC`。

**Q：上传的文件存在哪里？**
`static/uploads/` 目录，文件名加时间戳前缀防重名。

**Q：微信登录回调域名校验失败？**
确认微信开放平台填写的回调域名与 `WECHAT_REDIRECT_URI` 的域名完全一致（不含协议和路径）。

---

© 深蓝信息 · HR 专业社群
