import random   
import time
import datetime
responses = ["wow 😲", "interesting 🤔", "cool 😎"]
def say(text):
  print(text)
  time.sleep(1)
current_hour = datetime.datetime.now().hour
if current_hour < 12:
  greeting = "good morning!"
elif current_hour < 18:
  greeting = "good afternoon!"
elif current_hour < 21:
  greeting = "good evening!"
else:
  greeting = "good night!"
noise_words = ["i", "am", "I'm", "my", "name", "is", "im", "you", "can", "call", "me", "called", "they", "hi.", "hi,", ".", ",", "there,", "there", "hi", "hi!", "there!", "hello!", "hello,", "hello"]
while True:
  name_input = input(f"{greeting} what is your name? ").strip()
  words = name_input.lower().replace("'", "").replace("’", "").split()
  name_parts = []
  for w in words:
    if w not in noise_words:
      name_parts.append(w)
  clean_name = " ".join(name_parts).capitalize()
  if clean_name:
    break 
  else:
    say("I didn't catch your name, can you try again? ")
say(f"Nice to meet you, {clean_name}!")
while True:
    age_input = input("how old are you? ").strip()
    numbers = [int(w) for w in age_input.split() if w.isdigit()]    
    if numbers:
        found_age = numbers[0]
        if 9 < found_age < 75:
            age = found_age      
            say(f"You are {age} years older than me. I'm barely a few days old! 😁")
            break
        else:
            say("please enter your real age... 🙃")
    else:
        say("please use numbers 🙏")   
say(random.choice(responses))
color_list = ["red", "blue", "green", "yellow", "orange", "pink", "purple" ,"black", "white", "gray", "grey", "brown", "turquoise", "cyan", "gold", "silver"]
while True:
  color_input = input(f"so {clean_name}, what's your favorite color? ").strip().lower()
  found_color = None
  for color in color_list:
    if color in color_input:
      found_color = color
      break  
  if found_color:
    say(f"Oh, {found_color} is a beautiful color!")
    break 
  else:
    say("that doesn't look like a color name 😕, please enter a color 🙏")
say(f"it was a pleasure talking to you, {clean_name}. have a nice day!")