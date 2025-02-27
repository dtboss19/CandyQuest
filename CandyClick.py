import pyautogui
import time
import os
import keyboard  # pip install keyboard

# ---------------------------
# CONFIGURATION
# 
# TOO START, YOU WILL NEED TO INSTALL TELEGRAM AND OPEN THE CANDY QUEST BOT
# YOU WILL NEED TO FIGURE OUT THE DIMENSIONS TO CAPTURE THE GAME WINDOW
# VERY IMPORTANT THAT YOU CAPTURE THE ENTIRE GAME WINDOW.
# ---------------------------
# Replace 14-17 with your dimensions
window_left = 1300  
window_top = 8
window_width = 700
window_height = 1000

# Screenshot path for debugging
screenshot_path = os.path.join(os.getcwd(), 'game_window_screenshot.png')

# Page settings
page_count = 2
page_delay = 2

# Hotkey pause toggle
paused = False

# Paths to images
# You will need to right click images and COPY PATH and paste each once into the correct box below
GREEN_BOX_PATH = r"" #green_box_ready.png goes here
BLUE_BOX_PATH = r""#blue_box_ready.png goes here
PRESENT_BOX_PATH = r""#present_box_ready.png goes here
START_BUTTON_PATH = r""#Yellow_start_button.png goes here
POPUP_PATH = r""      #Start_button_popup.png goes here
BIG_CANDY_WORKING = r"" #big_candy_working.png goes here
BIG_CANDY_BOX = r"" #big_blue_arrow.png goes here
BIG_CANDY_PRESENT = r""#big_candy_present.png goes here

# Region of the game window
region = (window_left, window_top, window_width, window_height)

# ---------------------------
# HOTKEY / PAUSE HANDLING
# USES F12 to pause the script from running
# ---------------------------
def toggle_pause():
    global paused
    paused = not paused
    if paused:
        print("[DEBUG] Script paused. Press F12 to resume.")
    else:
        print("[DEBUG] Script resumed.")

keyboard.add_hotkey('F12', toggle_pause)
print("[DEBUG] Hotkey F12 registered for pause/resume.")

# ---------------------------
# SCREEN / IMAGE FUNCTIONS
# Each cycle of main loop will update the capture window
# ---------------------------
def capture_game_window(): 
    """Capture a screenshot for debugging."""
    try:
        ss = pyautogui.screenshot(region=region)
        ss.save(screenshot_path)
        print(f"[DEBUG] Saved screenshot to: {screenshot_path}")
    except Exception as e:
        print(f"[ERROR] capture_game_window failed: {e}")

# ---------------------------
# LOCATE FUNCTIONS
# Each of these uses confidence to match with the pngs provided, you can change
# the values that work best for you.
# ---------------------------

def locate_start_quest_popup(confidence=0.7):
    """
    Return True if the custom popup image is found in the region.
    """
    try:
        found = pyautogui.locateOnScreen(POPUP_PATH, region=region, confidence=confidence)
        return found is not None
    except Exception:
        return False

def locate_start_button(confidence=0.6):
    """Locate the 'Start' button image if present."""
    try:
        btn = pyautogui.locateOnScreen(START_BUTTON_PATH, region=region, confidence=confidence)
        if btn:
            print("[DEBUG] Found START button.")
        return btn
    except Exception:
        return None

def locate_green_boxes(confidence=0.6):
    try:
        return list(pyautogui.locateAllOnScreen(GREEN_BOX_PATH, region=region, confidence=confidence))
    except Exception:
        return []

def locate_blue_boxes(confidence=0.6):
    try:
        return list(pyautogui.locateAllOnScreen(BLUE_BOX_PATH, region=region, confidence=confidence))
    except Exception:
        return []

def locate_present_boxes(confidence=0.6):
    try:
        return list(pyautogui.locateAllOnScreen(PRESENT_BOX_PATH, region=region, confidence=confidence))
    except Exception:
        return []

# Big Candy functions (for the big piece of candy)
def locate_big_candy_working(confidence=0.65):
    try:
        found = pyautogui.locateOnScreen(BIG_CANDY_WORKING, region=region, confidence=confidence)
        return found is not None
    except Exception:
        return False

def locate_big_candy_box(confidence=0.65):
    try:
        found = pyautogui.locateOnScreen(BIG_CANDY_BOX, region=region, confidence=confidence)
        return found is not None
    except Exception:
        return False

def locate_big_candy_present(confidence=0.85):
    try:
        return list(pyautogui.locateAllOnScreen(BIG_CANDY_PRESENT, region=region, confidence=confidence))
    except Exception:
        return []

# ---------------------------
# AUTOMATE CLICK
# This function automates the clicking needed to be done.
# ---------------------------
def click_button(x, y):
    pyautogui.click(x, y)
    print(f"[DEBUG] Clicked at: ({x}, {y})")

# ---------------------------
# POPUP HANDLING
# Explicilty handles the win when you press the present and it brings up 
# the start quest page.
# ---------------------------
def handle_start_quest_popup(timeout=8):
    """
    If the 'Start Quest' popup is detected, repeatedly try to locate and click
    the 'Start' button for up to 'timeout' seconds.
    """
    print("[DEBUG] Detected 'Start Quest' popup. Handling it now...")
    end_time = time.time() + timeout
    while time.time() < end_time:
        while paused:
            time.sleep(10)
        btn = locate_start_button()
        if btn:
            sx, sy = pyautogui.center(btn)
            click_button(sx, sy)
            print("[DEBUG] Clicked START button; returning to normal flow.")
            time.sleep(1.5)
            return
        time.sleep(0.5)
    print("[DEBUG] Could not find START button before timeout. Moving on...")

# ---------------------------
# MAIN LOOP that contiounsly automates the clicking
# ---------------------------
def main_loop():
    cycle = 0
    while True:
        cycle += 1
        print(f"\n[DEBUG] Beginning cycle #{cycle}")
        capture_game_window()
        while paused:
            time.sleep(10)

        # -- GREEN BOXES: Click at most 2 green boxes once per cycle
        green_boxes = locate_green_boxes()
        print(f"[DEBUG] Found {len(green_boxes)} green boxes.")
        for box in green_boxes[:2]:
            center = pyautogui.center(box)
            click_button(*center)

        # Process blue boxes on each page
        for page in range(1, page_count + 1):
            print(f"[DEBUG] Page {page}/{page_count}")
            blue_boxes = locate_blue_boxes()
            print(f"[DEBUG] Found {len(blue_boxes)} blue boxes.")
            # Process at most 10 blue boxes per page
            for b_box in blue_boxes[:10]:
                bx, by = pyautogui.center(b_box)
                click_button(bx, by)
                time.sleep(2)
                # Immediately assume a present box is there and click it.
                p_boxes = locate_present_boxes()
                if p_boxes:
                    print("[DEBUG] Found present box after blue box click; handling it.")
                    p_center = pyautogui.center(p_boxes[0])
                    click_button(*p_center)
                    time.sleep(2)
                    # Now, the popup should appear after clicking the present box.
                    if locate_start_quest_popup():
                        handle_start_quest_popup(timeout=8)
                    # Delay before processing the next blue box
                    time.sleep(2)
                else:
                    print("[DEBUG] No present box found after blue box click.")
                    if locate_start_quest_popup():
                        handle_start_quest_popup(timeout=8)
                    else:
                        print("[DEBUG] Breaking out of blue box loop.")
                        break

            # At the end of processing blue boxes on this page, check for any leftover present boxes.
            p_boxes_remaining = locate_present_boxes()
            if p_boxes_remaining:
                print("[DEBUG] Found leftover present boxes; handling them.")
                clickCount=0
                for p_box in p_boxes_remaining:
                    if clickCount >= 2:
                         print("[DEBUG] Reached click threshold for leftover present boxes; breaking out.")
                         break
                    p_center = pyautogui.center(p_box)
                    click_button(*p_center)
                    time.sleep(2)
                    if locate_start_quest_popup():
                        handle_start_quest_popup(timeout=8)
                    time.sleep(2)
            pyautogui.press('pagedown')
            print("[DEBUG] Pressed Page Down.")
            time.sleep(page_delay)

        pyautogui.press('pageup')
        print("[DEBUG] Pressed Page Up.")
        time.sleep(page_delay)

        # --- BIG CANDY PROCESSING EVERY 40 CYCLES ---
        if cycle % 40 == 0:
        #if cycle==1:
            print("[DEBUG] 40 cycles completed. Initiating big candy processing.")
            # Page up twice
            pyautogui.press('pageup')
            time.sleep(page_delay)
            pyautogui.press('pageup')
            time.sleep(page_delay)
            if locate_big_candy_working():
                print("[DEBUG] Big candy working detected. Page down twice and resume main loop.")
                pyautogui.press('pagedown')
                time.sleep(page_delay)
                pyautogui.press('pagedown')
                time.sleep(page_delay)
            else:
                print("[DEBUG] Big candy working NOT detected. Checking for big candy box.")
                if locate_big_candy_box():
                    print("[DEBUG] Big candy box detected. Handling it.")
                    bc_box = pyautogui.locateOnScreen(BIG_CANDY_BOX, region=region, confidence=0.65)
                    if bc_box:
                        bc_box_center = pyautogui.center(bc_box)
                        click_button(*bc_box_center)
                        time.sleep(2)
                        bc_present = pyautogui.locateOnScreen(BIG_CANDY_PRESENT, region=region, confidence=0.85)
                        if bc_present:
                            bc_present_center = pyautogui.center(bc_present)
                            click_button(*bc_present_center)
                            time.sleep(2)
                            if locate_start_quest_popup():
                                handle_start_quest_popup(timeout=8)
                                pyautogui.press('pagedown')
                                time.sleep(page_delay)
                                pyautogui.press('pagedown')
                                time.sleep(page_delay)
                        else:
                            print("[DEBUG] No big candy present found.")
                    else:
                        print("[DEBUG] Big candy box not detected.")
            # End of big candy processing; then resume main loop.

        print("[DEBUG] Cycle complete. Waiting 30s before next cycle.\n")
        time.sleep(30)

if __name__ == "__main__":
    print("[DEBUG] Starting main loop...")
    main_loop()
    input("Press Enter to exit...")
