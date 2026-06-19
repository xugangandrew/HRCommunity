# -*- coding: utf-8 -*-
"""
深蓝信息 HR 社群网站 - 配置文件
================================

登录方式：邮箱注册登录
密码使用 werkzeug.security 进行哈希存储，不明文保存。
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

    # ---------- 站点信息 ----------
    SITE_NAME = "深蓝信息"
    SITE_SLOGAN = "HR 专业社群 · 共享信息、资料与工具"
    SITE_DESC = "深蓝信息 —— 为 HR 从业者打造的专属社群，登录后即可获取精选资讯、实用资料与效率工具。"
