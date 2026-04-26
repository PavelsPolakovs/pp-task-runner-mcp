Финальный объединённый план реализации (пункты 1–5)

Цель
----
Сделать проект `pp-task-runner-mcp` готовым для использования как в Monitor/Claude (через ".claude" кнопку), так и программно (через API `open_menu(description=...)`), при этом требуя от проекта‑потребителя минимальной конфигурации. Сохранить контракт событий: одна JSON‑строка в stdout = одно событие.

Ключевые выводы / пересечения
-----------------------------
- Общая механика: локальный HTTP UI (браузер) + эмит событий в stdout (json per line). Реализовано в `menu_server.py` и модульно в `src/menu_mcp`.
- Monitor (через `.claude`) и programmatic API должны сосуществовать. `.claude` даёт «кнопку» UI в Monitor; programmatic API даёт `open_menu` для кода‑потребителей.
- Формат событий должен быть единым: action (`greet`/`exit`/`close`/`timeout`), name, message и, опционально, timestamp/meta/schema.
- Терминология: заменить «skill» → «task / Main Menu» в UI и в константах (рекомендовано переименование `SKILLS` → `TASKS`).
- Совместимость: programmatic `open_menu` возвращает Python dict; `open_menu_json` / `menu_server.py` печатают JSON строки для Monitor.

Файлы, которые будут добавлены/изменены/удалены
-----------------------------------------------
(конкретно)
- Добавить: `/.claude/commands/pp-task-runner.md` (command: `python3 ./pp_task_runner.py`, params: `persistent=false`, `timeout_ms=300000`, `description="PP Task Runner — Main Menu"`).
- Удалить: `/.claude/commands/select-skill.md`.
- Изменить: `menu_server.py`
  - UI: заголовки и тексты заменить на «Main Menu / Tasks».
  - Переименовать (опционально) `SKILLS` → `TASKS` или поддержать alias.
  - Поддержать чтение таймаута/настроек из env: `MCP_MENU_TIMEOUT`, `MCP_PERSISTENT` (опционально).
- Изменить: `src/menu_mcp/constants.py` — `SKILLS` → `TASKS`, `_MENU_TIMEOUT` оставить/связать с env.
- Изменить: `src/menu_mcp/web.py` — UI тексты (skill→task) и handler factory.
- Изменить: `src/menu_mcp/tools.py` —
  - новое API: `open_menu(description: str | None = None) -> dict` (programmatic),
  - обёртка: `open_menu_json(description: str | None = None) -> str` (для CLI/Monitor adapter),
  - (опционально) поддержка загрузки задач из `task_config.json` или ENV.
- Добавить: entrypoint `pp_task_runner.py` в корне:
  - парсит args (default/open `menu`), запускает `menu_server.py` (для Monitor) или вызывает `open_menu_json` по необходимости.
- Добавить: `examples/open_menu_example.py` — пример programmatic использования и обработки возвращённого dict.
- Добавить (опционально): `task_config.json` — пример внешней конфигурации задач.
- Добавить/обновить: `README.md` — инструкции по Monitor (кнопка), CLI, programmatic API и формат событий.
- Добавить тест: `tests/test_tools_open_menu.py` (мокировать браузер/сервер; проверять возвращаемые dict и JSON).

Контракт событий (schema proposal)
----------------------------------
Каждый event — JSON‑объект, одна строка в stdout. Минимальные поля:
- action: "greet" / "exit" / "close" / "timeout"
- name: (string) — имя выбранного задания (если применимо)
- message: (string) — сообщение/payload (если применимо)
- timestamp: (ISO8601) — опционально
- schema_version: (string) — опционально (для будущих изменений)

Пример: {"action":"greet","name":"Run tests","message":"Started running tests","timestamp":"2026-04-26T12:34:56Z"}

Порядок и последовательность работ (рекомендуемый)
-------------------------------------------------
1) Небольшая подготовка (UI и терминология)
   - Заменить тексты в `menu_server.py` и `src/menu_mcp/web.py` (skill→task, заголовки → «Main Menu / Tasks»).
   - Переименование `SKILLS` → `TASKS` в `src/menu_mcp/constants.py` и добавить alias в `menu_server.py` если нужно плавное переключение.

2) API инструмента (programmatic)
   - Реализовать `open_menu(description=None) -> dict` в `src/menu_mcp/tools.py`.
   - Добавить `open_menu_json(...)` возвращающую JSON string (для Monitor/CLI compatibility).
   - Зарегистрировать оба инструмента через `mcp.tool()` (если MCP server доступен).

3) Entrypoint и .claude
   - Добавить `pp_task_runner.py` (CLI entrypoint) с обработкой аргументов. По умолчанию открывать меню.
   - Добавить/обновить файл `.claude/commands/pp-task-runner.md` (и удалить `select-skill.md`).

4) Конфигурация задач
   - Добавить поддержку чтения `task_config.json` или ENV переменной (если существует) в `src/menu_mcp/constants.py`/`tools.py`.

5) Тесты и документация
   - Написать тесты для `open_menu`/`open_menu_json`.
   - Обновить `README.md` с примерами использования: Monitor, CLI и programmatic.

6) Commit strategy (атомарные коммиты)
   - Commit 1: UI‑тексты + constants rename (skill→task), маленькие изменения в шаблонах.
   - Commit 2: Реализация `open_menu` + `open_menu_json` + регистрация mcp.tools.
   - Commit 3: Добавление entrypoint `pp_task_runner.py` и `.claude/commands/pp-task-runner.md` (удаление select-skill.md).
   - Commit 4: task_config sample + tests + README updates.

Технические замечания и trade‑offs
---------------------------------
- `.claude` — статический манифест: description будет фиксирован, динамику меню реализовать в коде.
- persistent=false: рекомендуемый режим для этого меню (одиночный интерактивный запуск); если потребуется долгоживущий процесс — можно переключиться на persistent=true и скорректировать логику shutdown.
- Programmatic API vs Monitor: programmatic возвращает dict (удобно для вызовов из кода), Monitor ожидает JSON в stdout — сохранить оба варианта.

Тестирование / ручная проверка
-----------------------------
- Локальный: запустить `python3 pp_task_runner.py` — браузер откроется; выбрать задачу; в терминале должна появиться JSON‑строка с event.
- Monitor: после добавления `.claude` проверить, что Monitor/Claude запускает команду и преобразует stdout в уведомления.
- Unit: запуск pytest (новые тесты), мокировать `webbrowser.open` и убедиться, что `open_menu` возвращает ожидаемый dict.

Что я буду делать дальше (по шагам)
-----------------------------------
1. Подготовить патчи/файлы в соответствии с планом (open_menu implementation, entrypoint, .claude file, UI text changes).
2. Создать/протестировать unit‑tests по API `open_menu`.
3. Обновить README и зафиксировать `.claude` в репозитории.
