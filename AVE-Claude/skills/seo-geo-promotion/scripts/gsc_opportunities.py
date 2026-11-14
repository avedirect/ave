#!/usr/bin/env python3
"""Find quick SEO wins in a Google Search Console / Yandex Webmaster query export.

Input: CSV with columns query, page (optional), clicks, impressions, ctr (optional), position.
Russian/English headers are recognised (Запрос, Страница, Клики, Показы, CTR, Позиция).

Reports:
  1. Striking distance  - positions 4-20 with enough impressions (cheapest growth).
  2. Low CTR            - CTR far below the typical curve for its position (rewrite title/description).
  3. Cannibalization    - one query split between several pages (needs page column).
  4. Missing occurrence - with --check-content: query words absent in title/H1/text of the page.

Usage:
    python gsc_opportunities.py export.csv
    python gsc_opportunities.py export.csv --min-impr 50 --check-content 30 > report.md

--check-content requires: requests, beautifulsoup4
"""
import argparse
import csv
import io
import re
import sys
from collections import defaultdict

ALIASES = {
    "query": ["query", "queries", "top queries", "запрос", "запросы", "поисковый запрос"],
    "page": ["page", "pages", "url", "landing page", "страница", "адрес", "url страницы"],
    "clicks": ["clicks", "клики", "переходы", "клики (всего)"],
    "impressions": ["impressions", "показы", "показы (всего)"],
    "ctr": ["ctr", "ctr, %"],
    "position": ["position", "average position", "позиция", "средняя позиция", "ср. позиция"],
}
# Rough organic CTR by position; used only to spot anomalies, not as a target.
EXPECTED_CTR = {1: .28, 2: .16, 3: .11, 4: .08, 5: .06, 6: .05, 7: .04, 8: .03, 9: .025, 10: .02}
STOP = set("и в во на с со по для от до из к о об а но или как что это не ли же у за при".split())


def num(v):
    if v is None:
        return 0.0
    s = str(v).strip().replace("\u00a0", "").replace(" ", "").replace(",", ".")
    pct = s.endswith("%")
    s = s.rstrip("%")
    try:
        x = float(s)
    except ValueError:
        return 0.0
    return x / 100 if pct else x


def load(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "cp1251"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    dialect = csv.Sniffer().sniff(text[:5000], delimiters=",;\t")
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    cols = {}
    for h in reader.fieldnames or []:
        key = h.strip().lower()
        for canon, names in ALIASES.items():
            if key in names and canon not in cols:
                cols[canon] = h
    missing = [c for c in ("query", "clicks", "impressions", "position") if c not in cols]
    if missing:
        sys.exit(f"Не найдены колонки {missing}. Заголовки файла: {reader.fieldnames}")
    rows = []
    for r in reader:
        q = (r.get(cols["query"]) or "").strip()
        if not q:
            continue
        impr = num(r.get(cols["impressions"]))
        clicks = num(r.get(cols["clicks"]))
        ctr = num(r.get(cols["ctr"])) if "ctr" in cols else (clicks / impr if impr else 0)
        if ctr > 1:
            ctr /= 100
        rows.append({"query": q, "page": (r.get(cols["page"]) or "").strip() if "page" in cols else "",
                     "clicks": clicks, "impressions": impr, "ctr": ctr,
                     "position": num(r.get(cols["position"]))})
    return rows, "page" in cols


def expected(pos):
    return EXPECTED_CTR.get(max(1, round(pos)), 0.01)


def words(s):
    return [w for w in re.findall(r"[a-zа-яё0-9]+", s.lower().replace("ё", "е")) if w not in STOP]


def same_word(a, b):
    """Crude Russian morphology: shared prefix covers the word minus a short ending."""
    if a == b:
        return True
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n >= 4 and n >= min(len(a), len(b)) - 2


def present(word, tokens):
    return word in tokens or any(same_word(word, t) for t in tokens if t[:2] == word[:2])


def check_page(url, query, cache):
    import requests
    from bs4 import BeautifulSoup
    if url not in cache:
        try:
            r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1)"})
            soup = BeautifulSoup(r.content, "html.parser")
            for t in soup(["script", "style", "noscript"]):
                t.decompose()
            title = soup.title.get_text(" ") if soup.title else ""
            h1 = " ".join(h.get_text(" ") for h in soup.find_all("h1"))
            body = soup.get_text(" ")
            cache[url] = {z: set(words(v)) for z, v in (("title", title), ("h1", h1), ("text", body))}
            cache[url]["raw"] = re.sub(r"\s+", " ", body.lower().replace("ё", "е"))
        except Exception as e:  # noqa: BLE001 - report any fetch problem as a row
            cache[url] = {"error": str(e)}
    page = cache[url]
    if "error" in page:
        return f"ошибка загрузки: {page['error'][:60]}"
    qs = words(query)
    exact = query.lower().replace("ё", "е") in page["raw"]
    notes = []
    for zone in ("title", "h1"):
        miss = [w for w in qs if not present(w, page[zone])]
        if miss:
            notes.append(f"нет в {zone.upper()}: {', '.join(miss)}")
    miss_text = [w for w in qs if not present(w, page["text"])]
    if miss_text:
        notes.append(f"нет в тексте: {', '.join(miss_text)}")
    if not exact:
        notes.append("нет точного вхождения")
    return "; ".join(notes) or "ок"


def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--min-impr", type=float, default=30, help="минимум показов для строки")
    ap.add_argument("--pos-from", type=float, default=4)
    ap.add_argument("--pos-to", type=float, default=20)
    ap.add_argument("--top", type=int, default=40, help="строк в каждом отчёте")
    ap.add_argument("--check-content", type=int, default=0, metavar="N",
                    help="проверить вхождения запроса на странице для N лучших строк отчёта 1")
    a = ap.parse_args()

    rows, has_page = load(a.csv)
    rows = [r for r in rows if r["impressions"] >= a.min_impr]
    print(f"# Точки роста по выгрузке `{a.csv}`\n\nСтрок с показами ≥ {a.min_impr:g}: {len(rows)}\n")

    sd = [r for r in rows if a.pos_from <= r["position"] <= a.pos_to]
    for r in sd:
        r["potential"] = max(0, r["impressions"] * expected(3) - r["clicks"])
    sd.sort(key=lambda r: -r["potential"])
    sd = sd[:a.top]
    cache = {}
    print(f"## 1. Почти в топе (позиции {a.pos_from:g}–{a.pos_to:g})\n")
    print("Дожать вхождениями в Title/H1/текст, новым блоком под запрос, внутренними ссылками.\n")
    hdr = ["Запрос"] + (["Страница"] if has_page else []) + ["Показы", "Клики", "Поз.", "Доп. клики в топ-3"]
    body = []
    for i, r in enumerate(sd):
        row = [r["query"]] + ([r["page"]] if has_page else []) + [
            int(r["impressions"]), int(r["clicks"]), f"{r['position']:.1f}", int(r["potential"])]
        if a.check_content and has_page and i < a.check_content and r["page"]:
            row.append(check_page(r["page"], r["query"], cache))
        body.append(row)
    if a.check_content and has_page:
        hdr.append("Вхождения на странице")
        body = [b + [""] * (len(hdr) - len(b)) for b in body]
    print(table(hdr, body) if body else "_нет строк_")

    low = [r for r in rows if r["position"] <= 10 and r["ctr"] < expected(r["position"]) * 0.5]
    low.sort(key=lambda r: -(r["impressions"] * (expected(r["position"]) - r["ctr"])))
    print("\n## 2. Низкий CTR для своей позиции\n")
    print("Переписать Title/Description под интент (цифры, цена, выгода, год, топоним), "
          "проверить расширенные сниппеты и не забирает ли клики нейроответ/колдунщик.\n")
    print(table(["Запрос"] + (["Страница"] if has_page else []) + ["Показы", "CTR", "Норма ~", "Поз."],
                [[r["query"]] + ([r["page"]] if has_page else []) +
                 [int(r["impressions"]), f"{r['ctr']:.1%}", f"{expected(r['position']):.0%}",
                  f"{r['position']:.1f}"] for r in low[:a.top]]) if low else "_нет строк_")

    if has_page:
        by_q = defaultdict(list)
        for r in rows:
            by_q[r["query"]].append(r)
        cann = []
        for q, rs in by_q.items():
            if len(rs) < 2:
                continue
            rs.sort(key=lambda r: -r["impressions"])
            total = sum(r["impressions"] for r in rs)
            if rs[1]["impressions"] / total >= 0.2:
                cann.append((q, total, rs))
        cann.sort(key=lambda x: -x[1])
        print("\n## 3. Каннибализация (запрос делят несколько страниц)\n")
        print("Выбрать целевую страницу, убрать запрос из Title/H1 остальных, поставить на целевую "
              "анкорные ссылки; если обе в топ-3 — не трогать.\n")
        print(table(["Запрос", "Показы всего", "Страницы (показы / поз.)"],
                    [[q, int(t), "<br>".join(f"{r['page']} ({int(r['impressions'])} / {r['position']:.1f})"
                                             for r in rs[:4])] for q, t, rs in cann[:a.top]])
              if cann else "_нет строк_")
    else:
        print("\n_Колонки страницы нет — отчёт по каннибализации пропущен. Выгрузите query+page через API._")


if __name__ == "__main__":
    main()
