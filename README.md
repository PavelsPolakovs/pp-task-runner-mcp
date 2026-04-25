# MCP Menu Runner — инструкция по запуску в Cloud Code / claude mcp

Коротко: этот репозиторий содержит минимальный MCP-сервер/меню, который показывает стартовое интерактивное меню (questionary/prompt_toolkit).
Основная точка запуска — `server.py` в корне репозитория. Она добавляет `src` в `PYTHONPATH` и вызывает `src.main`.

Важно про интерактивность
- Меню использует `questionary` / `prompt_toolkit` и требует TTY/stdin для интерактивной работы.
- Если среда запуска (например, менеджер `claude mcp`) не предоставляет TTY и использует stdio как машинный транспорт, интерактивное меню при старте НЕ будет показано. В таком случае можно заранее задать выбор через переменные окружения или вызывать меню вручную позже.

Файлы
- `server.py` — минимальная обёртка для запуска (рекомендуется использовать в командах внешних менеджеров).
- `Makefile` — цель `make run-menu` запускает меню локально.
- `src/menu_mcp_server.py` — логика меню и регистрация инструментов (`get_active_skill`, `reopen_menu`).
- `src/mcp/server/fastmcp.py` — локальный shim FastMCP для тестирования.

Зависимости
Убедитесь, что установлены зависимости из `requirements.txt`:

```bash
pip install --user -r requirements.txt
```

Локальный запуск

```bash
# из корня репозитория
make run-menu
# или
python3 server.py --transport stdio
```

Запуск в Cloud Code / через `claude mcp`

1) Если `claude mcp` (или ваша среда) проксирует TTY и вы получите интерактивный терминал:

```bash
# клонирует публичный репозиторий и запускает обёртку из временной папки
claude mcp add --transport stdio pp-task-runner -- sh -c 'git clone https://gitlab.com/PavelsPolakovs/pp-task-runner-mcp.git /tmp/pp-task-runner-mcp && python /tmp/pp-task-runner-mcp/server.py'
```

2) Если `claude mcp` не предоставляет TTY (stdio используется как машинный транспорт):

- Установите выбор заранее через переменные окружения (non-interactive startup):

```bash
# пример: заранее выбрать Greating (клонируем репозиторий и запускаем из /tmp)
claude mcp add --transport stdio pp-task-runner -- sh -c 'git clone https://gitlab.com/PavelsPolakovs/pp-task-runner-mcp.git /tmp/pp-task-runner-mcp && MCP_SELECTED_NAME=Greating MCP_SELECTED_URL="" PYTHONPATH=/tmp/pp-task-runner-mcp/src python /tmp/pp-task-runner-mcp/server.py --transport stdio'
```

- В этом режиме меню НЕ будет выводиться; активный skill будет установлен из `MCP_SELECTED_NAME`. Если позже у процесса появится TTY, можно вызвать инструмент `reopen_menu` чтобы показать меню вручную.

3) Принудительное попытка показать меню (не рекомендуется в non-TTY):

```bash
# опасно: может не сработать, если нет TTY. Клонируем репозиторий и пробуем запустить с форсированным меню.
claude mcp add --transport stdio pp-task-runner -- sh -c 'git clone https://gitlab.com/PavelsPolakovs/pp-task-runner-mcp.git /tmp/pp-task-runner-mcp && MCP_FORCE_MENU=1 PYTHONPATH=/tmp/pp-task-runner-mcp/src python /tmp/pp-task-runner-mcp/server.py --transport stdio'
```

Рекомендуемый безопасный рабочий поток
- Для интеграции с claude mcp лучше подготовить wrapper `server.py` (он уже присутствует в репозитории). Затем:
  - если хотите интерактивно работать — запускайте в среде, которая даёт TTY (например локально, Docker с `-it`, или k8s-под с `stdin: true` и `tty: true`).
  - если нужно автоматическое добавление в менеджер без TTY — передавайте `MCP_SELECTED_NAME` (и при необходимости `MCP_SELECTED_URL`) в командной строке запуска.

Примеры для Docker / Kubernetes

Docker (локальная проверка с TTY):

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/app/src
ENTRYPOINT ["python3", "server.py", "--transport", "stdio"]

# запустить интерактивно
docker build -t mcp-menu .
docker run -it --rm mcp-menu
```

Kubernetes (под с tty/stdin):

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mcp-menu
spec:
  containers:
  - name: mcp
    image: <your-image>
    command: ["python3","/app/server.py","--transport","stdio"]
    stdin: true
    tty: true
  restartPolicy: Never
```

Советы по отладке
- Если меню не появляется — проверьте, есть ли TTY: `python3 -c 'import sys; print(sys.stdin.isatty())'`.
- Если вы используете non-interactive менеджер, проверьте, что передаёте `MCP_SELECTED_NAME` окружением.
- Посмотрите логи процесса (`stderr/stdout`), там есть диагностические сообщения от FastMCP shim.

Если хотите, я могу добавить флаг `--skill NAME` в `server.py` (чтобы передавать выбор как аргумент), или подготовить пример Docker image / k8s manifest под ваш CI. Что предпочитаете — `--skill` флаг или Docker/manifest сейчас?

