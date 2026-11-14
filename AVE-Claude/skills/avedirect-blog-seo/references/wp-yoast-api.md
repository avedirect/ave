# Yoast Bulk Editor API на avedirect.ru

## Список статей

```
GET /wp-json/yoast/v1/bulk_editor/posts?content_type=articles&per_page=100&page={n}
```

Поля поста: `id`, `title`, `seo_title`, `meta_description`, fallbacks, `needs_improvement`.

Если `seo_title` / `meta_description` пустые — в сниппет уходит `%%title%% %%sep%% %%sitename%%` (длинный слоган сайта). Это нужно заполнять даже когда `needs_improvement.seo_title = false`.

## Обновление

```
POST /wp-json/yoast/v1/bulk_editor/update_search
{ "items": [ { "id": 1, "seo_title": "...", "meta_description": "..." } ] }
```

Успех: `results[].success = true` и `rendered`.

## Контент

```
GET/POST /wp-json/wp/v2/articles/{id}
```

Beget: заголовок `Cookie: beget=begetok` обязателен вместе с Basic Auth.
