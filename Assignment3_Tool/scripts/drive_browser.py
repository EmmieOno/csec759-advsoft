"""Log in to DVWA, optionally set its security level, and submit id=1."""

import os
import sys

from playwright.sync_api import sync_playwright


BASE = os.environ.get("PROXY_BASE", "http://localhost:8888").rstrip("/")
ALLOWED_SECURITY_LEVELS = {"low", "medium", "high", "impossible"}


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: drive_browser.py <case_page>")

    page_name = sys.argv[1].lstrip("/")
    if not page_name:
        raise SystemExit("case_page cannot be empty")

    user = os.environ.get("DVWA_USER")
    password = os.environ.get("DVWA_PASS")
    if not user or not password:
        raise SystemExit("set DVWA_USER and DVWA_PASS in your shell")

    security_level = os.environ.get("DVWA_SECURITY_LEVEL")
    if security_level and security_level not in ALLOWED_SECURITY_LEVELS:
        raise SystemExit(
            "DVWA_SECURITY_LEVEL must be low, medium, high, or impossible"
        )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)

        try:
            page = browser.new_context().new_page()

            response = page.goto(f"{BASE}/login.php")
            if response is None or response.status >= 400:
                raise RuntimeError("could not load the DVWA login page")

            page.locator('input[name="username"]').fill(user)
            page.locator('input[name="password"]').fill(password)
            page.locator('input[name="Login"]').click()
            page.wait_for_load_state("domcontentloaded")

            if "login.php" in page.url:
                raise RuntimeError("DVWA login failed; still on login.php")

            print("DVWA login succeeded")

            if security_level:
                response = page.goto(f"{BASE}/security.php")
                if response is None or response.status >= 400:
                    raise RuntimeError("could not load DVWA security.php")

                page.locator('select[name="security"]').select_option(
                    security_level
              )
                page.locator('input[name="seclev_submit"]').click()
                page.wait_for_load_state("domcontentloaded")

                selected_level = page.locator(
                    'select[name="security"]'
                ).input_value()
                print("DVWA security level:", selected_level)

                if selected_level != security_level:
                    raise RuntimeError(
                        f"requested {security_level}, but DVWA selected "
                        f"{selected_level}"
                    )

            target_url = f"{BASE}/{page_name}"
            response = page.goto(target_url)
            if response is None or response.status >= 400:
                raise RuntimeError(f"could not load test page: {target_url}")

            id_dropdown = page.locator('select[name="id"]')
            if id_dropdown.count() > 0:
                id_dropdown.select_option("1")
            else:
                id_input = page.locator('input[name="id"]')
                if id_input.count() == 0:
                    raise RuntimeError(
                        f"no id field found on {page.url}"
                    )
                id_input.fill("1")

            page.locator('input[name="Submit"]').click()
            page.wait_for_load_state("domcontentloaded")
            page.locator('input[name="Submit"]').click()
            page.wait_for_load_state("domcontentloaded")

            body = page.locator("body").inner_text()
            print("final url:", page.url)
            print("body:", body[:200].replace("\n", " "))

            if "ROWS=" not in body:
                print(
                    "WARNING: expected ROWS=<n> in the response. "
                    "Check that this page uses the expected form."
                )
        finally:
            browser.close()


if __name__ == "__main__":
    main()

