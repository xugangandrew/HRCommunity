# -*- coding: utf-8 -*-
"""
深蓝信息 - 微信扫码登录模块
============================

实现微信开放平台"网站应用"扫码登录（OAuth2.0）的完整后端流程：

1. build_authorize_url()  —— 生成跳转到微信的授权页地址
2. get_user_by_code(code) —— 用回调 code 换 access_token，再拉取用户信息

【演示模式】
当 config.WECHAT_DEMO_MODE 为 True（即未配置真实 AppID/Secret）时，
本模块提供 get_demo_users() 返回若干预设演示用户，前端可让访客
一键"以演示账号登录"来体验全部功能。

接入真实微信登录只需：
  1) 在 config.py 填入 WECHAT_APP_ID / WECHAT_APP_SECRET
  2) 在微信开放平台配置授权回调域名为你的域名
  3) 设置 WECHAT_REDIRECT_URI 为 https://你的域名/wechat/callback
其余代码无需改动。
"""

import requests
from config import Config


WX_AUTHORIZE_URL = "https://open.weixin.qq.com/connect/qrconnect"
WX_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token"
WX_USERINFO_URL = "https://api.weixin.qq.com/sns/userinfo"


def build_authorize_url(state="shenlan"):
    """生成微信扫码登录授权页 URL"""
    from urllib.parse import urlencode
    params = {
        "appid": Config.WECHAT_APP_ID,
        "redirect_uri": Config.WECHAT_REDIRECT_URI,
        "response_type": "code",
        "scope": "snsapi_login",   # 网站应用扫码登录固定用此 scope
        "state": state,
    }
    return f"{WX_AUTHORIZE_URL}?{urlencode(params)}#wechat_redirect"


def get_access_token(code):
    """用授权 code 换取 access_token + openid"""
    resp = requests.get(WX_TOKEN_URL, params={
        "appid": Config.WECHAT_APP_ID,
        "secret": Config.WECHAT_APP_SECRET,
        "code": code,
        "grant_type": "authorization_code",
    }, timeout=10)
    return resp.json()


def get_userinfo(access_token, openid):
    """用 access_token + openid 拉取用户资料（昵称、头像等）"""
    resp = requests.get(WX_USERINFO_URL, params={
        "access_token": access_token,
        "openid": openid,
        "lang": "zh_CN",
    }, timeout=10)
    return resp.json()


def get_user_by_code(code):
    """
    完整回调流程：code -> access_token -> userinfo
    返回 dict: {openid, unionid, nickname, avatar}
    失败时抛出 ValueError。
    """
    token_data = get_access_token(code)
    if "errcode" in token_data:
        raise ValueError(f"微信换取 token 失败: {token_data}")

    access_token = token_data["access_token"]
    openid = token_data["openid"]
    unionid = token_data.get("unionid", "")

    info = get_userinfo(access_token, openid)
    if "errcode" in info:
        raise ValueError(f"微信获取用户信息失败: {info}")

    return {
        "openid": openid,
        "unionid": unionid,
        "nickname": info.get("nickname", "微信用户"),
        "avatar": info.get("headimgurl", ""),
    }


# ---------- 演示模式 ----------
DEMO_USERS = [
    {"openid": "demo_hr_001", "nickname": "Helen", "avatar": "", "role": "member", "desc": "招聘HR · 普通成员视角"},
    {"openid": "demo_hr_002", "nickname": "David", "avatar": "", "role": "member", "desc": "培训HR · 普通成员视角"},
    {"openid": "demo_hr_003", "nickname": "Wendy", "avatar": "", "role": "member", "desc": "HRBP · 普通成员视角"},
    {"openid": "admin_shenlan", "nickname": "深蓝管理员", "avatar": "", "role": "admin", "desc": "管理员 · 可发布与管理内容"},
]


def get_demo_users():
    """返回演示账号列表（演示模式用）"""
    return DEMO_USERS
