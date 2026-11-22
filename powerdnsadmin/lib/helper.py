import json
from urllib.parse import urlsplit

import requests
from flask import Response, current_app, jsonify, request

from ..models import Setting


def forward_request():
    pdns_api_url = Setting().get("pdns_api_url")
    pdns_api_key = Setting().get("pdns_api_key")
    headers = {}
    data = None

    msg_str = "Sending request to powerdns API {0}"

    if request.method != "GET" and request.method != "DELETE":
        msg = msg_str.format(request.get_json(force=True, silent=True))
        current_app.logger.debug(msg)
        data = request.get_json(force=True, silent=True)

    verify = Setting().get("verify_ssl_connections")

    headers = {
        "user-agent": "powerdns-admin/api",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "accept": "application/json; q=1",
        "X-API-KEY": pdns_api_key,
    }

    # Validate and sanitize the target backend URL against SSRF
    base_parsed = urlsplit(pdns_api_url or "")
    if base_parsed.scheme not in ("http", "https") or not base_parsed.netloc:
        return Response(
            response='{"error":"invalid backend API configuration"}', status=500, mimetype="application/json"
        )

    # Sanitize incoming path to prevent protocol-relative host redirection
    req_path = request.path
    if not req_path.startswith("/"):
        req_path = "/" + req_path
    while req_path.startswith("//"):
        req_path = req_path[1:]

    base_prefix = base_parsed.path.rstrip("/")
    clean_path = req_path.lstrip("/")
    target_path = f"{base_prefix}/{clean_path}" if base_prefix else f"/{clean_path}"

    query_str = ""
    if request.query_string:
        # request.query_string is bytes; decode safely to str
        query_str = "?" + request.query_string.decode("utf-8", "ignore")

    url = f"{base_parsed.scheme}://{base_parsed.netloc}{target_path}{query_str}"

    # Verify that the target URL strictly matches the trusted backend scheme and host
    parsed_target = urlsplit(url)
    if parsed_target.scheme != base_parsed.scheme or parsed_target.netloc != base_parsed.netloc:
        return Response(response='{"error":"invalid request target"}', status=400, mimetype="application/json")

    resp = requests.request(request.method, url, headers=headers, verify=verify, json=data)

    return resp


def make_forward_response(resp):
    if isinstance(resp, Response):
        return resp
    if resp.status_code == 204 or not resp.content:
        return "", resp.status_code
    try:
        content_str = resp.content.decode("utf-8") if isinstance(resp.content, bytes) else str(resp.content)
        data = json.loads(content_str)
        return jsonify(data), resp.status_code
    except Exception:
        content_str = resp.content.decode("utf-8", "replace") if isinstance(resp.content, bytes) else str(resp.content)
        return Response(response=content_str, status=resp.status_code, mimetype="application/json")
