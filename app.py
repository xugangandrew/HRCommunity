# -*- coding: utf-8 -*-
"""
深蓝信息 - HR 社群网站 主应用
==============================

启动： python3.11 app.py
访问： http://127.0.0.1:5000

路由总览：
  前台：/ /login /register /logout
        /content/<category> /post/<id> /download/<id>
  后台：/admin /admin/new /admin/edit/<id> /admin/delete/<id>
"""

import os
import re
import functools
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, send_from_directory, abort, current_app
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import get_db, init_db

app = Flask(__name__)
app.config.from_object(Config)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# ============================================================
# 上下文注入：所有模板可用 site 和 current_user
# ============================================================
@app.context_processor
def inject_globals():
    return {
        "site": {
            "name": Config.SITE_NAME,
            "slogan": Config.SITE_SLOGAN,
            "desc": Config.SITE_DESC,
        },
        "current_user": get_current_user(),
        "year": datetime.now().year,
    }


# ============================================================
# 登录态工具函数
# ============================================================
def get_current_user():
    uid = session.get("uid")
    if not uid:
        return None
    db = get_db()
    u = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    db.close()
    return u


def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("uid"):
            flash("请先登录后查看", "warning")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        u = get_current_user()
        if not u or u["role"] != "admin":
            abort(403)
        return f(*args, **kwargs)
    return wrapper


EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


# ============================================================
# 前台路由
# ============================================================
CATEGORY_MAP = {
    "news": {"label": "信息资讯", "icon": "📰"},
    "resource": {"label": "实用资料", "icon": "📁"},
    "tool": {"label": "效率工具", "icon": "🛠️"},
}


@app.route("/")
def index():
    db = get_db()
    # 取每类最新的几条 + 置顶
    sections = {}
    for cat in CATEGORY_MAP:
        rows = db.execute(
            "SELECT * FROM posts WHERE category=? AND published=1 ORDER BY is_top DESC, created_at DESC LIMIT 4",
            (cat,)
        ).fetchall()
        sections[cat] = rows
    # 置顶/最新一条作为头条
    headline = db.execute(
        "SELECT * FROM posts WHERE published=1 AND is_top=1 ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    if not headline:
        headline = sections["news"][0] if sections["news"] else None
    db.close()
    return render_template("index.html", sections=sections, headline=headline,
                           categories=CATEGORY_MAP)


@app.route("/content/<category>")
@login_required
def content_list(category):
    if category not in CATEGORY_MAP:
        abort(404)
    db = get_db()
    rows = db.execute(
        "SELECT * FROM posts WHERE category=? AND published=1 ORDER BY is_top DESC, created_at DESC",
        (category,)
    ).fetchall()
    db.close()
    return render_template("content.html", posts=rows, cat=category,
                           cat_info=CATEGORY_MAP[category], categories=CATEGORY_MAP)


@app.route("/post/<int:pid>")
@login_required
def post_detail(pid):
    db = get_db()
    db.execute("UPDATE posts SET views=views+1 WHERE id=?", (pid,))
    db.commit()
    p = db.execute("SELECT * FROM posts WHERE id=? AND published=1", (pid,)).fetchone()
    db.close()
    if not p:
        abort(404)
    return render_template("detail.html", post=p, categories=CATEGORY_MAP)


@app.route("/download/<int:pid>")
@login_required
def download(pid):
    db = get_db()
    p = db.execute("SELECT * FROM posts WHERE id=?", (pid,)).fetchone()
    db.close()
    if not p or not p["file_path"]:
        abort(404)
    upload_dir = os.path.join(os.path.dirname(__file__), "static", "uploads")
    return send_from_directory(upload_dir, p["file_path"], as_attachment=True,
                               download_name=p["file_name"] or p["file_path"])


# ============================================================
# 注册 / 登录 / 登出
# ============================================================
# 演示账号（登录页一键填充，方便快速体验）
DEMO_ACCOUNTS = [
    {"email": "admin@shenlan.community", "password": "admin123", "nickname": "深蓝管理员", "role": "admin"},
    {"email": "helen@demo.com",  "password": "demo123", "nickname": "Helen", "role": "member"},
    {"email": "david@demo.com",  "password": "demo123", "nickname": "David", "role": "member"},
    {"email": "wendy@demo.com",  "password": "demo123", "nickname": "Wendy", "role": "member"},
]


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        next_url = request.form.get("next") or url_for("index")

        if not email or not password:
            flash("请输入邮箱和密码", "warning")
            return redirect(url_for("login", next=next_url))

        db = get_db()
        u = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        db.close()

        if not u or not check_password_hash(u["password_hash"], password):
            flash("邮箱或密码错误", "danger")
            return redirect(url_for("login", next=next_url))

        session["uid"] = u["id"]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db = get_db()
        db.execute("UPDATE users SET last_login=? WHERE id=?", (now, u["id"]))
        db.commit()
        db.close()
        flash(f"欢迎回来，{u['nickname']}！", "success")
        return redirect(next_url)

    next_url = request.args.get("next", "")
    return render_template("login.html", next_url=next_url, demo_accounts=DEMO_ACCOUNTS)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        nickname = request.form.get("nickname", "").strip()
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")

        # 校验
        if not EMAIL_RE.match(email):
            flash("邮箱格式不正确", "danger")
            return redirect(url_for("register"))
        if not nickname:
            flash("请填写昵称", "danger")
            return redirect(url_for("register"))
        if len(password) < 6:
            flash("密码至少 6 位", "danger")
            return redirect(url_for("register"))
        if password != password2:
            flash("两次输入的密码不一致", "danger")
            return redirect(url_for("register"))

        db = get_db()
        if db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone():
            db.close()
            flash("该邮箱已注册，请直接登录", "warning")
            return redirect(url_for("login"))

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            "INSERT INTO users(email,password_hash,nickname,avatar,role,created_at,last_login) VALUES(?,?,?,?,?,?,?)",
            (email, generate_password_hash(password), nickname, None, "member", now, now),
        )
        db.commit()
        uid = db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()[0]
        db.close()

        session["uid"] = uid
        flash(f"注册成功，欢迎加入{Config.SITE_NAME}，{nickname}！", "success")
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("已退出登录", "info")
    return redirect(url_for("index"))


# ============================================================
# 管理后台
# ============================================================
@app.route("/admin")
@admin_required
def admin():
    db = get_db()
    posts = db.execute(
        "SELECT p.*, u.nickname AS author FROM posts p LEFT JOIN users u ON p.author_id=u.id "
        "ORDER BY created_at DESC"
    ).fetchall()
    users = db.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    db.close()
    return render_template("admin.html", posts=posts, users=users, categories=CATEGORY_MAP)


@app.route("/admin/new", methods=["GET", "POST"])
@admin_required
def admin_new():
    if request.method == "POST":
        return save_post(None)
    return render_template("admin_edit.html", post=None, categories=CATEGORY_MAP)


@app.route("/admin/edit/<int:pid>", methods=["GET", "POST"])
@admin_required
def admin_edit(pid):
    db = get_db()
    post = db.execute("SELECT * FROM posts WHERE id=?", (pid,)).fetchone()
    db.close()
    if not post:
        abort(404)
    if request.method == "POST":
        return save_post(pid)
    return render_template("admin_edit.html", post=post, categories=CATEGORY_MAP)


def save_post(pid):
    db = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cat = request.form.get("category", "news")
    title = request.form.get("title", "").strip()
    summary = request.form.get("summary", "").strip()
    content = request.form.get("content", "").strip()
    link = request.form.get("link", "").strip()
    is_top = 1 if request.form.get("is_top") else 0
    published = 1 if request.form.get("published") else 0
    uid = session.get("uid")

    if not title:
        flash("标题不能为空", "danger")
        return redirect(url_for("admin_new"))

    file_path = None
    file_name = None
    f = request.files.get("file")
    if f and f.filename and allowed_file(f.filename):
        file_name = secure_filename(f.filename)
        # 加时间戳防重名
        ts = datetime.now().strftime("%Y%m%d%H%M%S_")
        file_path = ts + file_name
        f.save(os.path.join(app.config["UPLOAD_FOLDER"], file_path))

    if pid:
        old = db.execute("SELECT * FROM posts WHERE id=?", (pid,)).fetchone()
        file_path = file_path or old["file_path"]
        file_name = file_name or old["file_name"]
        db.execute(
            """UPDATE posts SET category=?,title=?,summary=?,content=?,link=?,
               file_path=?,file_name=?,is_top=?,published=?,updated_at=? WHERE id=?""",
            (cat, title, summary, content, link, file_path, file_name, is_top, published, now, pid),
        )
        flash("内容已更新", "success")
    else:
        db.execute(
            """INSERT INTO posts(category,title,summary,content,link,file_path,file_name,
               is_top,published,author_id,created_at,updated_at)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (cat, title, summary, content, link, file_path, file_name, is_top, published, uid, now, now),
        )
        flash("发布成功", "success")
    db.commit()
    db.close()
    return redirect(url_for("admin"))


@app.route("/admin/delete/<int:pid>", methods=["POST"])
@admin_required
def admin_delete(pid):
    db = get_db()
    p = db.execute("SELECT * FROM posts WHERE id=?", (pid,)).fetchone()
    if p and p["file_path"]:
        fp = os.path.join(app.config["UPLOAD_FOLDER"], p["file_path"])
        if os.path.exists(fp):
            os.remove(fp)
    db.execute("DELETE FROM posts WHERE id=?", (pid,))
    db.commit()
    db.close()
    flash("已删除", "info")
    return redirect(url_for("admin"))


@app.route("/admin/promote/<int:uid>", methods=["POST"])
@admin_required
def admin_promote(uid):
    """提升/取消管理员（仅演示用，方便把登录用户变管理员体验后台）"""
    db = get_db()
    u = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    new_role = "admin" if u["role"] != "admin" else "member"
    db.execute("UPDATE users SET role=? WHERE id=?", (new_role, uid))
    db.commit()
    db.close()
    flash(f"已将用户设为 {new_role}", "success")
    return redirect(url_for("admin"))


# ============================================================
# 错误页
# ============================================================
@app.errorhandler(403)
@app.errorhandler(404)
def page_error(e):
    return render_template("error.html", code=e.code, message=str(e.description)), e.code


# ============================================================
# 启动
# ============================================================
if __name__ == "__main__":
    init_db()
    print("=" * 50)
    print(f"  {Config.SITE_NAME} 启动中...")
    print(f"  登录方式: 邮箱注册登录")
    print(f"  访问地址: http://127.0.0.1:5000")
    print(f"  管理员账号: admin@shenlan.community / admin123")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True)
