import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

from openai import OpenAI
from gtts import gTTS

from services.supabase_client import get_supabase_client

client = OpenAI()

DIGEST_SUBJECT = "Your Weekly SalesVision AI Digest"


def _fetch_users() -> List[Dict[str, Any]]:
    supabase = get_supabase_client()
    resp = supabase.table("users").select("id,email,weekly_digest_enabled,weekly_digest_mode").eq("weekly_digest_enabled", True).execute()
    return resp.data or []


def _fetch_user_summaries(user_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()
    one_week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
    analyses = (
        supabase
        .table("analysis_results")
        .select("created_at,summary,key_factors,recommendations,data_points")
        .eq("user_id", user_id)
        .gte("created_at", one_week_ago)
        .order("created_at", desc=True)
        .limit(5)
        .execute()
    )
    forecasts = (
        supabase
        .table("forecast_results")
        .select("created_at,forecast_data")
        .eq("user_id", user_id)
        .gte("created_at", one_week_ago)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return {
        "analyses": analyses.data or [],
        "forecasts": forecasts.data or [],
    }


def _generate_text_digest(summary: Dict[str, Any]) -> str:
    analyses = summary.get("analyses", [])
    forecasts = summary.get("forecasts", [])

    prompt = (
        "Create a concise weekly digest for a sales analytics user. "
        "Summarize sales trends, key drivers, and a single actionable recommendation. "
        f"Analyses: {analyses[:3]} Forecasts: {forecasts[:1]}"
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a business analytics assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return "Weekly summary unavailable this week."


def _generate_voice_clip(text: str, out_path: str) -> str:
    try:
        tts = gTTS(text)
        tts.save(out_path)
        return out_path
    except Exception:
        return ""


def _send_email(email: str, text: str, attachment_path: str | None = None):
    # Minimal SMTP using environment vars; could be replaced with SendGrid
    import smtplib
    from email.message import EmailMessage

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    from_addr = os.getenv("SMTP_FROM", smtp_user or "noreply@salesvision.ai")

    msg = EmailMessage()
    msg["Subject"] = DIGEST_SUBJECT
    msg["From"] = from_addr
    msg["To"] = email
    msg.set_content(text)

    if attachment_path:
        try:
            with open(attachment_path, "rb") as f:
                data = f.read()
            msg.add_attachment(data, maintype="audio", subtype="mpeg", filename=os.path.basename(attachment_path))
        except Exception:
            pass

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)
        server.send_message(msg)


def run_weekly_digest_job():
    users = _fetch_users()
    for u in users:
        try:
            summary = _fetch_user_summaries(u["id"])
            text_digest = _generate_text_digest(summary)
            attachment = None
            mode = (u.get("weekly_digest_mode") or "both").lower()
            if mode in ("voice", "both"):
                attachment = _generate_voice_clip(text_digest, f"/tmp/digest-{u['id']}.mp3")
            _send_email(u["email"], text_digest, attachment_path=attachment if mode in ("voice", "both") else None)
        except Exception as e:
            print(f"Digest job failed for {u.get('email')}: {e}")
