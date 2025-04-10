import time
import joblib
import logging
import feature_extraction
from help import log_parser
import pandas as pd
import numpy as np
import os

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - DigitalTwin - %(levelname)s - %(message)s'
)

# Load model
try:
    model = joblib.load('isolation_forest_model.pkl')
    logging.info("Đã load model và scaler thành công")
except Exception as e:
    logging.error(f"Lỗi khi load model hoặc scaler: {e}")
    model = None

# Đọc file training data để biết chính xác cột nào được sử dụng
train_columns = []
if os.path.exists('dataset/isolation_forest_input.csv'):
    try:
        train_df = pd.read_csv('dataset/isolation_forest_input.csv', nrows=1)
        train_columns = joblib.load('model_features.pkl')
        logging.info(f"Đã load {len(train_columns)} cột từ file training data")
    except Exception as e:
        logging.error(f"Lỗi khi đọc file training data: {e}")

# Nếu không có file training, sử dụng danh sách cố định
if not train_columns:
    train_columns = [
        'url_entropy', 'special_char_count', 'contains_suspicious_patterns', 'query_param_count', 
        'path_depth', 'ua_length', 'ua_entropy', 'ua_is_bot', 'ua_is_browser', 'ua_is_tool', 
        'hour_sin', 'hour_cos', 'weekday_sin', 'weekday_cos', 'is_weekend', 'is_business_hours', 
        'is_night', 'request_count', 'error_ratio', 'status', 'size', 'url_length', 'has_query_params', 
        'is_timeout', 'is_error', 'is_client_error', 'is_server_error', 'is_suspicious_url', 'is_bot', 
        'is_script', 'url_entropy_zscore', 'special_char_count_zscore', 'path_depth_zscore', 
        'ua_length_zscore', 'ua_entropy_zscore', 'hour_sin_zscore', 'hour_cos_zscore', 
        'request_count_zscore', 'error_ratio_zscore', 'status_zscore', 'size_zscore', 
        'url_length_zscore', 'is_error_zscore', 'is_client_error_zscore', 'is_bot_zscore'
    ]
    logging.info(f"Sử dụng danh sách cột mặc định với {len(train_columns)} cột")

# Đọc dữ liệu mẫu để có giá trị mẫu
sample_data = None
if os.path.exists('dataset/isolation_forest_input.csv'):
    try:
        sample_data = pd.read_csv('dataset/isolation_forest_input.csv', nrows=1).iloc[0].to_dict()
        logging.info("Đã load dữ liệu mẫu từ file training")
    except Exception as e:
        logging.error(f"Lỗi khi đọc dữ liệu mẫu: {e}")

# Theo dõi số lượng log, đây là đường dẫn mặc định lưu log của Apache2 
log_file_path = '/var/log/apache2/access.log'
log_count = 0
alerts = 0

def send_alert(log_entry):
    global alerts
    alerts += 1
    logging.warning(f'Phát hiện bất thường! {log_entry["original_line"]}')
    # Log chi tiết về bất thường
    suspicious_fields = []
    if log_entry.get('is_suspicious_url', 0) == 1:
        suspicious_fields.append(f"Suspicious URL: {log_entry.get('url')}")
    if log_entry.get('is_error', 0) == 1:
        suspicious_fields.append(f"Error Status: {log_entry.get('status')}")
    if log_entry.get('is_script', 0) == 1 or log_entry.get('is_bot', 0) == 1:
        suspicious_fields.append(f"Suspicious Agent: {log_entry.get('user_agent')}")
    
    if suspicious_fields:
        logging.warning(f"Chi tiết bất thường: {', '.join(suspicious_fields)}")

def create_model_compatible_df(iso_forest_df):
    """
    Tạo DataFrame mới với chính xác cùng cấu trúc như training data
    """
    # Tạo DataFrame mới với tất cả các cột cần thiết
    result_df = pd.DataFrame(index=iso_forest_df.index)
    
    # Copy các cột thông thường (không phải zscore)
    for col in train_columns:
        if not col.endswith('_zscore'):
            if col in iso_forest_df.columns:
                result_df[col] = iso_forest_df[col]
            else:
                # Nếu không có, sử dụng giá trị mặc định hoặc 0
                result_df[col] = 0
    
    # Thêm các cột zscore với giá trị mẫu từ file training
    for col in train_columns:
        if col.endswith('_zscore'):
            # Lấy từ sample data nếu có, nếu không thì gán 0
            if sample_data and col in sample_data:
                result_df[col] = sample_data[col]
            else:
                result_df[col] = 0
    
    # Đảm bảo thứ tự cột giống file training
    return result_df[train_columns]

def monitor_logs():
    global log_count
    last_position = 0
    
    logging.info(f"Digital Twin bắt đầu giám sát với {len(train_columns)} cột")
    
    while True:
        with open(log_file_path, 'r') as f:
            f.seek(last_position)
            new_lines = f.readlines()
            last_position = f.tell()
            
        if new_lines:
            parsed_logs = []
            for line in new_lines:
                parsed = log_parser.parse_log_line(line)
                if parsed:
                    parsed_logs.append(parsed)
                    
            if parsed_logs:
                try:
                    # Chuyển danh sách các dict thành DataFrame
                    logs_df = pd.DataFrame(parsed_logs)
                    
                    # Sử dụng ApacheLogFeatureExtractor để trích xuất đặc trưng
                    extractor = feature_extraction.ApacheLogFeatureExtractor(logs_df)
                    features_df = extractor.extract_all_features()
                    
                    # Chuẩn bị dữ liệu cho isolation forest
                    iso_forest_df = feature_extraction.prepare_for_isolation_forest(features_df)
                    
                    # Tạo DataFrame tương thích với model
                    model_df = create_model_compatible_df(iso_forest_df)
                    
                    # Log thông tin
                    logging.info(f"Features sau khi xử lý: {model_df.shape[1]}")
                    

                    scores = model.decision_function(model_df) 
                    preds = np.where(scores < -0.11047, -1, 1) #-0.11047 is the optimized threshold in the previous step

                    for i, pred in enumerate(preds):
                        if pred == -1:  # Bất thường được phát hiện
                            send_alert(parsed_logs[i])
                            
                    log_count += len(parsed_logs)
                    logging.info(f'Đã xử lý {len(parsed_logs)} log entries mới')
                except Exception as e:
                    logging.error(f'Lỗi trong quá trình xử lý log mới: {e}')
                    import traceback
                    logging.error(traceback.format_exc())
                    
        logging.info(f'Trạng thái: True, Log count: {log_count}, Alerts: {alerts}')
        time.sleep(5)  # Kiểm tra mỗi 5 giây

if __name__ == '__main__':
    logging.info('Digital Twin bắt đầu giám sát...')
    monitor_logs()
