from time import sleep, time
import threading




def foo():
    sleep(2)
    return 12

t0 = time()
thread = threading.Thread(target=foo, args=())

a = thread.start()

while time() < t0 + 10:
    print("\r", a)
    sleep(0.5)

