import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_curve, f1_score, roc_curve, auc
import joblib
import os

def load_data(unlabeled_data, labeled_data):
    # Chỉ lấy 500k dòng từ dữ liệu không nhãn
    df_unlabeled = pd.read_csv(unlabeled_data, nrows = 2_500_000, on_bad_lines='skip')
    df_labeled = pd.read_csv(labeled_data)  #Test
    
    X_test = df_labeled.drop(columns='label')
    y_test = df_labeled['label']

    list_common_columns = list(set(X_test.columns) & set(df_unlabeled.columns))
    X_train = df_unlabeled[list_common_columns]
    X_test = X_test[list_common_columns]

    return X_train, X_test, y_test

def train_isolation_forest(X_train):
    iso_forest = IsolationForest(n_estimators=100, contamination=0.005, max_samples=256, random_state=42)
    iso_forest.fit(X_train)
    return iso_forest

def evaluate_model(y_test, X_test, iso_forest):
    anomaly_score = iso_forest.decision_function(X_test)
    precision, recall, thresholds = precision_recall_curve(y_test, -anomaly_score)
    f1 = 2 * (precision * recall) / (precision + recall + 1e-8)

    best_index = np.argmax(f1)
    best_threshold = thresholds[best_index]
    y_pred = (-anomaly_score >= best_threshold).astype(int)
    print("\n--- Kết quả đánh giá ---")
    print(classification_report(y_test, y_pred))
    print(f"F1 score tại threshold tối ưu: {f1[best_index]:.4f}")
    print(f"Threshold tối ưu: {best_threshold:.5f}")
    plt.plot(recall, precision, label='Precision-Recall curve')
    plt.scatter(recall[best_index], precision[best_index], c='red', label='Best F1')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend()
    plt.grid()
    plt.savefig('plt.png')
    # Bỏ comment nếu muốn dùng threshold mặc định là 0, code trên để xử lí tìm threshold tối ưu nhất
    # X_test['anomaly'] = iso_forest.predict(X_test)
    # X_test['anomaly'] = X_test['anomaly'].map({1:0, -1:1})
    # true_labels = y_test
    

    # print(classification_report(true_labels, X_test['anomaly']))


def main():
    # File paths
    unlabeled_file = 'dataset/isolation_forest_input.csv'  # File chứa dữ liệu không nhãn đã trích xuất đặc trưng
    labeled_file1 = 'dataset/test_combined_shuffled_access_logs.csv'  # File chứa dữ liệu có nhãn 
    print (f"Reading file {unlabeled_file} and {labeled_file1}...") #debug file name
    X_train, X_test, y_test = load_data(unlabeled_file, labeled_file1)
    train_columns = X_train.columns.tolist()
    joblib.dump(train_columns, 'model_features.pkl')
    model = train_isolation_forest(X_train)
    evaluate_model(y_test, X_test, model)
    joblib.dump(model, 'isolation_forest_model.pkl')
    print("[INFO] Đã lưu mô hình vào isolation_forest_model.pkl")

if __name__ == "__main__":
    main()
