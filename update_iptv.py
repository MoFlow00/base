import asyncio
import os
import subprocess
import sys

os.environ["ELECTRON_DISABLE_GPU"] = "1"

async def run_update():

    print("Starting CloakBrowser inside Debian Termux...")

    launch_kwargs = {
        "headless": False,
        "humanize": True,
        "args": [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-gpu-sandbox",
            "--disable-extensions",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-breakpad",
            "--disable-sync",
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

        print(f"Navigating to: {url}")

        await page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=90000
        )

        print("Waiting timer unlock...")

        await asyncio.sleep(15)

        print("Trying click...")

        await page.click("#create-btn", force=True)

        print("Waiting credentials fields...")

        await page.wait_for_selector(
            "input[readonly]",
            timeout=90000
        )

        inputs = await page.locator(
            "input[readonly]"
        ).all()

        print(f"Inputs found: {len(inputs)}")

        if len(inputs) >= 3:

            user = await inputs[1].get_attribute("value")
            pw = await inputs[2].get_attribute("value")

            print(f"USERNAME: {user}")
            print(f"PASSWORD: {pw}")

            base_file = "/root/base/base.m3u"
            final_file = "/root/base/final.m3u"

            if os.path.exists(base_file):

                with open(base_file, "r", encoding="utf-8") as f:
                    content = f.read()

                content = content.replace(
                    "{USERNAME}",
                    user
                ).replace(
                    "{PASSWORD}",
                    pw
                )

                with open(final_file, "w", encoding="utf-8") as f:
                    f.write(content)

                print("final.m3u generated")

                os.chdir("/root/base")

                subprocess.run([
                    "git",
                    "config",
                    "--local",
                    "user.name",
                    "Termux Debian Bot"
                ])

                subprocess.run([
                    "git",
                    "config",
                    "--local",
                    "user.email",
                    "debian@termux.bot"
                ])

                subprocess.run([
                    "git",
                    "add",
                    "final.m3u"
                ])

                status = subprocess.run(
                    [
                        "git",
                        "commit",
                        "-m",
                        "Auto update final.m3u"
                    ],
                    capture_output=True,
                    text=True
                )

                if "nothing to commit" in status.stdout:

                    print("No changes detected")

                else:

                    subprocess.run([
                        "git",
                        "push"
                    ])

                    print("GitHub push success")

            else:

                print("base.m3u missing")

        else:

            print("Inputs structure mismatch")

        screenshot_path = "/root/base/final_debug.png"

        await page.screenshot(
            path=screenshot_path
        )

        print(f"Screenshot saved: {screenshot_path}")

        await asyncio.sleep(10)

    except Exception as e:

        print(f"Execution error: {e}")

        try:

            await page.screenshot(
                path="/root/base/error_debug.png"
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
