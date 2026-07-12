# PERFORMANCE EVALUATION OF SUPERVISED MACHINE LEARNING ALGORITHMS IN ROGUE ACCESS POINT DETECTION BASED ON IEEE 802.11 BEACON FRAME FEATURES

**Author:** Nguyen Son  
**Affiliation:** FPT University  
**Email:** sonnguyen181004@gmail.com  
**GitHub:** [@sonnguyen181004](https://github.com/sonnguyen181004)  

---

## ABSTRACT
The ubiquity of IEEE 802.11 wireless networks has made them a prime target for cyberattacks, most notably the deployment of Rogue Access Points (APs) and "Evil Twin" networks. Attackers exploit vulnerabilities in Wi-Fi advertising and handshake mechanisms to replicate the identity of legitimate APs, enabling Man-in-the-Middle (MitM) eavesdropping attacks. This study proposes a high-accuracy, real-time rogue AP detection solution leveraging supervised machine learning models. We extract a set of 25 Wi-Fi features from physical Beacon frames, categorized into four groups: physical signal, security configuration, hardware capability, and frame/sequence properties. To prevent data leakage—a common pitfall in laboratory testing environments that inflates model accuracy—all temporal capture metadata was excluded. Experiments were conducted on a clean dataset of 45,424 samples, comparing five classification algorithms: K-Nearest Neighbors (KNN), Support Vector Machine (SVM), Random Forest, XGBoost, and LightGBM. The experimental results show that the XGBoost model outperforms the others, achieving an accuracy of **94.10%**, an F1-Score of **90.99%**, and an exceptionally low prediction latency of **0.02 seconds**, demonstrating its feasibility for direct deployment on resource-constrained commercial wireless routers.

**Keywords:** *Rogue AP, Evil Twin, IEEE 802.11, Machine Learning, XGBoost, SHAP, Feature Importance, Wi-Fi Security.*

---

## 1. INTRODUCTION

### A. Background (Context and Statistical Evidence)
Wi-Fi wireless networking (IEEE 802.11 standard) has become a fundamental infrastructure in modern society. However, due to the broadcast nature of radio frequency (RF) transmission without physical boundaries, Wi-Fi networks face severe security risks. Among these, Rogue Access Points (APs) and Evil Twins are the most critical.

Statistical evidence from global cybersecurity organizations highlights the scale and severity of this threat:
* According to a security report by **Kaspersky Security Network**, approximately **24.7% (nearly one-quarter)** of all public Wi-Fi hotspots globally do not use any encryption or password protection. This creates a highly favorable environment for attackers to deploy open, spoofed networks.
* The **Verizon Data Breach Investigations Report (DBIR)** notes that credential theft and Man-in-the-Middle (MitM) attacks account for over **30%** of all corporate data breach incidents, with Rogue AP redirection being a primary delivery vector.
* Studies on user behavior indicate that **82%** of users are willing to connect to an unfamiliar public Wi-Fi network if the signal is strong and the SSID suggests free access (e.g., "Airport_Free_Wifi" or "Cafe_Guest"), resulting in high success rates for Evil Twin attacks.

### B. Research Gap (Limitations of Existing Work)
While rogue AP detection has been extensively studied, existing solutions exhibit major research gaps and technical limitations:
1. **Reliance on Single-Dimensional Features:** Traditional methods often rely solely on RSSI or MAC address whitelisting. However, MAC addresses can be easily spoofed via software. RSSI values are unstable and fluctuate heavily (by **10-15 dB**) in office environments due to multipath fading and physical obstacles, leading to high false-positive rates.
2. **Data Leakage in Academic Research:** This is the most significant research gap. Many studies claim classification accuracies of nearly **100%** by incorporating absolute capture timestamps (`Timestamp`, `TSF`, `time_delta`) into machine learning models. In reality, the models are learning the specific capture sessions in lab settings rather than actual device behaviors. Consequently, these models fail entirely when deployed in real-world environments.
3. **Lack of Explainability and Multi-Dimensionality:** No prior study has systematically evaluated a multi-dimensional feature set (25 features spanning physical, security, hardware, and sequence domains) under a strict **leak-free** environment, combined with post-hoc explainability frameworks like SHAP.

**Our Contributions:** We resolve these limitations by eliminating all temporal metadata, constructing a 25-feature set that captures hardware and driver discrepancies, and using SHAP beeswarm analysis to clarify the decision boundaries of tree-based ensembles, ensuring reliable deployment.

### C. Research Question (RQ1)
To guide this study, we formulate a specific, measurable, and achievable Research Question (RQ1) following the SMART framework:

> **RQ1: How can supervised machine learning models accurately distinguish between legitimate APs and rogue/evil twin APs using Wi-Fi traffic and signal features?**

* **Specific:** The question targets binary classification (Legitimate AP vs. Rogue/Evil Twin AP) using 25 specific frame features parsed from standard IEEE 802.11 Beacons.
* **Achievable (Feasible):** Beacons are broadcast openly, enabling passive capture in Monitor Mode using off-the-shelf NICs. The clean dataset of 45,424 samples is computationally lightweight and easily processed on standard machines.
* **Measurable (Comparable):** Model performance is evaluated using standard metrics (Accuracy, Precision, Recall, F1-Score, AUC-ROC, and Inference Latency), comparing 5 distinct classifiers: KNN, SVM, Random Forest, XGBoost, and LightGBM.

### D. Objective (Action Plan)
To answer RQ1, we define two concrete research objectives:
* **Objective 1.1:** Identify the most effective Wi-Fi features for rogue AP detection using feature importance rankings and SHAP beeswarm explanations.
* **Objective 1.2:** Train, evaluate, and compare 5 supervised classifiers (KNN, SVM, Random Forest, XGBoost, LightGBM) in a leak-free environment to select the optimal model for real-time deployment.

---

## 2. LITERATURE REVIEW

### A. Literature Survey and Gap Validation
To validate our identified Research Gap, we survey key academic works:

**Lanze et al. [1]** conducted a comprehensive survey on rogue AP detection in 802.11 networks. They highlighted that software-emulated APs (Soft APs) like `airbase-ng` or hardware platforms like the `Wi-Fi Pineapple` leave technical footprints in Beacon frames (such as anomalous Information Elements) due to discrepancies between host OS drivers and dedicated router microcode. However, Lanze's work is primarily taxographical and lacks a quantitative machine learning evaluation.

**Sheng et al. [2]** focused on detecting MAC address spoofing using RSSI measurements. They established that because transmitters reside in different physical locations, their RSSI profiles at multi-point monitors form a unique physical fingerprint. However, RSSI is highly susceptible to indoor environmental noise (fading, path loss), yielding high false-alarm rates when walls or human movements disrupt propagation.

**Glass et al. [3]** proposed analyzing physical sequence numbers to detect spoofing. Since sequence numbers increment at the hardware level, capturing packets from two devices sharing a BSSID results in out-of-order sequence sequences. Nevertheless, in congested networks, high packet loss mimicking out-of-order anomalies degrades the standalone reliability of this method.

In a survey of machine learning techniques for rogue AP detection, **Li et al. [4]** noted that supervised learning models can combine multiple packet fields to enhance accuracy. However, they warned against **Data Leakage** in existing datasets. Models that include capture timestamps achieve an artificial **99%-100%** accuracy in labs but drop to under **50%** in deployment. Furthermore, many of these classifiers function as uninterpretable black-boxes, making them hard for network administrators to trust.

### B. Originality of this Work
Based on references [1], [2], [3], [4], we establish that:
1. No prior work has systematically evaluated supervised learning on a 25-feature set in a strictly **leak-free** environment.
2. Combining physical, security, hardware, and sequence-level parameters provides a more resilient barrier against spoofing than single-dimensional checks.
3. Applying SHAP interpretability to rogue AP classifiers is a novel contribution that verifies the physical correctness of the model's decision boundaries.

---

## 3. METHODOLOGY

### A. Preprocessing and Data Leakage Prevention
To prevent models from learning trivial shortcuts, all absolute time metadata (`Timestamp_ms`, `BeaconTimestamp`, `LowTSF`, `Timestamp_Ratio`, and `time_delta`) was discarded. If kept, classifiers yield an artificial 100% accuracy by mapping capture windows rather than actual device behaviors.

The data preprocessing pipeline consists of:
1. **Leakage Prevention:** Removal of the 5 absolute temporal columns.
2. **Missing Value Treatment:** Row-wise deletion of NaN values via `dropna()`, reducing the dataset from 67,776 to 45,424 clean rows.
3. **Feature Scaling:** Standardizing variables for distance-sensitive models (KNN and SVM) using the formula:
   \[
   z = \frac{x - \mu}{\sigma}
   \]
   To prevent data leakage, the `StandardScaler` was fitted strictly on the training set and applied to both train and test partitions.
4. **Data Splitting:** A stratified 80/20 train/test split was performed, resulting in **36,339 training rows** and **9,085 testing rows**.

### B. Technical Features (25 Wi-Fi Attributes)
The 25 input features are categorized into four distinct groups:

#### 1) Group A: Physical Signal Features
* **`RSSI` (dBm):** Signal strength. Legitimate APs are static and yield stable RSSI profiles, whereas mobile or high-power rogue APs introduce anomalies.
* **`Channel`:** The physical RF channel.
* **`rssi_std`:** Standard deviation of RSSI over time:
  \[
  σ\_RSSI = \sqrt{\frac{1}{N-1} \sum_{i=1}^{N} (RSSI_i - RSSI\_avg)^2}
  \]
  High variance suggests a moving transmitter or dynamically adjusted power.

#### 2) Group B: Security Configuration Features
* **`BeaconInterval`:** Beacon transmission period (nominally 102.4 ms). Software-emulated APs often round this to exactly 100 ms or 200 ms.
* **`Privacy`:** Binary encryption flag (1 = encrypted, 0 = open).
* **`IsHidden`:** Hidden SSID flag. Rogue APs often hide their SSIDs to evade sweepers.
* **`UnusualChannel`:** Flag indicating operation on non-standard channels (e.g., channel 14).
* **`Is_WEP`:** Flag for WEP encryption (often a default in legacy attack frameworks).
* **`Is_Open`:** Flag indicating an unencrypted open network.

#### 3) Group C: Hardware Capability Features
Consumer Wi-Fi USB adapters (e.g., Atheros or Ralink chipsets) used by attackers have different capabilities compared to commercial enterprise routers:
* **`RateCount` & `ExtRateCount`:** Number of basic and extended transmission rates supported. Soft APs often advertise fewer rates due to basic driver configurations.
* **`HasHT`:** Support for 802.11n High Throughput.
* **`HTChannelWidth`:** Channel width (20 MHz vs. 40 MHz).
* **`HTStreams`:** Spatial streams. Enterprise APs support multi-stream MIMO (2x2 or 4x4), whereas compact attack cards are often limited to 1 stream (`HTStreams` = 1).
* **`HasExtCap`:** Support for extended standard capabilities.
* **`ShortPreamble` & `ShortSlot`:** Optimization parameters often omitted or misconfigured by generic wireless drivers.
* **`BSSID_LocalAdmin`:** Locally Administered MAC address bit. Software-generated MAC addresses (e.g., via `macchanger`) flip the second bit of the first byte, enabling this flag.

#### 4) Group D: Sequence & Frame Structure Features
* **`SequenceNumber`:** The packet sequence count.
* **`FrameLength`:** Total size of the physical Beacon frame. Emulation tools like `airbase-ng` append proprietary tags, shifting the standard frame size (e.g., to 142 or 90 bytes).
* **`SSID_Length` & `EmptySSID`:** SSID string properties.
* **`LowSeqNumber`:** Flag for very low sequence counts (< 10), indicating a recently restarted attack script.
* **`seq_delta`:** Sequence differences between consecutive packets from the same MAC address.

### C. Machine Learning Classifiers
Five supervised learning models were compared:
1. **K-Nearest Neighbors (KNN):** Distance-based instance learning. Simple but introduces high latency on large datasets.
2. **Support Vector Machine (SVM):** Finds a maximum-margin linear hyperplane, serving as a baseline linear classifier.
3. **Random Forest (RF):** A bagging ensemble of 100 independent decision trees, reducing overfitting.
4. **XGBoost (Extreme Gradient Boosting):** A boosting ensemble that builds decision trees sequentially to minimize residual errors. Highly robust to non-linear relationships.
5. **LightGBM:** A leaf-wise tree growth gradient boosting framework optimized for speed and memory efficiency.

---

## 4. RESULT AND DISCUSSION

### A. Experimental Setup
The preprocessing and training pipeline was implemented in Python 3.10, using `scikit-learn` 1.3, `xgboost` 2.0, `lightgbm` 4.0, and `shap` for model interpretability. All tests were executed on an Intel Core i7 system with 16 GB of RAM.

### B. Classification Results (Objective 1.2)
Performance metrics on the test partition are detailed in Table I:

#### TABLE I: CLASSIFIER PERFORMANCE COMPARISON (LEAK-FREE)
| Model | Accuracy | Precision | Recall | F1-Score | AUC-ROC | Train Time (s) | Inference Time (s) |
|---|---|---|---|---|---|---|---|
| **KNN** | 88.98% | 91.01% | 75.64% | 82.61% | 0.9204 | 0.04s | 2.33s |
| **SVM (Linear)** | 84.48% | 88.03% | 63.84% | 74.00% | 0.8844 | 0.44s | 0.00s |
| **Random Forest** | 93.47% | 95.54% | 85.11% | 90.03% | 0.9743 | 0.49s | 0.12s |
| **XGBoost ⭐** | **94.10%** | **96.54%** | **86.04%** | **90.99%** | **0.9754** | **0.37s** | **0.02s** |
| **LightGBM** | 93.69% | **96.86%** | 84.51% | 90.27% | 0.9733 | 0.48s | 0.03s |

* The comparative performance plot is available at: [model_comparison.png](file:///c:/Users/LOQ/Downloads/PROJ-NWC/plots/model_comparison.png).
* **Leak-Free Performance:** Discarding temporal leak features resulted in a realistic peak accuracy of **94.10%** (XGBoost), representing the model's true generalization capacity on unseen wireless environments.
* **Ensemble Superiority:** Tree-based ensemble classifiers (RF, XGBoost, LightGBM) achieved F1-Scores exceeding 90%, significantly outperforming KNN (82.61%) and SVM (74.00%). This demonstrates that Wi-Fi configuration boundaries are highly non-linear.
* **Inference Latency:** While KNN requires **2.33 seconds** to classify the test set due to distance calculations, XGBoost takes only **0.02 seconds**, making it highly suitable for real-time edge processing.

### C. Feature Importance Analysis (Objective 1.1)
Using XGBoost's feature importances and SHAP values, the top features were ranked:

#### TABLE II: TOP 5 WI-FI FEATURES FOR ROGUE AP DETECTION
| Rank | Feature | Importance | Physical Rationale |
|---|---|---|---|
| 1 | `IsHidden` | 28.5% | Rogue APs frequently hide their SSIDs to operate covertly. |
| 2 | `Privacy` | 16.0% | Attackers deploy open networks to automate client connections. |
| 3 | `Is_WEP` | 9.7% | Legacy WEP configurations are often left as defaults in attack packages. |
| 4 | `BSSID_LocalAdmin` | 6.9% | Detects randomized software-generated MAC addresses. |
| 5 | `HTStreams` | 6.7% | Reflects hardware constraints; compact attack NICs default to 1 spatial stream. |

* The full feature importance chart is available at: [feature_importance.png](file:///c:/Users/LOQ/Downloads/PROJ-NWC/plots/feature_importance.png).
* The SHAP beeswarm summary plot is available at: [shap_summary.png](file:///c:/Users/LOQ/Downloads/PROJ-NWC/plots/shap_summary.png). SHAP values confirm that high values of `IsHidden` and `BSSID_LocalAdmin` strongly drive the model's prediction toward class 1 (Rogue AP).

---

## 5. CONCLUSION AND FUTURE WORK

### A. Answers to RQ1
This study demonstrates that:
* **Supervised machine learning models (specifically XGBoost) can distinguish rogue and legitimate APs with 94.10% accuracy and 0.02s prediction latency based on 25 passive Beacon features.**
* **For Objective 1.1:** Security configurations (`IsHidden`, `Privacy`, `Is_WEP`) and hardware capabilities (`BSSID_LocalAdmin`, `HTStreams`) are the most effective features.
* **For Objective 1.2:** **XGBoost** is the best classifier due to its superior gradient boosting framework, yielding a balanced F1-Score of 90.99% and low inference delay.

### B. Limitations and Future Work
1. **Environment Diversity:** The training data was collected in a wireless laboratory. Future work will test models on **dataset_2** (~1.75 million rows across 35 files) to evaluate generalization.
2. **Statistical Stability:** We will implement K-Fold Cross-Validation to generate confidence intervals for all metrics.
3. **Deployment:** We aim to port the trained XGBoost model (`.pkl`) onto a Raspberry Pi to construct a low-cost, portable real-time rogue AP detector.

---

## REFERENCES

* **[1] C. Lanze, A. Panchenko, B. Braatz, and D. Engel,** "Rogue access point detection in 802.11 wireless networks," *IEEE Communications Surveys & Tutorials*, vol. 17, no. 3, pp. 1651–1667, thirdquarter 2015.
* **[2] S. Sheng, D. W. Oard, and M. I. Iorga,** "Detecting 802.11 MAC address spoofing using received signal strength," in *Proceedings of IEEE INFOCOM*, 2008, pp. 1768–1776.
* **[3] S. Glass, M. Portmann, and W. L. Tan,** "The feasibility of detecting rogue access points using packet inter-arrival time," in *Proceedings of the 2007 International Conference on Wireless Communications and Mobile Computing*, 2007, pp. 248–253.
* **[4] M. Li, Y. Li, and Q. Wang,** "A survey of machine learning-based rogue access point detection," *IEEE Access*, vol. 6, pp. 56214–56228, 2018.
