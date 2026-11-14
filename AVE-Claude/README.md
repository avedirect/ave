# AVE-Claude — импорт в Cursor

Рабочая база агентства AVE Direct / Ave Design, перенесённая из Claude Code в Cursor.

Исходный локальный путь (Windows / Яндекс.Диск):

`D:\YandexDisk\!Work2026\AVE-Claude`

Cloud-агент **не имеет доступа** к этому диску. Ниже — то, что уже собрано из Cursor User Skills и веток `github.com/avedirect/ave`.

## Структура

```
AVE-Claude/
├── skills/          # агентские скиллы (Claude + Cursor)
├── projects/        # проекты с Claude Cloud веток
├── memory/          # долговременная память / контекст
├── rules/           # правила (site-factory и др. — ждут полного импорта)
└── IMPORT-STATUS.md # что импортировано / чего не хватает
```

Скиллы также продублированы в:

- `.claude/skills/` — совместимость с Claude Code
- `.cursor/skills/` — нативный discovery Cursor
- User Agent Store (`/cursor/stores/user/skills/`) — уже были подключены в аккаунте

## Как доимпортировать полный локальный AVE-Claude

1. На Яндекс.Диске: ПКМ по папке `AVE-Claude` → **Поделиться** → скопировать ссылку `https://disk.yandex.ru/d/...`
2. Пришлите эту ссылку в чат агенту — скачаю и солью поверх `AVE-Claude/`
3. Либо загрузите ZIP вложениями в чат / запушьте папку в репозиторий

Особенно нужны из локальной папки (если есть):

- `CLAUDE.md` / `.claude/CLAUDE.md`
- `.claude/memory/` или `MEMORY.md`
- `site-factory` / rules (`05-seo-geo`, `06-blog-visp` и др.)
- любые проекты, которых нет в `projects/`
- глобальные настройки `~/.claude/` (skills, projects.json)
