# -*- coding: utf-8 -*-
# =============================================================================
#  Conan Enhanced Log Parser v1.0
#  Автор / Author: Wizard
#  Discord: https://discord.gg/RuFq3ru
#  RU: Вопросы, помощь и обратная связь - в Discord автора.
#  EN: Questions, help and feedback - in the author's Discord.
#  Поддержать автора / Support the author:
#     https://www.buymeacoffee.com/wizardsurvival
#     PayPal: wizard.give@gmail.com
# =============================================================================
# =============================================================================
#  НАСТРОЙКИ ПАРСЕРА / PARSER SETTINGS
#  Меняйте только значения справа от "=" / Edit only the values right of "="
#  Сохраняйте файл в кодировке UTF-8 / Save this file as UTF-8
# =============================================================================

# -----------------------------------------------------------------------------
# 1. ВЕБХУК DISCORD / DISCORD WEBHOOK
# RU: Вставьте ссылку вебхука: Настройки канала -> Интеграции -> Вебхуки ->
#     "Копировать URL вебхука". Никому не показывайте эту ссылку!
# EN: Paste your webhook URL: Channel settings -> Integrations -> Webhooks ->
#     "Copy Webhook URL". Never share this URL with anyone!
# -----------------------------------------------------------------------------
WEBHOOK_URL = "PASTE_YOUR_WEBHOOK_URL_HERE"

# RU: Имя, под которым бот пишет в канал. Пусто "" = имя, заданное в самом вебхуке.
# EN: Name the bot posts under. Empty "" = use the name set in the webhook itself.
WEBHOOK_NAME = ""

# RU: Ссылка на аватар бота. Пусто "" = аватар вебхука.
# EN: Bot avatar image URL. Empty "" = use the webhook's own avatar.
WEBHOOK_AVATAR_URL = ""

# -----------------------------------------------------------------------------
# 2. ЛОГ-ФАЙЛ СЕРВЕРА / SERVER LOG FILE
# RU: Полный путь к ConanSandbox.log. Пример:
#     r"C:\Servers\Conan\ConanSandbox\Saved\Logs\ConanSandbox.log"
#     Если файл лежит рядом с parser.py, можно оставить просто имя файла.
# EN: Full path to ConanSandbox.log. Example above.
#     If the file is next to parser.py you can leave just the file name.
# -----------------------------------------------------------------------------
LOG_PATH = r"ConanSandbox.log"

# -----------------------------------------------------------------------------
# 3. ВРЕМЯ / TIME
# RU: Часовой пояс: смещение от UTC в часах. Москва = 3, Киев = 2 (зима) / 3 (лето),
#     Берлин = 1 (зима) / 2 (лето), Нью-Йорк = -5 (зима) / -4 (лето), Индия = 5.5.
#     Лог сервера пишет время в UTC, парсер переводит его в ваш пояс.
# EN: Timezone: offset from UTC in hours. Moscow = 3, Berlin = 1 (winter) / 2 (summer),
#     New York = -5 (winter) / -4 (summer), India = 5.5.
#     The server log stores UTC time, the parser converts it to your timezone.
# -----------------------------------------------------------------------------
UTC_OFFSET_HOURS = 3

# RU: Формат времени в сообщениях (стандарт Python strftime).
# EN: Time format used in messages (Python strftime syntax).
TIME_FORMAT = "%H:%M:%S"   # RU: с датой / EN: with date: "%d.%m.%Y %H:%M:%S"

# RU: Показывать дату-время в сообщениях о событиях (запуск, вход, выход, смерть)?
#     True = показывать, False = не показывать.
# EN: Show date-time in event messages (start, join, leave, death)?
#     True = show, False = hide.
SHOW_TIME = True

# RU: Как выглядит время перед сообщением. Метка {time} - дата-время по формату выше.
#     Хотите серый "код"-фон как раньше - напишите "`{time}` " (с обратными кавычками).
# EN: How the time looks in front of the message. {time} is the date-time in the format above.
#     For the grey "code" background use "`{time}` " (with backticks).
TIME_PREFIX = "[{time}] "

# RU: Как часто проверять лог (секунды).
# EN: How often to check the log (seconds).
POLL_INTERVAL = 1.0

# -----------------------------------------------------------------------------
# 4. ТЕКСТЫ СООБЩЕНИЙ / MESSAGE TEXTS
# RU: Меняйте текст как хотите. Значки (эмодзи) тоже можно менять или убрать.
#     Можно использовать эти метки, они заменяются автоматически:
#       {time_prefix}      - время в начале (по TIME_PREFIX; пусто, если SHOW_TIME = False)
#       {time}             - просто время события, без оформления
#       {player}           - ник игрока (для смерти - погибшего)
#       {steam_id}         - Steam ID игрока (для смерти - погибшего)
#       {killer}           - убийца (ник игрока, животное или NPC)
#       {killer_steam_id}  - Steam ID убийцы (только если убил игрок)
#     Ненужные метки можно удалять. Текст по умолчанию - английский.
# EN: Change the text freely. Icons (emoji) can be changed or removed too.
#     These placeholders are replaced automatically (see list above).
#     You can delete placeholders you do not need. Default text is English.
#
# RU: Пример на русском / EN: Russian example:
#     MSG_PLAYER_JOIN = "❗ {time_prefix}{player} зашёл на сервер (STEAM ID: {steam_id})"
# -----------------------------------------------------------------------------

# RU: Сервер загрузился. Сообщение приходит, когда сервер РЕАЛЬНО готов (после полной
#     загрузки мира, в логе - первый "Status report"), а не сразу после запуска.
#     Обычно это на 1-6 минут позже старта, в зависимости от сервера и модов.
# EN: Server finished loading. Sent when the server is REALLY ready (world fully loaded,
#     in the log: the first "Status report"), not right after launch.
#     Usually 1-6 minutes after start, depending on your server and mods.
MSG_SERVER_ONLINE = "✅ {time_prefix}Server has come online"

# RU: Сервер останавливается (выключение, перезагрузка). Сообщение придёт один раз.
#     Если сервер упал (краш), в логе нет записи об остановке - сообщения не будет.
# EN: Server is shutting down (stop, restart). Sent once per shutdown.
#     If the server crashes, the log has no shutdown entry - no message will be sent.
MSG_SERVER_OFFLINE = "❌ {time_prefix}Server is shutting down"

# RU: Сервер упал (краш, не обычная остановка). Сообщение придёт один раз, ВМЕСТО
#     обычного MSG_SERVER_OFFLINE (оно для этого же завершения работы не отправляется).
# EN: Server crashed (not a normal shutdown). Sent once, INSTEAD of the usual
#     MSG_SERVER_OFFLINE (that one is not sent for the same shutdown).
MSG_SERVER_CRASHED = "💥 {time_prefix}Server has crashed"

# RU: Игрок зашёл / EN: Player joined
MSG_PLAYER_JOIN = "❗ {time_prefix}{player} joined the server (STEAM ID: {steam_id})"

# RU: Игрок вышел / EN: Player left
MSG_PLAYER_LEAVE = "❗ {time_prefix}{player} left the server (STEAM ID: {steam_id})"

# RU: Убит другим игроком / EN: Killed by another player
MSG_KILLED_BY_PLAYER = ("⚔️ {time_prefix}{player} (STEAM ID: {steam_id}) was killed by "
                        "{killer} (STEAM ID: {killer_steam_id})")

# RU: Убит животным / EN: Killed by an animal
MSG_KILLED_BY_ANIMAL = "⚔️ {time_prefix}{player} (STEAM ID: {steam_id}) was killed by {killer}"

# RU: Убит NPC / EN: Killed by an NPC
MSG_KILLED_BY_NPC = "⚔️ {time_prefix}{player} (STEAM ID: {steam_id}) was killed by {killer}"

# RU: Убит чем-то ещё, что назвал сервер: падение (falling), утопление и т.п.
#     {killer} = причина так, как её написал сервер.
# EN: Killed by something else the server named: falling, drowning, etc.
#     {killer} = the cause as written by the server.
MSG_KILLED_BY_OTHER = "⚔️ {time_prefix}{player} (STEAM ID: {steam_id}) was killed by {killer}"

# RU: Убит неизвестной силой (падение, вода, яд и т.п. - сервер не назвал убийцу)
# EN: Killed by an unknown force (fall, drowning, poison, etc. - no killer given by the server)
MSG_KILLED_BY_UNKNOWN = "⚔️ {time_prefix}{player} (STEAM ID: {steam_id}) was killed by an unknown force"

# RU: Игрок убил сам себя (кнопка "убить персонажа") / EN: Player killed themselves (suicide)
MSG_KILLED_BY_SUICIDE = "⚔️ {time_prefix}{player} (STEAM ID: {steam_id}) was killed by themselves"

# -----------------------------------------------------------------------------
# 5. НАЗВАНИЯ NPC И ЖИВОТНЫХ / NPC AND ANIMAL NAMES
# RU: Сервер пишет убийц как NPC_PREFIX_Wildlife_Sabretooth. Парсер сам делает
#     из этого "Sabretooth". Чтобы задать своё название (например, на русском),
#     добавьте строку: "внутреннее имя из лога": "Ваше название",
# EN: The server logs killers as NPC_PREFIX_Wildlife_Sabretooth. The parser turns
#     that into "Sabretooth" by itself. To set your own name (e.g. translated),
#     add a line: "internal name from the log": "Your name",
# -----------------------------------------------------------------------------
NPC_NAMES = {
    # "NPC_PREFIX_Wildlife_Sabretooth": "Саблезубый тигр",
    # "NPC_PREFIX_EAAWildlife_Rhino_Feral": "Дикий носорог",
}

# =============================================================================
# 6. ЧАТ ИГРЫ / IN-GAME CHAT
# RU: Парсер читает чат из лога. Работает и БЕЗ мода Pippi (обычные строки ChatWindow),
#     и С модом Pippi (ChatWindow + PippiChat). С модом каждое сообщение записано в логе
#     дважды - парсер отправляет его в Discord только один раз. В обоих случаях сообщение
#     выглядит одинаково: только ник игрока, без служебных скобок (uid, player).
# EN: The parser reads chat from the log. It works WITHOUT the Pippi mod (plain ChatWindow
#     lines) and WITH Pippi (ChatWindow + PippiChat). With Pippi every message is written
#     twice in the log - the parser sends it to Discord only once. Either way the message
#     looks the same: just the player's name, without the technical (uid, player) part.
# =============================================================================

# RU: True = отправлять чат в Discord, False = не отправлять.
# EN: True = send chat to Discord, False = do not send.
CHAT_ENABLED = True

# RU: Вебхук для чата. Пусто "" = чат идёт в тот же канал, что и события (WEBHOOK_URL).
#     Чтобы чат шёл в ДРУГОЙ канал - создайте там второй вебхук и вставьте его ссылку.
# EN: Webhook for chat. Empty "" = chat goes to the same channel as events (WEBHOOK_URL).
#     To send chat to a DIFFERENT channel - create a second webhook there and paste its URL.
CHAT_WEBHOOK_URL = ""

# RU: Имя и аватар бота для чата. Пусто "" = как у вебхука.
# EN: Bot name and avatar for chat. Empty "" = as set in the webhook.
CHAT_WEBHOOK_NAME = ""
CHAT_WEBHOOK_AVATAR_URL = ""

# RU: Какие каналы чата пересылать. [] = все. Пример: ["Global"] = только общий чат.
#     Названия каналов есть в логе только с модом Pippi. Без Pippi канал неизвестен,
#     поэтому фильтр не применяется и пересылается весь чат.
# EN: Which chat channels to forward. [] = all. Example: ["Global"] = global chat only.
#     Channel names are in the log only with the Pippi mod. Without Pippi the channel is
#     unknown, so the filter is not applied and all chat is forwarded.
CHAT_CHANNELS = []

# RU: Формат времени в строке чата. Здесь только часы:минуты:секунды, как в Pippi.
# EN: Time format for chat lines. Hours:minutes:seconds only, like Pippi.
CHAT_TIME_FORMAT = "%H:%M:%S"

# RU: Показывать время в строке чата? True = да, False = нет.
# EN: Show time in chat lines? True = yes, False = no.
CHAT_SHOW_TIME = True

# RU: Оформление времени в чате. {time} - время по CHAT_TIME_FORMAT.
# EN: Time styling in chat. {time} is the time in CHAT_TIME_FORMAT.
CHAT_TIME_PREFIX = "[{time}] "

# RU: Текст сообщения чата. Метки: {time_prefix} {time} {player} {message} {channel} {steam_id}
# EN: Chat message text. Placeholders: {time_prefix} {time} {player} {message} {channel} {steam_id}
MSG_CHAT = "📣 {time_prefix}{player}: {message}"
