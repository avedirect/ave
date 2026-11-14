# Код для SEO/GEO: head, микроразметка, robots, рендеринг, индексация

## 1. Правила микроразметки

- Размечать **только видимое и правдивое**. Накрутка рейтингов («4,9 и сотни отзывов» на всех страницах), суммарный рейтинг сайта на каждой услуге, услуги как Recipe → отключение вывода всей разметки сайта или ручные санкции.
- Google рекомендует JSON-LD, Яндекс лучше понимает Microdata (особенно Product). Можно смешивать по разным сущностям (крошки в Microdata, организация в JSON-LD), но **одну сущность двумя форматами не дублировать**. Разметку, вставленную через GTM, Яндекс не видит — выводить в HTML с сервера.
- Указывать главную сущность: `mainEntity` (на WebPage) / `mainEntityOfPage`. Тип страницы: `AboutPage`, `ContactPage`, `FAQPage`, `ItemPage`, `CollectionPage`.
- Сущности раскрывать объектами: `Brand`/`Organization`/`Person` с `url` и `sameAs` (Википедия, Wikidata, соцсети) — для понимания сущности поиском и LLM.
- На позиции напрямую не влияет; эффект через CTR расширенных сниппетов (до +10–15% на карточках по опыту). Измерять A/B на группах страниц.
- Внутри значений JSON-LD — без HTML-тегов. Не вставлять H1–H6 в разметку.
- Проверка: validator.schema.org, Google Rich Results Test, валидатор Яндекс.Вебмастера. Новые типы по нише искать на schema.org (на английском); частые типы у топ-10 конкурентов — Screaming Frog в режиме List.
- QAPage — только для настоящих Q&A/форумов (на коммерческих и блоговых страницах тест уронил позиции). FAQ-сниппеты Google почти не показывает, но видимый FAQ полезен людям и LLM.
- Сомневаешься в правдивости поля — не размечай: за отсутствие разметки санкций нет.

## 2. Шаблоны JSON-LD

**Organization (главная)**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://example.ru/#organization",
  "name": "Компания",
  "url": "https://example.ru/",
  "logo": "https://example.ru/logo.png",
  "slogan": "Короткий слоган",
  "taxID": "7700000000",
  "telephone": "+7-495-000-00-00",
  "sameAs": ["https://vk.com/company", "https://t.me/company", "https://ru.wikipedia.org/wiki/..."]
}
</script>
```

**LocalBusiness (контакты; самый конкретный подтип: Dentist, AutoRepair, LegalService…)** — только если клиент приходит в офис.
```json
{
  "@context": "https://schema.org",
  "@type": "AutoRepair",
  "@id": "https://example.ru/contacts/#place",
  "name": "Компания — автосервис на Ленина",
  "parentOrganization": {"@id": "https://example.ru/#organization"},
  "address": {"@type": "PostalAddress", "streetAddress": "ул. Ленина, 1", "addressLocality": "Москва", "postalCode": "101000", "addressCountry": "RU"},
  "geo": {"@type": "GeoCoordinates", "latitude": 55.75, "longitude": 37.61},
  "telephone": "+7-495-000-00-00",
  "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "09:00", "closes": "20:00"}],
  "priceRange": "₽₽"
}
```

**Article + автор Person (статья блога)**
```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "mainEntityOfPage": "https://example.ru/blog/kak-vybrat-x/",
  "headline": "Как выбрать X: 7 критериев и таблица сравнения",
  "description": "Краткий ответ на вопрос статьи в 1–2 предложениях.",
  "image": ["https://example.ru/img/x-16x9.jpg", "https://example.ru/img/x-4x3.jpg"],
  "datePublished": "2026-03-01",
  "dateModified": "2026-10-01",
  "author": {
    "@type": "Person",
    "name": "Иван Иванов",
    "url": "https://example.ru/authors/ivanov/",
    "jobTitle": "Инженер-технолог",
    "knowsAbout": ["X", "Y"],
    "sameAs": ["https://vk.com/ivanov"]
  },
  "reviewedBy": {"@type": "Person", "name": "Пётр Петров", "url": "https://example.ru/authors/petrov/"},
  "publisher": {"@id": "https://example.ru/#organization"}
}
```
`NewsArticle` — только для СМИ (новости компании — это `BlogPosting`/`Article`). Даты в разметке должны совпадать с видимыми на странице.

**BreadcrumbList**
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Главная", "item": "https://example.ru/"},
    {"@type": "ListItem", "position": 2, "name": "Каталог", "item": "https://example.ru/catalog/"},
    {"@type": "ListItem", "position": 3, "name": "Роботы-пылесосы"}
  ]
}
```
В вёрстке — `<nav aria-label="breadcrumb"><ol>…</ol></nav>`.

**Product (карточка)** — обязательно `offers` или рейтинг/отзыв; без цены Google считает вас обзорником. Для Google — условия возврата и доставки.
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Робот-пылесос Model S10",
  "image": ["https://example.ru/img/s10.jpg"],
  "description": "Видимое описание товара.",
  "sku": "S10-BLK",
  "brand": {"@type": "Brand", "name": "Brand", "url": "https://example.ru/brands/brand/", "sameAs": ["https://ru.wikipedia.org/wiki/Brand"]},
  "offers": {
    "@type": "Offer",
    "url": "https://example.ru/product/s10/",
    "priceCurrency": "RUB",
    "price": "24990",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition",
    "hasMerchantReturnPolicy": {"@type": "MerchantReturnPolicy", "applicableCountry": "RU", "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow", "merchantReturnDays": 14, "returnFees": "https://schema.org/FreeReturn"},
    "shippingDetails": {"@type": "OfferShippingDetails", "shippingRate": {"@type": "MonetaryAmount", "value": "0", "currency": "RUB"}, "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "RU"}, "deliveryTime": {"@type": "ShippingDeliveryTime", "handlingTime": {"@type": "QuantitativeValue", "minValue": 0, "maxValue": 1, "unitCode": "DAY"}, "transitTime": {"@type": "QuantitativeValue", "minValue": 1, "maxValue": 5, "unitCode": "DAY"}}}
  },
  "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.7", "reviewCount": "38"}
}
```
`aggregateRating` — только при реальном функционале оценок, по шкале, по конкретному товару. Услуги — `Product` + `"additionalType": "https://schema.org/Service"` (основной тип Service убирал товары из отчётов GSC).

**Категория (листинг)**
```json
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "Роботы-пылесосы",
  "mainEntity": {
    "@type": "ItemList",
    "itemListElement": [
      {"@type": "ListItem", "position": 1, "url": "https://example.ru/product/s10/"},
      {"@type": "ListItem", "position": 2, "url": "https://example.ru/product/s12/"}
    ]
  }
}
```

**FAQPage** — только если вопросы и ответы видимы на странице, уникальны для неё.
```json
{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
  {"@type": "Question", "name": "Сколько стоит X?", "acceptedAnswer": {"@type": "Answer", "text": "От 2 500 ₽ за м²; итог зависит от площади и материалов."}}
]}
```

Другие полезные: `SearchAction` (поиск по сайту, на главной), `HowTo`, `VideoObject` (своё видео; YouTube-iframe не размечать), `SiteNavigationElement`, `speakable`, `about`/`mentions`.

## 3. Шаблон `<head>`

```html
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Главный ключ + модификатор — УТП | Бренд</title>
  <meta name="description" content="Ответ/выгода с ключом и цифрами, 120–160 символов, призыв.">
  <link rel="canonical" href="https://example.ru/current-page/">
  <link rel="alternate" hreflang="ru" href="https://example.ru/current-page/">
  <link rel="alternate" hreflang="en" href="https://example.ru/en/current-page/">
  <meta property="og:type" content="article">
  <meta property="og:title" content="Заголовок для соцсетей">
  <meta property="og:description" content="Короткое описание">
  <meta property="og:image" content="https://example.ru/og/page-1200x630.jpg">
  <meta property="og:url" content="https://example.ru/current-page/">
  <link rel="preload" as="image" href="/img/hero.webp" fetchpriority="high">
</head>
```
- Canonical — самоссылающийся на всех индексируемых страницах (URL без GET-параметров); это подсказка, держать согласованным с sitemap и коротким URL.
- Картинки: `width`/`height`, `loading="lazy"` ниже первого экрана, `srcset`/`<picture>` (боту — большое, мобильным — лёгкое); для Discover — 16:9, ≥1200 px.
- Ссылки — только `<a href>`, не `onclick`/div. Пагинация — HTML-ссылки даже при автоподгрузке.

## 4. robots.txt и управление индексом

```
User-agent: *
Disallow: /cart/
Disallow: /search/
Disallow: /*?sort=
Disallow: /*&sort=

User-agent: Yandex
Clean-param: utm_source&utm_medium&utm_campaign&utm_content&utm_term&yclid&gclid&from
Disallow: /cart/
Disallow: /search/

Sitemap: https://example.ru/sitemap.xml
```
- Не закрывать CSS/JS. robots.txt запрещает **сканирование, а не индексацию** — закрытые страницы со ссылками попадают в индекс.
- Удалить из индекса: `<meta name="robots" content="noindex">` или заголовок `X-Robots-Tag: noindex` (для PDF/DOC) — при **разрешённом** сканировании; либо код **410**. 404 висит в индексе месяцами; инструмент удаления GSC — временное скрытие.
- **GET-дубли:** полезные параметры (пагинация, востребованные фильтры) → ЧПУ + 301 + замена внутренних ссылок; самореферентный canonical везде; бесполезные → `Clean-param` (Яндекс; склеивает без захода, передаёт показатели) + `noindex` для Google без Disallow; nofollow на ссылки сортировок; ежемесячно проверять «Статистику обхода» Вебмастера по URL с «=». В Вебмастере есть «Настройка GET-параметров».
- Пагинация: страницы индексируются, canonical на себя (лучше `/page/2/`), без ссылок на `?page=1` (первая = корень), на стр. 2+ без SEO-текста, «— страница N» в Title/H1.
- Склейка версий: www/без www, http→https, слеш/без слеша, `index.php` — одна версия, остальные 301.
- AMP в Яндексе закрывать; корзина в индексе Яндекса — обычно из-за «обхода по счётчикам Метрики».
- ИИ-боты (GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended, YandexAdditional) не блокировать, если нужна видимость в нейроответах. `llms.txt` крупные LLM-компании не используют — не приоритет.

## 5. Рендеринг (JS-сайты)

LLM-боты и часто поисковые боты не выполняют JS. Очередь рендеринга Google в десятки раз медленнее голого HTML; сайт на 10 000 страниц без SSR индексируется на ~5–6%.

**Диагностика:** Wappalyzer (Next.js/Nuxt → SSR, вероятно, есть); сохранённая текстовая копия vs видимая страница; GSC «Проверка URL» → live-тест; Rich Results Test; Вебмастер — проверка с JS и без; `curl -A "Googlebot" URL` и поиск ключевых текстов в ответе; скрипт `scripts/seo_page_audit.py` (флаг render).

**Пороги:** полнота индекса <50% или не видно 10–20 важных элементов → нужен SSR. Без SSR можно жить при <100 страниц.

| Вариант | Когда |
|---|---|
| SSR | средние и крупные динамические сайты (каталоги) |
| SSG | до ~1–3 тыс. страниц, редкие обновления |
| ISR | небольшие/средние, перегенерация отдельных страниц |
| Dynamic rendering (ботам — статика) | не рекомендуется: ошибки незаметны до падения |

**ТЗ на SSR:** доказательства, что бот не видит контент; приоритет коробочного решения (Next.js, Nuxt); статика обновляется ≤5–10 мин после правок и совпадает с исходной; корректные коды 404/301 (SPA часто отдают soft 404 со статусом 200); где SSR не нужен (ЛК, корзина, поиск); по каждому типу страниц — список обязательных элементов в HTML: Title/H1, все тексты целиком (частая ошибка — текст до «Читать далее»), перелинковка, **пагинация**, hreflang, микроразметка. Проверять глазами Googlebot, а не Chrome. Мониторинг после каждого релиза, минимум ежемесячно. Сроки: внедрение в магазине 4–6 мес., индексация 80–90% — ещё ~4 мес. → ставить задачу первой.

Next.js (App Router) — метаданные и JSON-LD на сервере:
```tsx
export async function generateMetadata({ params }) {
  const p = await getPage(params.slug);
  return {
    title: p.title,
    description: p.description,
    alternates: { canonical: `https://example.ru/${p.slug}/` },
    openGraph: { title: p.title, images: [p.ogImage] },
  };
}
export default async function Page({ params }) {
  const p = await getPage(params.slug);
  return (
    <article>
      <script type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(p.jsonLd) }} />
      <h1>{p.h1}</h1>
      <div dangerouslySetInnerHTML={{ __html: p.html }} />
    </article>
  );
}
```

## 6. Индексация

- Яндекс индексирует почти всё; Google — с трудом (до 50% страниц, до 70% у крауд-ссылок не в индексе).
- Контроль: «Мониторинг важных страниц» и «Статистика обхода» в Вебмастере, GSC «Просканировано, но не проиндексировано», сверка списка продвигаемых URL с индексом в обе стороны; проверка по фрагменту текста в кавычках (страница должна быть №1 по своему уникальному фрагменту — заодно тест на санкции).
- Ускорение: sitemap.xml с `lastmod` (автообновляемый) в обеих панелях; IndexNow (Яндекс, Bing); Google Indexing API (200 URL/сутки на проект, сразу ставит в индекс, потом часть отсеивается); TG-боты индексации. Проверенная схема: все URL через индексатор → через месяц непопавшие дожать Indexing API → ~92–94%. Новые товары/статьи — блоком на главной.
- Долго не индексируется → тот же контент на новом URL (старый — 301) часто заходит за несколько дней.

IndexNow (Яндекс/Bing) — ключ-файл `https://example.ru/<key>.txt` с содержимым `<key>`:
```python
import requests
requests.post("https://yandex.com/indexnow", json={
    "host": "example.ru", "key": "<key>",
    "keyLocation": "https://example.ru/<key>.txt",
    "urlList": ["https://example.ru/new-page/"]}, timeout=30)
```

## 7. Скорость и мобильность

Mobile-first: контент, которого нет в мобильной версии, не учитывается. Мерить PageSpeed по всем шаблонам (главная, листинг, карточка, статья), сравнивать с топом кластера — достаточно быть лучше конкурентов; не жертвовать функционалом ради 100 баллов. Для статических сайтов — чистый HTML/CSS/JS без CDN (Tailwind CDN, Google Fonts, иконочные шрифты тянут балл вниз; в РФ CDN могут тормозить), иконки — inline SVG, первый экран ≤2–3 с. Проверять доступность хостинга и CDN у разных провайдеров РФ.
