import pandas as pd
import re
import os
from datetime import datetime
from dateutil import parser

log_pattern = re.compile(
    r'(?P<ip>\S+)\s+'             # IP address (IPv4 or IPv6)
    r'(?P<logname>\S+)\s+'        # Logname
    r'(?P<user>\S+)\s+'           # User
    r'\[(?P<timestamp>[^\]]+)\]\s+'  # Timestamp in square brackets
    r'"(?:(?P<method>[A-Z]+)\s+(?P<url>[^\s"]*)\s+(?P<protocol>[^"]*)|[^"]*)"\s+'  # HTTP request or "-"
    r'(?P<status>\d{3}|-)\s+'        # Status code
    r'(?P<size>\d+|-)\s+'            # Response size
    r'"(?P<referrer>[^"]*)"\s+'      # Referrer
    r'"(?P<user_agent>[^"]*)"'       # User agent
)

def parse_log_line(line):
    result = log_pattern.match(line)
    if result:
        data = result.groupdict()
        # Xử lý Timestamp
        try:
            dt = parser.parse(data['timestamp'], fuzzy=True)
            data['timestamp'] = dt
            
            # Thêm các trường thời gian
            data['hour'] = dt.hour
            data['day_of_week'] = dt.weekday()
            data['month'] = dt.month
            data['day'] = dt.day
            data['year'] = dt.year
            data['minute'] = dt.minute
            data['second'] = dt.second
        except Exception as e:
            data['timestamp'] = pd.NaT
            data['hour'] = -1
            data['day_of_week'] = -1
            data['month'] = -1
            data['day'] = -1
            data['year'] = -1
            data['minute'] = -1
            data['second'] = -1
            
        #các field thường bị None 
        for field in ['method', 'url', 'protocol', 'referrer', 'user_agent']:
            if data.get(field) is None:
                data[field] = None
        
        # URL
        if data['url'] is not None:
            data['url_length'] = len(data['url'])
            data['has_query_params'] = 1 if '?' in data['url'] else 0
            data['url_depth'] = len([part for part in data['url'].split('/') if part])
        else:
            data['url_length'] = 0
            data['has_query_params'] = 0
            data['url_depth'] = 0
        
        # Status, size must be number
        data['status'] = int(data['status']) if data['status'].isdigit() else -1
        data['size'] = int(data['size']) if data['size'].isdigit() else 0
        
        # Các field thường có giá trị "-"
        for field in ['logname', 'user', 'referrer', 'user_agent']:
            if data[field] == '-':
                data[field] = None
        
        # Lưu dòng gốc
        data['original_line'] = line.strip()
        
        # Thêm các features cho anomaly detection
        data['is_timeout'] = 1 if data['status'] == 408 else 0
        data['is_error'] = 1 if data['status'] >= 400 else 0
        data['is_client_error'] = 1 if 400 <= data['status'] < 500 else 0
        data['is_server_error'] = 1 if data['status'] >= 500 else 0
        
        # Check sus url if contains these pattern
        suspicious_patterns = [
            'admin', 'phpMyAdmin', 'wp-login', '.env', '../', '.git', 
            'passwd', 'wp-config', 'config.php', 'shell', 'eval'
        ]
        data['is_suspicious_url'] = 0
        if data['url']:
            data['is_suspicious_url'] = 1 if any(pattern in data['url'] for pattern in suspicious_patterns) else 0
            
        # Phát hiện các user-agent bất thường
        if data['user_agent']:
            data['is_bot'] = 1 if any(bot in data['user_agent'].lower() for bot in ['bot', 'crawler', 'spider']) else 0
            data['is_script'] = 1 if any(script in data['user_agent'].lower() for script in ['curl', 'wget', 'python', 'go-http']) else 0
        else:
            data['is_bot'] = 0
            data['is_script'] = 0

        return data
    return None

def parse_log_file(log_filepath, output_csv=None, sample_size=None):
    if not os.path.exists(log_filepath):
        print(f"Error: File not found at {log_filepath}")
        return pd.DataFrame()
    
    parsed_data = []
    failed_lines = []
    
    try:
        with open(log_filepath, 'r', encoding='utf-8', errors='replace') as f:
            line_count = 0
            parsed_count = 0
            
            for line in f:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                    
                line_count += 1
                parsed_line = parse_log_line(line)
                
                if parsed_line:
                    parsed_data.append(parsed_line)
                    parsed_count += 1
                else:
                    failed_lines.append(line)
                    
                # Stop after sample_size if specified
                if sample_size and line_count >= sample_size:
                    break

        success_rate = (parsed_count / line_count * 100) if line_count > 0 else 0
        print(f"Successfully parsed {parsed_count} out of {line_count} lines ({success_rate:.2f}%).")
        
        # Tạo DataFrame
        df = pd.DataFrame(parsed_data)
        
        # Lưu vào CSV 
        df.to_csv(output_csv, index=False)
        print(f"Parsed log saved to {output_csv}")
        return df
    
    except Exception as e:
        print(f"An error occurred during file processing: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    log_file = 'sample.log'
    output_csv = 'parsed_log.csv'

    df_log = parse_log_file(log_file, output_csv=output_csv)
    
    # Hiển thị thông tin cơ bản
    if not df_log.empty:
        print("\nFeature summary for anomaly detection:")
        for feature in ['is_error', 'is_client_error', 'is_server_error', 'is_suspicious_url', 'is_bot', 'is_script']:
            if feature in df_log.columns:
                count = df_log[feature].sum()
                print(f"  {feature}: {count} ({count/len(df_log)*100:.2f}%)")
    else:
        print("Could not generate DataFrame.")
