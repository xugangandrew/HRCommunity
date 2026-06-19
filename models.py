# -*- coding: utf-8 -*-
"""深蓝信息 - 数据模型（基于 SQLite）"""

import os
import time
from datetime import datetime


def get_db():
    """获取 SQLite 连接（轻量方案，不依赖 SQLAlchemy）"""
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), "shenlan.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_sample_files():
    """为示例资料生成可下载的占位文件（PDF / Excel）"""
    upload_dir = os.path.join(os.path.dirname(__file__), "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    # PDF：AI 人才胜任力模型
    pdf_path = os.path.join(upload_dir, "示例文件-AI胜任力模型.pdf")
    if not os.path.exists(pdf_path):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(pdf_path, pagesize=A4)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(72, 760, "ShenLan HR - AI Talent Competency Model v1.0")
            c.setFont("Helvetica", 11)
            lines = [
                "",
                "Sample resource for the ShenLan HR Community.",
                "",
                "Six dimensions:",
                "  1. AI Literacy",
                "  2. Business Insight",
                "  3. Tool Application",
                "  4. Data-driven Thinking",
                "  5. Ethics & Compliance",
                "  6. Continuous Learning",
                "",
                "(Demo placeholder - replace with real content.)",
            ]
            y = 720
            for ln in lines:
                c.drawString(72, y, ln)
                y -= 20
            c.save()
        except Exception as e:
            print(f"[sample] PDF 生成跳过: {e}")

    # Excel：HR 月报模板
    xlsx_path = os.path.join(upload_dir, "示例文件-HR月报模板.xlsx")
    if not os.path.exists(xlsx_path):
        try:
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "HR月报"
            ws.append(["指标", "本月", "上月", "环比变化"])
            ws.append(["在职人数", 120, 118, "+1.7%"])
            ws.append(["新入职人数", 5, 3, "+66.7%"])
            ws.append(["离职人数", 3, 2, "+50%"])
            ws.append(["月度流失率", "2.5%", "1.7%", "+0.8pp"])
            ws.append(["人均培训时长(h)", 4.2, 3.8, "+10.5%"])
            # 简单样式
            from openpyxl.styles import Font
            for col in ws[1]:
                col.font = Font(bold=True)
            wb.save(xlsx_path)
        except Exception as e:
            print(f"[sample] Excel 生成跳过: {e}")


def init_db():
    """建表 + 写入示例数据"""
    conn = get_db()
    c = conn.cursor()

    # ---------- 用户表 ----------
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        openid      TEXT UNIQUE,                 -- 微信 openid（演示模式用模拟值）
        unionid     TEXT,
        nickname    TEXT NOT NULL,
        avatar      TEXT,
        role        TEXT NOT NULL DEFAULT 'member',  -- member / admin
        created_at  TEXT NOT NULL,
        last_login  TEXT
    )
    """)

    # ---------- 内容表（信息 / 资料 / 工具 三类共用）----------
    c.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        category    TEXT NOT NULL,               -- news(信息) / resource(资料) / tool(工具)
        title       TEXT NOT NULL,
        summary     TEXT,                        -- 摘要/简介
        content     TEXT,                        -- 正文(支持简单HTML/纯文本)
        cover       TEXT,                        -- 封面图URL
        file_path   TEXT,                        -- 附件路径(资料类)
        file_name   TEXT,                        -- 附件原始文件名
        link        TEXT,                        -- 外链(工具类常用)
        views       INTEGER NOT NULL DEFAULT 0,
        is_top      INTEGER NOT NULL DEFAULT 0,
        published   INTEGER NOT NULL DEFAULT 1,
        author_id   INTEGER,
        created_at  TEXT NOT NULL,
        updated_at  TEXT NOT NULL,
        FOREIGN KEY (author_id) REFERENCES users(id)
    )
    """)

    # ---------- 示例数据 ----------
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 管理员
    c.execute("SELECT id FROM users WHERE openid=?", ("admin_shenlan",))
    if not c.fetchone():
        c.execute(
            "INSERT INTO users(openid,nickname,avatar,role,created_at,last_login) VALUES(?,?,?,?,?,?)",
            ("admin_shenlan", "深蓝管理员", None, "admin", now, now),
        )

    # 演示用户
    c.execute("SELECT id FROM users WHERE openid=?", ("demo_hr_001",))
    if not c.fetchone():
        c.execute(
            "INSERT INTO users(openid,nickname,avatar,role,created_at,last_login) VALUES(?,?,?,?,?,?)",
            ("demo_hr_001", "Helen(演示HR)", None, "member", now, now),
        )

    admin_id = c.execute("SELECT id FROM users WHERE openid=?", ("admin_shenlan",)).fetchone()[0]

    # 示例内容（字段顺序：category,title,summary,content,cover,file_path,file_name,
    #            link,views,is_top,published,author_id,created_at,updated_at）
    samples = [
        ("news", "2025 HR + AI 趋势观察：从工具到智能体的演进",
         "盘点本季度 HR 领域 AI 应用的关键变化，以及对从业者能力模型的影响。",
         "今年以来，HR 领域的 AI 应用正在从「单点工具」走向「智能体流程」。本文从招聘、培训、绩效三个场景切入，梳理值得关注的实践方向。\n\n1. 招聘：AI 辅助简历筛选与面试问答生成已较普及，下一步是端到端的智能招聘官。\n2. 培训：基于岗位胜任力的个性化学习路径推荐成为新热点。\n3. 绩效：AI 辅助的持续反馈与复盘工具，正在替代传统的年度评估。",
         None, None, None, None, 0, 1, 1, admin_id, now, now),
        ("news", "深蓝信息社群 7 月线上沙龙预告",
         "本期主题：如何用 AI 把员工手册变成可对话的智能助手。",
         "时间：7 月下旬\n形式：腾讯会议线上\n报名方式：登录后在「资料」区下载邀请函，或联系管理员。",
         None, None, None, None, 0, 0, 1, admin_id, now, now),
        ("resource", "《AI 人才胜任力模型 v1.0》完整文档",
         "涵盖 6 大维度、28 项指标的能力模型，附评估表模板。",
         "本资料为深蓝信息原创整理的 AI 人才胜任力模型，适用于企业开展 AI 转型人才盘点。\n\n包含：\n- 维度框架说明\n- 各层级行为锚定\n- 评估打分表（可编辑）\n- 落地实施建议",
         None, "示例文件-AI胜任力模型.pdf", "示例文件-AI胜任力模型.pdf", None, 0, 0, 1, admin_id, now, now),
        ("resource", "HR 月度数据分析报表模板（Excel）",
         "含考勤、人员结构、流失率等常用分析图表，开箱即用。",
         "基于真实项目沉淀的 Excel 模板，支持一键替换数据源刷新图表。",
         None, "示例文件-HR月报模板.xlsx", "示例文件-HR月报模板.xlsx", None, 0, 0, 1, admin_id, now, now),
        ("tool", "考勤异常智能检测工具",
         "上传考勤 Excel，自动完成匹配、异常检测并输出汇总表与 PPT。",
         "本工具由深蓝信息开发，实现从 Excel 转 JSON、员工匹配、异常检测到打包输出的全流程自动化。\n\n特点：\n- 一键运行\n- 支持自定义异常规则\n- 自动生成可视化报告",
         None, None, None, "https://shenlan.example.com/tools/attendance", 0, 0, 1, admin_id, now, now),
        ("tool", "AI 工作坊需求诊断小工具",
         "通过 10 个问题快速评估团队 AI 就绪度，生成建议方案。",
         "适用于 HR 在内训前做需求摸底，3 分钟出结果。",
         None, None, None, "https://shenlan.example.com/tools/diagnose", 0, 0, 1, admin_id, now, now),
    ]
    for s in samples:
        c.execute("SELECT id FROM posts WHERE title=?", (s[1],))
        if not c.fetchone():
            c.execute(
                """INSERT INTO posts(category,title,summary,content,cover,file_path,file_name,link,
                   views,is_top,published,author_id,created_at,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                s,
            )

    conn.commit()
    conn.close()
    create_sample_files()
    print("[init_db] 数据库初始化完成，已写入示例数据与示例文件。")


if __name__ == "__main__":
    init_db()
