# Conan Enhanced Log Parser

**Language / Язык:** [English](#english) | [Русский](#русский)

Author / Автор: **Wizard** · Discord: https://discord.gg/RuFq3ru · ☕ [Support / Поддержать](https://www.buymeacoffee.com/wizardsurvival)

---

## English

A small Python script that reads the `ConanSandbox.log` of a **Conan Exiles Enhanced (Unreal Engine 5)** dedicated server and posts server events and in-game chat to Discord through webhooks.

**Works with and without the Pippi mod.** 

### Features

- ✅ Server has come online (sent when the world has fully loaded, not right at launch)
- ❌ Server is shutting down
- 💥 Server has crashed (sent instead of the shutdown message, when the crash is caused by an engine error)
- ❗ Player joined / left (character name + Steam ID)
- ⚔️ Player deaths: killed by another player, animal, NPC, by themselves, by something else the server names (e.g. falling), or by an unknown force. Victim and killer names + Steam IDs
- 📣 In-game chat: works **with and without** the Pippi mod, Cyrillic and other languages supported
- Every message text, icon and time format can be changed in `config.py`
- Timezone option, separate webhook for chat, chat channel filter (with Pippi)
- Comments in `config.py` are in Russian and English

### Example output

```
✅ [04:17:11] Server has come online
❗ [04:38:24] Wizard joined the server (STEAM ID: 76561198837452398)
⚔️ [05:29:02] Wizard (STEAM ID: 76561198837452398) was killed by Catty (STEAM ID: 76561198013388251)
📣 [04:45:55] Wizard: hello
❌ [05:30:06] Server is shutting down
```

### Requirements

- Windows (the launcher is a `.cmd` file; the script itself is plain Python)
- [Python 3.8+](https://www.python.org/downloads/) — during installation tick **"Add Python to PATH"**
- Access to the server's `ConanSandbox.log` (the parser runs on the same machine as the server)

### Setup

1. Put `parser.py`, `config.py` and `!Start.cmd` into any folder on the server machine.
2. In Discord: **Channel settings → Integrations → Webhooks → New Webhook → Copy Webhook URL**.
3. Open `config.py` in a text editor (save as UTF-8) and set:
   - `WEBHOOK_URL` — your webhook URL
   - `LOG_PATH` — full path to `ConanSandbox.log`, usually `...\ConanSandbox\Saved\Logs\ConanSandbox.log`
   - `UTC_OFFSET_HOURS` — your timezone offset from UTC (Moscow = `3`)
4. Run `!Start.cmd`. Start the parser **before** the server (or at the same time), otherwise the "server came online" message for that start is missed.

**Keep your webhook URL private** — anyone who has it can post to your channel. Never upload your own edited `config.py` with a real URL to GitHub.

### Configuration highlights (`config.py`)

| Option | What it does |
|---|---|
| `WEBHOOK_URL`, `WEBHOOK_NAME`, `WEBHOOK_AVATAR_URL` | Webhook and how the bot appears |
| `LOG_PATH` | Path to `ConanSandbox.log` (a folder path also works) |
| `UTC_OFFSET_HOURS`, `TIME_FORMAT` | Timezone and time format |
| `SHOW_TIME`, `TIME_PREFIX` | Show/hide time in event messages and how it looks |
| `MSG_*` | Text of every event message (placeholders: `{player}`, `{steam_id}`, `{killer}`, `{killer_steam_id}`, `{time_prefix}`) |
| `NPC_NAMES` | Your own names for NPCs and animals (e.g. translations) |
| `CHAT_ENABLED`, `CHAT_WEBHOOK_URL`, `CHAT_CHANNELS`, `CHAT_SHOW_TIME`, `MSG_CHAT` | Chat forwarding, separate chat webhook, channel filter, chat format |

Russian texts example:

```python
MSG_PLAYER_JOIN = "❗ {time_prefix}{player} зашёл на сервер (STEAM ID: {steam_id})"
MSG_SERVER_ONLINE = "✅ {time_prefix}Сервер загрузился"
```

### Dry run (no Discord needed)

```
python parser.py --replay ConanSandbox.log
```

Prints everything the parser would send, without sending anything.

### How it works and limitations

- On start the parser reads the existing log once **without sending** (to learn who is online and their Steam IDs), then follows new lines. Events that happened before the parser started are not sent.
- "Server has come online" is sent at the first `Status report` line, i.e. when the world has really finished loading. This is usually 1–6 minutes after launch, depending on your server and mods.
- Chat is read from the game's own `ChatWindow` log lines (works without mods) and, if the Pippi mod is installed, from its `PippiChat` lines. Only Pippi writes the chat channel name to the log, so `{channel}` and the `CHAT_CHANNELS` filter work only with Pippi; without it all chat is forwarded.
- Server crashes leave no shutdown entry in the log, so no message is sent for them (not supported yet).
- Killers that are not players are shown by their internal names, made readable automatically; use `NPC_NAMES` to rename them.

### Support the author

If the parser is useful to you, you can support its development:

- ☕ Buy Me a Coffee: https://www.buymeacoffee.com/wizardsurvival
- PayPal: wizard.give@gmail.com

### License

MIT — see [LICENSE](LICENSE).

---

## Русский

Небольшой скрипт на Python, который читает `ConanSandbox.log` выделенного сервера **Conan Exiles Enhanced (Unreal Engine 5)** и отправляет события сервера и чат игры в Discord через вебхуки.

**Работает и с модом Pippi, и без него.** 

### Возможности

- ✅ Сервер загрузился (сообщение приходит, когда мир полностью загрузился, а не сразу после запуска)
- ❌ Сервер останавливается
- 💥 Сервер упал (приходит вместо сообщения об остановке, если причина - ошибка движка)
- ❗ Игрок зашёл / вышел (ник персонажа + Steam ID)
- ⚔️ Смерти игроков: убит другим игроком, животным, NPC, самим собой, чем-то ещё, что назвал сервер (например, падение), или неизвестной силой. Ники и Steam ID погибшего и убийцы
- 📣 Чат игры: работает **и с модом Pippi, и без него**, кириллица и другие языки поддерживаются
- Тексты всех сообщений, значки и формат времени меняются в `config.py`
- Настройка часового пояса, отдельный вебхук для чата, фильтр каналов чата (с Pippi)
- Комментарии в `config.py` на русском и английском

### Пример

```
✅ [04:17:11] Server has come online
❗ [04:38:24] Wizard joined the server (STEAM ID: 76561198837452398)
⚔️ [05:29:02] Wizard (STEAM ID: 76561198837452398) was killed by Catty (STEAM ID: 76561198013388251)
📣 [04:45:55] Wizard: привет
❌ [05:30:06] Server is shutting down
```

По умолчанию тексты английские; на русский их можно заменить в `config.py` (пример ниже).

### Требования

- Windows (запуск через `.cmd`-файл; сам скрипт — обычный Python)
- [Python 3.8+](https://www.python.org/downloads/) — при установке отметь галочку **«Add Python to PATH»**
- Доступ к `ConanSandbox.log` сервера (парсер запускается на той же машине, где сервер)

### Установка

1. Положи `parser.py`, `config.py` и `!Start.cmd` в любую папку на машине с сервером.
2. В Discord: **Настройки канала → Интеграции → Вебхуки → Новый вебхук → Копировать URL вебхука**.
3. Открой `config.py` в текстовом редакторе (сохраняй в UTF-8) и укажи:
   - `WEBHOOK_URL` — ссылка вебхука
   - `LOG_PATH` — полный путь к `ConanSandbox.log`, обычно `...\ConanSandbox\Saved\Logs\ConanSandbox.log`
   - `UTC_OFFSET_HOURS` — смещение твоего часового пояса от UTC (Москва = `3`)
4. Запусти `!Start.cmd`. Запускай парсер **до** сервера (или одновременно с ним), иначе сообщение «сервер загрузился» для этого запуска будет пропущено.

**Не показывай ссылку вебхука посторонним:** любой, у кого она есть, может писать в твой канал. Не загружай на GitHub свой `config.py` с настоящей ссылкой.

### Основные настройки (`config.py`)

| Параметр | Что делает |
|---|---|
| `WEBHOOK_URL`, `WEBHOOK_NAME`, `WEBHOOK_AVATAR_URL` | Вебхук и как выглядит бот |
| `LOG_PATH` | Путь к `ConanSandbox.log` (можно указать и папку) |
| `UTC_OFFSET_HOURS`, `TIME_FORMAT` | Часовой пояс и формат времени |
| `SHOW_TIME`, `TIME_PREFIX` | Показывать ли время в сообщениях о событиях и как оно выглядит |
| `MSG_*` | Текст каждого сообщения (метки: `{player}`, `{steam_id}`, `{killer}`, `{killer_steam_id}`, `{time_prefix}`) |
| `NPC_NAMES` | Свои названия NPC и животных (например, перевод) |
| `CHAT_ENABLED`, `CHAT_WEBHOOK_URL`, `CHAT_CHANNELS`, `CHAT_SHOW_TIME`, `MSG_CHAT` | Пересылка чата, отдельный вебхук, фильтр каналов, формат чата |

Пример русских текстов:

```python
MSG_PLAYER_JOIN = "❗ {time_prefix}{player} зашёл на сервер (STEAM ID: {steam_id})"
MSG_SERVER_ONLINE = "✅ {time_prefix}Сервер загрузился"
```

### Проверка без Discord

```
python parser.py --replay ConanSandbox.log
```

Выводит в консоль всё, что парсер отправил бы, ничего не отправляя.

### Как работает и ограничения

- При запуске парсер один раз читает существующий лог **без отправки** (чтобы узнать, кто онлайн, и запомнить Steam ID), затем следит за новыми строками. События до запуска парсера не отправляются.
- «Сервер загрузился» отправляется по первой строке `Status report`, то есть когда мир действительно догрузился. Обычно это через 1–6 минут после запуска, в зависимости от сервера и модов.
- Чат берётся из собственных строк игры `ChatWindow` (работает без модов) и, если установлен мод Pippi, из его строк `PippiChat`. Название канала чата в лог пишет только Pippi, поэтому `{channel}` и фильтр `CHAT_CHANNELS` работают только с Pippi; без него пересылается весь чат.
- При краше сервера в логе нет записи об остановке, поэтому сообщения о нём нет (пока не поддерживается).
- Убийцы, не являющиеся игроками, показываются по внутренним названиям, автоматически приведённым к читаемому виду; переименовать их можно в `NPC_NAMES`.

### Поддержать автора

Если парсер вам полезен, можно поддержать его развитие:

- ☕ Buy Me a Coffee: https://www.buymeacoffee.com/wizardsurvival
- PayPal: wizard.give@gmail.com

### Лицензия

MIT — см. [LICENSE](LICENSE).

---

**Author / Автор:** Wizard · **Discord:** https://discord.gg/RuFq3ru
