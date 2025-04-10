# Workflow: **Real-time Anomaly Detection System for Apache2 Web Server**.

This document outlines the step-by-step workflow for building and testing an anomaly detection system using Apache web server logs and the **Isolation Forest** algorithm.

---

## 1. Dataset Preparation

### 1.1 Source

Download the dataset from Kaggle:

🔗 [Web Server Access Logs - Kaggle](https://www.kaggle.com/datasets/eliasdabbas/web-server-access-logs/data)

>Format: Raw Apache log (`.log`)

---

## 2. Log Parsing

Use the `log_parser.py` script to convert raw log data into a structured format (`.csv`). This script extracts important fields such as:

- IP address
- Timestamp (day, month, hour, minute)
- HTTP method
- URL
- Status code
- User agent
- etc.

✅ Output: `parsed_logs.csv`

### 🔧 To use a custom input file:

```bash
cd helper/
nano log_parser.py
```
Update the line:

```bash
input_file = 'sample.log'
```
Replace `'sample.log'` with the desired file name.

---

## 3. Feature Engineering

Run `feature_extraction.py` to:

- Extract content-based and time-based features (status code, response size, etc.)
- Normalize values using `StandardScaler` (**Z-score**)
- Drop columns with excessive missing values (you can adjust the drop threshold)
- Fill remaining missing values with column means

✅ Output: `isolation_forest_input.csv`

---

## 4. Model Training

Run `train_model.py` to:

- Load the features in the previous step.
- Train an **Isolation Forest** model (unsupervised).
- Save the trained model and feature list using `joblib`.

✅ Output:

- `isolation_forest_model.pkl`
- `model_features.pkl`

✅ Evaluation summary.

```bash
--- Evaluation Results ---
               precision    recall  f1-score   support

     Normal       1.00       0.71      0.83     10587
    Anomaly       0.37       1.00      0.54      1805

    Accuracy:                           0.75     12392
Macro average:       0.69       0.85     0.69
Weighted average:    0.91       0.75     0.79

Best F1 Score: 0.5403 at Threshold: -0.11047
```

>The model is tuned to prioritize **recall** for anomaly detection (all anomalies are caught), at the cost of lower **precision** (possible false positives).

---

## 5. Deploy the Digital Twin

Run `digital_twin.py` to simulate a **live monitoring environment**. It will:

- Continuously monitor real-time logs.
- Parse and extract features on-the-fly.
- Apply the trained model to detect anomalies with the optimized threshold.
- Display alerts in real-time.

✅ Real-time alerts example:

```bash
2025-04-10 18:16:19,125 - DigitalTwin - WARNING - Phát hiện bất thường! 127.0.0.1 - - [10/Apr/2025:17:56:30 +0700] "GET /profile?search=%27%3Balert%28String.fromCharCode%2888%2C83%2C83%29%29%2F%2F%27%3Balert%28String.fromCharCode%2888%2C83%2C83%29%29%2F%2F%22%3Balert%28String.fromCharCode%2888%2C83%2C83%29%29%2F%2F%22%3Balert%28String.fromCharCode%2888%2C83%2C83%29%29%2F%2F--%3E%3C%2FSCRIPT%3E%22%3E%27%3E%3CSCRIPT%3Ealert%28String.fromCharCode%2888%2C83%2C83%29%29%3C%2FSCRIPT%3E HTTP/1.1" 404 488 "-" "Wget/1.20.3 (linux-gnu)"
2025-04-10 18:16:19,125 - DigitalTwin - WARNING - Chi tiết bất thường: Error Status: 404, Suspicious Agent: Wget/1.20.3 (linux-gnu)
```
---

## 6. Test with Synthetic Traffic

Run the script `anomaly_maker.py` to simulate traffic for testing:

- Generate normal vs anomaly traffic.
- Observe how the digital twin reacts.

Open a new Ubuntu terminal.

```bash
cd traffic_maker
python3 anomaly_traffic.py
```

---

## 7. (Optional) Use Other Datasets

>You can reuse the pipeline with other Apache log datasets. Just ensure:

- Ensure they are in standard Apache log format.
- Modify or reuse `log_parser.py` to parse them.
- Run the same pipeline:
    - Parse ➜ Feature Engineering ➜ Train ➜ Deploy.

> Tools provided:

- `normal_traffic.py` and `anomaly_traffic.py` – simulate labeled traffic
- `labeling.py` – add labels to your dataset
- `combine_shuffle.py` – combine and shuffle labeled data

>**Tip:** Use datasets with less than **1% contamination** for best results.  
>**Feature Engineering Tip:** Set the column drop threshold to **< 0.3** to reduce noise.

---


