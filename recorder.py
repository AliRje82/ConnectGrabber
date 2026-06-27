import os
import time
import subprocess
from xvfbwrapper import Xvfb
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import traceback

CLASS_URL = os.environ.get("CLASS_URL")
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
RECORD_DURATION = int(os.environ.get("RECORD_DURATION", 3600))
OUTPUT_FILE = os.environ.get("OUTPUT_FILE", "/output/recording.mp4")

def start_recording():
    global CLASS_URL
    global USERNAME
    global PASSWORD
    global RECORD_DURATION
    global OUTPUT_FILE
    
    vdisplay = Xvfb(width=1920, height=1080, colordepth=24)
    vdisplay.start()

    subprocess.Popen(["pulseaudio", "--start", "--exit-idle-time=-1"])
    time.sleep(2)

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")

    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1920, 1080)
    
    if "?launcher=false" not in CLASS_URL:
        CLASS_URL += "?launcher=false" if "?" not in CLASS_URL else "&launcher=false"

    print("Navigating to login page...")
    driver.get(CLASS_URL)

    try:
        username_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "login")) 
        )
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys(USERNAME)
        password_field.send_keys(PASSWORD)
        
        login_button = driver.find_element(By.ID, "login-button")
        login_button.click()
        print("Login submitted. Waiting for Adobe Connect room to load...")
        
        time.sleep(15) 

        
        print("Attempting true hardware-level click via OS...")
        try:
            # 1. Prepare the environment to point to our specific Xvfb virtual monitor
            x_env = os.environ.copy()
            x_env["DISPLAY"] = f":{vdisplay.new_display}"
            
            
            xdotool_cmd = ["xdotool", "mousemove", "960", "580", "click", "1"]
            
            subprocess.run(xdotool_cmd, env=x_env, check=True)
            print("OS-level mouse moved and clicked successfully!")
            
            time.sleep(2)
            
            # Send the 'k' key as a backup
            body = driver.find_element(By.TAG_NAME, 'body')
            body.send_keys('k')
            print("Pressed 'k' key as backup.")
            
        except Exception as error:
            print(f"Hardware click failed: {error}")
            
        time.sleep(5) 
        

    except Exception as e:
        print(f"Error type: {type(e).__name__}")
        print(f"Error: {e}")
        traceback.print_exc()
        driver.save_screenshot("/tmp/error.png")
        driver.quit()
        vdisplay.stop()
        return

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "x11grab", "-s", "1920x1080", "-i", f":{vdisplay.new_display}",
        "-f", "pulse", "-i", "default",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(RECORD_DURATION),
        OUTPUT_FILE
    ]
    
    print(f"Starting recording for {RECORD_DURATION} seconds...")
    subprocess.run(ffmpeg_cmd)
    
    driver.quit()
    vdisplay.stop()
    print("Recording finished and saved!")

if __name__ == "__main__":
    start_recording()