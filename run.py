# -*- coding: utf-8 -*-
"""深蓝信息 - 生产启动入口（关闭 debug，绑定 0.0.0.0:8000）"""

import os
from app import app, init_db
from config import Config

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 8000))
    print("=" * 50)
    print(f"  {Config.SITE_NAME} 启动中（生产模式）...")
    print(f"  微信登录模式: {'演示模式（未配置真实凭证）' if Config.WECHAT_DEMO_MODE else '真实微信登录'}")
    print(f"  监听地址: http://0.0.0.0:{port}")
    print(f"  管理员 openid: {Config.ADMIN_OPENID}")
    print("=" * 50)
    app.run(host="0.0.0.0", port=port, debug=False)
