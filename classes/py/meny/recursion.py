from time import sleep 

def star(n):
    if n > 0:
        print("*", end="", flush=True)
        sleep(0.1)
        star(n - 1)

def revarse(n):
    if n:
        print(n % 10, end="")
        revarse(n // 10)