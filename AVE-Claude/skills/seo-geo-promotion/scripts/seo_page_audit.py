#!/usr/bin/env python3
"""On-page SEO + GEO audit for one or many URLs.

Usage:
    python seo_page_audit.py https://site.ru/page/ [more urls]
    python seo_page_audit.py --file urls.txt --json > report.json
    python seo_page_audit.py https://site.ru/ --ua yandex

Requires: requests, beautifulsoup4 (pip install requests beautifulsoup4)
"""
import argparse
import json
import re
import sys
import time
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("Install deps: pip install requests beautifulsoup4")

UA = {
    "google": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "yandex": "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
    "browser": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
               "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
}
AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "PerplexityBot",
           "Google-Extended", "YandexAdditional", "YandexGPT"]

_robots_cache = {}


def site_files(base, session):
    if base in _robots_cache:
        return _robots_cache[base]
    info = {"robots_txt": None, "sitemaps": [], "llms_txt": False, "parser": None,
            "ai_bots_blocked": []}
    try:
        r = session.get(urljoin(base, "/robots.txt"), timeout=15)
        if r.status_code == 200 and "text" in r.headers.get("content-type", "text"):
            info["robots_txt"] = r.text
            rp = RobotFileParser()
            rp.parse(r.text.splitlines())
            info["parser"] = rp
            info["sitemaps"] = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", r.text)
            info["ai_bots_blocked"] = [b for b in AI_BOTS if not rp.can_fetch(b, base + "/")]
    except requests.RequestException:
        pass
    try:
        r = session.get(urljoin(base, "/llms.txt"), timeout=10)
        info["llms_txt"] = r.status_code == 200 and len(r.text.strip()) > 20 \
            and "<html" not in r.text[:500].lower()
    except requests.RequestException:
        pass
    _robots_cache[base] = info
    return info


def jsonld_types(soup):
    types, errors = [], 0

    def walk(node):
        if isinstance(node, dict):
            t = node.get("@type")
            if t:
                types.extend(t if isinstance(t, list) else [t])
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    blocks = soup.find_all("script", type="application/ld+json")
    raw = []
    for s in blocks:
        try:
            data = json.loads(s.string or "")
            raw.append(data)
            walk(data)
        except (json.JSONDecodeError, TypeError):
            errors += 1
    return sorted(set(types)), errors, raw


def find_in_jsonld(raw, key):
    found = []

    def walk(node):
        if isinstance(node, dict):
            if key in node:
                found.append(node[key])
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(raw)
    return found


def word_count(node):
    return len(re.findall(r"\w+", node.get_text(" ")))


def main_text(soup):
    """Returns (main text, main node, words in whole cleaned body)."""
    s = BeautifulSoup(str(soup), "html.parser")
    for tag in s(["script", "style", "noscript", "template", "svg"]):
        tag.decompose()
    body = s.body or s
    body_words = word_count(body)
    for tag in body(["header", "footer", "nav", "aside", "form"]):
        tag.decompose()
    root = body
    articles = body.find_all("article")
    main = body.find("main")
    if len(articles) == 1 and word_count(articles[0]) >= 0.4 * word_count(body):
        root = articles[0]
    elif main and word_count(main) >= 0.4 * word_count(body):
        root = main
    return re.sub(r"\s+", " ", root.get_text(" ")).strip(), root, body_words


def audit(url, ua_key="google"):
    session = requests.Session()
    session.headers["User-Agent"] = UA[ua_key]
    res = {"url": url, "checks": []}

    def add(level, area, msg):
        res["checks"].append({"level": level, "area": area, "msg": msg})

    t0 = time.time()
    try:
        r = session.get(url, timeout=30, allow_redirects=True)
    except requests.RequestException as e:
        add("error", "fetch", f"Не удалось загрузить: {e}")
        return res
    res["ttfb_total_s"] = round(time.time() - t0, 2)
    res["status"] = r.status_code
    res["final_url"] = r.url
    chain = [h.status_code for h in r.history]
    if chain:
        add("warn" if len(chain) == 1 else "error", "tech",
            f"Редиректы {chain} -> {r.status_code}; ссылки должны вести сразу на {r.url}")
    if r.status_code != 200:
        add("error", "tech", f"HTTP {r.status_code}")
        return res
    if res["ttfb_total_s"] > 2.5:
        add("warn", "speed", f"Ответ сервера + загрузка HTML {res['ttfb_total_s']} с (цель < 1 с)")
    size_kb = len(r.content) / 1024
    if size_kb > 500:
        add("warn", "speed", f"HTML {size_kb:.0f} КБ — тяжёлый документ")

    xrt = r.headers.get("X-Robots-Tag", "")
    if "noindex" in xrt.lower():
        add("error", "index", f"X-Robots-Tag: {xrt}")

    if "charset" not in r.headers.get("content-type", "").lower():
        soup = BeautifulSoup(r.content, "html.parser")
    else:
        soup = BeautifulSoup(r.text, "html.parser")
    parsed = urlparse(r.url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    files = site_files(base, session)
    if files["robots_txt"] is None:
        add("warn", "index", "robots.txt не найден")
    else:
        rp = files["parser"]
        for bot in ("Googlebot", "Yandex"):
            if rp and not rp.can_fetch(bot, r.url):
                add("error", "index", f"URL закрыт в robots.txt для {bot}")
        if not files["sitemaps"]:
            add("warn", "index", "В robots.txt нет директивы Sitemap")
        if files["ai_bots_blocked"]:
            add("warn", "geo", "robots.txt блокирует ИИ-ботов: " + ", ".join(files["ai_bots_blocked"]))
    res["llms_txt"] = files["llms_txt"]

    # --- head ---
    title = (soup.title.string or "").strip() if soup.title else ""
    res["title"] = title
    if not title:
        add("error", "meta", "Нет <title>")
    elif not 30 <= len(title) <= 70:
        add("warn", "meta", f"Длина title {len(title)} симв. (ориентир 30–70)")
    desc_tag = soup.find("meta", attrs={"name": re.compile("^description$", re.I)})
    desc = (desc_tag.get("content") or "").strip() if desc_tag else ""
    res["description"] = desc
    if not desc:
        add("warn", "meta", "Нет meta description")
    elif not 70 <= len(desc) <= 170:
        add("warn", "meta", f"Длина description {len(desc)} симв. (ориентир 70–170)")
    robots_meta = soup.find("meta", attrs={"name": re.compile("^robots$", re.I)})
    if robots_meta and "noindex" in (robots_meta.get("content") or "").lower():
        add("error", "index", f"meta robots: {robots_meta.get('content')}")
    canon = soup.find("link", rel=lambda v: v and "canonical" in v)
    if not canon:
        add("warn", "index", "Нет rel=canonical")
    else:
        href = urljoin(r.url, canon.get("href", ""))
        res["canonical"] = href
        if href.rstrip("/") != r.url.split("#")[0].rstrip("/"):
            add("warn", "index", f"canonical указывает на другой URL: {href}")
    if not soup.find("meta", attrs={"name": "viewport"}):
        add("error", "mobile", "Нет meta viewport")
    html_tag = soup.find("html")
    if not (html_tag and html_tag.get("lang")):
        add("warn", "meta", "Нет атрибута lang у <html>")
    if not soup.find("meta", property="og:title"):
        add("info", "meta", "Нет Open Graph (og:title / og:image) — хуже превью в соцсетях и мессенджерах")

    # --- headings ---
    h1s = [h.get_text(" ", strip=True) for h in soup.find_all("h1")]
    res["h1"] = h1s
    if len(h1s) != 1:
        add("error" if not h1s else "warn", "content", f"H1 на странице: {len(h1s)} (нужен ровно 1)")
    elif title and h1s[0].strip().lower() == title.lower():
        add("info", "content", "H1 полностью совпадает с title — допустимо, но лучше варьировать формулировки")
    heads = [(int(h.name[1]), h.get_text(" ", strip=True)) for h in soup.find_all(re.compile("^h[1-6]$"))]
    skips = [f"H{a}->H{b}" for (a, _), (b, _) in zip(heads, heads[1:]) if b - a > 1]
    if skips:
        add("info", "content", f"Пропуски уровней заголовков: {', '.join(skips[:5])}")
    res["outline"] = [f"{'  ' * (lvl - 1)}H{lvl}: {txt[:90]}" for lvl, txt in heads[:40]]

    # --- content ---
    text, root, body_words = main_text(soup)
    words = len(re.findall(r"\w+", text))
    res["words"] = words
    scripts = len(soup.find_all("script"))
    if body_words < 100 and scripts > 10:
        add("error", "render", f"В исходном HTML всего {body_words} слов при {scripts} скриптах — похоже на "
            "CSR-рендеринг: роботы и LLM видят пустую страницу. Нужен SSR/SSG/пререндер")
    elif words < 300:
        add("warn", "content", f"Мало основного текста: {words} слов")
    imgs = soup.find_all("img")
    no_alt = [i for i in imgs if not (i.get("alt") or "").strip()]
    if imgs and no_alt:
        add("warn", "content", f"Картинок без alt: {len(no_alt)} из {len(imgs)}")
    lazy_missing = [i for i in imgs[3:] if i.get("loading") != "lazy" and not i.get("data-src")]
    if len(lazy_missing) > 5:
        add("info", "speed", f"{len(lazy_missing)} изображений ниже первого экрана без loading=lazy")

    links = soup.find_all("a", href=True)
    internal = [a for a in links if urlparse(urljoin(r.url, a["href"])).netloc == parsed.netloc]
    res["links_internal"], res["links_external"] = len(internal), len(links) - len(internal)
    body_links = [a for a in root.find_all("a", href=True)
                  if urlparse(urljoin(r.url, a["href"])).netloc == parsed.netloc]
    if words > 600 and len(body_links) < 2:
        add("warn", "linking", "В основном тексте почти нет внутренних ссылок — добавьте контекстную перелинковку")

    # --- schema ---
    types, bad_json, raw = jsonld_types(soup)
    res["schema_types"] = types
    microdata = sorted({m.get("itemtype", "").split("/")[-1] for m in soup.find_all(attrs={"itemtype": True})})
    res["microdata_types"] = microdata
    if bad_json:
        add("error", "schema", f"Невалидный JSON-LD блоков: {bad_json}")
    if not types and not microdata:
        add("warn", "schema", "Нет микроразметки Schema.org")
    for want, why in (("Organization", "сущность бренда для поиска и LLM"),
                      ("BreadcrumbList", "хлебные крошки в сниппете")):
        if want not in types and want not in microdata:
            add("info", "schema", f"Нет {want} — {why}")

    # --- GEO / E-E-A-T signals ---
    geo = {}
    dates = find_in_jsonld(raw, "dateModified") + find_in_jsonld(raw, "datePublished")
    dates += [m.get("content") for m in soup.find_all("meta", property=re.compile("article:(modified|published)_time"))]
    dates += [t.get("datetime") for t in soup.find_all("time") if t.get("datetime")]
    geo["date"] = next((d for d in dates if d), None)
    author_ld = find_in_jsonld(raw, "author")
    author_html = soup.find(attrs={"rel": "author"}) or soup.find(class_=re.compile("author", re.I)) \
        or soup.find(itemprop="author")
    geo["author"] = bool(author_ld or author_html)
    geo["faq"] = "FAQPage" in types or bool(soup.find(string=re.compile(r"Частые вопросы|Вопросы и ответы|FAQ", re.I)))
    geo["lists"] = len(root.find_all(["ul", "ol"]))
    geo["tables"] = len(root.find_all("table"))
    q_heads = [t for lvl, t in heads if lvl in (2, 3) and t.strip().endswith("?")]
    geo["question_headings"] = len(q_heads)
    first_p = root.find("p")
    fp_words = len(re.findall(r"\w+", first_p.get_text(" "))) if first_p else 0
    geo["first_paragraph_words"] = fp_words
    numbers = len(re.findall(r"\b\d+[.,]?\d*\s?(%|₽|руб|лет|мин|кг|м²|шт|раз)", text))
    geo["facts_with_numbers"] = numbers
    res["geo"] = geo

    is_article = bool({"Article", "BlogPosting", "NewsArticle"} & set(types)) or root.name == "article"
    geo["is_article"] = is_article
    lvl = "warn" if is_article else "info"
    if not geo["date"]:
        add(lvl, "geo", "Не найдена дата публикации/обновления (datePublished/dateModified, <time>)")
    if not geo["author"]:
        add(lvl, "geo", "Нет явного автора (блок автора + author в Article) — минус E-E-A-T и цитируемости")
    if words > 500:
        if geo["lists"] + geo["tables"] == 0:
            add("warn", "geo", "Нет списков и таблиц — LLM и быстрые ответы охотнее цитируют структурированные фрагменты")
        if geo["question_headings"] == 0 and not geo["faq"]:
            add("info", "geo", "Нет подзаголовков-вопросов и FAQ — добавьте блоки «вопрос → короткий ответ»")
        if fp_words > 80:
            add("info", "geo", f"Первый абзац {fp_words} слов — начните с прямого ответа в 40–60 слов")
        if numbers < 3:
            add("info", "geo", "Мало конкретики (цифры, цены, сроки) — добавьте факты, которые можно процитировать")

    score = 100
    for c in res["checks"]:
        score -= {"error": 15, "warn": 5, "info": 1}.get(c["level"], 0)
    res["score"] = max(score, 0)
    return res


ICON = {"error": "❌", "warn": "⚠️", "info": "ℹ️"}


def to_markdown(r):
    out = [f"## {r['url']}"]
    if "status" in r:
        out.append(f"HTTP {r['status']} · {r.get('ttfb_total_s')} с · слов: {r.get('words', '—')} · "
                   f"оценка: **{r.get('score', 0)}/100**")
    if r.get("title"):
        out.append(f"- **Title** ({len(r['title'])}): {r['title']}")
    if r.get("description"):
        out.append(f"- **Description** ({len(r['description'])}): {r['description']}")
    if r.get("h1"):
        out.append(f"- **H1**: {' | '.join(r['h1'])}")
    if "schema_types" in r:
        out.append(f"- **Schema**: {', '.join(r['schema_types'] + r.get('microdata_types', [])) or '—'}")
    if r.get("geo"):
        g = r["geo"]
        out.append(f"- **GEO-сигналы**: дата={g['date'] or '—'}, автор={'да' if g['author'] else 'нет'}, "
                   f"FAQ={'да' if g['faq'] else 'нет'}, списков={g['lists']}, таблиц={g['tables']}, "
                   f"вопросов в H2/H3={g['question_headings']}, фактов с цифрами={g['facts_with_numbers']}")
    order = {"error": 0, "warn": 1, "info": 2}
    out.append("\n**Проблемы:**")
    for c in sorted(r["checks"], key=lambda c: order[c["level"]]):
        out.append(f"- {ICON[c['level']]} [{c['area']}] {c['msg']}")
    if not r["checks"]:
        out.append("- ✅ Критичных замечаний нет")
    if r.get("outline"):
        out.append("\n<details><summary>Структура заголовков</summary>\n\n```\n" +
                   "\n".join(r["outline"]) + "\n```\n</details>")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="On-page SEO + GEO audit")
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--file", help="файл со списком URL, по одному в строке")
    ap.add_argument("--ua", choices=UA.keys(), default="google")
    ap.add_argument("--json", action="store_true", help="вывод в JSON")
    a = ap.parse_args()
    urls = list(a.urls)
    if a.file:
        with open(a.file, encoding="utf-8") as f:
            urls += [u.strip() for u in f if u.strip() and not u.startswith("#")]
    if not urls:
        ap.error("укажите URL или --file")
    reports = [audit(u, a.ua) for u in urls]
    if a.json:
        print(json.dumps(reports, ensure_ascii=False, indent=2))
    else:
        print("\n\n".join(to_markdown(r) for r in reports))


if __name__ == "__main__":
    main()
