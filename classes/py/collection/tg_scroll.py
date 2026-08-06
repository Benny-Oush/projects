import time
import pyautogui

wait_time = 300  # 5 minutes
press_time = 2    
 
print("Scrolling script is running!\n")

count = 0

while True:
    
    try:
        time.sleep(wait_time)
        
        print(f"Starting a new pressing sequence...")

        count += 1
        
        end_time = time.time() + press_time
        
        while time.time() < end_time:
            pyautogui.press('pagedown')
            time.sleep(0.01)
      
        print("The pressing round has ended successfully. Returning to standby mode.")
        print(f'-- {count} -- sequences by now\n')
        

    except Exception as e:
        print(f"Error: {e}")