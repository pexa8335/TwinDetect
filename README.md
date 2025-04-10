
1. Download Apache2 & relevant library.

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y apache2 python3-pip git nano 
sudo apt install python3-venv -y
```

2. In your project directory (or wherever you prefer), create a virtual environment (e.g., named dgtwin - digital twin environment):

```bash
python3 -m venv dgtwin
```

3. Activate venv.

```bash
source dgtwin/bin/activate
```

You will see (dgtwin) appear at the beginning of the command line, indicating that the virtual environment is active.

4. **Install packages:** Now you can safely use pip (or pip3) because it will install into the virtual environment:

```bash
pip install pandas numpy psutil scikit-learn joblib matplotlib 
```

5. Implement digital twin to observe log.

```bash
python3 digital_twin.py
```

6. Test the digital twin with the anomaly traffic generator.

```bash
cd traffic_maker
python3 anomaly_maker.py
```

---
> ✍️ _This README provides an overview of how to run the system. For workflow steps and module usage, see [`WORKFLOW.md`](./WORKFLOW.md)._

> ✍️ _For detailed research notes, technical explanations, and results, see [`RESEARCH.md`](./RESEARCH.md)._

