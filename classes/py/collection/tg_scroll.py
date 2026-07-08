import time
import pyautogui

wait_time = 300
press_time = 2    

text = "הסקריפט הכללי פעיל!"
print(text[::-1])

count = 1

while True:
    
    try:
        time.sleep(wait_time)
        
        print(f"Starts pressing sequence number {count}")

        count += 1
        
        end_time = time.time() + press_time
        
        while time.time() < end_time:
            pyautogui.press('pagedown')
            time.sleep(0.01)
      
        print("the pressing round has ended successfully. Returning to standby mode.")
        

    except Exception as e:
        print(f"שגיאה: {e}")