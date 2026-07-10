import asyncio

import os

import subprocess

import sys

import requests

from datetime import datetime



# --- Configuration ---

BOT_TOKEN = "8843435187:AAGIrQnBPbsyXu959Oq95MGIvo92Q9JTeGM"  # Replace with your actual bot token

CHAT_ID = "365163909"



# --- Telegram Notification Functions ---

def send_message(text):

    """Sends a text message to the Telegram chat."""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {

        "chat_id": CHAT_ID,

        "text": text,

        "parse_mode": "HTML"

    }

    try:

        response = requests.post(url, json=payload, timeout=10)

        response.raise_for_status()

        print(f"Telegram message sent: {text}")

    except requests.exceptions.RequestException as e:

        print(f"Failed to send Telegram message: {e}")



async def send_photo(path, caption=""):

    """Sends a photo to the Telegram chat."""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    payload = {

        "chat_id": CHAT_ID,

        "caption": caption,

        "parse_mode": "HTML"

    }

    try:

        with open(path, "rb") as photo_file:

            files = {"photo": photo_file}

            response = requests.post(url, data=payload, files=files, timeout=30)

            response.raise_for_status()

            print(f"Telegram photo sent: {path}")

    except requests.exceptions.RequestException as e:

        print(f"Failed to send Telegram photo: {e}")

    except FileNotFoundError:

        print(f"Screenshot file not found: {path}")

    except Exception as e:

        print(f"An unexpected error occurred while sending photo: {e}")



# --- Helper for Screenshots ---

async def take_screenshot(page, attempt_num, suffix="debug"):

    """Takes a full-page screenshot with a timestamped filename."""

    if not page:

        print("Cannot take screenshot: page object is None.")

        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    screenshot_dir = "/root/projects"

    os.makedirs(screenshot_dir, exist_ok=True) # Ensure directory exists

    screenshot_path = os.path.join(screenshot_dir, f"attempt{attempt_num}_{timestamp}_{suffix}.png")

    try:

        await page.screenshot(path=screenshot_path, full_page=True)

        print(f"Screenshot saved: {screenshot_path}")

        return screenshot_path

    except Exception as e:

        print(f"Failed to take screenshot: {e}")

        return None



os.environ["ELECTRON_DISABLE_GPU"] = "1"



async def run_update():

    print("Starting CloakBrowser inside Debian Termux...")

    send_message("🚀 IPTV Job Started")



    launch_kwargs = {

        "headless": False,

        "humanize": True,



    }



    try:

        from cloakbrowser import launch_context_async

    except ImportError:

        print("cloakbrowser not installed")

        send_message("❌ Script Error: cloakbrowser not installed. Exiting.")

        sys.exit(1)



    # Variables to track overall status

    final_context = None

    github_push_success = False

    attempts_used = 0

    script_success = False # True if the main logic completes successfully



    try: # Outer try block for final context cleanup

        for attempt_num in range(1, 4):

            attempts_used = attempt_num

            context = None

            page = None

            print(f"\n--- Starting Attempt {attempt_num} ---")



            try:

                print("Launching browser...")

                context = await launch_context_async(**launch_kwargs)

                final_context = context # Keep track of the current context for final cleanup

                page = await context.new_page()



                url = "https://freeiptv2023-d.ottc.xyz/?action=view"

                print(f"Navigating to: {url}")



                await page.goto(

                    url,

                    wait_until="domcontentloaded",

                    timeout=90000

                )



                # --- Attempt-specific logic for waiting and page checks ---

                if attempt_num == 1:

                    print("Waiting timer unlock (Attempt 1 - 15s)...")

                    await asyncio.sleep(15)

                else: # Attempt 2 and 3

                    print("Waiting timer unlock (Attempt 2/3 - 12s)...")

                    await asyncio.sleep(12)



                    # Check page content and reload if necessary

                    for reload_check in range(1, 4): # Max 3 reloads

                        print(f"Performing page content check (Reload attempt {reload_check})...")

                        content = await page.content()

                        needs_reload = False



                        if "are you a robot?" in content.lower(): # Case-insensitive check

                            print("Detected 'Are you a robot?'.")

                            needs_reload = True

                        if "request has been denied" in content.lower(): # Case-insensitive check

                            print("Detected 'request has been denied'.")

                            needs_reload = True



                        # Check if create button is missing or not visible

                        create_btn_locator = page.locator("#create-btn")

                        is_create_btn_visible = False

                        try:

                            # Use a short timeout for visibility check to avoid long waits if element is truly missing

                            is_create_btn_visible = await create_btn_locator.is_visible(timeout=5000)

                        except Exception as e:

                            # If locator itself fails (e.g., element never appears in DOM), treat as not visible

                            print(f"Error checking visibility of #create-btn: {e}")

                            is_create_btn_visible = False



                        if not is_create_btn_visible:

                            print("Create button (#create-btn) is not visible or not found.")

                            needs_reload = True

                        else:

                            print("Create button (#create-btn) is visible.")



                        if needs_reload:

                            if reload_check < 3:

                                print(f"Page issues detected. Reloading page (Reload {reload_check}/3)...")

                                await page.reload(wait_until="domcontentloaded", timeout=90000)

                                await asyncio.sleep(12)

                            else:

                                raise Exception("Page content issues persisted after multiple reloads.")

                        else:

                            print("Page content looks good and create button is visible.")

                            break # Exit reload loop if content is fine



                print("Trying click on #create-btn...")

                await page.click("#create-btn", force=True)



                print("Waiting for credentials fields (input[readonly])...")

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



                    base_file = "/root/projects/base.m3u"

                    final_file = "/root/projects/final.m3u"



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



                        # Git operations

                        original_cwd = os.getcwd()

                        try:

                            os.chdir("/root/projects")



                            # Configure Git user

                            subprocess.run([

                                "git", "config", "--local", "user.name", "Termux Debian Bot"

                            ], check=True, capture_output=True, text=True)

                            subprocess.run([

                                "git", "config", "--local", "user.email", "debian@termux.bot"

                            ], check=True, capture_output=True, text=True)



                            # Add the file

                            subprocess.run(["git", "add", "-A"], check=True, capture_output=True, text=True)



                            # Commit changes

                            commit_status = subprocess.run(

                                [

                                    "git", "commit", "-m", "Auto update final.m3u"

                                ],

                                capture_output=True,

                                text=True,

                                check=False # Don't raise error for no changes

                            )



                            output = (commit_status.stdout + commit_status.stderr).lower()



                            if "nothing to commit" in output or "nothing added to commit" in output:

                                print("No changes detected, no commit needed.")

                                github_push_success = True # Consider it a success if nothing to commit

                            elif commit_status.returncode != 0:

                                raise Exception(f"Git commit failed: {commit_status.stderr.strip()}")

                            else:

                                print("Changes committed.")

                                # Push changes

                                push_status = subprocess.run(["git", "push"], capture_output=True, text=True, check=False)



                                if push_status.returncode == 0:

                                    print("GitHub push success")

                                    github_push_success = True

                                else:

                                    raise Exception(f"Git push failed: {push_status.stderr.strip()}")

                                # Push changes

                                push_status = subprocess.run([

                                    "git", "push"

                                ], capture_output=True, text=True, check=False)



                                if push_status.returncode == 0:

                                    print("GitHub push success")

                                    github_push_success = True

                                else:

                                    raise Exception(f"Git push failed: {push_status.stderr.strip()}")

                        except subprocess.CalledProcessError as git_e:

                            raise Exception(f"Git command failed: {git_e.cmd} -> {git_e.stderr.strip()}")

                        except Exception as git_e:

                            raise Exception(f"An error occurred during Git operations: {git_e}")

                        finally:

                            os.chdir(original_cwd) # Restore original CWD



                    else:

                        raise Exception("base.m3u missing at /root/projects/base.m3u")



                else:

                    raise Exception(f"Inputs structure mismatch: Expected at least 3 inputs, found {len(inputs)}")



                # If we reach here, the current attempt was successful

                script_success = True

                break # Exit the retry loop



            except Exception as e:

                error_message = str(e)

                print(f"Attempt {attempt_num} failed: {error_message}")



                # Take screenshot and send to Telegram

                screenshot_path = await take_screenshot(page, attempt_num, "error")

                caption_text = f"❌ Attempt {attempt_num} Failed\nReason: {error_message}"

                if attempt_num == 3:

                    caption_text = f"🚨 Final Failure\nReason: {error_message}"



                if screenshot_path:

                    await send_photo(screenshot_path, caption=caption_text)

                else:

                    send_message(f"{caption_text}\n(Screenshot failed or not taken)")



                # Close browser for the failed attempt

                if context:

                    await context.close()

                    print(f"Browser closed for failed attempt {attempt_num}")

                

                # If it's the final attempt, re-raise the exception

                if attempt_num == 3:

                    send_message(f"🚨 Final Failure\nReason: {error_message}") # Redundant but ensures message if photo fails

                    raise e # Re-raise the exception after final failure notification



    finally:

        # Ensure the last active browser context is closed

        if final_context:

            await final_context.close()

            print("Browser closed.")



        # Send final success/failure notification

        if script_success:

            push_status_msg = "Success" if github_push_success else "Failed/No changes"

            send_message(f"✅ IPTV Updated Successfully\nAttempts Used: {attempts_used}\nGitHub Push: {push_status_msg}")

        else:

            # This block is reached if all attempts failed and the last exception was caught by the outer try-except

            # or if an error occurred outside the retry loop.

            # The final failure message would have been sent by the last attempt's except block.

            print("Script finished without overall success.")



if __name__ == "__main__":

    try:

        asyncio.run(run_update())

    except Exception as main_e:

        print(f"Script terminated with an unhandled error: {main_e}")

