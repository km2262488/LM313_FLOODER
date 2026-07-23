#!/usr/bin/env python3
# ----------------------------------------------------------------------------------------------
# LM_313 Load Tester 
# Usage: python3 LM_313.py https://target.com 50 600 20
# ----------------------------------------------------------------------------------------------

import urllib.request
import urllib.error
import threading
import random
import time
import sys
import os
from collections import Counter

# ==================== BANNER ASCII ====================
BANNER = """
                                                                                                  
 ░██         ░███     ░███              ░██████    ░██    ░██████     
░██         ░████   ░████             ░██   ░██ ░████   ░██   ░██    
░██         ░██░██ ░██░██                   ░██   ░██         ░██    
░██         ░██ ░████ ░██               ░█████    ░██     ░█████     
░██         ░██  ░██  ░██                   ░██   ░██         ░██    
░██         ░██       ░██             ░██   ░██   ░██   ░██   ░██    
░██████████ ░██       ░██ ░██████████  ░██████  ░██████  ░██████     
                                                                     
        """

def tampilkan_banner():
    """Tampilkan banner dengan efek berkedip."""
    for _ in range(3):
        os.system('clear' if os.name == 'posix' else 'cls')
        print(BANNER)
        time.sleep(0.4)
        os.system('clear' if os.name == 'posix' else 'cls')
        time.sleep(0.2)
    print(BANNER)

# ==================== KONFIGURASI ====================
url = ''
request_counter = 0
error_counter = 0
response_times = []
error_codes = Counter()
lock = threading.Lock()
stop_flag = False
TIMEOUT = 20
MAX_RETRY = 5

headers_useragents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15'
]

def usage():
    print("--------------------------------------------------")
    print('USAGE: python3 LM_313.py https://target.com 50 600 20')
    print("-------------------------------------------------")

def build_params():
    if "?" in url:
        return "&" + ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5)) + "=1"
    else:
        return "?" + ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5)) + "=1"

def http_call():
    global request_counter, error_counter, stop_flag
    while not stop_flag:
        retry = 0
        success = False
        while retry < MAX_RETRY and not success and not stop_flag:
            try:
                target = url + build_params()
                req = urllib.request.Request(target)
                req.add_header('User-Agent', random.choice(headers_useragents))
                req.add_header('Cache-Control', 'no-cache')

                start_time = time.time()
                with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                    code = resp.getcode()
                    resp_time = (time.time() - start_time) * 1000
                    with lock:
                        request_counter += 1
                        response_times.append(resp_time)
                    if not stop_flag:
                        # TAMPILKAN URL DI SETIAP RESPON SUKSES
                        print(f"[{code}] {resp_time:.0f}ms - Total: {request_counter} - URL: {url}")
                    success = True

            except urllib.error.HTTPError as e:
                retry += 1
                if retry == MAX_RETRY:
                    with lock:
                        error_counter += 1
                        request_counter += 1
                        error_codes[e.code] += 1
                    if not stop_flag:
                        print(f"[{e.code}] HTTP Error setelah {MAX_RETRY}x retry - URL: {url}")

            except urllib.error.URLError as e:
                retry += 1
                if retry == MAX_RETRY:
                    with lock:
                        error_counter += 1
                        error_codes['TIMEOUT'] += 1
                    if not stop_flag:
                        print(f"[TIMEOUT] Setelah {MAX_RETRY}x retry - URL: {url}")

            except Exception as e:
                retry += 1
                if retry == MAX_RETRY:
                    with lock:
                        error_counter += 1
                        error_codes['OTHER'] += 1
                    if not stop_flag:
                        print(f"[ERR] Setelah {MAX_RETRY}x retry - URL: {url}")

            time.sleep(0.2)
        time.sleep(0.05)

def monitor(total_requests):
    global stop_flag
    start = time.time()
    while request_counter < total_requests and not stop_flag:
        with lock:
            err_rate = (error_counter / request_counter * 100) if request_counter > 0 else 0
            ok = request_counter - error_counter
        # TAMPILKAN URL DI PROGRESS
        print(f"Progress: {request_counter}/{total_requests} | OK: {ok} | Err: {error_counter} | {err_rate:.1f}% | Target: {url}")
        time.sleep(2)

    stop_flag = True
    elapsed = time.time() - start
    time.sleep(0.5)
    print_summary(elapsed)

def print_summary(elapsed):
    print("\n" + "="*50)
    print(" LM_313 TEST SELESAI")
    print("="*50)
    print(f"Target URL : {url}")
    print(f"Threads : {threads} | Timeout : {TIMEOUT}s | Retry : {MAX_RETRY}x")
    print(f"Total Request : {request_counter}")
    print(f"Berhasil : {request_counter - error_counter} ({((request_counter-error_counter)/request_counter*100):.1f}%)")
    print(f"Gagal : {error_counter} ({(error_counter/request_counter*100):.1f}%)")
    print(f"Waktu Total : {elapsed:.2f} detik")
    print(f"RPS Rata-rata : {request_counter/elapsed:.2f}" if elapsed > 0 else "RPS: 0")

    if response_times:
        print(f"Response Time : Min {min(response_times):.0f}ms | Avg {sum(response_times)/len(response_times):.0f}ms | Max {max(response_times):.0f}ms")

    if error_codes:
        print("\n--- Breakdown Error ---")
        for code, count in error_codes.most_common():
            print(f" {code}: {count}x")
    print("="*50 + "\n")

# ==================== EKSEKUSI UTAMA ====================
if __name__ == "__main__":
    tampilkan_banner()

    if len(sys.argv) < 2:
        usage()
        sys.exit()

    url = sys.argv[1]
    threads = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    total_requests = int(sys.argv[3]) if len(sys.argv) > 3 else 500
    TIMEOUT = int(sys.argv[4]) if len(sys.argv) > 4 else 30

    if not url.startswith("http"):
        url = "https://" + url

    print(f"\nMulai test ke: {url}")
    print(f"Threads: {threads} | Target: {total_requests} | Timeout: {TIMEOUT}s | Retry: {MAX_RETRY}x\n")

    monitor_thread = threading.Thread(target=monitor, args=(total_requests,))
    monitor_thread.start()

    thread_list = []
    for i in range(threads):
        t = threading.Thread(target=http_call)
        t.start()
        thread_list.append(t)

    for t in thread_list:
        t.join()
    monitor_thread.join()
