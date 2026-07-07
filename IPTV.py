import asyncio
import os
import subprocess
import sys
import requests
import time
from datetime import datetime
import traceback # Import traceback for detailed error logging

#--- Configuration ---
# BOT_TOKEN and CHAT_ID should be passed as environment variables in GitHub Actions secrets.
# Using os.getenv allows setting them via environment variables or falling back to defaults.
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_DEFAULT_BOT_TOKEN") # Replace with a placeholder or remove default
CHAT_ID = os.getenv("CHAT_ID", "YOUR_DEFAULT_CHAT_ID")     # Replace with a placeholder or remove default
LOG_FILE = "iptv_last_result.txt" # Changed to a relative path, suitable for GitHub Actions workspace

#--- Telegram Notification Functions ---
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    for attempt in range(3):
        print(f"Attempting to send Telegram message (attempt {attempt + 1}/3)...")
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            print("Telegram message sent successfully.")
            return True
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")
            time.sleep(2)
    print("Failed to send Telegram message after multiple attempts.")
    return False

async def run_update():
    start_time = datetime.now()
    current_step = "Initialization"
    script_success = False
    no_changes = False
    attempts_used = 0
    last_error = "None"
    username = "N/A"
    github_push_success = False

    print(f"[START] Script started at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        from cloakbrowser import launch_context_async
    except ImportError:
        print("Error: cloakbrowser not found. Please ensure it's installed in your GitHub Actions workflow.")
        print("You might need `pip install cloakbrowser` and potentially `playwright install` if it's Playwright-based.")
        sys.exit(1)

    final_context = None # Initialize final_context outside the loop

    try:
        for attempt_num in range(1, 4):
            attempts_used = attempt_num
            print(f"\n[ATTEMPT {attempt_num}/3] Starting update attempt...")
            try:
                current_step = "Launch Browser"
                print(f"[STEP] {current_step}")
                # Changed headless=False to headless=True for GitHub Actions environment.
                # GitHub Actions runners are typically headless Linux environments.
                final_context = await launch_context_async(headless=True, humanize=True)
                print("Browser context launched successfully.")

                current_step = "Open Website"
                print(f"[STEP] {current_step}")
                page = await final_context.new_page()
                print(f"Navigating to https://freeiptv2023-d.ottc.xyz/?action=view")
                await page.goto("https://freeiptv2023-d.ottc.xyz/?action=view", wait_until="domcontentloaded", timeout=90000)
                print("Website loaded.")

                current_step = "Wait Timer"
                print(f"[STEP] {current_step}")
                print("Waiting for 15 seconds...")
                await asyncio.sleep(15)
                print("Wait complete.")

                current_step = "Click Create Button"
                print(f"[STEP] {current_step}")
                print("Clicking '#create-btn'...")
                await page.click("#create-btn", force=True)
                await page.wait_for_selector("input[readonly]", timeout=90000)
                print("Create button clicked and input fields appeared.")

                current_step = "Read Credentials"
                print(f"[STEP] {current_step}")
                inputs = await page.locator("input[readonly]").all()
                if len(inputs) >= 3:
                    username = await inputs[1].get_attribute("value")
                    pw = await inputs[2].get_attribute("value")
                    print(f"Credentials read: Username='{username}', Password='{'*' * len(pw)}'")
                else:
                    raise ValueError("Could not find enough input fields for credentials.")

                current_step = "Sync Git Repository"
                print(f"[STEP] {current_step}")
                print("Configuring Git user...")
                res = subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=True, capture_output=True, text=True)
                print(f"Command: {' '.join(res.args)}\nSTDOUT:\n{res.stdout.strip()}\nSTDERR:\n{res.stderr.strip()}")
                res = subprocess.run(["git", "config", "--global", "user.name", "GitHub Actions"], check=True, capture_output=True, text=True)
                print(f"Command: {' '.join(res.args)}\nSTDOUT:\n{res.stdout.strip()}\nSTDERR:\n{res.stderr.strip()}")

                print("Fetching latest changes from origin...")
                res = subprocess.run(["git", "fetch", "origin"], check=True, capture_output=True, text=True)
                print(f"Command: {' '.join(res.args)}\nSTDOUT:\n{res.stdout.strip()}\nSTDERR:\n{res.stderr.strip()}")

                print("Resetting local branch to origin/main...")
                res = subprocess.run(["git", "reset", "--hard", "origin/main"], check=True, capture_output=True, text=True)
                print(f"Command: {' '.join(res.args)}\nSTDOUT:\n{res.stdout.strip()}\nSTDERR:\n{res.stderr.strip()}")

                local_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
                remote_hash = subprocess.check_output(["git", "rev-parse", "origin/main"]).decode().strip()
                print(f"Current Local Commit: {local_hash}\nCurrent Remote Commit: {remote_hash}")

                current_step = "Generate final.m3u"
                print(f"[STEP] {current_step}")
                print("Reading base.m3u...")
                with open("base.m3u", "r", encoding="utf-8") as f: content = f.read()
                print("Writing final.m3u with updated credentials...")
                with open("final.m3u", "w", encoding="utf-8") as f: f.write(content.replace("{USERNAME}", username).replace("{PASSWORD}", pw))
                print("final.m3u generated.")

                print("Adding final.m3u to Git staging area...")
                res = subprocess.run(["git", "add", "final.m3u"], check=True, capture_output=True, text=True)
                print(f"Command: {' '.join(res.args)}\nSTDOUT:\n{res.stdout.strip()}\nSTDERR:\n{res.stderr.strip()}")

                print("Attempting to commit changes...")
                res = subprocess.run(["git", "commit", "-m", "Auto update final.m3u"], capture_output=True, text=True)
                print(f"Command: {' '.join(res.args)}\nSTDOUT:\n{res.stdout.strip()}\nSTDERR:\n{res.stderr.strip()}")

                if "nothing to commit" in (res.stdout + res.stderr).lower():
                    no_changes = True
                    github_push_success = True
                    print("No changes detected in final.m3u. Skipping Git push.")
                else:
                    current_step = "Git Push"
                    print(f"[STEP] {current_step}")
                    print("Pushing changes to origin/main...")
                    res = subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True, text=True)
                    print(f"Command: {' '.join(res.args)}\nSTDOUT:\n{res.stdout.strip()}\nSTDERR:\n{res.stderr.strip()}")
                    github_push_success = True
                    print("Git push successful.")

                script_success = True
                print(f"[ATTEMPT {attempt_num}/3] Update successful!")
                break # Exit the retry loop on success

            except subprocess.CalledProcessError as e:
                last_error = f"Git command failed: {e}\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}"
                print(f"Error at {current_step}: {last_error}")
                if attempt_num < 3:
                    print(f"Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    raise # Re-raise on final attempt failure
            except Exception as e:
                last_error = traceback.format_exc() # Capture full traceback
                print(f"Error at {current_step}: {e}\n{last_error}")
                if attempt_num < 3:
                    print(f"Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    raise # Re-raise on final attempt failure
            finally:
                if final_context:
                    print("Closing browser context...")
                    await final_context.close()
                    final_context = None # Reset for next attempt if needed, or ensure it's closed
                    print("Browser context closed.")

    except Exception as e:
        # This catches exceptions re-raised from the inner loop or critical failures outside it
        last_error = traceback.format_exc()
        print(f"Critical Failure at {current_step}: {e}\n{last_error}")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"\n[END] Script finished at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total execution time: {duration:.2f} seconds.")

    # Generate Report
    report = (
        f"Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Success: {script_success}\n"
        f"Attempts Used: {attempts_used}\n"
        f"Username: {username}\n"
        f"GitHub Push: {github_push_success}\n"
        f"No Changes: {no_changes}\n"
        f"Last Error: {last_error}\n"
        f"Execution Time Seconds: {duration:.2f}\n"
    )
    print(f"Writing final report to {LOG_FILE}...")
    with open(LOG_FILE, "w") as f: f.write(report)
    print("Report written.")

    # Notification
    print("Sending Telegram notification...")
    if script_success:
        msg = "No Changes Detected" if no_changes else "GitHub Push: Success"
        send_message(f"✅ IPTV Updated Successfully\n\n{msg}\nDuration: {int(duration)}s")
    else:
        send_message(f"🚨 IPTV Update Failed\n\nFailure Step: {current_step}\nReason: {last_error}")
    print("Telegram notification sent (or attempted).")

if __name__ == "__main__":
    asyncio.run(run_update())
