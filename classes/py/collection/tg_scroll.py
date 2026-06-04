import time
import pyautogui

wait_time = 60
press_time = 2    

text = "הסקריפט הכללי פעיל!"
print(text[::-1])


while True:
    try:
        time.sleep(wait_time)
        text = "מתחיל רצף לחיצות על חץ למטה..."
        print(text[::-1])
        
        end_time = time.time() + press_time
        
        while time.time() < end_time:
            pyautogui.press('pagedown')
            time.sleep(0.01)
        text = "סבב הלחיצות הסתיים. חוזר להמתנה."
        print(text[::-1])
        
    except Exception as e:
        print(f"שגיאה: {e}")