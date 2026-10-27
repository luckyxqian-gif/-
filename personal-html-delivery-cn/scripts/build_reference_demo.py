#!/usr/bin/env python3
"""Build a self-contained, domain-neutral fixture for visual-baseline verification."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "tests" / "fixtures" / "reference-driven-learning-demo.html"


def main() -> None:
    css = (ROOT / "assets" / "layout-print.css").read_text(encoding="utf-8")
    js = (ROOT / "assets" / "interactions.js").read_text(encoding="utf-8")
    html = f"""<!doctype html>
<html lang="zh-CN" data-capabilities="navigation search focus print" data-document-key="visual-baseline-demo" data-content-version="v1">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>知识整理示例</title><style>{css}</style></head>
<body>
<div class="reading-progress" data-reading-progress></div>
<div class="document-header"><div class="document-shell"><h1>知识整理示例</h1><p class="document-subtitle">以结论、对照与行动条件组织高密度资料。</p><div class="header-meta"><span class="header-chip is-key">重点复习</span><span class="header-chip">本次交付</span></div></div></div>
<nav class="section-nav" aria-label="知识导航"><a href="#principle">基本原则</a><a href="#compare">条件对照</a><a href="#practice">应用检查</a></nav>
<div data-search-panel hidden><div class="search-panel__row"><input data-search-input type="search" placeholder="搜索结论、条件或行动"><span data-search-count></span><button data-action="search-prev" type="button">上一个</button><button data-action="search-next" type="button">下一个</button><button data-action="search-close" type="button">关闭</button></div></div>
<main class="document-shell room-stack">
  <section id="principle" class="document-section" data-section data-room-scroll><div class="section-heading"><span class="section-index">01</span><h2>基本原则</h2><span class="section-priority">优先掌握</span></div><p class="section-lead">先判断结论，再核对条件，最后安排动作。</p><p data-role="key"><span class="system-key">结论必须与决定它的条件一起记忆。</span></p><p data-role="supporting">普通说明用于解释关系，不与结论争夺相同视觉权重。</p><div class="semantic-note semantic-note--info"><span class="semantic-note__title">信息</span>信息色只说明需要核对的背景，不代替结论。</div><div class="semantic-note semantic-note--success"><span class="semantic-note__title">已确认</span>成立条件完整时，结论可以进入执行。</div><div class="semantic-note semantic-note--caution"><span class="semantic-note__title">注意</span>缺少关键条件时，不应直接复用结论。</div></section>
  <section id="compare" class="document-section" data-section data-room-scroll><div class="section-heading"><span class="section-index">02</span><h2>条件对照</h2></div><p class="section-lead">并列只服务真实差异，不把连续内容拆成卡片。</p><div class="comparison"><div><strong>条件已经满足</strong><p data-role="key"><span class="key-phrase">可以执行既定方案。</span></p></div><div><strong>条件尚未满足</strong><p data-role="supporting">补齐信息或改用保守方案。</p></div></div><table><thead><tr><th>判断项</th><th>已满足</th><th>未满足</th></tr></thead><tbody><tr><td>核心条件</td><td>进入下一步</td><td>补充核验</td></tr><tr><td>例外情况</td><td>记录依据</td><td>暂停决定</td></tr></tbody></table></section>
  <section id="practice" class="document-section" data-section data-room-scroll><div class="section-heading"><span class="section-index">03</span><h2>应用检查</h2></div><p class="section-lead">把可执行路径压缩为可快速扫读的顺序。</p><div class="flow" style="--flow-columns:3"><div><span class="flow__title">识别</span>明确对象与问题。</div><div><span class="flow__title">核对</span>检查条件、例外和证据。</div><div><span class="flow__title">行动</span>记录结论并执行。</div></div><div class="evidence-qa"><div class="evidence-qa__question">信息不足时应如何处理？</div><div class="evidence-qa__answer"><span class="system-key">先补齐决定性条件，再输出结论。</span></div></div></section>
</main>
<div class="floating-actions" aria-label="阅读操作"><button data-action="search" type="button"><span class="action-icon">⌕</span>搜索全文</button><button data-action="focus" type="button" aria-pressed="false"><span class="action-icon">◎</span>聚焦重点</button><button data-action="print" type="button"><span class="action-icon">⎙</span>打印 / 存 PDF</button><button data-action="top" type="button"><span class="action-icon">↑</span>回到顶部</button></div><div role="status" aria-live="polite"></div>
<script>{js}</script>
</body></html>"""
    OUTPUT.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
