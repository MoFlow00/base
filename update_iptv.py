import asyncio
import os
import subprocess
import sys


async def run_update():

    print("Starting CloakBrowser Stealth Engine...")

    launch_kwargs = {
        "headless": False,
        "humanize": True,
        "args": [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-extensions",
            "--no-first-run",
            "--single-process",
            "--no-zygote"
        ]
    }

    try:
        from cloakbrowser import launch_context_async

    except ImportError:
        print("cloakbrowser not installed")
        sys.exit(1)

    context = None

    try:

        print("Launching browser...")

        context = await launch_context_async(**launch_kwargs)

        page = await context.new_page()

        url = "https://freeiptv2023-d.ottc.xyz/?action=view"

        print(f"Opening URL: {url}")

        await page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        print("Waiting for unlock button...")

        await asyncio.sleep(10)

        buttons = await page.locator("button").all()

        print(f"Found buttons: {len(buttons)}")

        for i, btn in enumerate(buttons):

            try:
                text = await btn.inner_text()
                print(f"Button {i}: {text}")

            except:
                pass

        await asyncio.sleep(2)

        print("Clicking create button...")

        await page.click("#create-btn")

        print("Waiting credentials fields...")

        await page.wait_for_selector(
            "input[readonly]",
            timeout=60000
        )

        inputs = await page.locator("input[readonly]").all()

        if len(inputs) >= 3:

            user = await inputs[1].get_attribute("value")
            password = await inputs[2].get_attribute("value")

            print(f"SUCCESS USER: {user}")
            print(f"SUCCESS PASSWORD: {password}")

            screenshot_path = "/root/projects/success.png"

            await page.screenshot(path=screenshot_path)

            print(f"Screenshot saved: {screenshot_path}")

        else:

            print("Inputs structure mismatch")

    except Exception as e:

        print(f"Execution error: {e}")

        try:
            await page.screenshot(
                path="/root/projects/error.png"
            )

            print("Error screenshot saved")

        except:
            pass

        raise e

    finally:

        if context:
            await context.close()

        print("Browser closed")


if __name__ == "__main__":
    asyncio.run(run_update())
