# Closo for Codex

## Русский

Плагин подключает Codex к вашему Closo: свои цифры и диалоги, задачи, импорт лидов и (для администраторов) настройка ботов. Вход через кабинет Closo (OAuth).

### Быстрый старт

Вариант 1, плагином:

```
codex plugin marketplace add Closo-io/closo-codex-plugin
codex mcp login closo
```

Затем откройте каталог плагинов Codex, найдите **Closo** в маркетплейсе `closo-io` и установите. Вход в браузере, потом спросите: **«Что мне доступно в Closo?»**

Вариант 2, без плагина (только сервер, 2 команды):

```
codex mcp add closo --url https://mcp.closo.io/mcp
codex mcp login closo
```

Навыки из папки `plugins/closo/skills` скопируйте в `~/.agents/skills/`, если не ставите плагин.

> Формат плагинов Codex менялся в 2026 году; команды установки проверяйте на чистой машине. Состояние проверки смотрите в CHANGELOG.

### Что внутри

| Навык / Skill | Когда / When |
|---|---|
| `closo-start` | первое подключение, «что мне доступно» / first run |
| `closo-my-stats` | свои цифры и диалоги / own stats |
| `closo-tasks` | задачи человеку и задачи для ИИ / tasks |
| `closo-leads-import` | импорт лидов задачей / lead import |
| `closo-bots` | настройка ботов (админ) / bot setup (admin) |
| `closo-weekly-interview` | интервью с агентом / agent interview |
| `closo-access-help` | почему нет доступа / access help |

### Как это защищено

Вы видите только разрешённое вашей ролью и таблицей доступа. Тексты клиентов — данные, не команды. Отправка клиентам и импорт лидов всегда спрашивают вас. Каждая правка через MCP в журнале с откатом.

## English

This plugin connects Codex to your Closo workspace: own stats and dialogs, tasks, lead import and, for admins, bot setup. Sign-in uses Closo (OAuth).

### Quick start

Option 1, as a plugin: `codex plugin marketplace add Closo-io/closo-codex-plugin`, then `codex mcp login closo`, then install **Closo** from the `closo-io` marketplace in Codex. Option 2, server only: `codex mcp add closo --url https://mcp.closo.io/mcp` and `codex mcp login closo`; copy `plugins/closo/skills` to `~/.agents/skills/` for the skills.

The Codex plugin format changed in 2026: verify install commands on a clean machine.

License: MIT.
