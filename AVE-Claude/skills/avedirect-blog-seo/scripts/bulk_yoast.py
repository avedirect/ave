# -*- coding: utf-8 -*-
import os, re, json, time, base64, urllib.request, ssl, urllib.error

AUTH = os.environ.get('WP_AUTH', '')
if not AUTH:
    raise SystemExit('WP_AUTH missing')
BASIC = base64.b64encode(AUTH.encode('utf-8')).decode('ascii')
CTX = ssl.create_default_context()
LOG = r'C:\Users\avede\AppData\Local\Temp\ave-seo'
BATCH = 10

def req(method, url, data=None):
    headers = {
        'Authorization': f'Basic {BASIC}',
        'Cookie': 'beget=begetok',
        'User-Agent': 'AVE-SEO-Bulk/1.1',
    }
    body = None
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        headers['Content-Type'] = 'application/json; charset=utf-8'
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, context=CTX, timeout=120) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        err = e.read().decode('utf-8', errors='replace')
        raise RuntimeError(f'HTTP {e.code}: {err[:500]}') from e

def limit_chars(text, max_len):
    t = re.sub(r'\s+', ' ', text).strip()
    if len(t) <= max_len:
        return t
    cut = t[:max_len]
    sp = cut.rfind(' ')
    if sp > int(max_len * 0.6):
        cut = cut[:sp]
    return cut.rstrip(' ,.;:') + '…'

def make_seo_title(title):
    clean = re.sub(r'\s+', ' ', title).strip()
    with_brand = f'{clean} | AVE Direct'
    if len(with_brand) <= 70:
        return with_brand
    if len(clean) <= 70:
        return clean
    return limit_chars(clean, 68)

def strip_html(html):
    t = re.sub(r'(?is)<script[^>]*>.*?</script>', ' ', html or '')
    t = re.sub(r'(?is)<style[^>]*>.*?</style>', ' ', t)
    t = re.sub(r'(?is)<[^>]+>', ' ', t)
    t = t.replace('&nbsp;', ' ').replace('&mdash;', '—').replace('&ndash;', '—')
    t = re.sub(r'&[a-zA-Z]+;', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()

def make_desc(title, html):
    plain = strip_html(html)
    if plain.lower().startswith(title.lower()):
        plain = plain[len(title):].lstrip(' —–-')
    # drop leading template noise
    plain = re.sub(r'^(практическ\w+\s+статья\s+по\s+материалам[^.]*\.\s*)', '', plain, flags=re.I)
    if len(plain) >= 60:
        # ensure starts with capital and includes topic cue
        if not plain[0].isupper():
            plain = plain[0].upper() + plain[1:]
        if title.split()[0].lower() not in plain[:80].lower():
            plain = f'{title}: {plain}'
        return limit_chars(plain, 155)
    return limit_chars(
        f'{title}: что проверить, какие ошибки типичны и как закрепить результат на практике.',
        155,
    )

def needs_update(p):
    st = (p.get('seo_title') or '').strip()
    md = (p.get('meta_description') or '').strip()
    bad = 'Квизмаркетинг'
    if not st or not md:
        return True
    if bad in st or bad in md:
        return True
    if 'роли, показатели, ошибки' in md:
        return True
    return False

def main():
    planned_path = os.path.join(LOG, 'planned-updates.json')
    if os.path.exists(planned_path):
        items = json.load(open(planned_path, encoding='utf-8'))
        # refresh empty/bad only: rebuild from live list for accuracy
        print(f'Loaded prior plan {len(items)}, rebuilding…', flush=True)

    all_posts = []
    page = 1
    total_pages = 1
    while page <= total_pages:
        data = req('GET', f'https://avedirect.ru/wp-json/yoast/v1/bulk_editor/posts?content_type=articles&per_page=100&page={page}&status[]=publish')
        total_pages = int(data['total_pages'])
        all_posts.extend(data['posts'])
        print(f'Listed page {page}/{total_pages} posts={len(all_posts)}', flush=True)
        page += 1

    todo = [p for p in all_posts if needs_update(p)]
    print(f'Need update: {len(todo)} / {len(all_posts)}', flush=True)

    content_map = {}
    ids = [int(p['id']) for p in todo]
    for i in range(0, len(ids), 100):
        chunk = ids[i:i+100]
        include = ','.join(str(x) for x in chunk)
        arts = req('GET', f'https://avedirect.ru/wp-json/wp/v2/articles?include={include}&per_page=100&_fields=id,content')
        if isinstance(arts, dict):
            arts = [arts]
        for a in arts:
            html = (a.get('content') or {}).get('rendered') or (a.get('content') or {}).get('raw') or ''
            content_map[int(a['id'])] = html
        print(f'Content {len(content_map)}/{len(ids)}', flush=True)

    items = []
    for p in todo:
        pid = int(p['id'])
        title = p.get('title') or ''
        st = (p.get('seo_title') or '').strip()
        if st and 'Квизмаркетинг' not in st:
            seo_title = st
        else:
            seo_title = make_seo_title(title)
        md = (p.get('meta_description') or '').strip()
        if md and 'Квизмаркетинг' not in md and 'роли, показатели, ошибки' not in md and len(md) >= 80:
            meta_description = md
        else:
            meta_description = make_desc(title, content_map.get(pid, ''))
        # Yoast limits
        seo_title = limit_chars(seo_title, 70).rstrip('…')
        if len(seo_title) > 70:
            seo_title = seo_title[:70]
        meta_description = limit_chars(meta_description, 156).rstrip('…')
        if len(meta_description) > 156:
            meta_description = meta_description[:156]
        items.append({'id': pid, 'seo_title': seo_title, 'meta_description': meta_description})

    with open(os.path.join(LOG, 'planned-updates.json'), 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f'To update: {len(items)} batch={BATCH}', flush=True)

    ok = fail = 0
    for i in range(0, len(items), BATCH):
        batch = items[i:i+BATCH]
        try:
            res = req('POST', 'https://avedirect.ru/wp-json/yoast/v1/bulk_editor/update_search', {'items': batch})
            batch_ok = sum(1 for r in res.get('results', []) if r.get('success'))
            batch_fail = len(batch) - batch_ok
            ok += batch_ok
            fail += batch_fail
            print(f'Batch {i+1}-{i+len(batch)}: ok={batch_ok} fail={batch_fail}', flush=True)
        except Exception as e:
            # retry one-by-one
            print(f'Batch error {i+1}: {e}; retry singles', flush=True)
            for it in batch:
                try:
                    res = req('POST', 'https://avedirect.ru/wp-json/yoast/v1/bulk_editor/update_search', {'items': [it]})
                    if res.get('results', [{}])[0].get('success'):
                        ok += 1
                    else:
                        fail += 1
                        print(f'  fail id={it["id"]} {res}', flush=True)
                except Exception as e2:
                    fail += 1
                    print(f'  fail id={it["id"]} {e2}', flush=True)
                time.sleep(0.15)
        time.sleep(0.2)

    summary = f'ok={ok} fail={fail} planned={len(items)} totalArticles={len(all_posts)}'
    print('DONE ' + summary, flush=True)
    with open(os.path.join(LOG, 'bulk-result.txt'), 'w', encoding='utf-8') as f:
        f.write(summary)

if __name__ == '__main__':
    main()
