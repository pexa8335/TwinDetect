
# **Real-time Anomaly Detection System for Apache2 Web Server**.

## ⚙️ Setup Instructions

### 1. Install Apache2 & Required Libraries.

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y apache2 python3-pip git nano 
sudo apt install python3-venv -y
```

### 2. Create and Activate a Virtual Environment.

```bash
python3 -m venv dgtwin
```

### 3. Activate venv.

```bash
source dgtwin/bin/activate
```

>You will see (dgtwin) appear at the beginning of the command line, indicating that the virtual environment is active.

### 4. Install Python Dependencies.

```bash
pip install pandas numpy psutil scikit-learn joblib matplotlib 
```

### 5. Download the Dataset (Large Files).

```bash
python3 digital_twin.py
```

### 6. The dataset is too large so you need to download it.

```bash
FILE_ID=17xyuKBt5SWPsypWao4d7YrE1ImLY3O61
FILE_NAME=dataset.zip

CONFIRM=$(wget --quiet --save-cookies cookies.txt --keep-session-cookies --no-check-certificate \
"https://docs.google.com/uc?export=download&id=${FILE_ID}" -O- | \
sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1/p')

wget --load-cookies cookies.txt "https://docs.google.com/uc?export=download&confirm=${CONFIRM}&id=${FILE_ID}" \
-O ${FILE_NAME}

rm -f cookies.txt
unzip dataset.zip
```
>📦 Dataset includes large Apache2 logs and preprocessed CSV files for anomaly detection.

### 7. Run the Digital Twin Observer.

```bash
cd traffic_maker
python3 anomaly_maker.py
```

---
## 📄 License

This project is licensed under the [MIT License](./LICENSE).

---
> ✍️ _This README provides an overview of how to run the system. For workflow steps and module usage, see [`WORKFLOW.md`](./WORKFLOW.md)._

> ✍️ _For detailed research notes, technical explanations, and results, see [`RESEARCH.md`](./RESEARCH.md)._


