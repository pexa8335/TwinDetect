# Web Server Anomaly Detection using Digital Twin and Isolation Forest

## 1. Background

In the context of cybersecurity and system health monitoring, **web server logs** are a valuable source for understanding system behavior and detecting **anomalous patterns**.

This project aims to build a **basic Digital Twin** of the web server by modeling its behavior and detecting deviations from the norm using **unsupervised learning**.

---

## 2. Anomaly Types

As categorized in Chandola et al. (2009) [1], three relevant types of anomalies are targeted:

| Type         | Description | Web Example |
|--------------|-------------|-------------|
| **Point**     | Individual data instances significantly different from others | Sudden 5xx server error |
| **Contextual** | Unusual behavior in a specific context | Request spike at 3AM |
| **Collective** | Group of related data points that are abnormal together | Repeated scan-like requests from multiple IPs |

---

## 3. Literature Review

### 📘 **Chandola et al. (2009)** – *Anomaly Detection: A Survey*

- **Key Insight:** When labels are unavailable, **unsupervised anomaly detection** becomes necessary.
- **Section 2.3.3:** *“Unsupervised techniques do not assume any knowledge about the data and work by identifying patterns that deviate significantly from the rest of the data.”*
- This motivates the use of **Isolation Forest**, which detects anomalies based on how easily data points can be isolated.

---

## 4. Justification for Isolation Forest

| Criteria                           | Justification |
|------------------------------------|---------------|
| **Unsupervised Capability**         | No need for labeled data |
| **Computational Efficiency**        | Linear time complexity, scalable |
| **Scoring Output**                  | Provides anomaly score per sample |
| **Interpretability**                | Easy to trace why a data point is isolated |
| **Suitability for Tabular Data**    | Works well with structured features from parsed logs |
| **Support in Scikit-Learn**         | Easy implementation and customization |

---

## 5. Alternatives Considered

| Method              | Rejected Because |
|---------------------|------------------|
| **One-Class SVM**    | Sensitive to parameter tuning, not scalable |
| **Autoencoders**     | Requires more time/resources, GPU preferred |
| **LOF (Local Outlier Factor)** | Poor performance on large or high-dimensional datasets |
| **K-Means**          | Not anomaly-focused, lacks scoring system |

---

## 6. Challenges Identified

- Log data is **semi-structured** and must be **parsed and encoded** before modeling.
- **Contextual anomalies** depend on **temporal features**, requiring careful **feature engineering** (e.g., hour of request, request count window).
- No ground-truth labels → evaluation relies on **manual inspection** and **proxy metrics** (e.g., rare status codes, abnormal access patterns).

---

## 7. References

[1] Chandola, V., Banerjee, A., & Kumar, V. (2009). *Anomaly detection: A survey*. ACM Computing Surveys (CSUR), 41(3), 1–58.

---

> ✍️ *This README provides an overview of the objectives and design decisions. For detailed research notes, see [`RESEARCH.md`](./RESEARCH.md).*
