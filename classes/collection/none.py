import math
import random
def IsHot(fahrenheit):
  celsius = (fahrenheit - 32) / 1.8
  return celsius
for i in range(math.floor(random.random() * 101), 101, 13):
  celsius = IsHot(i)
  fixedcelsius = f"{celsius:.2f}"
  if (celsius >= 28):
    print(f"temperature: {fixedcelsius} \nit is hot")
  elif celsius < 28 and celsius >= 10:
    print(f"temperature: {fixedcelsius} \nit is comfortable")
  else:
    print(f"temperature: {fixedcelsius} \nit is cold")
