import pandas as pd

# Đọc 2 file CSV
df_anomaly = pd.read_csv('anomaly_traffic.csv')
df_normal = pd.read_csv('normal_traffic.csv')

df_anomaly['label'] = 1
df_normal['label'] = 0

# Gộp 2 dataframe lại
df_combined = pd.concat([df_anomaly, df_normal], ignore_index=True)

# Xáo trộn dữ liệu
df_shuffled = df_combined.sample(frac=1, random_state=42).reset_index(drop=True)

# Lưu vào file mới
df_shuffled.to_csv('combined_shuffled_access_logs.csv', index=False)

print("Kết quả lưu vào combined_shuffled_access_logs.csv")
