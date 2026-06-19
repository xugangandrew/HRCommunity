# -*- coding: utf-8 -*-
"""
深蓝信息 HR 社群网站 - 配置文件
================================

【微信登录配置说明】
要启用真实的微信扫码登录，需要：
1. 前往 https://open.weixin.qq.com/ 注册微信开放平台账号（需企业资质）
2. 创建"网站应用"，通过审核后获得 AppID 和 AppSecret
3. 在网站应用里配置授权回调域名（必须已ICP备案）
4. 将下方 WECHAT_APP_ID / WECHAT_APP_SECRET 填入，并将
   WECHAT_DEMO_MODE 设为 False

未配置真实凭证时，网站默认运行在"演示模式"，
可用预设演示账号体验全部功能，方便本地开发和预览。
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # ---------- Flask 基础 ----------
    SECRET_KEY = os.environ.get("SECRET_KEY", "shenlan-hr-community-2025-secret")

    # ---------- 数据库 ----------
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "shenlan.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---------- 文件上传 ----------
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
                          "zip", "rar", "txt", "png", "jpg", "jpeg", "gif", "mp4"}

    # ---------- 微信开放平台（网站应用扫码登录）----------
    # 填入真实凭证后即可启用微信登录；留空则自动进入演示模式
    WECHAT_APP_ID = os.environ.get("WECHAT_APP_ID", "")
    WECHAT_APP_SECRET = os.environ.get("WECHAT_APP_SECRET", "")
    # 授权回调地址（需与微信开放平台中配置一致，指向 /wechat/callback）
    # 本地调试可用 http://127.0.0.1:5000；上线后改成你的备案域名
    WECHAT_REDIRECT_URI = os.environ.get(
        "WECHAT_REDIRECT_URI", "http://127.0.0.1:5000/wechat/callback"
    )
    # 演示模式开关：未配置微信凭证时自动开启
    WECHAT_DEMO_MODE = not (WECHAT_APP_ID and WECHAT_APP_SECRET)

    # ---------- 管理员 ----------
    # 首次初始化时创建的管理员账号（演示模式登录后可在此提升为管理员）
    ADMIN_OPENID = "admin_shenlan"

    # ---------- 站点信息 ----------
    SITE_NAME = "深蓝信息"
    SITE_SLOGAN = "HR 专业社群 · 共享信息、资料与工具"
    SITE_DESC = "深蓝信息 —— 为 HR 从业者打造的专属社群，登录后即可获取精选资讯、实用资料与效率工具。"
