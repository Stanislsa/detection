"""
Service Telegram Bot — configuration et envoi d'alertes.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict, fields
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


@dataclass
class TelegramConfig:
    enabled: bool = False
    bot_token: str = ""
    chat_id: str = ""
    send_critical: bool = True
    send_high: bool = True
    send_medium: bool = False
    send_low: bool = False
    include_location: bool = True
    include_camera: bool = True
    silent: bool = False  # disable_notification on Telegram

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TelegramConfig":
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in (data or {}).items() if k in known})

    @property
    def is_configured(self) -> bool:
        return bool(self.bot_token.strip() and self.chat_id.strip())


class TelegramService:
    """Client Bot API Telegram (urllib — pas de dépendance requests)."""

    API = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, config_path: Optional[str] = None):
        self._path = Path(
            config_path
            or os.path.join(os.path.expanduser("~"), ".sentinelai", "telegram.json")
        )
        self._config = self._load()

    # ---------------------------------------------------------------- config
    def _load(self) -> TelegramConfig:
        if self._path.exists():
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    return TelegramConfig.from_dict(json.load(f))
            except Exception as exc:
                print(f"[Telegram] load error: {exc}")
        return TelegramConfig()

    def _save(self) -> bool:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(self._config.to_dict(), f, indent=2)
            return True
        except Exception as exc:
            print(f"[Telegram] save error: {exc}")
            return False

    def get_config(self) -> Dict[str, Any]:
        d = self._config.to_dict()
        # Mask token for UI display helpers
        token = d.get("bot_token") or ""
        d["bot_token_masked"] = (
            (token[:6] + "…" + token[-4:]) if len(token) > 12 else ("*" * len(token) if token else "")
        )
        d["is_configured"] = self._config.is_configured
        return d

    def update_config(self, data: Dict[str, Any]) -> Dict[str, Any]:
        merged = {**self._config.to_dict(), **(data or {})}
        # Don't overwrite token with masked placeholder
        if "bot_token" in merged and "…" in str(merged["bot_token"]):
            merged["bot_token"] = self._config.bot_token
        self._config = TelegramConfig.from_dict(merged)
        self._save()
        return self.get_config()

    # ---------------------------------------------------------------- HTTP
    def _call(self, method: str, payload: Optional[dict] = None) -> Tuple[bool, Any]:
        token = self._config.bot_token.strip()
        if not token:
            return False, "Bot token missing"

        url = self.API.format(token=token, method=method)
        try:
            if payload is not None:
                body = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=body,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
            else:
                req = urllib.request.Request(url, method="GET")

            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok"):
                return True, data.get("result")
            return False, data.get("description") or "Telegram API error"
        except urllib.error.HTTPError as exc:
            try:
                err = json.loads(exc.read().decode("utf-8"))
                return False, err.get("description") or str(exc)
            except Exception:
                return False, f"HTTP {exc.code}: {exc.reason}"
        except Exception as exc:
            return False, str(exc)

    def test_connection(self) -> Tuple[bool, str]:
        """getMe + optional ping message."""
        ok, result = self._call("getMe")
        if not ok:
            return False, f"getMe failed: {result}"
        username = ""
        if isinstance(result, dict):
            username = result.get("username") or result.get("first_name") or ""
        msg = f"Bot OK (@{username})" if username else "Bot OK"

        if self._config.chat_id.strip():
            ok2, res2 = self.send_message(
                "🛡️ <b>SentinelAI</b> — Telegram connection test successful."
            )
            if ok2:
                return True, msg + " · test message sent"
            return False, f"{msg} but send failed: {res2}"
        return True, msg + " · set chat_id to send messages"

    def send_message(self, text: str, chat_id: Optional[str] = None) -> Tuple[bool, Any]:
        cid = (chat_id or self._config.chat_id).strip()
        if not cid:
            return False, "chat_id missing"
        payload = {
            "chat_id": cid,
            "text": text,
            "parse_mode": "HTML",
            "disable_notification": bool(self._config.silent),
        }
        return self._call("sendMessage", payload)

    def should_send_priority(self, priority: str) -> bool:
        if not self._config.enabled or not self._config.is_configured:
            return False
        p = (priority or "").upper()
        return {
            "CRITICAL": self._config.send_critical,
            "HIGH": self._config.send_high,
            "MEDIUM": self._config.send_medium,
            "LOW": self._config.send_low,
        }.get(p, False)

    def send_alert(self, alert: dict) -> Tuple[bool, Any]:
        """Formate et envoie une alerte si la config le permet."""
        priority = (alert.get("priority") or "HIGH").upper()
        if not self.should_send_priority(priority):
            return False, "priority filtered or telegram disabled"

        title = alert.get("title") or "Security Alert"
        desc = alert.get("description") or ""
        lines = [
            f"🚨 <b>[{priority}] {title}</b>",
        ]
        if desc:
            lines.append(desc[:400])
        if self._config.include_location and alert.get("location"):
            lines.append(f"📍 {alert['location']}")
        if self._config.include_camera and (alert.get("camera_name") or alert.get("camera_id")):
            lines.append(f"📷 {alert.get('camera_name') or alert.get('camera_id')}")
        if alert.get("id"):
            lines.append(f"ID: <code>{alert['id']}</code>")

        return self.send_message("\n".join(lines))

    # ---------------------------------------------------------- bot permissions
    def get_me(self) -> Tuple[bool, Any]:
        return self._call("getMe")

    def get_chat(self, chat_id: Optional[str] = None) -> Tuple[bool, Any]:
        cid = (chat_id or self._config.chat_id).strip()
        if not cid:
            return False, "chat_id missing"
        return self._call("getChat", {"chat_id": cid})

    def get_chat_member(self, user_id: int, chat_id: Optional[str] = None) -> Tuple[bool, Any]:
        cid = (chat_id or self._config.chat_id).strip()
        if not cid:
            return False, "chat_id missing"
        return self._call("getChatMember", {"chat_id": cid, "user_id": user_id})

    def get_my_commands(self) -> Tuple[bool, Any]:
        return self._call("getMyCommands")

    def set_my_commands(self, commands: list) -> Tuple[bool, Any]:
        """commands: list of {command, description}."""
        return self._call("setMyCommands", {"commands": commands})

    def check_bot_permissions(self) -> Dict[str, Any]:
        """
        Analyse les droits du bot dans le chat configuré.
        Retourne un rapport structuré pour l'UI.
        """
        report: Dict[str, Any] = {
            "ok": False,
            "bot_id": None,
            "bot_username": "",
            "bot_name": "",
            "chat_id": self._config.chat_id,
            "chat_type": "",
            "chat_title": "",
            "status": "unknown",  # creator|administrator|member|restricted|left|kicked
            "can_send_messages": False,
            "can_send_media": False,
            "can_delete_messages": False,
            "can_pin_messages": False,
            "can_manage_chat": False,
            "is_admin": False,
            "issues": [],
            "hints": [],
            "raw_member": None,
        }

        if not self._config.bot_token.strip():
            report["issues"].append("Bot token is missing")
            return report
        if not self._config.chat_id.strip():
            report["issues"].append("Chat ID is missing")
            return report

        ok, me = self.get_me()
        if not ok or not isinstance(me, dict):
            report["issues"].append(f"getMe failed: {me}")
            return report

        report["bot_id"] = me.get("id")
        report["bot_username"] = me.get("username") or ""
        report["bot_name"] = me.get("first_name") or ""

        ok_chat, chat = self.get_chat()
        if ok_chat and isinstance(chat, dict):
            report["chat_type"] = chat.get("type") or ""
            report["chat_title"] = (
                chat.get("title")
                or chat.get("username")
                or chat.get("first_name")
                or str(self._config.chat_id)
            )
            # Private chats: permissions are implicit if we can message
            if report["chat_type"] == "private":
                report["status"] = "member"
                report["can_send_messages"] = True
                report["can_send_media"] = True
                report["ok"] = True
                report["hints"].append("Private chat: bot can message this user if they started the conversation.")
                return report
        else:
            report["issues"].append(f"getChat failed: {chat}")
            # continue to try getChatMember anyway

        bot_id = report["bot_id"]
        ok_mem, member = self.get_chat_member(int(bot_id))
        if not ok_mem or not isinstance(member, dict):
            report["issues"].append(f"getChatMember failed: {member}")
            report["hints"].append(
                "Add the bot to the group/channel and grant it permission to post."
            )
            return report

        report["raw_member"] = member
        status = member.get("status") or "unknown"
        report["status"] = status

        if status in ("left", "kicked"):
            report["issues"].append(f"Bot is '{status}' in this chat — re-add the bot.")
            report["hints"].append("Open the group → Add members → select your bot.")
            return report

        if status == "restricted":
            report["issues"].append("Bot is restricted in this chat.")

        # Administrator privileges object (groups/channels)
        privileges = member.get("can_post_messages")
        # For groups, "member" may still send if default perms allow
        if status in ("creator", "administrator"):
            report["is_admin"] = True
            report["can_send_messages"] = bool(
                member.get("can_post_messages", True)
                if report["chat_type"] == "channel"
                else True
            )
            report["can_send_media"] = bool(member.get("can_post_messages", True))
            report["can_delete_messages"] = bool(member.get("can_delete_messages", False))
            report["can_pin_messages"] = bool(member.get("can_pin_messages", False))
            report["can_manage_chat"] = bool(member.get("can_manage_chat", False))
            # Channel-specific: must have can_post_messages
            if report["chat_type"] == "channel" and not member.get("can_post_messages", False):
                report["can_send_messages"] = False
                report["issues"].append(
                    "Bot is admin but cannot post messages in this channel. "
                    "Enable 'Post Messages' in channel admin rights."
                )
        elif status == "member":
            report["can_send_messages"] = True
            report["can_send_media"] = True
            if report["chat_type"] == "channel":
                report["can_send_messages"] = False
                report["issues"].append(
                    "In channels the bot must be administrator with Post Messages."
                )
        elif status == "restricted":
            report["can_send_messages"] = bool(member.get("can_send_messages", False))
            report["can_send_media"] = bool(member.get("can_send_media_messages", False))

        # Final ok flag
        report["ok"] = report["can_send_messages"] and not any(
            "cannot post" in i.lower() or "kicked" in i.lower() or "left" in i.lower()
            for i in report["issues"]
        )
        if report["ok"] and not report["issues"]:
            report["hints"].append("Bot has sufficient rights to send alert messages.")
        if not report["can_send_messages"]:
            report["hints"].append(
                "Grant the bot permission to send messages (group default perms or channel admin Post Messages)."
            )

        return report

    def setup_default_commands(self) -> Tuple[bool, Any]:
        """Enregistre les commandes bot standard SentinelAI."""
        commands = [
            {"command": "start", "description": "Start / link with SentinelAI"},
            {"command": "status", "description": "Bot & connection status"},
            {"command": "mute", "description": "Mute non-critical alerts"},
            {"command": "unmute", "description": "Unmute all alert priorities"},
            {"command": "help", "description": "Help & commands"},
        ]
        return self.set_my_commands(commands)
