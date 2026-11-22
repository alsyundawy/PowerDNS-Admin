import requests
from urllib.parse import urljoin, urlsplit
from flask import Response, current_app, jsonify, request

from ..models import Setting


def forward_request():
    pdns_api_url = Setting().get('pdns_api_url')
    pdns_api_key = Setting().get('pdns_api_key')
    headers = {}
    data = None

    msg_str = "Sending request to powerdns API {0}"

    if request.method != 'GET' and request.method != 'DELETE':
        msg = msg_str.format(request.get_json(force=True, silent=True))
        current_app.logger.debug(msg)
        data = request.get_json(force=True, silent=True)

    verify = Setting().get('verify_ssl_connections')

    headers = {
        'user-agent': 'powerdns-admin/api',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'accept': 'application/json; q=1',
        'X-API-KEY': pdns_api_key
    }

    # Build a safe relative path from the incoming request path and query string
    parsed_path = urlsplit(request.path)
    if parsed_path.scheme or parsed_path.netloc:
        return Response(response='{"error":"invalid request path"}',
                        status=400,
                        mimetype="application/json")

    safe_path = request.path.lstrip("/")
    relative_path = safe_path
    if request.query_string:
        # request.query_string is bytes; decode safely to str
        relative_path = relative_path + "?" + request.query_string.decode("utf-8", "ignore")

    url = urljoin(pdns_api_url.rstrip("/") + "/", relative_path)

    resp = requests.request(request.method,
                            url,
                            headers=headers,
                            verify=verify,
                            json=data)

    return resp


def make_forward_response(resp):
    if resp.status_code == 204 or not resp.content:
        return "", resp.status_code
    try:
        data = resp.json()
        return jsonify(data), resp.status_code
    except Exception:
        return Response(response=resp.content, status=resp.status_code, mimetype="application/json")
