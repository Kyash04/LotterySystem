import time
import random
import threading
import signal
import string
import os
from datetime import datetime, timedelta

# Globals
users = set()
lock = threading.Lock()
log_file = 'lottery_log.txt'
backup_file = 'backup_users.txt'
start_time = datetime.now()
registration_period = timedelta(minutes=1)
extended_period = timedelta(minutes=1)
registration_end_time = start_time + registration_period
next_backup_time = time.time() + 30  # every 30 seconds
extended = False
running = True

# Logging
def log(msg):
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")

# Backup
def save_backup():
    with open(backup_file, 'w') as f:
        for user in users:
            f.write(f"{user}\n")

def load_backup():
    if os.path.exists(backup_file):
        with open(backup_file, 'r') as f:
            for line in f:
                users.add(line.strip())

# Announcing time
def time_announcer():
    while running:
        time.sleep(30)  # every 30 seconds
        with lock:
            if running:
                time_left = max((registration_end_time - datetime.now()).total_seconds(), 0)
                sec = int(time_left)
                print(f"\n[INFO] Time remaining for registration: {sec} second(s)")
                print(f"[INFO] Registered users: {len(users)}\n")

# Handling signals
def signal_handler(sig, frame):
    print("\n[INFO] Program interrupted. Saving progress...")
    with lock:
        save_backup()
        log("Program interrupted. Backup saved.")
        print("[INFO] Backup saved. Exiting.")
    exit(0)

# Checking for valid username
def is_valid_username(username):
    if not username:
        return False
    allowed = string.ascii_letters + string.digits + "_"
    return all(char in allowed for char in username)

# Registration
def register_users():
    global registration_end_time, extended, running, next_backup_time

    while datetime.now() < registration_end_time:
        username = input("Enter a unique username to register: ").strip()

        if not is_valid_username(username):
            print("[ERROR] Invalid username. Use letters, digits, and underscores only.")
            continue

        with lock:
            if username in users:
                print("[ERROR] Username already registered.")
                continue

            users.add(username)
            log(f"User registered: {username}")
            print(f"[INFO] {username} registered successfully. Total users: {len(users)}")

        # Saving backup every 30 seconds
        if time.time() > next_backup_time:
            with lock:
                save_backup()
                next_backup_time = time.time() + 30

    # Checking if extension is needed
    if len(users) < 5 and not extended:
        print("\n[INFO] Less than 5 users registered. Extending registration by 30 minutes...")
        registration_end_time = datetime.now() + extended_period
        extended = True
        register_users()  # Recursively call for extension
    elif len(users) == 0:
        print("[INFO] No users registered. Exiting.")
        log("No users registered. Lottery ended with no participants.")
        running = False
        return

# Selecting Winner
def pick_winner():
    print("\n[INFO] Registration period ended.")
    if len(users) == 0:
        print("[INFO] No participants. Exiting.")
        return

    winner = random.choice(list(users))
    print("\n🎉🎉🎉 Lottery Winner 🎉🎉🎉")
    print(f"Winner: {winner}")
    print(f"Total Participants: {len(users)}")
    print("Thank you for participating!")

    log(f"Winner declared: {winner}")
    log(f"Total Participants: {len(users)}")

    # Cleaning up backup file
    if os.path.exists(backup_file):
        os.remove(backup_file)

# === Main Function ===
def main():
    print("=== Welcome to the Terminal Lottery System ===")
    print("Registration is open for 1 minutes.")
    print("You will be prompted to enter your username.")

    signal.signal(signal.SIGINT, signal_handler)
    load_backup()

    # Starting time announced
    announcer = threading.Thread(target=time_announcer, daemon=True)
    announcer.start()

    # Begin registration
    register_users()

    # Draw winner
    if running:
        pick_winner()

# === Entry Point ===
if __name__ == "__main__":
    main()
