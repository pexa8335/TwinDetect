import pandas as pd
import numpy as np
from scipy.stats import zscore
import re
from collections import Counter, defaultdict
import math
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

class ApacheLogFeatureExtractor:
    def __init__(self, log_df):
        self.log_df = log_df
        self.ip_request_counts = Counter(log_df['ip'])
        self.ip_status_counters = defaultdict(Counter)
        
        for _, row in log_df.iterrows():
            self.ip_status_counters[row['ip']][row['status']] += 1
    
    def calculate_entropy(self, s):
        if not s:
            return 0
            
        p, lns = Counter(s), float(len(s))
        return -sum(count/lns * math.log(count/lns, 2) for count in p.values())
    
    def count_special_chars(self, s):
        return len(re.sub(r'[a-zA-Z0-9\/?=&.]', '', s))
    
    def contains_suspicious_patterns(self, url):
        patterns = [
            r'cat.*\/etc',
            r'\/\.\./',
            r'union\s+select',
            r'script>',
            r'exec\(',
            r'eval\(',
            r'select.*from',
            r'delete.*from',
            r'drop.*table',
            r'etc\/passwd',
            r'etc\/shadow',
            r'proc\/self',
            r'\/bin\/(?:ba)?sh',
            r'whoami',
            r'%0[aAdD]'
        ]
        
        for pattern in patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return 1
        return 0
    
    def extract_url_features(self, url):
        url_entropy = self.calculate_entropy(url)
        special_char_count = self.count_special_chars(url)
        suspicious_pattern = self.contains_suspicious_patterns(url)
        
        query_param_count = 0
        if '?' in url:
            query_part = url.split('?', 1)[1] 
            query_param_count = len(query_part.split('&'))
        
        path = url.split('?',0)[0]
        path_depth = len([p for p in path.split('/') if p])
        
        return {
            'url_entropy': url_entropy,
            'special_char_count': special_char_count,
            'contains_suspicious_patterns': suspicious_pattern,
            'query_param_count': query_param_count,
            'path_depth': path_depth
        }
    
    def extract_user_agent_features(self, ua):
        ua_length = len(ua) if ua else 0
        ua_entropy = self.calculate_entropy(ua) if ua else 0
        
        ua_category = 'other'
        if ua:
            ua_lower = ua.lower()
            if any(bot in ua_lower for bot in ['bot', 'crawler', 'spider']):
                ua_category = 'bot'
            elif any(browser in ua for browser in ['Chrome', 'Firefox', 'Safari', 'MSIE', 'Edge']):
                ua_category = 'browser'
            elif any(tool in ua_lower for tool in ['curl', 'wget', 'postman']):
                ua_category = 'tool'
        
        return {
            'ua_length': ua_length,
            'ua_entropy': ua_entropy,
            'ua_is_bot': 1 if ua_category == 'bot' else 0,
            'ua_is_browser': 1 if ua_category == 'browser' else 0,
            'ua_is_tool': 1 if ua_category == 'tool' else 0
        }
    
    def extract_time_features(self, row):
        hour = row['hour']
        day_of_week = row['day_of_week']
        
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)
        weekday_sin = np.sin(2 * np.pi * day_of_week / 7)
        weekday_cos = np.cos(2 * np.pi * day_of_week / 7)
        
        is_weekend = 1 if day_of_week in [0, 6] else 0
        is_business_hours = 1 if 8 <= hour < 17 else 0
        is_night = 1 if hour >= 22 or hour < 6 else 0
        
        return {
            'hour_sin': hour_sin,
            'hour_cos': hour_cos,
            'weekday_sin': weekday_sin,
            'weekday_cos': weekday_cos,
            'is_weekend': is_weekend,
            'is_business_hours': is_business_hours,
            'is_night': is_night
        }
    
    def extract_ip_features(self, ip):
        request_count = self.ip_request_counts[ip]
        
        status_counter = self.ip_status_counters[ip]
        error_count = sum(status_counter[s] for s in status_counter if s >= 400)
        error_ratio = error_count / request_count if request_count > 0 else 0
        
        return {
            'request_count': request_count,
            'error_ratio': error_ratio
        }
    
    def extract_all_features(self):
        feature_rows = []
        
        for _, row in self.log_df.iterrows():
            url_features = self.extract_url_features(row['url'])
            
            ua_features = self.extract_user_agent_features(row['user_agent'])
            
            time_features = self.extract_time_features(row)
            
            ip_features = self.extract_ip_features(row['ip'])
            
            existing_features = {
                'status': row['status'],
                'size': row['size'],
                'method': row['method'],
                'url_length': row['url_length'],
                'has_query_params': row['has_query_params'],
                'is_timeout': row['is_timeout'],
                'is_error': row['is_error'],
                'is_client_error': row['is_client_error'],
                'is_server_error': row['is_server_error'],
                'is_suspicious_url': row['is_suspicious_url'],
                'is_bot': row['is_bot'],
                'is_script': row['is_script']
            }
            
            combined_features = {
                'ip': row['ip'],
                'timestamp': row['timestamp'],
                **url_features,
                **ua_features,
                **time_features,
                **ip_features,
                **existing_features
            }
            
            feature_rows.append(combined_features)
        
        features_df = pd.DataFrame(feature_rows)
        
        # Standard scaler: ZScore
        numeric_columns = features_df.select_dtypes(include=['number']).columns
        for col in numeric_columns:
            if set(features_df[col].unique()).issubset({0, 1}):
                continue
            features_df[f'{col}_zscore'] = zscore(features_df[col], nan_policy='omit')
        
        categorical_columns = ['method']
        features_df = pd.get_dummies(features_df, columns=categorical_columns, prefix=categorical_columns)
        if 'label' in self.log_df.columns:
             features_df['label'] = self.log_df['label'].reset_index(drop=True)
        return features_df

def prepare_for_isolation_forest(features_df):
    numeric_df = features_df.select_dtypes(include=['number'])

    threshold = 0.2 #If any column has >20% NaN value -> drop
    columns_to_keep = [col for col in numeric_df.columns if numeric_df[col].isna().mean() <= threshold]
    
    clean_df = numeric_df[columns_to_keep].fillna(numeric_df[columns_to_keep].mean())
    
    return clean_df

def main():
    input_file = 'test_combined_shuffled_access_logs.csv'
    #output_file = 'apache_features_for_isolation_forest.csv'
    
    print(f"Đọc dữ liệu từ {input_file}...")
    logs_df = pd.read_csv(input_file)
    
    numeric_columns = ['hour', 'day_of_week', 'month', 'day', 'year', 'minute', 'second',
                       'url_length', 'has_query_params', 'url_depth', 'is_timeout', 'is_error',
                       'is_client_error', 'is_server_error', 'is_suspicious_url', 'is_bot', 'is_script']
    
    for col in numeric_columns:
        if col in logs_df.columns:
            logs_df[col] = pd.to_numeric(logs_df[col], errors='coerce')
    
    string_columns = ['ip', 'logname', 'user', 'timestamp', 'method', 'url', 'protocol', 'referrer', 'user_agent', 'original_line']
    for col in string_columns:
        if col in logs_df.columns:
            logs_df[col] = logs_df[col].astype(str)

    # feature extraction
    extractor = ApacheLogFeatureExtractor(logs_df)
    features_df = extractor.extract_all_features()

    iso_forest_df = prepare_for_isolation_forest(features_df) #data for training model

    #features_df.to_csv(output_file, index=False) 
    
    iso_forest_file = 'isolation_forest_input.csv'
    print(f"Lưu dữ liệu cho Isolation Forest vào {iso_forest_file}...")
    iso_forest_df.to_csv(iso_forest_file, index=False)
    
    print(f"Số lượng đặc trưng ban đầu: {len(logs_df.columns)}")
    print(f"Số lượng đặc trưng sau khi trích xuất: {len(features_df.columns)}")
    print(f"Số lượng đặc trưng cho Isolation Forest: {len(iso_forest_df.columns)}")
    print("Hoàn thành!")

if __name__ == "__main__":
    main()
