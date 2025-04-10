import pandas as pd

file_path = 'anomaly_traffic_logs.csv'  
df = pd.read_csv(file_path, header=None) 

# Thêm cột 'label' và gán giá trị 1 cho tất cả các hàng
df['label'] = 1

output_file_path = 'anomaly_traffic_labeled.csv' 
df.to_csv(output_file_path, index=False, header=False)

print(f"File anomaly data đã được label và lưu tại: {output_file_path}")
