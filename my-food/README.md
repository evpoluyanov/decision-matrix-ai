# Моя еда — публикация на Cloudflare

Этот каталог независим от проекта Decision Matrix AI. Публикация на production пока **не выполнена**.

## Состав

- `worker/worker.js` — Worker v1.14, Cloudflare Workers AI; `worker/wrangler.toml` — конфигурация существующего `food-ai-inference`.
- `site/` — PWA v0.9.11, статические файлы для существующего проекта Cloudflare Pages `drop-443886b1-4e5`.
- `.github/workflows/deploy-my-food.yml` — CI/CD: после изменения файлов в `my-food/` сначала Worker, затем Pages. Если изменился только один компонент, публикуется только он. Можно запустить вручную (workflow_dispatch).

## Однократная настройка (выполняется владельцем аккаунта)

1. В Cloudflare: создать **ограниченный по аккаунту** API token с правами **Workers Scripts: Edit** и **Cloudflare Pages: Edit**, нужными для этих двух проектов (не давать Global API Key). Убедиться, что у существующего Worker есть Workers AI binding `AI`.
2. В GitHub: репозиторий → Settings → Secrets and variables → Actions → New repository secret. Добавить ровно два секрета: `CLOUDFLARE_ACCOUNT_ID` и `CLOUDFLARE_API_TOKEN`. Значения никому не отправлять и в файлы не включать.
3. После публикации ветки `main` выполнить `Actions → Deploy My Food to Cloudflare → Run workflow`. Проверить статусы обоих этапов и адреса сайта/Worker, в том числе `/health` у Worker.
4. В Cloudflare Pages проверить, что **production branch** называется `main`. Если другое имя — изменить `--branch=main` в workflow на фактическую production branch.

**Предупреждение:** существующий `decision-matrix-ai` — публичный репозиторий. Код `Моя еда` после слияния будет публично виден. Ни ключи, ни личные данные пользователя в проект помещать нельзя. Код Worker сейчас показывает ознакомительный публичный API без аутентификации; ограничение доступа нужно решить отдельно.

**Не объединять ветку без предварительной настройки секретов**, иначе задача CI/CD не сможет развернуть код. Слияние также может запустить несвязанные существующие deployment-настройки другого проекта.
