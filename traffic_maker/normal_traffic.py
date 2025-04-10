#!/usr/bin/env python3
"""
Simplified Traffic Generator - Focus on Normal Traffic
Generates configurable, multi-threaded normal HTTP GET traffic with logging.
"""

import requests
import random
import time
import threading
import argparse
import logging

# --- Cấu hình Logging ---
# Ghi log ra file và console, thêm tên thread để dễ theo dõi
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s',
    handlers=[
	#logging.FileHandler("normal_traffic.log"),
        logging.StreamHandler() # Hiển thị ra màn hình
    ]
)

# --- Lớp Tạo Traffic Chính ---
class NormalTrafficGenerator:
    def __init__(self, target_url, num_threads=5, request_delay=1.0):
        # Đảm bảo URL kết thúc bằng dấu / để nối endpoint dễ dàng
        if not target_url.endswith('/'):
            target_url += '/'
        self.target_url = target_url
        self.num_threads = num_threads
        self.request_delay = request_delay # Độ trễ cơ bản giữa các request của 1 thread
        self.running = False
        self.threads = []

        # Danh sách User-Agent đa dạng
        self.user_agents = [
            # === Chrome ===
            # Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            # macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            # Linux
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            # Android
            "Mozilla/5.0 (Linux; Android 13; SM-G991U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36",

            # === Firefox ===
            # Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0", # Phiên bản mới
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0", # ESR (Extended Support Release)
            # macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0",
            # Linux
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            # Android
            "Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/114.0 Firefox/114.0",

            # === Safari ===
            # macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
            # iOS (iPhone & iPad)
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 15_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Mobile/15E148 Safari/604.1",

            # === Edge ===
            # Windows (Chromium-based)
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.41",

            # === Bots phổ biến ===
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.179 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)", # Googlebot Mobile
            "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)",
            # "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)" # Facebook crawler
        ]

        # Các endpoint "bình thường" phổ biến
        self.normal_endpoints = [
            # === Trang Cốt lõi ===
            "",                    # Thường dùng / thay vì ""
            "index.html",
            "index.php",           # Nếu dùng PHP
            "home",
            "about",
            "about-us",
            "contact",
            "contact-us",
            "products",
            "services",
            "portfolio",
            "blog",
            "news",
            "faq",
            "help",
            "support",

            # === Tài nguyên Tĩnh ===
            # CSS
            "/css/style.css",
            "/css/main.css",
            "/css/vendor.css",
            "/css/theme.css",
            # JavaScript
            "assets/js/main.js",
            "assets/js/script.js",
            "assets/js/vendor.js",
            "assets/js/analytics.js",
            "assets/js/app.js",
            # Hình ảnh
            "/images/logo.png",
            "/images/logo.svg",
            "/images/banner.jpg",
            "/images/hero.jpeg",
            "/images/icons/favicon.ico",
            "/images/icons/icon-cart.svg",
            "/images/image1.png",
            # Fonts
            "/fonts/opensans-regular.woff",
            "/fonts/roboto.ttf",
            # Khác
            "robots.txt",
            "sitemap.xml",
            "favicon.ico",

        

            # === Trang Chi tiết ===
            "/products/item/12345", # Ví dụ ID
            "/products/cool-widget-pro", # Ví dụ slug
            "/services/web-development",



            # === API Endpoints (Nếu có dùng phía client) ===
            # "/api/v1/products?limit=10&page=1",
            # "/api/v1/search?q=query",
            # "/api/v2/user/status",
            # "/api/notifications/count",

            # === Trang Tiện ích / Khác ===
            "/terms-of-service",
            "/privacy-policy",
            "/careers",
            "/download/document.pdf",
        ]

    def send_normal_request(self):
        """Gửi một request GET bình thường đến một endpoint ngẫu nhiên."""
        endpoint = random.choice(self.normal_endpoints)
        # Nối URL đích và endpoint (loại bỏ / nếu endpoint đã có sẵn)
        url = self.target_url + endpoint.lstrip('/')
        headers = {"User-Agent": random.choice(self.user_agents)}

        try:
            start_time = time.time()
            # Gửi request GET với timeout
            response = requests.get(url, headers=headers, timeout=10)
            elapsed = time.time() - start_time

            # Ghi log kết quả
            logging.info(f"GET {url} - Status: {response.status_code} - Time: {elapsed:.2f}s")

            # (Tùy chọn) Cảnh báo nếu gặp lỗi phía server (status >= 400)
            # if response.status_code >= 400:
            #    logging.warning(f"Potential Issue: GET {url} returned status {response.status_code}")

        except requests.exceptions.Timeout:
            logging.warning(f"TIMEOUT requesting {url}")
        except requests.exceptions.RequestException as e:
            # Ghi log các lỗi request khác (kết nối, DNS, ...)
            logging.error(f"Error requesting {url}: {str(e)}")

    def worker(self):
        """Hàm công việc cho mỗi thread, chỉ gửi normal request."""
        thread_name = threading.current_thread().name # Lấy tên thread để log rõ hơn
        logging.info(f"Worker {thread_name} started.")
        while self.running:
            # Chỉ gửi request bình thường
            self.send_normal_request()

            # Chờ một khoảng thời gian ngẫu nhiên dựa trên delay cơ bản
            # Ví dụ: delay 1.0s -> chờ từ 0.7s đến 1.3s
            sleep_time = self.request_delay * random.uniform(0.7, 1.3)
            time.sleep(sleep_time)
        logging.info(f"Worker {thread_name} stopping.")

    def start(self):
        """Bắt đầu các thread tạo traffic."""
        if self.running:
            logging.warning("Generator is already running.")
            return

        self.running = True
        logging.info(f"Starting generator: Target={self.target_url}, Threads={self.num_threads}, BaseDelay={self.request_delay}s")
        self.threads = [] # Xóa danh sách thread cũ (nếu có)
        # Tạo và khởi chạy các thread
        for i in range(self.num_threads):
            # Đặt tên cho thread để log dễ đọc hơn
            thread = threading.Thread(target=self.worker, name=f"Worker-{i+1}", daemon=True)
            thread.start()
            self.threads.append(thread)
        logging.info("All worker threads started.")

    def stop(self):
        """Dừng các thread tạo traffic một cách an toàn."""
        if not self.running:
            logging.warning("Generator is not running.")
            return

        logging.info("Stopping generator...")
        self.running = False # Ra tín hiệu cho các thread dừng vòng lặp while

        # Chờ các thread kết thúc công việc hiện tại và thoát ra
        # Đặt timeout để tránh bị treo nếu thread nào đó gặp vấn đề
        join_timeout = self.request_delay * 2 # Chờ tối đa gấp đôi delay cơ bản
        for thread in self.threads:
            thread.join(timeout=join_timeout)
            # (Tùy chọn) Kiểm tra xem thread còn sống không sau khi join
            # if thread.is_alive():
            #    logging.warning(f"Thread {thread.name} did not stop gracefully.")

        self.threads = [] # Xóa danh sách thread đã dừng
        logging.info("Generator stopped.")

# --- Hàm Chính và Xử lý Tham số Dòng lệnh ---
def main():
    parser = argparse.ArgumentParser(description="Normal HTTP Traffic Generator")
    # Các tham số cấu hình
    parser.add_argument("--url", default="http://localhost/", help="URL đích (mặc định: http://localhost/)")
    parser.add_argument("--threads", type=int, default=5, help="Số lượng luồng worker (mặc định: 5)")
    parser.add_argument("--delay", type=float, default=1.0, help="Độ trễ trung bình giữa các request/worker (giây, mặc định: 1.0)")
    parser.add_argument("--duration", type=int, default=2500, help="Thời gian chạy (giây, mặc định: 2500 ~ 12000 traffic)")

    args = parser.parse_args()

    # Kiểm tra cơ bản giá trị tham số
    if args.threads <= 0 or args.delay < 0 or args.duration <= 0:
         print("Lỗi: Số luồng, độ trễ, và thời gian chạy phải là số dương.")
         exit(1) # Thoát chương trình

    # Khởi tạo generator
    generator = NormalTrafficGenerator(
        target_url=args.url,
        num_threads=args.threads,
        request_delay=args.delay
    )

    try:
        generator.start() # Bắt đầu tạo traffic
        logging.info(f"Running for {args.duration} seconds. Press Ctrl+C to stop early.")

        # Giữ chương trình chính chạy trong thời gian quy định
        # Các thread worker sẽ làm việc trong nền
        end_time = time.time() + args.duration
        while time.time() < end_time and generator.running:
             # Kiểm tra định kỳ (ví dụ: mỗi giây) để thoát sớm nếu cần (Ctrl+C)
             time.sleep(1)

    except KeyboardInterrupt:
        # Xử lý khi người dùng nhấn Ctrl+C
        logging.info("Ctrl+C received, stopping...")
    except Exception as e:
        # Bắt các lỗi không mong muốn khác
        logging.error(f"An unexpected error occurred: {str(e)}")
    finally:
        # Luôn đảm bảo gọi stop() để dọn dẹp threads
        if generator.running:
            generator.stop()
        logging.info("Traffic generation finished.")

# --- Điểm Bắt đầu Thực thi ---
if __name__ == "__main__":
    main()

