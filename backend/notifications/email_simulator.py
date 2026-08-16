"""Simulation e-mails — codes dans le terminal."""
from __future__ import annotations
import secrets, string, threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from backend.core.logger import get_logger
logger = get_logger(__name__)
_lock = threading.Lock()
def _code(n=6): return "".join(secrets.choice(string.digits) for _ in range(n))
def _token(n=32): return secrets.token_urlsafe(n)
@dataclass
class PendingMail:
    kind: str; email: str; code: Optional[str]=None; token: Optional[str]=None
    payload: Dict[str, Any]=field(default_factory=dict)
    created_at: datetime=field(default_factory=datetime.utcnow)
    expires_at: datetime=field(default_factory=lambda: datetime.utcnow()+timedelta(minutes=15))
    used: bool=False
    def is_valid(self): return not self.used and datetime.utcnow()<=self.expires_at
class EmailSimulator:
    def __init__(self):
        self._by_email={}; self._by_token={}; self._history=[]
    def _banner(self, title, lines):
        bar="="*62
        msg=f"\n{bar}\n  📧  SENTINELAI EMAIL SIMULATOR — {title}\n{bar}\n"+"\n".join(f"  {l}" for l in lines)+f"\n{bar}\n"
        print(msg, flush=True); logger.info(f"[EMAIL-SIM] {title}")
    def _store(self, mail):
        with _lock:
            self._by_email.setdefault(mail.email.lower(),{})[mail.kind]=mail
            if mail.token: self._by_token[mail.token]=mail
            self._history.append(mail)
        return mail
    def send_verification(self, email, username=""):
        mail=PendingMail(kind="verify_email",email=email,code=_code(),token=_token(),payload={"username":username})
        self._store(mail); self._banner("VÉRIFICATION E-MAIL",[f"À : {email}",f"CODE : {mail.code}",f"TOKEN : {mail.token}"]); return mail
    def send_password_reset(self, email):
        mail=PendingMail(kind="password_reset",email=email,code=_code(),token=_token())
        self._store(mail); self._banner("RESET MDP",[f"À : {email}",f"CODE : {mail.code}"]); return mail
    def send_login_otp(self, email, username=""):
        mail=PendingMail(kind="login_otp",email=email,code=_code(),payload={"username":username},expires_at=datetime.utcnow()+timedelta(minutes=5))
        self._store(mail); self._banner("OTP",[f"À : {email}",f"CODE OTP : {mail.code}"]); return mail
    def send_alert(self, email, subject, body):
        mail=PendingMail(kind="alert",email=email,payload={"subject":subject,"body":body[:500]})
        self._store(mail); self._banner("ALERTE",[f"À : {email}",f"Sujet : {subject}"]); return mail
    def get(self, email, kind):
        with _lock: return self._by_email.get(email.lower(),{}).get(kind)
    def consume_code(self, email, kind, code):
        mail=self.get(email,kind)
        if not mail or not mail.is_valid() or (mail.code or "")!=str(code).strip(): return False
        with _lock: mail.used=True; return True
    def history(self, limit=20):
        with _lock: items=list(reversed(self._history[-limit:]))
        return [{"kind":m.kind,"email":m.email,"code":m.code,"used":m.used,"valid":m.is_valid()} for m in items]
email_sim=EmailSimulator()
