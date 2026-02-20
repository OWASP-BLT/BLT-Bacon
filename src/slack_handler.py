"""
Slack bot handler for the /bacon slash command.

Command usage: /bacon @user <amount>
Example:       /bacon @alice 50

This handler:
  1. Verifies the request comes from Slack via HMAC-SHA256 signature check.
  2. Parses the target Slack user and BACON amount from the command text.
  3. Records the BACON transfer (logged to Cloudflare observability / KV if bound).
  4. Returns an ephemeral Slack message confirming the transfer.

Environment variables / Worker secrets required:
  SLACK_SIGNING_SECRET  – Found in your Slack app's "Basic Information" page.
  SLACK_BOT_TOKEN       – Bot OAuth token (xoxb-…) for optional Slack API calls.
"""

import hashlib
import hmac
import json
import re
import time


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_text(text: str):
    """
    Parse the slash-command text field.

    Accepts formats:
      @username 50
      <@U12345678|username> 50
      @Username 50.5

    Returns (recipient_display, amount) or (None, None) on parse failure.
    """
    text = text.strip()

    # Slack sometimes sends rich mention format: <@U12345|displayname>
    rich = re.match(r"^<@([A-Z0-9]+)\|?([^>]*)>\s+([\d]+(?:\.\d+)?)$", text)
    if rich:
        user_id = rich.group(1)
        display = rich.group(2) or user_id
        amount = float(rich.group(3))
        return f"<@{user_id}>" , amount, display

    # Plain @username format
    plain = re.match(r"^@([\w.\-]+)\s+([\d]+(?:\.\d+)?)$", text)
    if plain:
        username = plain.group(1)
        amount = float(plain.group(2))
        return f"@{username}", amount, username

    return None, None, None


def _verify_slack_signature(signing_secret: str, request_body: str,
                             timestamp: str, signature: str) -> bool:
    """
    Verify Slack's request signature to ensure the request is authentic.
    See: https://api.slack.com/authentication/verifying-requests-from-slack
    """
    # Reject requests older than 5 minutes to prevent replay attacks.
    try:
        if abs(time.time() - float(timestamp)) > 300:
            return False
    except (ValueError, TypeError):
        return False

    sig_basestring = f"v0:{timestamp}:{request_body}".encode("utf-8")
    computed = "v0=" + hmac.new(
        signing_secret.encode("utf-8"),
        sig_basestring,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(computed, signature)


def _slack_response(text: str, response_type: str = "ephemeral") -> dict:
    """Build a minimal Slack response payload."""
    return {
        "response_type": response_type,  # "ephemeral" | "in_channel"
        "text": text,
    }


# ---------------------------------------------------------------------------
# Main entry point called from index.py
# ---------------------------------------------------------------------------

async def handle_bacon_command(request, env):
    """
    Handle POST /api/slack/bacon

    Parses and validates the Slack slash command, then dispatches the BACON
    transfer.  Returns a Response-compatible dict with JSON body and headers.
    """
    from js import Response  # Cloudflare Workers JS interop

    json_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
    }

    # ------------------------------------------------------------------ #
    # 1. Read raw body (needed for signature verification)                 #
    # ------------------------------------------------------------------ #
    try:
        body_text = await request.text()
    except Exception:
        payload = _slack_response(":x: Could not read request body.")
        return Response.new(json.dumps(payload), {"status": 400, "headers": json_headers})

    # ------------------------------------------------------------------ #
    # 2. Verify Slack signature                                            #
    # ------------------------------------------------------------------ #
    signing_secret = getattr(env, "SLACK_SIGNING_SECRET", None)
    if signing_secret:
        timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
        signature = request.headers.get("X-Slack-Signature", "")
        if not _verify_slack_signature(signing_secret, body_text, timestamp, signature):
            payload = _slack_response(":x: Request signature verification failed.")
            return Response.new(json.dumps(payload), {"status": 401, "headers": json_headers})

    # ------------------------------------------------------------------ #
    # 3. Parse form body                                                   #
    # ------------------------------------------------------------------ #
    # Slack sends application/x-www-form-urlencoded
    # urllib.parse is available in Cloudflare's Python Workers runtime.
    from urllib.parse import unquote_plus

    form_data: dict = {}
    for pair in body_text.split("&"):
        if "=" in pair:
            k, _, v = pair.partition("=")
            form_data[k] = unquote_plus(v)

    command_text = form_data.get("text", "").strip()
    sender_name = form_data.get("user_name", "someone")
    sender_id = form_data.get("user_id", "")
    channel_id = form_data.get("channel_id", "")

    # ------------------------------------------------------------------ #
    # 4. Parse @user and amount                                            #
    # ------------------------------------------------------------------ #
    if not command_text:
        usage = (
            ":bacon: *Usage:* `/bacon @user <amount>`\n"
            "Example: `/bacon @alice 50`"
        )
        payload = _slack_response(usage)
        return Response.new(json.dumps(payload), {"status": 200, "headers": json_headers})

    mention, amount, display_name = _parse_text(command_text)

    if mention is None:
        error_msg = (
            f":x: Could not parse `{command_text}`.\n"
            "*Usage:* `/bacon @user <amount>`\n"
            "Example: `/bacon @alice 50`"
        )
        payload = _slack_response(error_msg)
        return Response.new(json.dumps(payload), {"status": 200, "headers": json_headers})

    if amount <= 0:
        payload = _slack_response(":x: Amount must be greater than 0.")
        return Response.new(json.dumps(payload), {"status": 200, "headers": json_headers})

    # ------------------------------------------------------------------ #
    # 5. Record the transfer                                               #
    # ------------------------------------------------------------------ #
    # If a KV namespace called BACON_LEDGER is bound in wrangler.toml you
    # can persist balances here.  For now we log the event and respond.
    transfer_record = {
        "from_user_id": sender_id,
        "from_user_name": sender_name,
        "to_user_display": display_name,
        "amount": amount,
        "channel_id": channel_id,
        "timestamp": int(time.time()),
    }

    # Optional: persist to KV
    bacon_kv = getattr(env, "BACON_LEDGER", None)
    if bacon_kv:
        try:
            record_key = f"transfer:{sender_id}:{int(time.time())}"
            await bacon_kv.put(record_key, json.dumps(transfer_record))
        except Exception:
            pass  # Non-fatal – transfer is still announced

    # ------------------------------------------------------------------ #
    # 6. Respond to Slack                                                  #
    # ------------------------------------------------------------------ #
    success_msg = (
        f":bacon: *@{sender_name}* sent *{amount:g} BACON* to *{mention}*! "
        f"Keep contributing to earn more! :rocket:"
    )
    # in_channel makes the message visible to the whole channel
    payload = _slack_response(success_msg, response_type="in_channel")
    return Response.new(json.dumps(payload), {"status": 200, "headers": json_headers})
