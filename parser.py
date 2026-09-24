# -*- coding: utf-8 -*-
"""
Conan Enhanced Log Parser v1.1
Author / Автор: Wizard
Discord: https://discord.gg/RuFq3ru

Conan Exiles Enhanced (Unreal Engine 5) -> Discord log parser
Логпарсер Conan Exiles Enhanced (Unreal Engine 5) -> Discord

RU: Читает ConanSandbox.log в реальном времени и отправляет в Discord (через вебхук):
    запуск сервера, вход/выход игроков, смерти. Все настройки и тексты - в config.py.
EN: Reads ConanSandbox.log in real time and sends to Discord (via webhook):
    server start, player join/leave, deaths. All settings and texts are in config.py.

Запуск / Run:  !Start.cmd   (или / or)   python parser.py
Проверка без отправки / Dry run without sending:  python parser.py --replay ConanSandbox.log
"""
import json
import os
import queue
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

import config

VERSION = "1.0"
AUTHOR = "Wizard"
DISCORD = "https://discord.gg/RuFq3ru"

# ------------------------------------------------------------------ regexes --
# RU: Шаблоны строк лога. EN: Log line patterns.
RE_TS = re.compile(r"^\[(\d{4})\.(\d{2})\.(\d{2})-(\d{2})\.(\d{2})\.(\d{2}):\d+\]")
RE_CHAT_WINDOW = re.compile(r"\]ChatWindow: Character (.+?) said: (.*)$")
RE_CHAT_NAME = re.compile(r"^(.*) \(uid \d+, player (\d+)\)$")   # vanilla: "Name (uid 126, player 7656...)"
RE_CHAT_PIPPI = re.compile(r"\]PippiChat: (.+?) said in channel \[(.*?)\]: (.*)$")
CHAT_WAIT = 3.0   # RU: сек. ждать строку PippiChat / EN: seconds to wait for the PippiChat line
RE_STARTUP = re.compile(r"LogServerStats: Startup report")
RE_LOGIN = re.compile(r"LogNet: Login request: userId: STEAM:(\d+)")
RE_JOIN = re.compile(r"LogNet: Join succeeded: (.+?)\s*$")
RE_DISC = re.compile(r"LogNet: Player disconnected: (.+?)\s*$")
RE_CHAR = re.compile(r"ConanSandbox: Display: Character ID \d+ has name (.+?) and guild ID")
RE_KILL = re.compile(
    r"KillCharacterWithRagdoll_Implementation\. KillerNameInput: (.*?) CauseOfDeath: (\S*)\. "
    r"IsThrall: (\d+) Name: (\S+) CharacterName: (.*?)\s*$")

JOIN_WAIT = timedelta(seconds=15)     # RU: ждать ник персонажа / EN: wait for character name
PENDING_LOGIN_TTL = timedelta(minutes=10)

TZ = timezone(timedelta(hours=config.UTC_OFFSET_HOURS))


def fmt_time(dt_utc):
    """RU: время UTC -> ваш пояс. EN: UTC time -> your timezone."""
    return dt_utc.astimezone(TZ).strftime(config.TIME_FORMAT)


def time_prefix(dt_utc):
    """RU: начало сообщения со временем (или пусто). EN: time part of a message (or empty)."""
    if not getattr(config, "SHOW_TIME", True):
        return ""
    return getattr(config, "TIME_PREFIX", "`{time}` ").format(time=fmt_time(dt_utc))


def humanize_npc(raw):
    """RU: NPC_PREFIX_Wildlife_RocknoseMoss -> Rocknose Moss. EN: same, readable name."""
    if raw in config.NPC_NAMES:
        return config.NPC_NAMES[raw]
    name = raw
    for prefix in ("NPC_PREFIX_", "EAAWildlife_", "Wildlife_"):
        if name.startswith(prefix):
            name = name[len(prefix):]
    name = name.replace("_", " ")
    name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", name)
    return name.strip() or raw


# -------------------------------------------------------------------- state --
class LogState:
    """
    RU: Следит за событиями в логе. emit(text) вызывается для каждого готового сообщения.
    EN: Tracks log events. emit(text) is called for every finished message.
    """

    def __init__(self, emit, emit_chat=None):
        self.emit = emit
        self.emit_chat = emit_chat or emit
        self.shutdown_sent = False    # shutdown message already sent for this session
        self.crashed = False          # a crash marker was seen for this session
        self.awaiting_online = False  # startup seen, waiting for the first Status report
        self.chat_pending = None      # ChatWindow line waiting for its PippiChat twin
        self.last_chat_key = None     # last sent chat message (duplicate guard)
        self.ts_key = ""              # raw log timestamp of the current line
        self.now = None               # last log time (UTC) / последнее время в логе
        self.pending_logins = []      # [(steam_id, time)]
        self.pending_join = None      # {"account","steam","t"}
        self.online = {}              # account -> (char_name, steam_id)
        self.steam_by_char = {}       # char_name -> steam_id (kept for the whole run)

    def reset_session(self):
        """RU: сервер перезапустился - все игроки отключены. EN: server restarted."""
        self.pending_logins.clear()
        self.pending_join = None
        self.online.clear()
        self.shutdown_sent = False
        self.awaiting_online = False
        self.crashed = False

    # ---- helpers
    def _finish_join(self, char_name=None):
        pj = self.pending_join
        if not pj:
            return
        self.pending_join = None
        name = char_name or pj["account"].split("#")[0]
        self.online[pj["account"]] = (name, pj["steam"])
        self.steam_by_char[name] = pj["steam"]
        self.emit(config.MSG_PLAYER_JOIN.format(
            time=fmt_time(pj["t"]), time_prefix=time_prefix(pj["t"]),
            player=name, steam_id=pj["steam"]))

    # ---- main entry
    def feed(self, line):
        m = RE_TS.match(line)
        if m:
            y, mo, d, h, mi, s = map(int, m.groups())
            self.now = datetime(y, mo, d, h, mi, s, tzinfo=timezone.utc)
            self.ts_key = line[:m.end()]
        if self.now is None:
            return

        # ---- chat / чат
        m = RE_CHAT_PIPPI.search(line)
        if m:
            name, channel, text = m.groups()
            self.chat_pending = None      # its ChatWindow twin - do not send twice
            self._send_chat(name, text, channel)
            return
        m = RE_CHAT_WINDOW.search(line)
        if m:
            self.flush_chat()             # previous one had no twin - send it as is
            name, text = m.groups()
            # RU: без Pippi ник приходит как "Ник (uid 126, player 7656...)" - убираем скобки
            # EN: without Pippi the name looks like "Name (uid 126, player 7656...)" - strip it
            nm = RE_CHAT_NAME.match(name)
            if nm:
                name = nm.group(1)
                self.steam_by_char[name] = nm.group(2)
            if (self.ts_key, name, text) != self.last_chat_key:
                self.chat_pending = (self.now, self.ts_key, name, text, time.monotonic())
            return
        self.flush_chat()

        # RU: не дождались ника персонажа - используем ник аккаунта
        # EN: character name did not show up in time - fall back to account name
        if self.pending_join and self.now - self.pending_join["t"] > JOIN_WAIT:
            self._finish_join()

        # RU: краш сервера (Unreal Engine пишет эту строку при фатальной ошибке)
        # EN: server crash (Unreal Engine writes this line on a fatal error)
        if "LogWindows: Error: === Critical error:" in line:
            self.crashed = True
            self.awaiting_online = False
            if not self.shutdown_sent:
                self.shutdown_sent = True
                self.emit(config.MSG_SERVER_CRASHED.format(
                    time=fmt_time(self.now), time_prefix=time_prefix(self.now)))
            return

        # RU: остановка сервера (строка встречается дважды - шлём один раз; при краше
        #     эта же строка тоже появляется, но сообщение о краше уже отправлено выше)
        # EN: server shutdown (the line appears twice - send once; a crash also produces
        #     this same line, but the crash message was already sent above)
        if "LogCore: Engine exit requested" in line:
            self.awaiting_online = False
            if not self.shutdown_sent and not self.crashed:
                self.shutdown_sent = True
                self.emit(config.MSG_SERVER_OFFLINE.format(
                    time=fmt_time(self.now), time_prefix=time_prefix(self.now)))
            return

        # RU: "Startup report" пишется сразу после инициализации движка, но мир ещё грузится.
        #     Сервер по-настоящему готов, когда пришёл первый "Status report".
        # EN: "Startup report" is written right after engine init, but the world is still
        #     loading. The server is really ready at the first "Status report".
        if "LogServerStats: Startup report" in line:
            self.reset_session()
            self.awaiting_online = True
            return

        if self.awaiting_online and "LogServerStats: Status report" in line:
            self.awaiting_online = False
            self.emit(config.MSG_SERVER_ONLINE.format(
                time=fmt_time(self.now), time_prefix=time_prefix(self.now)))
            return

        m = RE_LOGIN.search(line)
        if m:
            self.pending_logins = [(s, t) for s, t in self.pending_logins
                                   if self.now - t < PENDING_LOGIN_TTL]
            self.pending_logins.append((m.group(1), self.now))
            return

        m = RE_JOIN.search(line)
        if m:
            self._finish_join()   # RU: закрыть предыдущий вход / EN: close previous join
            steam = self.pending_logins.pop(0)[0] if self.pending_logins else "unknown"
            self.pending_join = {"account": m.group(1), "steam": steam, "t": self.now}
            return

        m = RE_CHAR.search(line)
        if m:
            if self.pending_join:
                self._finish_join(m.group(1))
            return

        m = RE_DISC.search(line)
        if m:
            account = m.group(1)
            if account == "Unknown":
                # RU: неудачная попытка входа - убрать последний Login request
                # EN: failed login attempt - drop the most recent login request
                if self.pending_logins:
                    self.pending_logins.pop()
                return
            if self.pending_join and self.pending_join["account"] == account:
                self._finish_join()
            info = self.online.pop(account, None)
            if info:
                self.emit(config.MSG_PLAYER_LEAVE.format(
                    time=fmt_time(self.now), time_prefix=time_prefix(self.now),
                    player=info[0], steam_id=info[1]))
            return

        m = RE_KILL.search(line)
        if m:
            self._handle_kill(*m.groups())

    # ---- chat helpers
    def _send_chat(self, name, text, channel, when=None, ts_key=None):
        self.last_chat_key = (ts_key or self.ts_key, name, text)
        if not config.CHAT_ENABLED:
            return
        wanted = [c.lower() for c in config.CHAT_CHANNELS]
        if wanted and channel and channel.lower() not in wanted:
            return   # RU: канал не выбран / EN: channel filtered out
        # RU: канал неизвестен (без Pippi) - фильтр не применяется
        # EN: channel unknown (no Pippi) - the filter is not applied
        t = (when or self.now).astimezone(TZ).strftime(config.CHAT_TIME_FORMAT)
        prefix = config.CHAT_TIME_PREFIX.format(time=t) if getattr(config, "CHAT_SHOW_TIME", True) else ""
        self.emit_chat(config.MSG_CHAT.format(
            time=t, time_prefix=prefix,
            player=name, message=text, channel=channel,
            steam_id=self.steam_by_char.get(name, "unknown"))[:1900])

    def flush_chat(self):
        """RU: отправить ChatWindow, если PippiChat так и не пришёл. EN: send pending ChatWindow."""
        cp = self.chat_pending
        if cp:
            self.chat_pending = None
            self._send_chat(cp[2], cp[3], "", when=cp[0], ts_key=cp[1])

    def flush_chat_if_stale(self):
        cp = self.chat_pending
        if cp and time.monotonic() - cp[4] > CHAT_WAIT:
            self.flush_chat()

    def _handle_kill(self, killer, cause, is_thrall, obj_name, victim):
        # RU: интересуют только смерти игроков. EN: player deaths only.
        if not obj_name.startswith("BasePlayerChar") or is_thrall != "0":
            return
        common = dict(time=fmt_time(self.now), time_prefix=time_prefix(self.now), player=victim,
                      steam_id=self.steam_by_char.get(victim, "unknown"),
                      killer=killer, killer_steam_id="")
        killer = killer.strip()
        if cause == "Suicide" or killer.lower() == "yourself":
            text = config.MSG_KILLED_BY_SUICIDE.format(**common)
        elif not killer:
            text = config.MSG_KILLED_BY_UNKNOWN.format(**common)
        elif killer.startswith("NPC_PREFIX_"):
            common["killer"] = humanize_npc(killer)
            tpl = config.MSG_KILLED_BY_ANIMAL if "Wildlife" in killer else config.MSG_KILLED_BY_NPC
            text = tpl.format(**common)
        elif killer in self.steam_by_char:
            common["killer_steam_id"] = self.steam_by_char[killer]
            text = config.MSG_KILLED_BY_PLAYER.format(**common)
        else:
            # RU: не игрок и не NPC: падение, утопление и т.п. (или игрок, которого парсер не знает)
            # EN: not a player and not an NPC: falling, drowning, etc. (or a player unknown to the parser)
            common["killer"] = humanize_npc(killer)
            text = getattr(config, "MSG_KILLED_BY_OTHER", config.MSG_KILLED_BY_NPC).format(**common)
        self.emit(text)


# ------------------------------------------------------------------ discord --
class DiscordSender(threading.Thread):
    """RU: очередь отправки, чтобы не упереться в лимиты Discord. EN: send queue (rate limits)."""

    def __init__(self, url, name="", avatar=""):
        super().__init__(daemon=True)
        self.q = queue.Queue()
        self.url, self.name, self.avatar = url, name, avatar

    def send(self, text):
        self.q.put(text)

    def run(self):
        while True:
            text = self.q.get()
            for _ in range(5):
                if self._post(text):
                    break
                time.sleep(3)
            time.sleep(0.6)

    def _post(self, text):
        payload = {"content": text, "allowed_mentions": {"parse": []}}
        if self.name:
            payload["username"] = self.name
        if self.avatar:
            payload["avatar_url"] = self.avatar
        req = urllib.request.Request(
            self.url, data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "User-Agent": "ConanLogParser/1.0"})
        try:
            urllib.request.urlopen(req, timeout=15).read()
            return True
        except urllib.error.HTTPError as e:
            if e.code == 429:   # rate limited
                try:
                    wait = float(json.loads(e.read().decode()).get("retry_after", 2))
                except Exception:
                    wait = 2
                time.sleep(wait + 0.2)
            else:
                print(f"[!] Discord HTTP {e.code}: check webhook URL / проверьте ссылку вебхука")
            return False
        except Exception as e:
            print(f"[!] Discord error: {e}")
            return False


# ---------------------------------------------------------------------- tail --
SIG_LEN = 36   # RU: длина шапки "Log file open, дата время" / EN: length of the "Log file open, date time" header


def read_lines(path, pos, sig):
    """
    RU: Читает новые строки с позиции pos. Возвращает (lines, new_pos, sig, rotated).
        Новый лог (перезапуск сервера) определяется по первой строке файла
        "Log file open, <дата время>" - она у каждого запуска своя. Это надёжнее,
        чем размер или дата создания файла.
    EN: Reads new lines from pos. Returns (lines, new_pos, sig, rotated).
        A new log (server restart) is detected by the first line of the file
        "Log file open, <date time>" - unique for every run. More reliable than
        file size or creation date.
    """
    size = os.stat(path).st_size
    rotated = False
    with open(path, "rb") as f:
        head = f.read(SIG_LEN)
        if len(head) >= SIG_LEN:
            if sig is not None and head != sig:
                rotated = True
            sig = head
        if size < pos:
            rotated = True
        if rotated:
            pos = 0
        f.seek(pos)
        data = f.read()
    # RU: берём только целые строки / EN: whole lines only
    cut = data.rfind(b"\n")
    if cut < 0:
        return [], pos, sig, rotated
    chunk = data[:cut + 1]
    lines = chunk.decode("utf-8", errors="replace").splitlines()
    return lines, pos + len(chunk), sig, rotated


def replay(path):
    """RU: тест - вывод в консоль без отправки. EN: test - print to console, no sending."""
    state = LogState(lambda t: print(t), lambda t: print("[CHAT]", t))
    with open(path, "rb") as f:
        for line in f.read().decode("utf-8", errors="replace").splitlines():
            state.feed(line)
    state.flush_chat()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print(f"Conan Enhanced Log Parser v{VERSION} by {AUTHOR} | Discord: {DISCORD}")
    print("-" * 60)

    if len(sys.argv) >= 3 and sys.argv[1] == "--replay":
        replay(sys.argv[2])
        return

    if not config.WEBHOOK_URL.startswith("https://") or "PASTE_YOUR" in config.WEBHOOK_URL:
        print("[!] Укажите WEBHOOK_URL в config.py / Set WEBHOOK_URL in config.py")
        return
    log_path = config.LOG_PATH
    if not os.path.isabs(log_path):
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), log_path)
        if not os.path.exists(log_path) and os.path.exists(config.LOG_PATH):
            log_path = os.path.abspath(config.LOG_PATH)
    if os.path.isdir(log_path):
        # RU: указана папка - берём файл ConanSandbox.log внутри неё
        # EN: a folder was given - use ConanSandbox.log inside it
        log_path = os.path.join(log_path, "ConanSandbox.log")
    print(f"Log: {log_path}")

    sender = DiscordSender(config.WEBHOOK_URL, config.WEBHOOK_NAME, config.WEBHOOK_AVATAR_URL)
    sender.start()
    chat_url = config.CHAT_WEBHOOK_URL.strip()
    if chat_url.startswith("https://"):
        chat_sender = DiscordSender(chat_url, config.CHAT_WEBHOOK_NAME,
                                    config.CHAT_WEBHOOK_AVATAR_URL)
        chat_sender.start()
    else:
        chat_sender = sender   # RU: чат в тот же канал / EN: chat into the same channel
    state = LogState(lambda t: (print(t), sender.send(t)),
                     lambda t: (print(t), chat_sender.send(t)))

    # RU: 1) Прочитать уже написанное, НЕ отправляя - чтобы знать, кто сейчас онлайн
    #     и какой Steam ID у какого ника. 2) Дальше следить только за новыми строками.
    # EN: 1) Read existing log WITHOUT sending - to learn who is online and each
    #     player's Steam ID. 2) Then watch only new lines.
    quiet, quiet_chat = state.emit, state.emit_chat
    state.emit = state.emit_chat = lambda t: None
    pos, sig = 0, None
    while True:
        try:
            lines, pos, sig, _ = read_lines(log_path, 0, None)
            break
        except FileNotFoundError:
            print("Waiting for log file... / Ждём лог-файл...")
            time.sleep(5)
    for line in lines:
        state.feed(line)
    state.chat_pending = None
    state.emit, state.emit_chat = quiet, quiet_chat
    print("Started. Watching the log... / Запущено. Слежу за логом...")

    while True:
        time.sleep(config.POLL_INTERVAL)
        state.flush_chat_if_stale()
        try:
            lines, pos, sig, rotated = read_lines(log_path, pos, sig)
        except FileNotFoundError:
            continue
        except OSError as e:
            print(f"[!] {e}")
            continue
        if rotated:
            print("Log restarted (new server session) / Лог перезапущен (новый запуск сервера)")
            state.reset_session()
        for line in lines:
            state.feed(line)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
