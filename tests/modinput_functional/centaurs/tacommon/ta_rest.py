try:
    from urllib import urlencode  ## Python 2
except ImportError:
    from urllib.parse import urlencode  ## Python 3
import json
from httplib2 import Http

__all__ = [
    "splunkd_request",
    "parse_entries",
    "get_session_key",
]


def splunkd_request(
    splunkd_uri,
    session_key,
    endpoint,
    app,
    user="nobody",
    method="GET",
    query=None,
    payload=None,
    timeout=None,
):
    # Query
    query = query or {}
    query["output_mode"] = "json"
    query = urlencode(query)

    # Payload
    payload = urlencode(payload) if payload else ""

    # URL
    if user and app:
        namespace = f"NS/{user}/{app}"
    else:
        namespace = ""
    url_temp = "{splunkd_uri}/services{namespace}/{endpoint}?{query}"
    url = url_temp.format(
        splunkd_uri=splunkd_uri.strip(),
        namespace=namespace,
        endpoint=endpoint.strip("/"),
        query=query,
    )

    # Header
    headers = {
        "Connection": "keep-alive",
        "User-Agent": "curl/7.53.1",
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": str(len(payload)),
    }

    # Authorization
    if session_key:
        headers["Authorization"] = "Splunk %s" % session_key

    # HTTP Request
    http = Http(
        timeout=timeout or 30,
        disable_ssl_certificate_validation=True,
    )
    return http.request(
        url,
        method=method,
        headers=headers,
        body=payload,
    )


def parse_entries(content):
    entries = json.loads(content)["entry"]
    for entry in entries:
        entry["content"]["name"] = entry["name"]
    return [entry["content"] for entry in entries]


def get_session_key(splunkd_uri, username, password):
    credentials = {
        "username": username,
        "password": password,
    }
    response, content = splunkd_request(
        splunkd_uri,
        None,
        "auth/login",
        app=None,
        method="POST",
        payload=credentials,
    )
    try:
        return json.loads(content)["sessionKey"]
    except KeyError:
        raise Exception("Login Failed: %s" % content)


def get_stanza(splunkd_uri, session_key, app_name, conf_name, stanza):
    response, content = splunkd_request(
        splunkd_uri,
        session_key,
        f"configs/conf-{conf_name}/{stanza}",
        app=app_name,
        method="GET",
    )
    return json.loads(content)
