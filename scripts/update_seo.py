#!/usr/bin/env python3
"""Generate the public information pages and static material cards (stdlib only)."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import re
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = "https://wodemac.com"
UPDATED = "2026-11-07"

FAQ = [
    ("service", "wodeMac 提供什么服务？", "wodeMac 提供位于美国加州、租期内独享的实体 Mac mini 租赁。按约配合远程连接、开发工具与 AI 编程工作流支持；机器用于软件开发与测试，例如产品原型、自动化脚本、构建和测试。具体配置、库存和支持范围在下单或报价时确认。"),
    ("account", "租一台 Mac，是否就包含 Claude Code 账号或订阅？", "机器租赁不等于第三方 AI 账号或模型订阅。Claude Code 等工具使用客户本人或企业通过官方渠道持有的账号，订阅及模型费用另行确认；wodeMac 不转卖、代持或共享第三方账号，也不以第三方官方或授权代理身份提供 AI 服务。"),
    ("eligibility", "美国加州的机器能否替代第三方工具的地区或年龄资格？", "不能。海外机器、远程连接或支付方式都不能替代第三方工具要求的用户地区、年龄及账号资格。确认真实用户、所在地区、用途和适用条款后，才能决定可提供的机器配置与支持，不承诺保证注册或开通。"),
    ("tasks", "出海团队和 AI 编程老师适合从什么任务开始？", "团队可以选一个产品原型、一段自动化脚本，或一次能复跑的构建与测试；成年老师可以先跑通自己的编程作品或课程项目。先确定负责人、样本、交付物与验收方式，再讨论环境配置。家庭编程项目由符合工具资格的成年家长操作并引导，不直接向未成年人提供第三方账号。"),
    ("delivery", "如何确认交付、计费和远程连接安排？", "当前官网服务条款说明通常在 24 小时内交付，最迟 3 个工作日，计费从付款当天开始。下单前应确认当期库存、配置、远程连接方式、交付时间和售后边界；具体订单及当前官网条款是核对依据，不能把场景示意或营销目标当成交付保证。"),
    ("scope", "“独享”是否表示没有托管维护权限？", "独享指租期内这台实体 Mac 分配给该客户使用，不与其他租赁客户拆分共用。它不表示托管方没有维护或排障权限。管理员权限、支持访问、数据处理、备份和服务结束后的清理安排，应在当前官网条款及交付清单中逐项确认。"),
    ("partner", "哪些机构可以讨论渠道合作？", "AI 编程老师、服务出海开发团队的顾问，以及 IT 或 AI 实施服务商，都可以带着一个真实客户需求讨论合作。先确认客户任务、第三方资格、双方责任与可交付性；沟通中的机构只是候选，只有达成具体约定后才称为合作伙伴。"),
    ("commission", "推广伙伴的首单佣金怎么计算？", "当前 Mac 租赁推广规则按客户首单实际付款计佣：月付 5%、季付 7.5%、半年付 10%、年付 15%。注册、未付款订单、续费及退款订单不计佣，退款会作废相应佣金。推荐计划只有一级，不按招募其他推荐人发奖励，不承诺合作收入。"),
    ("attribution", "客户归属和佣金结算怎样核对？", "推广伙伴登录官网生成专属链接，首次访问来源保留 30 天，并在新用户首次登录时绑定；以官网实际记录和当期规则核验归属。佣金每月对账、人工审核并线下结算，不是自动打款；正式沟通前确认链接、客户归属、退款及对账方式。"),
    ("reseller", "推广伙伴和经销商是否使用同一份协议？", "推广伙伴使用官网推荐链接和当期首单计佣规则；经销合作的价格、客户关系、服务责任及收益分配单独沟通。Mac 租赁费用与额外支持分别列明，未经核定的一站式套餐不直接报价。批量配置和折扣按当前实际订单或书面报价确认，不根据营销测算自动承诺。"),
    ("proof", "宣传素材、任务示例和客户案例有什么区别？", "素材库里的海报和场景图用于解释服务，不是客户已经取得结果的证明。任务示例说明如何验证开发与测试；真实案例需要客户授权、过程记录和可以核对的结果。当前客户案例库仍待补充，价格、佣金与批量测算都不是已发生的销量或收入。"),
    ("contact", "想购买或合作，第一步提供什么？", "先说明你是开发团队、成年 AI 编程老师还是实施服务商，以及想完成的一个开发或测试任务、负责人、预计时间和预算范围。随后一起确认工具资格、配置、费用、交付与验收。不需要在首次咨询里发送账号密码、付款信息、私人客户表或儿童个人资料。"),
]


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def sidebar(current: str) -> str:
    entries = [("index.html", "合作伙伴手册"), ("partners.html", "渠道合作"), ("faq.html", "购买与合作问答"), ("materials.html", "宣传素材"), ("cases.html", "客户案例（待补充）")]
    links = []
    for href, name in entries:
        active = ' class="current" aria-current="page"' if href == current else ""
        links.append(f'<a href="{href}"{active}><span aria-hidden="true">↗</span>{name}</a>')
    return '<aside class="sidebar" aria-label="wodeMac 伙伴资料"><a class="wordmark" href="index.html">wodeMac<span class="brand-dot" aria-hidden="true"></span></a><p class="sidebar-caption">服务与渠道合作</p><nav class="chapter-nav" aria-label="页面导航">' + "".join(links) + '</nav><a class="official-link" href="https://wodemac.com/">访问 wodeMac 官网 <span aria-hidden="true">↗</span></a></aside>'


def resources() -> str:
    links = [
        ("/guides/", "官网中文指南", "核对服务事实与适用条件"),
        ("/guides/mac-mini-rental.html", "美国 Mac mini 租赁指南", "配置、费用、远程连接与交付"),
        ("/guides/claude-code-remote-mac.html", "Claude Code 远程开发", "自有账号、项目准备与任务验证"),
        ("/guides/codex-remote-mac.html", "Codex 远程开发", "预装 Codex，用自己的 ChatGPT 或 API 账号"),
        ("/guides/claude-code-vs-codex.html", "Claude Code 和 Codex 怎么选", "同一台 Mac 上用真实任务对比"),
        ("/guides/ai-coding-agent-always-on-mac.html", "Agent 7×24 持续工作", "合上笔记本，任务继续跑"),
        ("/guides/ios-app-claude-code-codex.html", "没有 Mac 也能做 iOS", "Claude Code / Codex + Xcode 远程构建"),
        ("/guides/en.html", "English guides", "Claude Code & Codex on a dedicated Mac mini"),
        ("/guides/teams-and-educators.html", "团队与编程老师", "从真实项目确定环境与验收"),
        ("/guides/partners.html", "官网合作说明", "合作分工、推荐与沟通入口"),
    ]
    return '<section class="seo-section" aria-labelledby="resources-title"><h2 id="resources-title">继续了解服务与使用方式</h2><ul class="seo-resource-list">' + "".join(f'<li><a href="{OFFICIAL}{path}"><b>{title} ↗</b><span>{desc}</span></a></li>' for path, title, desc in links) + '</ul></section>'


def faq_articles(items: list[tuple[str, str, str]], heading: str = "h2") -> str:
    if heading not in ("h2", "h3"):
        raise ValueError("FAQ headings must be h2 or h3")
    return "\n".join(f'<article class="seo-faq" id="{key}"><{heading}>{esc(question)}</{heading}><p>{esc(answer)}</p></article>' for key, question, answer in items)


def schema(base: str, filename: str, title: str, description: str, items: list[tuple[str, str, str]] | None = None, kind: str = "WebPage") -> str:
    url = base + ("/" if filename == "index.html" else "/" + filename)
    graph = [
        {"@type": "Organization", "@id": OFFICIAL + "/#organization", "name": "wodeMac", "url": OFFICIAL + "/"},
        {"@type": "WebSite", "@id": base + "/#website", "name": "wodeMac 服务与渠道合作资料", "url": base + "/", "inLanguage": "zh-CN", "publisher": {"@id": OFFICIAL + "/#organization"}},
        {"@type": kind, "@id": url + "#webpage", "url": url, "name": title, "description": description, "inLanguage": "zh-CN", "isPartOf": {"@id": base + "/#website"}, "about": {"@id": OFFICIAL + "/#organization"}},
    ]
    if filename in ("partners.html", "faq.html"):
        graph[-1]["dateModified"] = UPDATED
    if filename != "index.html":
        graph.append({"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "合作伙伴手册", "item": base + "/"}, {"@type": "ListItem", "position": 2, "name": title, "item": url}]})
    if items:
        graph.append({"@type": "FAQPage", "@id": url + "#questions", "mainEntity": [{"@type": "Question", "name": question, "acceptedAnswer": {"@type": "Answer", "text": answer}} for _, question, answer in items]})
    data = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return '<script id="wodemac-seo-schema" type="application/ld+json">' + data + '</script>'


def update_head(source: str, base: str, filename: str, title: str, description: str, noindex: bool = False, items: list[tuple[str, str, str]] | None = None, kind: str = "WebPage") -> str:
    match = re.search(r"<head>(.*?)</head>", source, re.S | re.I)
    if not match:
        raise ValueError(f"Missing head in {filename}")
    head = match.group(1)
    head = re.sub(r'<link\b[^>]*href=["\'][^"\']*fonts\.(?:googleapis|gstatic)\.com[^"\']*["\'][^>]*>\s*', "", head, flags=re.I)
    head = re.sub(r'<title\b[^>]*>.*?</title>\s*', "", head, flags=re.S | re.I)
    head = re.sub(r'<meta\b[^>]*(?:name=["\'](?:description|robots|twitter:[^"\']+)["\']|property=["\']og:[^"\']+["\'])[^>]*>\s*', "", head, flags=re.I)
    head = re.sub(r'<link\b[^>]*rel=["\']canonical["\'][^>]*>\s*', "", head, flags=re.I)
    head = re.sub(r'<link\b[^>]*href=["\']seo\.css["\'][^>]*>\s*', "", head, flags=re.I)
    head = re.sub(r'<script\b[^>]*id=["\']wodemac-seo-schema["\'][^>]*>.*?</script>\s*', "", head, flags=re.S | re.I)
    url = base + ("/" if filename == "index.html" else "/" + filename)
    robots = "noindex,follow" if noindex else "index,follow,max-image-preview:large"
    additions = f'''<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="zh_CN">
<meta property="og:site_name" content="wodeMac">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://wodemac.com/assets/wodemac-og.jpg">
<meta name="twitter:card" content="summary_large_image">
'''
    if 'href="seo.css"' not in head:
        additions += '<link rel="stylesheet" href="seo.css">\n'
    if not noindex:
        additions += schema(base, filename, title, description, items, kind) + "\n"
    return source[:match.start(1)] + head.strip() + "\n" + additions + source[match.end(1):]


def document(filename: str, content: str) -> str:
    return '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<meta name="theme-color" content="#f6f4ee">\n<link rel="stylesheet" href="styles.css">\n</head>\n<body class="seo-page">\n<a class="skip-link" href="#content">跳到正文</a>\n' + sidebar(filename) + '\n<main id="content">' + content + '<footer class="seo-footer"><span>wodeMac · 服务与渠道合作资料</span><a href="index.html#contact">微信联系 Elian ↗</a><a href="https://wodemac.com/legal/terms.html">核对官网服务条款 ↗</a></footer></main>\n</body>\n</html>\n'


def partners_content() -> str:
    return '''<header class="seo-hero"><p class="seo-eyebrow">渠道合作 / AI 编程与开发服务</p><h1>把客户的真实项目，<br>和合适的开发环境接起来。</h1><p class="seo-lead">wodeMac 面向 AI 编程老师、出海开发服务商与 IT 实施伙伴，提供美国加州独享 Mac mini 租赁，以及按约配合的远程开发与测试环境支持。先确认客户任务、第三方工具资格、责任与报价，再决定转介或经销合作。</p><p class="seo-updated">资料核对与更新：<time datetime="2026-11-07">2026 年 11 月 7 日</time> · 具体订单与当前官网规则为准</p><div class="seo-actions"><a href="index.html#contact">联系 Elian，聊一个真实需求 ↗</a><a href="faq.html">先看购买与合作问答 →</a></div></header>
<section class="seo-section" aria-labelledby="who-title"><h2 id="who-title">我们想与谁合作</h2><div class="seo-cards"><article class="seo-card"><p class="seo-step">01 / 教学</p><h3>成年 AI 编程老师</h3><p>从老师自己的工具或课程项目开始。先形成能复跑的开发实践，再判断哪些学员或企业客户确实需要远程 Mac 环境，不用招生或收入保证吸引合作。</p></article><article class="seo-card"><p class="seo-step">02 / 企业</p><h3>出海开发服务商</h3><p>围绕产品原型、代码交付和构建测试确认需求。伙伴了解客户业务，双方约定机器、环境、实施与客户关系的边界，避免只转发海报却说不清交付。</p></article><article class="seo-card"><p class="seo-step">03 / 实施</p><h3>IT 与 AI 实施团队</h3><p>先评估现有项目是否需要独享远程 Mac。用样本验证工具、权限与工作流，再明确谁处理环境、谁负责业务实施，以及怎样验收与持续支持。</p></article></div></section>
<section class="seo-section" aria-labelledby="start-title"><h2 id="start-title">第一单怎样开始</h2><ol><li><strong>说清任务：</strong>准备一个开发或测试项目、负责人、时间与预算范围，不传账号密码或未经授权的客户资料。</li><li><strong>确认适用：</strong>核实第三方工具的用户资格、账号归属、远程连接和项目数据要求；海外机器不替代地区或年龄条件。</li><li><strong>列清交付：</strong>确认配置、费用、环境支持、实施责任、验收和后续维护，客户本人或企业持有自己的第三方账号。</li><li><strong>约定合作：</strong>确认推荐链接、客户归属、对账方式或单独的经销协议，再依据真实订单推进，不把意向机构称作已签约伙伴。</li></ol></section>
<section class="seo-section" aria-labelledby="rules-title"><h2 id="rules-title">推广伙伴的首单规则</h2><table class="seo-table"><thead><tr><th scope="col">客户首单方案</th><th scope="col">按实际付款计佣</th></tr></thead><tbody><tr><th scope="row">月付</th><td>5%</td></tr><tr><th scope="row">季付</th><td>7.5%</td></tr><tr><th scope="row">半年付</th><td>10%</td></tr><tr><th scope="row">年付</th><td>15%</td></tr></tbody></table><p class="seo-table-caption">以上为 Mac 租赁推广规则；续费、注册、未付款和退款订单不计佣。只有一级推荐，不按招募推荐人发奖励，不承诺合作收入。经销价格和协议单独沟通。</p><p class="seo-source">核对依据：<a href="https://wodemac.com/legal/terms.html">官网服务条款中的推荐计划</a>与<a href="https://wodemac.com/#partners">官网伙伴入口</a>。</p></section>
<aside class="seo-callout" aria-labelledby="boundary-title"><h2 id="boundary-title">合作之前，把边界讲清楚</h2><p>机器仅用于软件开发与测试。Claude Code 等第三方工具的账号、订阅和模型费用由客户按官方渠道及适用条件确认；不转售、共享或代持账号，不保证注册或开通。Mac 租赁与额外支持分别列明，批量配置、折扣和经销收益按当前订单或书面约定确认。</p><p>按官网推荐规则，推广内容须标明“广告”并说明拿佣金，同时遵守所在平台的广告、外链和私信规则。不买私人名单、不群发，对方拒绝即停止。海报和场景图不是客户成果，真实案例需客户授权和实际记录。</p></aside>
<section class="seo-section" aria-labelledby="partner-faq-title"><h2 id="partner-faq-title">合作前常见问题</h2>''' + faq_articles([FAQ[8], FAQ[9], FAQ[10]], "h3") + '</section>' + resources()


def faq_content() -> str:
    return '''<header class="seo-hero"><p class="seo-eyebrow">购买与合作 / 常见问题</p><h1>租什么、怎样交付，<br>合作如何核对。</h1><p class="seo-lead">wodeMac 提供美国加州独享 Mac mini，用于远程软件开发与测试。机器、环境支持和第三方 AI 账号是不同事项；购买或合作前，先核对用途、资格、配置、费用和责任。这里把客户与渠道伙伴常问的问题集中说明。</p><p class="seo-updated">资料核对与更新：<time datetime="2026-11-07">2026 年 11 月 7 日</time> · 当前官网条款、实际订单与双方书面约定为核对依据</p><div class="seo-actions"><a href="index.html#contact">带一个具体任务来咨询 ↗</a><a href="partners.html">了解渠道合作 →</a></div></header><section aria-label="常见问题回答">''' + faq_articles(FAQ) + '</section><aside class="seo-callout"><h2>先核对信息，再确定方案</h2><p>配置、库存、支持范围和报价可能调整。请同时查看<a href="https://wodemac.com/">官网当前方案</a>、<a href="https://wodemac.com/legal/terms.html">服务条款</a>与<a href="https://wodemac.com/legal/privacy.html">隐私政策</a>；本页不替代订单和协议，不作收益、提效、招生或第三方账号开通保证。</p></aside>' + resources()


def render_materials() -> str:
    catalog = json.loads((ROOT / "materials.json").read_text())
    groups = {group["id"]: group["name"] for group in catalog["groups"]}
    ids = set()
    cards = []
    for item in catalog["items"]:
        if item["id"] in ids or item["group"] not in groups or not re.fullmatch(r"[a-z0-9-]+", item["id"] + item["group"]):
            raise ValueError("Invalid material identifier or group")
        ids.add(item["id"])
        for key in ("image", "download"):
            path = item.get(key)
            if path and (urlparse(path).scheme or not (ROOT / path).resolve().is_relative_to(ROOT) or not (ROOT / path).is_file()):
                raise ValueError(f"Expected an existing local material: {path}")
        image, download = item["image"], item.get("download") or item["image"]
        ratio = f'{catalog["format"]["width"]}/{catalog["format"]["height"]}'
        cards.append(f'''<article class="asset-card" data-asset-id="{esc(item['id'])}" data-group="{esc(item['group'])}"><a class="poster-preview {esc(item['group'])}" style="aspect-ratio:{ratio}" href="{esc(download)}" target="_blank" rel="noopener" aria-label="查看原图：{esc(item['title'])}"><img src="{esc(image)}" alt="{esc(item['title'])}" loading="lazy"></a><div class="asset-details"><p class="asset-category">{esc(groups[item['group']])}{'<span class="asset-new">最新</span>' if item.get('new') else ''}</p><h2>{esc(item['title'])}</h2><p class="asset-description">{esc(item['description'])}</p>{'<div class="asset-promo"><p class="asset-promo-label">推广文案</p><p class="asset-promo-text">' + esc(item['promo']) + '</p><button type="button" class="asset-copy">复制文案</button></div>' if item.get('promo') else ''}<a class="asset-download" href="{esc(download)}" download>下载图片 ↓</a></div></article>''')
    return "\n<!-- materials:generated:start -->\n" + "\n".join(cards) + "\n<!-- materials:generated:end -->\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="https://wodemac.vilesaint.com", help="Verified marketing-site origin, without a trailing slash")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    parsed = urlparse(base)
    if parsed.scheme not in ("http", "https") or not parsed.netloc or parsed.path:
        raise ValueError("--base-url must be an HTTP(S) origin")
    pages = {
        "index.html": ("合作伙伴手册：Mac mini 租赁推广与经销合作 | wodeMac", "wodeMac 合作伙伴手册：美国加州独享 Mac mini 租赁的推广与经销合作方式、三类客户怎么讲、价格与首单佣金、建立合作步骤、前 30 天执行和分工。", False, None, "WebPage"),
        "partners.html": ("Mac mini 租赁渠道合作：AI 编程老师与实施伙伴 | wodeMac", "了解 wodeMac 美国加州独享 Mac mini 的渠道合作方式：面向 AI 编程老师、出海开发服务商与 IT 实施伙伴，说明交付分工、首单计佣、客户归属和人工对账。", False, [FAQ[8], FAQ[9], FAQ[10]], "WebPage"),
        "faq.html": ("美国 Mac mini 租赁与渠道合作常见问题 | wodeMac", "购买与合作前核对 wodeMac 的开发测试用途、第三方自有账号与资格、交付、独享权限、首单佣金、每月对账和经销边界。", False, FAQ, "WebPage"),
        "materials.html": ("伙伴宣传素材：61 张场景海报与参考截图 | wodeMac", "wodeMac 合作伙伴宣传素材，包含 61 张场景化海报与 1 张家长参考截图，按品牌理念、学生家长、个人用户、出海企业、AI 老师与大V、渠道伙伴和一站式服务分类查看及下载，最新素材排在最前。", False, None, "CollectionPage"),
        "cases.html": ("客户案例资料待补充 | wodeMac", "wodeMac 客户案例资料页，当前预留分类位置，真实客户照片与案例说明待客户授权和核验后补充。", True, None, "CollectionPage"),
        "materials-preview.html": ("海报样稿预览 | wodeMac", "wodeMac 首批四款海报的创意思路与大图预览，完整宣传海报可在素材库查看和下载；创意场景不代表实际客户案例。", True, None, "WebPage"),
    }
    (ROOT / "partners.html").write_text(document("partners.html", partners_content()))
    (ROOT / "faq.html").write_text(document("faq.html", faq_content()))
    for filename, (title, description, noindex, items, kind) in pages.items():
        source = (ROOT / filename).read_text()
        source = update_head(source, base, filename, title, description, noindex, items, kind)
        if filename not in ("partners.html", "faq.html") and 'href="partners.html"' not in source:
            source = source.replace('</nav>', '<a href="partners.html"><span>↗</span>渠道合作</a><a href="faq.html"><span>↗</span>购买与合作问答</a>\n  </nav>', 1)
        if filename == "index.html":
            facts = '''<!-- service-facts:start --><section class="seo-facts" aria-labelledby="service-facts-title"><h2 id="service-facts-title">先了解服务，再讨论合作</h2><p>wodeMac 提供美国加州独享 Mac mini 租赁，用于软件开发与测试，按约配合远程环境和 AI 编程工作流支持。第三方工具账号与订阅由客户本人或企业通过官方渠道持有，需满足相应的年龄、地区与使用条件。</p><p>本页的价格、佣金与批量测算仅供估算，不是已发生的销量或收入。推广伙伴首单规则、客户归属及对账方式可先查看合作说明；配置、批量价格、经销协议与额外支持按当前订单或书面确认核对。</p><nav aria-label="服务与合作资料"><a href="partners.html">渠道合作说明 →</a><a href="faq.html">购买与合作问答 →</a><a href="https://wodemac.com/guides/">官网中文指南 ↗</a></nav></section><!-- service-facts:end -->'''
            if '<!-- service-facts:start -->' in source:
                source = re.sub(r'<!-- service-facts:start -->.*?<!-- service-facts:end -->', lambda _: facts, source, flags=re.S)
            else:
                source = source.replace('  <section class="belief"', "  " + facts + '\n\n  <section class="belief"', 1)
        if filename == "materials.html":
            source = re.sub(r'<div class="asset-grid" id="asset-grid">.*?</div>\s*(?=<p class="library-error")', lambda _: '<div class="asset-grid" id="asset-grid">' + render_materials() + '</div>\n    ', source, flags=re.S)
            source = re.sub(r'(<p id="asset-count" aria-live="polite">).*?(</p>)', r'\g<1>62 项素材 · 62 项已上架\2', source)
        (ROOT / filename).write_text(source)
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n")
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    urlset = ET.Element("{" + namespace + "}urlset")
    for filename, (_, _, noindex, _, _) in pages.items():
        if noindex:
            continue
        node = ET.SubElement(urlset, "{" + namespace + "}url")
        ET.SubElement(node, "{" + namespace + "}loc").text = base + ("/" if filename == "index.html" else "/" + filename)
    ET.indent(urlset, space="  ")
    ET.ElementTree(urlset).write(ROOT / "sitemap.xml", encoding="utf-8", xml_declaration=True)
    (ROOT / "llms.txt").write_text(f'''# wodeMac 服务与渠道合作资料

> wodeMac 提供美国加州独享 Mac mini 租赁，用于软件开发与测试，按约配合远程环境与 AI 编程工作流支持。此文件是公开资料目录，不代表任何搜索或 AI 平台已收录、推荐或引用本站。

## 公开资料
- [渠道合作]({base}/partners.html)：适合的伙伴、首单推广规则、责任与对账方式。
- [购买与合作常见问题]({base}/faq.html)：用途、第三方账号资格、交付、权限与合作边界。
- [宣传素材]({base}/materials.html)：61 张场景海报与 1 张参考截图，不代表客户成果。
- [合作伙伴手册]({base}/)：合作方式、建立合作步骤、前 30 天执行与分工；价格与佣金测算仅供估算。

## 核对官网
- [wodeMac 官网]({OFFICIAL}/)
- [中文使用指南]({OFFICIAL}/guides/)
- [美国 Mac mini 租赁指南]({OFFICIAL}/guides/mac-mini-rental.html)
- [Claude Code 远程开发指南]({OFFICIAL}/guides/claude-code-remote-mac.html)
- [团队与编程老师]({OFFICIAL}/guides/teams-and-educators.html)
- [官网合作说明]({OFFICIAL}/guides/partners.html)
- [服务条款]({OFFICIAL}/legal/terms.html)
- [隐私政策]({OFFICIAL}/legal/privacy.html)

## 解释边界
第三方账号及订阅由客户本人或企业通过官方渠道持有，机器不能替代年龄、地区或其他平台资格。首单佣金按真实付款和当期规则核验；注册、未付款、续费、退款订单不计佣，经销协议单独沟通。批量配置、价格与额外支持以当前订单或书面确认核对。客户案例仍待授权和真实记录补充，不将空案例页当作成果证据。

资料更新：{UPDATED}。该日期表示资料维护日期，不表示已获任何平台收录。
''')
    print(f"Updated {len(pages)} HTML pages, static material cards, robots, sitemap and llms directory for {base}")


if __name__ == "__main__":
    main()
