import requests
import time
import subprocess
import json
import sys

print("Starting app.py...")
with open("app_out.txt", "w") as out:
    p = subprocess.Popen([r".\venv\Scripts\python.exe", "app.py"], stdout=out, stderr=subprocess.STDOUT)
    
print("Waiting 15 seconds for TF to init...")
time.sleep(15) 

if p.poll() is not None:
    print("app.py exited prematurely with code", p.returncode)
    with open("app_out.txt", "r") as f:
        print(f.read())
    sys.exit(1)

try:
    print("\n--- Triggering Training ---")
    r1 = requests.post("http://127.0.0.1:5000/api/train")
    if r1.status_code == 200:
        print("Response:", r1.json())
    else:
        print("Training API Failed:", r1.status_code)
    
    print("\nWarning: Waiting 60 seconds for training to complete in background...")
    time.sleep(60)
    
    print("\n--- Testing Chat ---")
    headers = {"Content-Type": "application/json"}
    payload = {"message": "what is the fee?"}
    r2 = requests.post("http://127.0.0.1:5000/chat", headers=headers, json=payload)
    if r2.status_code == 200:
        print("Chat Response:", json.dumps(r2.json(), indent=2))
    else:
        print("Chat API Failed:", r2.status_code, r2.text)

finally:
    print("\nTerminating app.py...")
    p.terminate()
    p.wait()
    print("Done.")
