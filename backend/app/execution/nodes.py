import asyncio
import base64
import csv
import io
import operator
from datetime import date, datetime
from email.message import EmailMessage
from typing import Any

import aiosmtplib
import httpx
from openai import AsyncOpenAI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.execution.context import render_template, resolve_path


class NodeExecutionError(RuntimeError):
    pass


async def execute_node(
    node: dict[str, Any],
    context: dict[str, Any],
    db: AsyncSession,
) -> dict[str, Any]:
    node_type = node["type"]
    configuration = render_template(node.get("configuration", {}), context)
    handlers = {
        "ai_prompt": execute_ai_prompt,
        "api_request": execute_api_request,
        "condition": execute_condition,
        "delay": execute_delay,
        "database": execute_database,
        "webhook": execute_webhook,
        "email": execute_email,
        "scheduler": execute_scheduler,
        "logic": execute_logic,
        "file_processing": execute_file_processing,
    }
    return await handlers[node_type](configuration, context, db)


async def execute_ai_prompt(
    configuration: dict[str, Any],
    context: dict[str, Any],
    db: AsyncSession,
) -> dict[str, Any]:
    prompt = configuration.get("prompt")
    if not prompt:
        raise NodeExecutionError("AI prompt node requires a prompt")
    if not settings.openai_api_key:
        raise NodeExecutionError("OPENAI_API_KEY is required for ai_prompt nodes")

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.responses.create(
        model=configuration.get("model", settings.openai_model),
        input=str(prompt),
    )
    return {
        "text": response.output_text,
        "model": configuration.get("model", settings.openai_model),
        "token_usage": getattr(response.usage, "total_tokens", 0) if response.usage else 0,
    }


async def execute_api_request(
    configuration: dict[str, Any],
    context: dict[str, Any],
    db: AsyncSession,
) -> dict[str, Any]:
    url = configuration.get("url")
    method = str(configuration.get("method", "GET")).upper()
    if not url:
        raise NodeExecutionError("API request node requires a url")
    async with httpx.AsyncClient(timeout=settings.workflow_node_timeout_seconds) as client:
        response = await client.request(
            method,
            url,
            headers=configuration.get("headers") or {},
            json=configuration.get("json"),
            params=configuration.get("params"),
        )
    response.raise_for_status()
    return {
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "body": _parse_response_body(response),
    }


async def execute_condition(
    configuration: dict[str, Any],
    context: dict[str, Any],
    db: AsyncSession,
) -> dict[str, Any]:
    operations = {
        "eq": operator.eq,
        "ne": operator.ne,
        "gt": operator.gt,
        "gte": operator.ge,
        "lt": operator.lt,
        "lte": operator.le,
        "contains": lambda left, right: right in left if left is not None else False,
    }
    op_name = configuration.get("operator", "eq")
    if op_name not in operations:
        raise NodeExecutionError(f"Unsupported condition operator: {op_name}")
    left = resolve_path(context, str(configuration.get("left", "$")))
    right = configuration.get("right")
    return {"result": bool(operations[op_name](left, right)), "left": left, "right": right}


async def execute_delay(
    configuration: dict[str, Any],
    context: dict[str, Any],
    db: AsyncSession,
) -> dict[str, Any]:
    seconds = int(configuration.get("seconds", 0))
    if seconds < 0 or seconds > 3600:
        raise NodeExecutionError("Delay seconds must be between 0 and 3600")
    await asyncio.sleep(seconds)
    return {"delayed_seconds": seconds}


async def execute_database(
    configuration: dict[str, Any],
    context: dict[str, Any],
    db: AsyncSession,
) -> dict[str, Any]:
    query = str(configuration.get("query", "")).strip()
    if not query.lower().startswith("select"):
        raise NodeExecutionError("Database node only allows SELECT queries")
    result = await db.execute(text(query), configuration.get("params") or {})
    rows = [_json_safe(dict(row._mapping)) for row in result.fetchall()]
    return {"rows": rows, "row_count": len(rows)}


async def execute_webhook(
    configuration: dict[str, Any],
    context: dict[str, Any],
    db: AsyncSession,
) -> dict[str, Any]:
    if "payload" not in configuration:
        configuration["payload"] = context
    return await execute_api_request(
        {
            "url": configuration.get("url"),
            "method": "POST",
            "headers": configuration.get("headers") or {},
            "json": configuration.get("payload"),
        },
        context,
        db,
    )


async def execute_email(
    configuration: dict[str, Any],
    context: dict[str, Any],
    db: AsyncSession,
) -> dict[str, Any]:
    required_settings = [
        settings.smtp_host,
        settings.smtp_username,
        settings.smtp_password,
        settings.smtp_from_email,
    ]
    if any(value is None for value in required_settings):
        raise NodeExecutionError("SMTP settings are required for email nodes")
    recipient = configuration.get("to")
    subject = configuration.get("subject")
    body = configuration.get("body")
    if not recipient or not subject or not body:
        raise NodeExecutionError("Email node requires to, subject, and body")

    message = EmailMessage()
    message["From"] = settings.smtp_from_email
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_username,
        password=settings.smtp_password,
        start_tls=settings.smtp_use_tls,
    )
    return {"sent": True, "to": recipient, "subject": subject}


async def execute_scheduler(
    configuration: dict[str, Any],
    context: dict[str, Any],
    db: AsyncSession,
) -> dict[str, Any]:
    delay_seconds = int(configuration.get("delay_seconds", 0))
    if delay_seconds < 0 or delay_seconds > 86400:
        raise NodeExecutionError("Scheduler delay_seconds must be between 0 and 86400")
    if delay_seconds:
        await asyncio.sleep(delay_seconds)
    return {"released": True, "delay_seconds": delay_seconds}


async def execute_logic(
    configuration: dict[str, Any],
    context: dict[str, Any],
    db: AsyncSession,
) -> dict[str, Any]:
    operation = configuration.get("operation", "set")
    if operation == "set":
        return {"value": configuration.get("value")}
    if operation == "merge":
        values = configuration.get("values")
        if not isinstance(values, list):
            raise NodeExecutionError("Merge operation requires a values list")
        merged: dict[str, Any] = {}
        for value in values:
            if not isinstance(value, dict):
                raise NodeExecutionError("Merge values must be objects")
            merged.update(value)
        return merged
    if operation == "pick":
        keys = configuration.get("keys")
        if not isinstance(keys, list):
            raise NodeExecutionError("Pick operation requires a keys list")
        return {key: context.get(key) for key in keys}
    raise NodeExecutionError(f"Unsupported logic operation: {operation}")


async def execute_file_processing(
    configuration: dict[str, Any],
    context: dict[str, Any],
    db: AsyncSession,
) -> dict[str, Any]:
    content = configuration.get("content", "")
    encoding = configuration.get("encoding", "plain")
    if encoding == "base64":
        content = base64.b64decode(content).decode("utf-8")
    if not isinstance(content, str):
        raise NodeExecutionError("File processing content must be text")

    mode = configuration.get("mode", "text_stats")
    if mode == "text_stats":
        words = [word for word in content.split() if word]
        return {"characters": len(content), "lines": len(content.splitlines()), "words": len(words)}
    if mode == "csv_rows":
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        return {"rows": rows, "row_count": len(rows)}
    raise NodeExecutionError(f"Unsupported file processing mode: {mode}")


def _parse_response_body(response: httpx.Response) -> Any:
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        return response.json()
    return response.text


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value
