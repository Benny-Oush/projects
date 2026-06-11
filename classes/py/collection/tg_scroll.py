import time
import pyautogui

wait_time = 0.3
press_time = 2    

text = "הסקריפט הכללי פעיל!"
print(text[::-1])

count = 1

while True:
    
    try:
        time.sleep(wait_time)
        text = f"...למטה לחץ על {count} מס' לחיצות רצף מתחיל"
        print(text)

        count += 1
        
        end_time = time.time() + press_time
        
        while time.time() < end_time:
            pyautogui.press('pagedown')
            time.sleep(0.01)
        text = "להמתנה חוזר הסתיים. הלחיצות סבב"
        print(text)
        

    except Exception as e:
        print(f"שגיאה: {e}")