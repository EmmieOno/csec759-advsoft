"""Log in to DVWA through the mitmproxy port and submit id=1 on one case page.

This replaces the manual browser steps: log in, open the page, type 1, press Submit.
Usage:  python3 scripts/drive_browser.py a2_filtered.php
Env:    DVWA_USER, DVWA_PASS (required), PROXY_BASE (default http://localhost:8888)
Needs Playwright's Chromium: `playwright install chromium` if it is missing.
"""
import os
import sys

from playwright.sync_api import sync_playwright

BASE = os.environ.get("PROXY_BASE", "http://localhost:8888").rstrip("/")


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: drive_browser.py <case_page.php>")
    page_name = sys.argv[1]
    user, pw = os.environ.get("DVWA_USER"), os.environ.get("DVWA_PASS")
    if not user or not pw:
        sys.exit("set DVWA_USER and DVWA_PASS in your shell")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context().new_page()

        page.goto(f"{BASE}/login.php")
        page.fill("input[name=username]", user)
        page.fill("input[name=password]", pw)
        page.click("input[name=Login]")
        page.wait_for_load_state()
        if "login.php" in page.url:
            print("LOGIN FAILED: still on login page")
            browser.close()
            sys.exit(3)

        page.goto(f"{BASE}/{page_name}")
        page.fill("input[name=id]", "1")
        page.click("input[name=Submit]")
        page.wait_for_load_state()

        body = page.inner_text("body")
        print("final url:", page.url)
        print("body:", body[:200].replace("\n", " "))
        if "ROWS=" not in body:
            print("WARNING: expected ROWS=<n> in the page for id=1 (page missing or rejected?)")
        browser.close()


if __name__ == "__main__":
    main()
