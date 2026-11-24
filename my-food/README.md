# «Моя еда»: автоматическая публикация в Cloudflare

**Состояние:** на 22.11.2026 GitHub Actions успешно опубликовал обе версии — PWA **v0.9.11**, API Worker **v1.14**. Успешный запуск: https://github.com/evpoluyanov/decision-matrix-ai/actions/runs/45019959952.

## Развёртывание (оба — Cloudflare Workers, не Cloudflare Pages)

- `my-food/worker/worker.js`: backend Worker `food-ai-inference`, binding Workers AI `AI`, доступен по `https://food-ai-inference.evpoluyanov.workers.dev`. Конфигурация `my-food/worker/wrangler.toml`.
- `my-food/site/`: PWA; раздаётся из **Worker со статическими ассетами** `drop-443886b1-4e5`, `https://drop-443886b1-4e5.evpoluyanov.workers.dev`. Конфигурация `my-food/site-worker/wrangler.toml`.
- `.github/workflows/deploy-my-food.yml`: автоматически публикует только изменившиеся части. Если изменились оба — сначала backend, потом пользовательское приложение. Проверяет синтаксис перед публикацией.

## Ветка, из которой выполняются публикации

**Только `codex/my-food-cloudflare-cicd`.** Изменения исходников «Моя еда» необходимо коммитить и пушить именно в эту ветку. Подключённая GitHub Actions публикация запускается по push при изменениях `my-food/**` (или самого workflow). После публикации необходимо проверять статус в Actions.

**Не сливать ветку в `main` репозитория `decision-matrix-ai`** без отдельной подготовки. Этот репозиторий содержит другой работающий проект с независимым Vercel Production deployment; его `main` не должен затрагиваться обновлениями «Моей еды».

## Секреты

В GitHub `Settings → Secrets and variables → Actions → Repository secrets` должны быть:
- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_TOKEN` с минимально необходимыми правами для публикации Workers.

Значения секретов **никогда не помещать в git, документы, сообщения или исходный код**. Токен при необходимости заменяется в GitHub Secrets; текущие значения недоступны через подключённый GitHub-инструмент.

## Контроль после публикации

- Открыть `https://food-ai-inference.evpoluyanov.workers.dev/health`; должен возвращаться `ok:true`, `ai_binding:true` и ожидаемая версия.
- Открыть `https://drop-443886b1-4e5.evpoluyanov.workers.dev`; должна отобразиться новая версия PWA.
- Проверить распознавание в приложении на iPhone. Прохождение GitHub Actions подтверждает публикацию, но не заменяет проверку реального сценария.

Репозиторий `decision-matrix-ai` **публичный**: код приложения и Worker в этой ветке доступен для просмотра. В перспективе рекомендуется перенести «Мою еду» в отдельный приватный репозиторий без смешивания с другим проектом.
