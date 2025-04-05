
# Research Notes: Digital Twins and Anomaly Detection for Cybersecurity

## 1. Digital Twins for Cybersecurity

_Cited: [Security Attacks and Solutions for Digital Twins](https://arxiv.org/pdf/2202.12501)_

### 1.1 Problem

- **CPS** - Cybersecurity Physical Systems
- **ICS** - Industrial Control Systems

ICSs provide promising solutions to various industrial ecosystems but they substantially expand the attack surface. By exploiting different attack vectors, attackers can launch APT (Advanced Persistent Threat) attacks, allowing them to reside in the system to eavesdrop or exfiltrate sensitive information.

To ensure that the system operates securely and safely, we need essential measures to secure CPSs:

- Conducting penetration testing
- Evaluating the operational behavior of the system

### 1.2 Solution

As CPSs can't be deactivated for conducting such analysis, assessing the system's security level requires online solutions that accurately reflect the actual CPS operations while avoiding any interference or side-effects of testing on the live systems.

- Digital twins are virtual replicas of physical assets used for analysis, prediction, and optimization.
- They enhance CPS security through system training, security testing, and misconfiguration detection.
- Digital twins run synchronously with physical assets to track data inconsistencies.
- They integrate data from various sources to learn emergent behavior for anomaly detection.
- Optimized data from digital twins is fed back to the physical entity to adapt operations.

### 1.3 Drawbacks

Digital Twins allow attackers to exploit digital twins to launch attacks on the CPS. Digital twins, being the virtual (digital) replicas of their physical counterparts, share functional requirements and operational behavior of the underlying systems. Therefore, digital twins may act as a potential source of data breaches, leading to the abuse case of digital twins.

Attackers may exploit the deep knowledge about the physical process and devices accessible through digital twins with a two-stage strategy:

1. Use the key input data source, namely digital twins, into a malicious state
2. Through that state, manipulate the underlying physical system's behavior covertly

**Key**: It is necessary to ensure the trustworthiness of digital twins.

---

## 2. Anomaly Detection Techniques

_Cited: [Anomaly Detection: A Survey by Chandola et al](http://cucis.ece.northwestern.edu/projects/DMS/publications/AnomalyDetection.pdf)_

### 2.1 Definition & Importance

Anomalies are patterns in data that do not conform to a well-defined notion of normal behavior.

Anomaly detection finds extensive use in a wide variety of applications such as:

- Fraud detection for credit cards, insurance or health care
- Intrusion detection for cyber-security
- Fault detection in safety critical systems
- Military surveillance for enemy activities

### 2.2 Section 2.2, Types of Anomalies.

1. **Point Anomalies**: "If an individual data instance can be considered as anomalous with respect to the rest of data, then the instance is termed as a point anomaly."
    
2. **Contextual Anomalies**: "If a data instance is anomalous in a specific context (but not otherwise), then it is termed as a contextual anomaly."
    
    - Example: 90% CPU usage is normal during heavy computational tasks but abnormal at midnight when the system should be idle.

3. **Collective Anomalies**: "If a collection of related data instances is anomalous with respect to the entire data set, it is termed as a collective anomaly. The individual data instances in a collective anomaly may not be anomalies by themselves..."
    
    - Example: A sequence of seemingly harmless web requests that together constitute a scanning attack.

### 2.3 Major Approaches to Anomaly Detection

#### 2.3.1 Section 4, Classification based.

Classification-based anomaly detection techniques operate under the following general assumption: 

_Assumption: "A classifier that can distinguish between normal and anomalous classes can be learnt in the given feature space."_

#### 2.3.2 Section 5, Nearest Neighbor-based

The concept of nearest neighbor analysis has been used in several anomaly detection techniques. Such techniques are based on the following key assumption: 

_Assumption"Normal data instances occur in dense neighborhoods, while anomalies occur far from their closest neighbors."_

#### 2.3.3 Section 6, Clustering-based

Clustering [Jain and Dubes 1988; Tan et al. 2005] is used to group similar data instances into clusters. Clustering is primarily an unsupervised technique though semi-supervised clustering [Basu et al. 2004] has also been explored lately. 

_Assumption: "Normal data instances belong to a cluster in the data, while anomalies either do not belong to any cluster."_

#### 2.3.4 Section 7, Statistical-based

The underlying principle of any statistical anomaly detection technique is: _"An anomaly is an observation which is suspected of being partially or wholly irrelevant because it is not generated by the stochastic model assumed" [Anscombe and Guttman 1960]._

Statistical anomaly detection techniques are based on the following key assumption: 

_Assumption: "Normal data instances occur in high probability regions of a stochastic model, while anomalies occur in the low probability regions of the stochastic model."_

### 2.3.5 Section 2.4, Output Format

_"**Scoring techniques assign an anomaly score to each instance** in the test data depending on the degree to which that instance is considered an anomaly. Thus the output of such techniques is a **ranked list of anomalies**. An analyst may choose to either analyze top few anomalies or **use a cut-off threshold to select the anomalies**."_

**Therefore, based on the flexibility that scores provide (ability to set thresholds, ranking), prioritization techniques are those that can provide an Anomaly Score.** (Such as Isolation Forest).

---

## 3. Integration of Digital Twins and Anomaly Detection

The combination of Digital Twins and Anomaly Detection techniques creates a powerful framework for cybersecurity monitoring and threat detection:

1. **Real-time monitoring**: Digital twins can mirror the behavior of physical systems in real-time, while anomaly detection algorithms can continuously analyze this data stream for deviations.
    
2. **Proactive threat detection**: By applying anomaly detection to digital twin data, potential security threats can be identified before they impact the physical system.
    
3. **Safe testing environment**: Security tests and simulated attacks can be performed on the digital twin without risking the operational stability of the physical system.
    
4. **Behavioral modeling**: Digital twins can generate normal behavior profiles that serve as baselines for anomaly detection algorithms.
    
5. **Contextual awareness**: The integration enables contextual anomaly detection by incorporating knowledge about the system's operational states and expected behaviors from the digital twin.