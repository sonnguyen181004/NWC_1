# 🛡️ Rogue AP Detection using Machine Learning (RQ1)

> Phát hiện Access Point giả mạo (Rogue AP / Evil Twin) bằng các thuật toán học máy có giám sát, dựa trên phân tích 25 đặc trưng từ gói tin Wi-Fi Beacon.

---

## 📌 Mục tiêu Nghiên cứu (Research Questions)

### RQ1 — Phát hiện Rogue AP bằng Học máy
**Objective 1.1:** Xác định các đặc trưng Wi-Fi (features) hiệu quả nhất để phân biệt AP hợp lệ và AP giả mạo.  
**Objective 1.2:** So sánh hiệu năng của 5 thuật toán học máy có giám sát: **KNN, SVM, Random Forest, XGBoost, LightGBM**.

---

## 🗂️ Cấu trúc Dự án

```
PROJ-NWC/
├── dataset/
│   ├── clean_dataset.csv              # Tập dữ liệu sạch (dùng để train)
│   ├── dataset_knn_imputer.csv        # Dữ liệu sau KNN Imputation
│   ├── dataset_iterative_imputer.csv  # Dữ liệu sau MICE Imputation
│   └── dataset_padding.csv            # Dữ liệu sau Padding Imputation
│
├── models/                            # Mô hình đã train (file .pkl)
│   ├── KNN_model.pkl
│   ├── KNN_scaler.pkl
│   ├── SVM_model.pkl
│   ├── SVM_scaler.pkl
│   ├── Random_Forest_model.pkl
│   ├── XGBoost_model.pkl
│   ├── LightGBM_model.pkl
│   └── feature_cols.json              # Danh sách 25 đặc trưng theo thứ tự
│
├── plots/                             # Biểu đồ kết quả thực nghiệm
│   ├── model_comparison.png           # So sánh hiệu năng 5 mô hình
│   ├── feature_importance.png         # Độ quan trọng đặc trưng (XGBoost)
│   ├── shap_summary.png               # Biểu đồ SHAP phân tích quyết định
│   ├── imputation_comparison.png      # So sánh phương pháp điền khuyết
│   ├── rssi_noise_robustness.png      # Kiểm tra độ bền với nhiễu RSSI
│   └── model_comparison_results.csv   # Kết quả số đầy đủ
│
├── run_experiments.py                 # Script huấn luyện chính (RQ1 + RQ2)
├── generate_docx.py                   # Tạo báo cáo thực nghiệm (.docx)
├── generate_theory_docx.py            # Tạo tài liệu lý thuyết (.docx)
└── README.md
```

---

## 📊 Kết quả Thực nghiệm (RQ1 — Không rò rỉ dữ liệu)

Tập dữ liệu: `clean_dataset.csv` sau khi loại bỏ 5 cột rò rỉ thời gian.  
Phân chia: **80% Train / 20% Test** — Stratified Split.

| Thuật toán | Accuracy | Precision | Recall | F1-Score | AUC-ROC | Predict time |
|---|---|---|---|---|---|---|
| KNN | 88.98% | 91.01% | 75.64% | 82.61% | 0.9204 | 3.54s |
| SVM (Linear) | 84.48% | 88.03% | 63.84% | 74.00% | 0.8844 | 0.00s |
| Random Forest | 93.47% | 95.54% | 85.11% | 90.03% | 0.9743 | 0.16s |
| **XGBoost ⭐** | **94.10%** | **96.54%** | **86.04%** | **90.99%** | **0.9754** | **0.03s** |
| LightGBM | 93.69% | 96.86% | 84.51% | 90.27% | 0.9733 | 0.04s |

> **XGBoost** là thuật toán tốt nhất: Accuracy cao nhất (94.10%), F1-Score 90.99%, thời gian dự đoán chỉ 0.03 giây — khả thi cho triển khai thời gian thực.

---

## 🔑 Top 5 Đặc trưng Quan trọng nhất (XGBoost + SHAP)

| Hạng | Đặc trưng | Tầm quan trọng | Ý nghĩa |
|---|---|---|---|
| 1 | `IsHidden` | 28.5% | AP giả thường ẩn tên SSID để tránh bị quản trị viên phát hiện |
| 2 | `Privacy` | 16.0% | AP giả tạo mạng mở (không mật khẩu) để bẫy người dùng |
| 3 | `Is_WEP` | 9.7% | Công cụ tấn công hay dùng mã hóa WEP cũ làm mặc định |
| 4 | `BSSID_LocalAdmin` | 6.9% | Địa chỉ MAC ngẫu nhiên bằng phần mềm → cờ LocalAdmin bật |
| 5 | `HTStreams` | 6.7% | Card tấn công chỉ có 1 luồng MIMO; Router thật có 2–4 luồng |

---

## 🧩 25 Đặc trưng Wi-Fi sử dụng

Chia thành 4 nhóm:

**Nhóm A — Tín hiệu vật lý:** `RSSI`, `Channel`, `rssi_std`

**Nhóm B — Cấu hình mạng & Bảo mật:** `BeaconInterval`, `Privacy`, `IsHidden`, `UnusualChannel`, `Is_WEP`, `Is_Open`

**Nhóm C — Năng lực phần cứng:** `RateCount`, `ExtRateCount`, `HasHT`, `HTChannelWidth`, `HTStreams`, `HasExtCap`, `ShortPreamble`, `ShortSlot`, `BSSID_LocalAdmin`

**Nhóm D — Số thứ tự & Cấu trúc gói tin:** `SequenceNumber`, `FrameLength`, `SSID_Length`, `EmptySSID`, `DSChannel`, `LowSeqNumber`, `seq_delta`

---

## ⚠️ Chống Rò rỉ Dữ liệu (Data Leakage Prevention)

5 cột thời gian sau đây đã bị **loại bỏ hoàn toàn** trước khi huấn luyện:

```
Timestamp_ms | BeaconTimestamp | LowTSF | Timestamp_Ratio | time_delta
```

Nếu giữ lại các cột này → mô hình đạt **~100% Accuracy ảo** (học thời điểm capture chứ không học đặc trưng Wi-Fi thực sự). Sau khi loại bỏ → kết quả thực tế **94.10%**.

---

## 🚀 Hướng dẫn Chạy

### Yêu cầu

```bash
pip install scikit-learn xgboost lightgbm shap pandas numpy matplotlib seaborn joblib python-docx tabulate
```

### Huấn luyện tất cả mô hình

```bash
python run_experiments.py
```

Kết quả:
- File `.pkl` lưu vào `models/`
- Biểu đồ lưu vào `plots/`
- Bảng kết quả in ra terminal

### Load lại mô hình (không cần train lại)

```python
import joblib, json

# Load danh sách đặc trưng
feature_cols = json.load(open("models/feature_cols.json"))

# Load mô hình
model = joblib.load("models/XGBoost_model.pkl")

# Dự đoán trên dữ liệu mới
y_pred = model.predict(df_new[feature_cols])
# 0 = AP hợp lệ | 1 = Rogue AP
```

### Tạo báo cáo Word

```bash
# Báo cáo thực nghiệm RQ1 (có bảng kết quả + hình ảnh)
python generate_docx.py

# Tài liệu lý thuyết 15-20 trang (khái niệm Wi-Fi, ML, Evil Twin...)
python generate_theory_docx.py
```

---

## 📁 Tập dữ liệu

| File | Mô tả | Số dòng |
|---|---|---|
| `clean_dataset.csv` | Dữ liệu gốc sạch, có giá trị NaN | 67,776 |
| `clean_dataset.csv` (sau dropna) | Dùng để train trực tiếp | 45,424 |
| `dataset_knn_imputer.csv` | Điền khuyết bằng KNN Imputer | ~67,776 |
| `dataset_iterative_imputer.csv` | Điền khuyết bằng MICE/Iterative | ~67,776 |
| `dataset_padding.csv` | Điền khuyết bằng hằng số -100 | ~67,776 |

---

## 🛠️ Công nghệ sử dụng

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3-orange?logo=scikit-learn)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0-red)
![LightGBM](https://img.shields.io/badge/LightGBM-4.0-green)
![SHAP](https://img.shields.io/badge/SHAP-explainability-purple)

---

## 👤 Tác giả

**Nguyen Tan Son** — FPT University  
GitHub: [@sonnguyen181004](https://github.com/sonnguyen181004)
