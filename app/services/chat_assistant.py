"""
SEAIT Lost & Found assistant — knowledge-based replies with optional OpenAI.
"""
import json
import os
import re
import urllib.request
from typing import Optional

_DEFAULT = (
    "I'm your **SEAIT Lost & Found** assistant. Try asking about:\n\n"
    "• **Students:** reporting a lost item, matches, claiming with QR\n"
    "• **Staff:** logging found items, verifying claims\n"
    "• **General:** login, passwords, what each status means\n\n"
    "Ask a specific question and I'll guide you step by step."
)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _match_score(query: str, keywords: tuple) -> int:
    q = _normalize(query)
    if not q:
        return 0
    score = 0
    for kw in keywords:
        if kw in q:
            score += 2
    for kw in keywords:
        if any(part in q for part in kw.split()):
            score += 1
    return score


def _kb_answer(query: str, role: str) -> str:
    """Return best answer from local knowledge base."""
    role = (role or "student").lower()
    pairs = [
        (
            (
                "login",
                "sign in",
                "password",
                "forgot password",
                "account",
                "cannot log",
                "cant log",
            ),
            "Sign in at **Auth → Login** with your SEAIT email and password.\n\n"
            "Default demo accounts (if seeded): **admin@seait.edu**, **staff@seait.edu**, "
            "**student1@seait.edu**. Forgot password? Contact your administrator — "
            "self-service reset is not enabled in this build.",
        ),
        (
            ("report", "lost item", "i lost", "missing item", "lost my"),
            "Students: open **My Items** and use **Report a lost item** at the top.\n\n"
            "Fill **name, category, date lost** (required), add description, color, "
            "location, and an optional photo. Submit — the system runs **matching** "
            "against available found items and may suggest matches under **Matches**.",
        ),
        (
            ("my items", "my lost", "list my", "see my items"),
            "**My Items** lists everything you reported with status: Pending → Matched → Claimed.\n\n"
            "Use filters, then **View matches** for items that have suggestions.",
        ),
        (
            (
                "match",
                "suggested",
                "confirm match",
                "score",
                "how matching",
                "ai match",
            ),
            "**Matches** show possible pairings between your lost report and a found item.\n\n"
            "Review the score, **Confirm** if you believe it's yours — that creates a "
            "**claim** and unlocks the **QR code** for staff to verify.",
        ),
        (
            ("qr", "claim code", "claim", "confirm match", "pick up", "release"),
            "After you **confirm a match**, open **Claim QR** (from the claim flow).\n\n"
            "Show the QR to **Staff → Verify claim**. Staff can release the item when the "
            "code checks out. Keep your claim code private.",
        ),
        (
            (
                "staff",
                "log found",
                "found item",
                "inventory",
                "storage",
                "where to log",
            ),
            "Staff: open **Found Items** — **Log a new found item** is at the top of that page.\n\n"
            "Record item name, category, date found, location, storage spot, priority, and "
            "optional photo. High-value categories (ID/Wallet/Phone) can auto-flag as priority.",
        ),
        (
            ("verify", "release", "pending claim", "staff claim"),
            "Staff: **Verify claim** — enter the student's claim code or use the link from the "
            "dashboard. Confirm details, then **release** when the item is handed over.",
        ),
        (
            ("status", "pending", "available", "matched", "claimed"),
            "**Statuses (simplified):**\n\n"
            "• **Lost — Pending:** reported, no confirmed match yet.\n"
            "• **Lost — Matched:** you confirmed a match; claim in progress.\n"
            "• **Lost — Claimed:** item released to you.\n"
            "• **Found — Available:** in the office, not matched/claimed.\n"
            "• **Match — Suggested:** system proposal — confirm or skip in **Matches**.",
        ),
        (
            ("notify", "notification", "bell", "alert"),
            "Students get **notifications** when strong matches appear (and for other events "
            "the system sends). Check **Notifications** and mark items read as you go.",
        ),
        (
            ("admin", "dashboard admin", "users", "report"),
            "Admins use **Dashboard** for totals, **Users** to manage accounts, "
            "and **Reports** for overview. Staff/students use their own sidebars.",
        ),
        (
            ("help", "hello", "hi", "what can you", "who are you"),
            "I'm the in-app assistant for the **SEAIT Lost & Found** system. "
            "Ask how to report items, confirm matches, use QR claims, or log found property.",
        ),
    ]

    best = (-1, _DEFAULT)
    for kws, ans in pairs:
        sc = _match_score(query, kws)
        if sc > best[0]:
            best = (sc, ans)

    if role in ("staff", "admin"):
        extra = (
            "\n\n**Staff tip:** Logging and the inventory table live together under "
            "**Found Items** for a faster workflow."
        )
        if best[0] >= 2:
            return best[1] + extra
    if best[0] >= 2:
        return best[1]
    return _DEFAULT


def _openai_reply(user_message: str, role: str) -> Optional[str]:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    try:
        system = (
            "You are SEAIT Lost & Found assistant. Be concise, friendly, step-by-step. "
            "Cover students (report lost, matches, QR claims), staff (log found under Found Items, "
            f"verify claims). User role: {role}. Never invent school policies; if unsure, suggest "
            "contacting the Lost & Found office or admin."
        )
        body = json.dumps(
            {
                "model": os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_message[:8000]},
                ],
                "max_tokens": 450,
                "temperature": 0.5,
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def reply(user_message: str, role: str = "student") -> dict:
    """Return assistant message text and metadata."""
    text = (user_message or "").strip()
    if not text:
        return {"reply": _DEFAULT, "source": "default"}

    ai = _openai_reply(text, role)
    if ai:
        return {"reply": ai, "source": "openai"}

    return {"reply": _kb_answer(text, role), "source": "knowledge"}
