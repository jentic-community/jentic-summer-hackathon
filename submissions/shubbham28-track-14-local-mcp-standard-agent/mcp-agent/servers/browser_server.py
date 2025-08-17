"""
TODO: Browser MCP server stub (e.g., Playwright/Puppeteer integration).

No business logic yet.
"""

from __future__ import annotations

import sys
import csv
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, List

from fastapi import FastAPI  # type: ignore
from pydantic import BaseModel  # type: ignore

# Ensure project root (mcp-agent) is importable when running directly
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from servers.shared.security import is_allowed_host  # noqa: E402
from urllib.parse import urlencode  # cleaned

app = FastAPI(title="Browser MCP Server", version="0.1.0")


class ToolRequest(BaseModel):
    action: str
    args: Dict[str, Any] = {}
    request_id: Optional[str] = None


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log(level: str, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    entry = {"ts": _ts(), "level": level, "message": message}
    if context:
        entry["context"] = context
    return entry


@app.post("/tool/browser_op")
def browser_op(req: ToolRequest) -> Dict[str, Any]:
    logs = [_log("INFO", "request.received", {"action": req.action})]

    if req.action not in {"open_title", "booking_search"}:
        logs.append(_log("ERROR", "validation.unsupported_action", {"action": req.action}))
        return {"ok": False, "error": {"type": "ValidationError", "message": "Unsupported action"}, "logs": logs}

    # Import lazily to avoid hard dependency when not used
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as e:  # pragma: no cover - optional dependency
        logs.append(_log("ERROR", "dependency.missing", {"error": str(e)}))
        return {"ok": False, "error": {"type": "DependencyError", "message": "Playwright not installed"}, "logs": logs}

    if req.action == "open_title":
        url = req.args.get("url")
        if not isinstance(url, str) or not url:
            logs.append(_log("ERROR", "validation.invalid_args", {"args": req.args}))
            return {"ok": False, "error": {"type": "ValidationError", "message": "Missing or invalid 'url'"}, "logs": logs}
        # Host allowlist
        if not is_allowed_host(url, ["booking.com", "localhost", "google.com", "example.org"]):
            logs.append(_log("ERROR", "security.disallowed_host", {"url": url}))
            return {"ok": False, "error": {"type": "SecurityError", "message": "Host not allowed"}, "logs": logs}
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_default_navigation_timeout(20000)
                page.set_default_timeout(20000)
                page.goto(url)
                title = page.title()
                browser.close()
            logs.append(_log("INFO", "browser.open_title.ok"))
            return {"ok": True, "result": {"title": title}, "logs": logs}
        except Exception as e:
            logs.append(_log("ERROR", "browser.open_title.failed", {"error": str(e)}))
            return {"ok": False, "error": {"type": "NavigationError", "message": str(e)}, "logs": logs}

    # booking_search
    city = req.args.get("city")
    n = req.args.get("n", 5)
    date_from = req.args.get("date_from")  # optional string YYYY-MM-DD
    date_to = req.args.get("date_to")

    if not isinstance(city, str) or not city.strip():
        logs.append(_log("ERROR", "validation.invalid_args", {"args": req.args}))
        return {"ok": False, "error": {"type": "ValidationError", "message": "Missing or invalid 'city'"}, "logs": logs}
    if not isinstance(n, int) or n <= 0:
        logs.append(_log("ERROR", "validation.invalid_args", {"args": req.args}))
        return {"ok": False, "error": {"type": "ValidationError", "message": "'n' must be positive int"}, "logs": logs}

    # Validate dates if provided
    valid_dates = False
    if date_from or date_to:
        if not (isinstance(date_from, str) and isinstance(date_to, str)):
            logs.append(_log("ERROR", "validation.invalid_dates", {"date_from": date_from, "date_to": date_to}))
            return {"ok": False, "error": {"type": "ValidationError", "message": "Provide both date_from and date_to as YYYY-MM-DD"}, "logs": logs}
        try:
            from datetime import datetime as _dt
            df = _dt.strptime(date_from, "%Y-%m-%d")
            dt = _dt.strptime(date_to, "%Y-%m-%d")
            if dt < df:
                raise ValueError("checkout before checkin")
            valid_dates = True
        except Exception as e:
            logs.append(_log("ERROR", "validation.invalid_dates", {"error": str(e)}))
            return {"ok": False, "error": {"type": "ValidationError", "message": "Invalid dates; expected YYYY-MM-DD and checkout>=checkin"}, "logs": logs}

    target_host_url = "https://www.booking.com/"
    if not is_allowed_host(target_host_url, ["booking.com", "localhost", "google.com", "example.org"]):
        logs.append(_log("ERROR", "security.disallowed_host", {"url": target_host_url}))
        return {"ok": False, "error": {"type": "SecurityError", "message": "Host not allowed"}, "logs": logs}

    artifacts_dir = PROJECT_ROOT / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    city_slug = city.lower().replace(" ", "_")
    csv_path = artifacts_dir / f"booking_{city_slug}.csv"
    screenshot_path = artifacts_dir / f"booking_{city_slug}.png"

    def _extract_float(text: str) -> Optional[float]:
        import re
        m = re.search(r"([0-9]+(?:\.[0-9]+)?)", text or "")
        try:
            return float(m.group(1)) if m else None
        except Exception:
            return None

    rows: List[Dict[str, Any]] = []
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.set_default_navigation_timeout(30000)
            page.set_default_timeout(30000)

            # Build direct search URL (more reliable than homepage form fill)
            base_url = "https://www.booking.com/searchresults.html"
            query: Dict[str, Any] = {
                "ss": city,
                "dest_type": "city",
                "group_adults": 2,
                "no_rooms": 1,
                "group_children": 0,
                "sb_travel_purpose": "leisure",
                "lang": "en-us",
            }
            if valid_dates:
                query.update({
                    "checkin": date_from,
                    "checkout": date_to,
                })
            full_url = f"{base_url}?{urlencode(query)}"

            # Navigate and ensure we remain on searchresults page
            page.goto(full_url, wait_until="domcontentloaded")
            try:
                page.wait_for_load_state("networkidle", timeout=12000)
            except Exception:
                pass

            # Some flows redirect to city canonical page; attempt recovery by following the
            # canonical searchresults link present on that page (it usually contains dest_id)
            if "searchresults" not in (page.url or ""):
                try:
                    # Try to find any link pointing to searchresults
                    link_el = page.wait_for_selector('a[href*="/searchresults"]', timeout=8000, state="attached")
                    href = link_el.get_attribute("href") if link_el else None
                    if href:
                        # Absolutize and inject dates if missing
                        try:
                            import urllib.parse as _up
                            abs_url = href
                            if href.startswith("/"):
                                abs_url = f"https://www.booking.com{href}"
                            # Append dates if required and not present
                            if valid_dates:
                                parsed = _up.urlparse(abs_url)
                                q = _up.parse_qs(parsed.query)
                                # Only add if not already provided
                                if "checkin" not in q or "checkout" not in q:
                                    q.update({"checkin": [date_from], "checkout": [date_to]})
                                    new_query = _up.urlencode({k: v[0] if isinstance(v, list) else v for k, v in q.items()})
                                    abs_url = _up.urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
                            page.goto(abs_url, wait_until="domcontentloaded")
                            try:
                                page.wait_for_load_state("networkidle", timeout=12000)
                            except Exception:
                                pass
                        except Exception:
                            # Fallback to original URL
                            page.goto(full_url, wait_until="domcontentloaded")
                    else:
                        # No link found; retry original URL once
                        page.goto(full_url, wait_until="domcontentloaded")
                except Exception:
                    # Any failure: retry original URL once
                    page.goto(full_url, wait_until="domcontentloaded")
                    try:
                        page.wait_for_load_state("networkidle", timeout=8000)
                    except Exception:
                        pass

            time.sleep(0.3)  # throttle

            # Accept cookies if prompt appears (best-effort, selector may vary)
            for sel in [
                'button:has-text("Accept")',
                'button:has-text("I agree")',
                'button[aria-label*="Accept"]',
            ]:
                try:
                    btn = page.query_selector(sel)
                    if btn:
                        btn.click()
                        time.sleep(0.2)
                        break
                except Exception:
                    continue

            # Wait for results to load (broaden selectors and wait for attachment)
            selectors = [
                '[data-testid="property-card"]',
                '[data-testid="property-list"]',
                '[data-testid="title-link"]',
                '#search_results_table',
            ]
            loaded = False
            for sel in selectors:
                try:
                    page.wait_for_selector(sel, timeout=45000, state="attached")
                    loaded = True
                    break
                except Exception:
                    continue
            if not loaded:
                raise RuntimeError("Search results did not load in time")

            cards = page.query_selector_all('[data-testid="property-card"]')
            if not cards:
                cards = page.query_selector_all('[data-testid="title-link"]')

            for card in cards[: n * 2]:  # scrape a few extra to handle missing fields
                try:
                    name_el = card.query_selector('[data-testid="title"]') or card.query_selector('[data-testid="title-link"]')
                    link_el = card.query_selector('a[data-testid="title-link"]') or card.query_selector('a')
                    price_el = card.query_selector('[data-testid="price-and-discounted-price"]')
                    rating_el = card.query_selector('[data-testid="review-score"] div')

                    name = (name_el.inner_text().strip() if name_el else None)
                    link = (link_el.get_attribute("href") if link_el else None)
                    price = (price_el.inner_text().strip() if price_el else None)
                    rating_text = (rating_el.inner_text().strip() if rating_el else None)
                    rating = _extract_float(rating_text) if rating_text else None

                    if not name and not link:
                        continue
                    rows.append({
                        "name": name,
                        "price": price,
                        "rating": rating,
                        "link": link,
                    })
                    if len(rows) >= n:
                        break
                    time.sleep(0.1)
                except Exception:
                    continue

            # Screenshot
            try:
                page.screenshot(path=str(screenshot_path), full_page=True)
            except Exception:
                page.screenshot(path=str(screenshot_path), full_page=False)

            browser.close()

        # Save CSV with header even if rows empty
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "price", "rating", "link"])
            writer.writeheader()
            for r in rows:
                writer.writerow({
                    "name": r.get("name", ""),
                    "price": r.get("price", ""),
                    "rating": r.get("rating", ""),
                    "link": r.get("link", ""),
                })

        preview = rows[: min(5, len(rows))]
        logs.append(_log("INFO", "browser.booking_search.ok", {"rows": len(rows), "with_dates": valid_dates}))
        return {
            "ok": True,
            "result": {
                "csv_path": str(csv_path),
                "screenshot_path": str(screenshot_path),
                "rows": preview,
            },
            "logs": logs,
        }
    except Exception as e:
        logs.append(_log("ERROR", "browser.booking_search.failed", {"error": str(e)}))
        return {"ok": False, "error": {"type": "NavigationError", "message": str(e)}, "logs": logs}


if __name__ == "__main__":
    import uvicorn  # type: ignore

    uvicorn.run(app, host="0.0.0.0", port=8003)
