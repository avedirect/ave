# AVE — долговременная память агента

## Кто мы

- **AVE Direct** — агентство контекстной рекламы (Яндекс Директ), сайт https://avedirect.ru/
- **Ave Design** — дизайн-студия, сайт https://avedesign.ru/
- Владелец / основной контакт: Александр Евстигнеев (`avedesign@gmail.com`)

## Блог AVE Direct

- CPT: `articles`, REST `/wp-json/wp/v2/articles`
- Рубрики `articles-cat`: Яндекс Директ = 28, Маркетинг = 35 и др.
- SEO: ВИСП + GEO, Yoast Bulk Editor API (не REST `meta._yoast_*`)
- Хостинг Beget: cookie `beget=begetok` + Application Password в `WP_AUTH`
- Body SEO (intro + Коротко + FAQ + links + CTA + Yoast) по planned cats **закрыт** к 2026-10-17; cumulative ≈ 2517; см. `blog-seo-resume.md`

## Скиллы — когда что брать

| Задача | Skill |
|---|---|
| Директ, Метрика, офферы, аудиты кабинета | `yandex-direct-offers` |
| SEO/GEO статьи, техаудит, микроразметка | `seo-geo-promotion` |
| Статьи блога avedirect.ru + Yoast | `avedirect-blog-seo` |
| Кейсы маркетолога / агентства | `marketing-case-writer` |
| UI/UX лендинги, палитры, типографика | `ui-ux-pro-max` |

## Правила из site-factory

Упоминаются в `avedirect-blog-seo`: rules `05-seo-geo` и `06-blog-visp` (ВИСП, GEO, мета).  
**Файлы rules ещё не импортированы** — лежат в локальном AVE-Claude / site-factory. После получения папки положить в `AVE-Claude/rules/`.

## Проекты в репозитории

| Папка | Суть |
|---|---|
| `projects/kurs-svyazka` | Сайт курса «Связка» по Яндекс Директу |
| `projects/hyliox-portfolio` | Vite/React лендинг портфолио Hyliox |
| `projects/fir-design` | Лендинг Fir Design (ремонт квартир, Tilda-экспорт) |
| `projects/tesla-future-lab` | TESLA FUTURE LAB — анимированный лендинг |

## Секреты

Никогда не коммитить: `WP_AUTH`, Application Passwords, FTP, токены Директа/Метрики/GSC.  
Держать в Cursor Secrets / env.
