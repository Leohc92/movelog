"""Incrementally import COROS China activities without committing raw exports."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import tempfile
import urllib.error
import urllib.parse
import urllib.request

from coros_fit import read_activity

API = "https://teamcnapi.coros.com"
OUTPUT = Path(__file__).resolve().parents[1] / "src/static/activities.json"


class CorosSyncError(RuntimeError):
    pass


def result_code(result):
    code = str(result.get("result", result.get("code", "unknown")))
    return code if code.isdigit() and len(code) <= 12 else "unknown"


def request_json(path, data=None, headers=None):
    body = json.dumps(data).encode() if data is not None else None
    request = urllib.request.Request(
        API + path,
        data=body,
        headers={
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "MoveLog COROS Sync",
            "Origin": "https://t.coros.com",
            **(headers or {}),
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def sync(account, password, output=OUTPUT):
    login = request_json(
        "/account/login",
        {
            "account": account,
            "accountType": 2,
            "pwd": hashlib.md5(password.encode()).hexdigest(),
        },
    )
    token = (login.get("data") or {}).get("accessToken")
    if not token:
        raise CorosSyncError(
            f"COROS login failed (status {result_code(login)}); check the account, password, and region"
        )
    print("COROS authentication succeeded", flush=True)
    headers = {"accesstoken": token}
    activities = []
    seen_ids = set()
    page = 1
    while True:
        result = request_json(
            f"/activity/query?modeList=&pageNumber={page}&size=20", headers=headers
        )
        data = result.get("data")
        batch = data.get("dataList") if isinstance(data, dict) else None
        # COROS can return null rather than [] after the final page.
        if batch is None and activities and result_code(result) == "0000":
            break
        if not isinstance(batch, list):
            raise CorosSyncError(
                f"Unexpected COROS activity list on page {page} after {len(activities)} records (status {result_code(result)})"
            )
        if not batch:
            break
        for activity in batch:
            label_id = activity.get("labelId")
            if label_id is None:
                continue
            label_id = str(label_id)
            if label_id in seen_ids:
                raise CorosSyncError(
                    "COROS returned a repeated page; published data was not changed"
                )
            seen_ids.add(label_id)
            activities.append(activity)
        page += 1
    if not activities:
        raise CorosSyncError(
            "COROS returned no activities; existing published data was kept"
        )
    print(f"Retrieved {len(activities)} COROS activities", flush=True)
    previous = json.loads(output.read_text()) if output.exists() else []
    previous_by_id = {str(a["coros_id"]): a for a in previous if "coros_id" in a}

    with tempfile.TemporaryDirectory(prefix="movelog-coros-") as folder:

        def import_activity(item):
            label_id = str(item["labelId"])
            old = previous_by_id.get(label_id, {})
            if old.get("coros_fit_imported"):
                return old
            code = item.get("sportType")
            if code is None:
                raise CorosSyncError(
                    "An activity has no COROS sport type; import stopped"
                )
            params = urllib.parse.urlencode(
                {"labelId": label_id, "sportType": code, "fileType": 4}
            )
            result = request_json("/activity/detail/download?" + params, {}, headers)
            url = (result.get("data") or {}).get("fileUrl")
            parsed = urllib.parse.urlparse(url or "")
            if parsed.scheme != "https" or not (parsed.hostname or "").endswith(
                ".coros.com"
            ):
                raise CorosSyncError(
                    f"COROS did not return a valid FIT download (status {result_code(result)}); import stopped"
                )
            path = Path(folder) / (label_id + ".fit")
            with urllib.request.urlopen(url, timeout=120) as response:
                path.write_bytes(response.read())
            return read_activity(
                path,
                label_id,
                int(code),
                previous=old,
                timezone_name=os.environ.get("COROS_TIMEZONE", "Asia/Shanghai"),
            )

        with ThreadPoolExecutor(max_workers=4) as pool:
            exported = list(pool.map(import_activity, activities))
    exported.sort(key=lambda a: a["start_date"], reverse=True)
    temporary = output.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(exported, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(output)
    print(f"Synced {len(exported)} COROS activities")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("account", nargs="?", default=os.environ.get("COROS_ACCOUNT"))
    parser.add_argument("password", nargs="?", default=os.environ.get("COROS_PASSWORD"))
    args = parser.parse_args()
    if not args.account or not args.password:
        parser.error("Configure COROS_ACCOUNT and COROS_PASSWORD first")
    try:
        sync(args.account, args.password)
    except Exception as error:
        # Avoid printing credentials, session headers, or download URLs in CI logs.
        detail = (
            str(error)
            if isinstance(error, CorosSyncError)
            else f"HTTP {error.code}"
            if isinstance(error, urllib.error.HTTPError)
            else type(error).__name__
        )
        print(f"COROS sync failed: {detail}; published data was not changed")
        raise SystemExit(1)
