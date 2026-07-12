# ĐÁNH GIÁ HIỆU NĂNG CÁC THUẬT TOÁN HỌC MÁY CÓ GIÁM SÁT TRONG PHÁT HIỆN ACCESS POINT GIẢ MẠO DỰA TRÊN ĐẶC TRƯNG KHUNG HÌNH BEACON 802.11

**Tác giả:** Nguyễn Sơn  
**Đơn vị:** Đại học FPT (FPT University)  
**Email:** sonnguyen181004@gmail.com  
**GitHub:** [@sonnguyen181004](https://github.com/sonnguyen181004)  

---

## TÓM TẮT (ABSTRACT)
Sự phổ biến của mạng không dây IEEE 802.11 đã biến chúng thành mục tiêu hàng đầu cho các cuộc tấn công mạng, trong đó nghiêm trọng nhất là sự xuất hiện của các Access Point giả mạo (Rogue AP) và thiết lập mạng "Evil Twin" (Anh em song sinh). Kẻ tấn công lợi dụng các lỗ hổng trong cơ chế bắt tay và quảng bá của Wi-Fi để sao chép thông tin nhận diện của AP hợp lệ nhằm thực hiện các cuộc tấn công nghe lén dữ liệu (Man-in-the-Middle). Nghiên cứu này đề xuất một giải pháp phát hiện Rogue AP có độ chính xác cao và khả thi trong thời gian thực bằng cách sử dụng các mô hình học máy có giám sát. Chúng tôi trích xuất một tập gồm 25 đặc trưng Wi-Fi từ các gói tin Beacon vật lý, được phân loại thành bốn nhóm chính: tín hiệu vật lý, cấu hình bảo mật, năng lực phần cứng và cấu trúc gói tin. Để đảm bảo tính khách quan và ngăn chặn hiện tượng rò rỉ dữ liệu (Data Leakage) thường gặp trong môi trường kiểm thử lab, toàn bộ các tham số liên quan đến thời gian ghi nhận gói tin đã bị loại bỏ. Thực nghiệm được tiến hành trên tập dữ liệu gồm 45.424 mẫu sạch để so sánh 5 thuật toán học máy phổ biến: K-Nearest Neighbors (KNN), Support Vector Machine (SVM), Random Forest, XGBoost và LightGBM. Kết quả thực nghiệm cho thấy mô hình XGBoost đạt hiệu năng vượt trội nhất với độ chính xác (Accuracy) đạt **94,10%**, điểm F1-Score đạt **90,99%** và thời gian dự đoán cực kỳ thấp (**0,02 giây**), chứng minh khả năng triển khai trực tiếp trên các thiết bị định tuyến thương mại có tài nguyên hạn chế.

**Từ khóa:** *Rogue AP, Evil Twin, IEEE 802.11, Machine Learning, XGBoost, SHAP, Feature Importance, Wi-Fi Security.*

---

## 1. INTRODUCTION (GIỚI THIỆU)

### A. Background (Bối cảnh và Số liệu Thực tế)
Công nghệ mạng không dây Wi-Fi (chuẩn IEEE 802.11) đã trở thành một phần hạ tầng thiết yếu trong đời sống kinh tế - xã hội hiện đại. Tuy nhiên, do bản chất truyền dẫn quảng bá qua môi trường không khí không có ranh giới vật lý cố định, Wi-Fi luôn đối mặt với nhiều nguy cơ an ninh nghiêm trọng. Một trong những mối đe dọa phổ biến và nguy hiểm nhất là sự xuất hiện của các Access Point giả mạo (Rogue AP) và đặc biệt là các biến thể tinh vi hơn như Evil Twin.

Các số liệu thống kê thực tế từ các tổ chức an ninh mạng toàn cầu đã vạch trần quy mô và mức độ nghiêm trọng của mối đe dọa này:
* Theo báo cáo bảo mật của **Kaspersky Security Network**, khoảng **24,7% (xấp xỉ 1/4)** tổng số điểm Wi-Fi công cộng trên toàn thế giới hoàn toàn không sử dụng bất kỳ cơ chế mã hóa hay mật khẩu bảo vệ nào. Điều này tạo ra một "mảnh đất màu mỡ" cho kẻ tấn công dễ dàng thiết lập các mạng mở giả mạo để bẫy người dùng.
* Theo báo cáo **Verizon Data Breach Investigations Report (DBIR)**, các cuộc tấn công thu thập thông tin đăng nhập và tấn công trung gian (Man-in-the-Middle - MitM) chiếm hơn **30%** tổng số sự cố rò rỉ dữ liệu của doanh nghiệp, trong đó việc sử dụng Rogue AP để điều hướng lưu lượng là một trong những phương thức phổ biến nhất.
* Các nghiên cứu về hành vi người dùng chỉ ra rằng **82%** người dùng sẵn sàng kết nối vào một mạng Wi-Fi công cộng không quen thuộc nếu mạng đó có cường độ tín hiệu mạnh và tên SSID gợi ý dịch vụ miễn phí (ví dụ: "Airport_Free_Wifi" hoặc "Cafe_Guest"), tạo điều kiện cho các cuộc tấn công Evil Twin đạt tỷ lệ thành công cực kỳ cao.

### B. Research Gap (Khoảng trống Nghiên cứu và Giới hạn)
Mặc dù bài toán phát hiện Rogue AP đã được nghiên cứu từ lâu, các giải pháp hiện tại vẫn tồn tại những khoảng trống và giới hạn kỹ thuật lớn:
1. **Sự phụ thuộc vào đặc trưng đơn lẻ:** Nhiều phương pháp truyền thống chỉ dựa vào cường độ tín hiệu RSSI hoặc danh sách trắng địa chỉ MAC (MAC Whitelisting). Tuy nhiên, địa chỉ MAC có thể bị thay đổi dễ dàng (MAC Spoofing) thông qua phần mềm. Cường độ RSSI lại cực kỳ không ổn định và dao động mạnh trong môi trường văn phòng do hiện tượng đa đường truyền (multipath fading) và vật cản, dẫn đến tỷ lệ cảnh báo sai (False Positive) rất cao.
2. **Hiện tượng rò rỉ dữ liệu (Data Leakage) trong nghiên cứu:** Đây là khoảng trống nghiên cứu lớn nhất. Nhiều công trình công bố độ chính xác phát hiện đạt xấp xỉ **100%** bằng cách đưa các trường thời gian (`Timestamp`, `TSF`, `time_delta`) vào mô hình học máy. Thực chất, mô hình chỉ học được thời điểm capture gói tin của AP thật và giả trong môi trường phòng thí nghiệm (lab) chứ không học được hành vi đặc trưng kỹ thuật thực sự của thiết bị. Khi mang ra môi trường thực tế, các mô hình này hoàn toàn thất bại.
3. **Thiếu tính đa chiều và khả năng giải thích (Interpretability):** Chưa có nghiên cứu nào đánh giá một cách hệ thống hệ thống đặc trưng đa chiều (25 đặc trưng kết hợp vật lý, bảo mật, năng lực phần cứng, cấu trúc gói tin) trong một môi trường kiểm thử **hoàn toàn sạch rò rỉ dữ liệu (leak-free)**, đồng thời sử dụng các phương pháp giải thích mô hình hiện đại như SHAP để làm rõ cơ chế ra quyết định của thuật toán.

**Giải pháp của nghiên cứu này:** Chúng tôi giải quyết triệt để các giới hạn trên bằng cách: loại bỏ hoàn toàn các trường thời gian rò rỉ; xây dựng bộ đặc trưng đa chiều 25 thuộc tính khai thác sâu sự khác biệt phần cứng và driver; và áp dụng phân tích SHAP để chứng minh tính giải thích được của mô hình, đảm bảo khả năng triển khai thực tế với độ tin cậy cao.

### C. Research Question (Câu hỏi Nghiên cứu)
Để định hướng cho nghiên cứu, chúng tôi đặt ra Câu hỏi Nghiên cứu cốt lõi (RQ1) được thiết lập chặt chẽ theo tiêu chí SMART để đảm bảo tính cụ thể, khả năng thực thi và tính đo lường:

> **RQ1: Làm thế nào các mô hình học máy có giám sát có thể phân biệt chính xác giữa Access Point hợp lệ và Access Point giả mạo (Rogue/Evil Twin AP) bằng cách sử dụng các đặc trưng lưu lượng và tín hiệu Wi-Fi?**

* **Tính cụ thể (Specific):** RQ1 tập trung vào bài toán phân loại nhị phân (Legitimate AP vs. Rogue/Evil Twin AP) trong mạng WLAN chuẩn IEEE 802.11 dựa trên 25 đặc trưng trích xuất từ khung hình Beacon.
* **Tính khả thi (Achievable):** Các gói tin Beacon được phát công khai không mã hóa, cho phép thu thập thụ động bằng card mạng thông thường ở chế độ Monitor Mode mà không gây ảnh hưởng đến hiệu năng mạng. Tập dữ liệu thực tế gồm 45.424 mẫu sạch hoàn toàn nằm trong năng lực tính toán của các thiết bị phổ thông.
* **Tính đo lường/so sánh được (Measurable):** Hiệu năng phân loại được đo lường bằng các chỉ số toán học chuẩn: Accuracy, Precision, Recall, F1-Score, AUC-ROC và thời gian trễ dự đoán (Inference Latency). Chúng tôi tiến hành so sánh đối chứng trực tiếp giữa 5 thuật toán học máy: KNN, SVM, Random Forest, XGBoost và LightGBM để chọn ra mô hình tối ưu nhất.

### D. Objective (Mục tiêu Nghiên cứu)
Để trả lời cho câu hỏi nghiên cứu RQ1, chúng tôi cụ thể hóa thành hai mục tiêu hành động chi tiết:
* **Mục tiêu 1.1 (Objective 1.1):** Xác định các đặc trưng (features) lưu lượng và tín hiệu Wi-Fi đóng vai trò quan trọng nhất, mang lại hiệu quả phân loại cao nhất để vạch trần Rogue AP thông qua thuật toán Feature Importance và phân tích SHAP Beeswarm.
* **Mục tiêu 1.2 (Objective 1.2):** Huấn luyện, đánh giá và so sánh hiệu năng thực tế của 5 thuật toán học máy có giám sát (KNN, SVM, Random Forest, XGBoost, LightGBM) trên tập dữ liệu không rò rỉ để lựa chọn mô hình tối ưu nhất về cả độ chính xác lẫn tốc độ xử lý cho việc triển khai thời gian thực.

---

## 2. LITERATURE REVIEW (TỔNG QUAN TÀI LIỆU)

### A. Khảo sát các Nghiên cứu đi trước và Biện giải Research Gap
Để làm rõ khoảng trống nghiên cứu (Research Gap) đã nêu ở Phần I, chúng tôi tiến hành khảo sát và phân tích các công trình nghiên cứu tiêu biểu của các tác giả đi trước:

Trong nghiên cứu của **Lanze và cộng sự [1]**, các tác giả đã thực hiện một cuộc khảo sát toàn diện về các kỹ thuật phát hiện Rogue AP trong mạng 802.11. Công trình chỉ ra rằng kẻ tấn công sử dụng các công cụ giả lập phần mềm (Soft AP) như `airbase-ng` hoặc thiết bị chuyên dụng như `Wi-Fi Pineapple` thường để lộ các dấu vết driver do sự khác biệt trong việc xử lý các tag thông tin (Information Elements - IEs) của gói tin Beacon so với chip vi điều khiển của router thật. Tuy nhiên, nghiên cứu của Lanze chủ yếu mang tính phân loại lý thuyết và chưa đưa ra một mô hình thực nghiệm định lượng sử dụng học máy đa chiều để tự động hóa quy trình phát hiện này.

**Sheng và cộng sự [2]** tập trung giải quyết bài toán phát hiện giả mạo địa chỉ MAC (MAC Address Spoofing) bằng cách sử dụng cường độ tín hiệu nhận được (RSSI). Tác giả chứng minh rằng do mỗi thiết bị phát sóng nằm ở một vị trí vật lý khác nhau, RSSI của chúng thu được tại các điểm giám sát sẽ tạo thành một "dấu vân tay vật lý" duy nhất. Tuy nhiên, hạn chế lớn của nghiên cứu này là RSSI cực kỳ nhạy cảm với sự thay đổi của môi trường. Trong không gian văn phòng thực tế, sự di chuyển của con người hoặc việc đóng/mở cửa có thể làm cường độ tín hiệu dao động lên tới **10-15 dB**, dẫn đến tỷ lệ báo động nhầm (False Positive) rất cao nếu chỉ dựa vào RSSI đơn lẻ.

Để khắc phục nhược điểm của RSSI, **Glass và cộng sự [3]** đề xuất phương pháp phân tích số thứ tự gói tin (Sequence Number) của khung hình 802.11. Vì số sequence được quản lý bởi bộ đếm phần cứng tự động tăng dần tuần tự, khi có hai thiết bị (AP thật và AP giả) phát sóng song song với cùng một địa chỉ MAC BSSID, bộ đếm sequence thu được tại card mạng giám sát sẽ có hiện tượng nhảy vọt không liên tục (ví dụ: đang 100 nhảy xuống 15 rồi vọt lên 101). Mặc dù phương pháp này có tính cụ thể cao, nó lại gặp giới hạn lớn trong môi trường mạng bị nghẽn (congested networks). Hiện tượng mất gói tin vật lý do nhiễu sóng cũng gây ra sự mất tuần tự sequence, khiến mô hình dễ nhầm lẫn giữa việc mất gói tin thông thường và cuộc tấn công Evil Twin thực tế.

Trong nghiên cứu tổng quan về học máy cho phát hiện Rogue AP của **Li và cộng sự [4]**, tác giả chỉ ra xu hướng sử dụng các thuật toán học máy có giám sát để kết hợp nhiều thuộc tính của gói tin Wi-Fi nhằm tăng độ chính xác. Tuy nhiên, Li cũng cảnh báo một lỗ hổng lớn trong hầu hết các tập dữ liệu lab hiện nay: **sự rò rỉ thông tin thời gian (Data Leakage)**. Các nghiên cứu sử dụng học máy dạng cây (Decision Tree, Random Forest) thường đạt độ chính xác ảo **99% - 100%** do mô hình học trực tiếp thuộc tính `Timestamp` của phiên capture dữ liệu. Khi triển khai thực tế ở một phiên làm việc khác, độ chính xác giảm xuống dưới **50%** (tương đương đoán ngẫu nhiên). Hơn nữa, các mô hình này hoạt động như một "hộp đen" (black-box), không giải thích được lý do tại sao một AP bị coi là giả mạo, gây khó khăn cho quản trị viên mạng trong việc đưa ra quyết định xử lý.

### B. Kết luận về tính độc lập của Nghiên cứu
Qua khảo sát tài liệu tham khảo [1], [2], [3], [4], chúng tôi xác nhận rằng:
1. Khoảng trống nghiên cứu về việc đánh giá hiệu năng học máy trên tập đặc trưng **hoàn toàn sạch rò rỉ dữ liệu (leak-free)** vẫn chưa được giải quyết triệt để trong các công trình trước đây.
2. Chưa có nghiên cứu nào kết hợp đồng thời cả 4 nhóm đặc trưng (vật lý, bảo mật, năng lực phần cứng, cấu trúc gói tin) để tạo ra một cơ chế phát hiện đa chiều bền vững trước các kỹ thuật ẩn danh tinh vi của kẻ tấn công.
3. Việc ứng dụng công cụ giải thích SHAP để tường minh hóa cơ chế ra quyết định của mô hình phát hiện Rogue AP là đóng góp hoàn toàn mới của nghiên cứu này, giúp kiểm chứng tính đúng đắn về mặt vật lý của mô hình thay vì chỉ dựa vào các chỉ số chính xác toán học đơn thuần.

---

## 3. METHODOLOGY (PHƯƠNG PHÁP NGHIÊN CỨU)

### A. Quy trình Xử lý Dữ liệu và Ngăn ngừa Rò rỉ Dữ liệu (Data Leakage Prevention)
Quy trình thực nghiệm được thiết kế nghiêm ngặt để phản ánh chính xác hiệu năng thực tế của mô hình. Trong nhiều nghiên cứu trước đây, các tác giả thường đưa trực tiếp các trường thời gian chụp gói tin như `Timestamp_ms`, `BeaconTimestamp`, `LowTSF` vào mô hình. Do dữ liệu AP thật và AP giả trong môi trường lab được thu thập vào các khoảng thời gian khác nhau, các mô hình học máy (đặc biệt là các mô hình dạng cây) sẽ dễ dàng học được thuộc tính thời gian này để phân loại hoàn hảo (đạt độ chính xác xấp xỉ 100%). Tuy nhiên, mô hình này hoàn toàn vô dụng trong thực tế vì kẻ tấn công có thể ra tay vào bất kỳ thời điểm nào.

Để ngăn chặn lỗi nghiêm trọng này, chúng tôi thực hiện quy trình tiền xử lý gồm 4 bước:
1. **Loại bỏ đặc trưng rò rỉ (Leakage Elimination):** Loại bỏ hoàn toàn 5 cột liên quan đến thời gian: `Timestamp_ms`, `BeaconTimestamp`, `LowTSF`, `Timestamp_Ratio`, và `time_delta`.
2. **Xử lý giá trị thiếu (Missing Data Handling):** Sử dụng phương pháp loại bỏ các dòng chứa giá trị thiếu thông qua hàm `dropna()`. Sau bước này, tập dữ liệu thu gọn từ 67.776 dòng xuống còn 45.424 dòng sạch hoàn toàn.
3. **Chuẩn hóa thang đo (Feature Scaling):** Đối với các thuật toán nhạy cảm với khoảng cách (KNN và SVM), áp dụng công thức chuẩn hóa phân phối chuẩn:
   \[
   z = \frac{x - \mu}{\sigma}
   \]
   Trong đó \(\mu\) là trung bình và \(\sigma\) là độ lệch chuẩn của đặc trưng trên tập huấn luyện. Để đảm bảo không rò rỉ thông tin từ tập kiểm thử, bộ chuẩn hóa `StandardScaler` chỉ được tính toán thông số (FIT) dựa trên tập Train và áp dụng (TRANSFORM) lên cả hai tập Train và Test.
4. **Phân chia tập dữ liệu (Dataset Partitioning):** Sử dụng phương pháp phân chia ngẫu nhiên phân tầng (Stratified Train-Test Split) với tỷ lệ **80% huấn luyện (36.339 dòng)** và **20% kiểm thử (9.085 dòng)** để giữ nguyên tỷ lệ phân bổ nhãn gốc.

### B. Hệ thống 25 Đặc trưng Wi-Fi Cốt lõi
Hệ thống 25 đặc trưng đầu vào sau khi xử lý được phân loại thành 4 nhóm mang ý nghĩa vật lý và kỹ thuật sâu sắc:

#### 1) Nhóm A: Tín hiệu vật lý (Physical Signal Features)
* **`RSSI` (dBm):** Cường độ tín hiệu nhận được. AP thật cố định thường có RSSI ổn định, trong khi AP giả di động hoặc đặt quá gần nạn nhân sẽ có RSSI biến động mạnh.
* **`Channel`:** Kênh phát sóng vật lý.
* **`rssi_std`:** Độ lệch chuẩn của RSSI trong một khung thời gian. Công thức tính:
  \[
  σ\_RSSI = \sqrt{\frac{1}{N-1} \sum_{i=1}^{N} (RSSI_i - RSSI\_avg)^2}
  \]
  \(\sigma_{RSSI}\) lớn là dấu hiệu chỉ ra thiết bị phát đang di chuyển hoặc thay đổi công suất liên tục.

#### 2) Nhóm B: Cấu hình mạng & Bảo mật (Network Configuration & Security Features)
* **`BeaconInterval`:** Khoảng thời gian định kỳ giữa các gói Beacon. Các công cụ giả lập phần mềm cũ thường mặc định phát ở khoảng chẵn 100 ms hoặc 200 ms thay vì mức tiêu chuẩn 102,4 ms của các router chuyên dụng.
* **`Privacy`:** Trạng thái mã hóa của mạng (1 = yêu cầu mật khẩu, 0 = mạng mở).
* **`IsHidden`:** Cờ ẩn SSID. AP giả thường ẩn tên để tránh bị quản trị viên quét.
* **`UnusualChannel`:** Cờ phát hiện AP hoạt động trên các kênh không phổ biến tại địa phương (ví dụ kênh 14).
* **`Is_WEP`:** Mạng sử dụng mã hóa cổ điển WEP (thường là cấu hình mặc định của các công cụ hack lỗi thời).
* **`Is_Open`:** Cờ xác định mạng hoàn toàn không có mật khẩu bảo vệ.

#### 3) Nhóm C: Năng lực phần cứng (Hardware Capability Features)
Kẻ tấn công sử dụng các card mạng USB Wi-Fi thông dụng (như các dòng chipset Atheros hoặc Ralink) thường bị giới hạn về khả năng phần cứng so với các Router thương mại cao cấp:
* **`RateCount` & `ExtRateCount`:** Số lượng tốc độ truyền dữ liệu cơ bản và mở rộng được hỗ trợ. Các driver thô sơ của kẻ tấn công thường chỉ hỗ trợ một tập tốc độ rất nghèo nàn (ví dụ 4 mức cơ bản thay vì 8 mức).
* **`HasHT`:** Hỗ trợ chuẩn High Throughput (802.11n).
* **`HTChannelWidth`:** Độ rộng băng thông (20 MHz so với 40 MHz).
* **`HTStreams`:** Số luồng MIMO tối đa. Router thật thường hỗ trợ MIMO 2x2 hoặc 4x4, trong khi card USB của kẻ tấn công thường chỉ hỗ trợ 1 luồng phát (HTStreams = 1).
* **`HasExtCap`:** Hỗ trợ các tính năng mở rộng đặc biệt.
* **`ShortPreamble` & `ShortSlot`:** Các thông số tối ưu hóa khe thời gian truyền vật lý thường bị tắt hoặc cấu hình sai trên driver giả lập.
* **`BSSID_LocalAdmin`:** Cờ địa chỉ MAC được quản lý nội bộ. Khi kẻ tấn công dùng phần mềm sinh ngẫu nhiên địa chỉ MAC, bit thứ hai của byte đầu tiên trong địa chỉ MAC sẽ bị đổi thành 1, kích hoạt cờ LocalAdmin này.

#### 4) Nhóm D: Số thứ tự & Cấu trúc gói tin (Sequence & Frame Features)
* **`SequenceNumber`:** Số sequence của gói tin.
* **`FrameLength` (bytes):** Kích thước vật lý của khung hình Beacon. Các phần mềm hack như `airbase-ng` thường vô tình chèn thêm các tag đặc trưng riêng làm kích thước khung hình thay đổi bất thường (ví dụ tăng lên 142 bytes hoặc giảm xuống 90 bytes).
* **`SSID_Length` & `EmptySSID`:** Độ dài tên mạng và cờ mạng không tên.
* **`LowSeqNumber`:** Cờ báo số sequence nhỏ bất thường (< 10), vạch trần các công cụ hack liên tục bị crash và tự khởi động lại.
* **`seq_delta`:** Hiệu số Sequence Number giữa hai gói tin liên tiếp từ cùng một nguồn phát.

### C. Các Thuật toán Học máy sử dụng
Chúng tôi lựa chọn 5 mô hình đại diện cho các trường phái học máy khác nhau để thực hiện so sánh đối chứng:
1. **K-Nearest Neighbors (KNN):** Phân loại dựa trên khoảng cách hình học Euclidean. Phù hợp cho việc đánh giá trực quan nhưng có độ trễ lớn khi tập dữ liệu lớn do phải tính toán khoảng cách với tất cả các mẫu huấn luyện.
2. **Support Vector Machine (SVM):** Sử dụng thuật toán tối ưu hóa lồi để tìm siêu phẳng phân chia lớp tuyến tính với biên lớn nhất. SVM đóng vai trò là mô hình phân loại tuyến tính cơ bản để đối chứng.
3. **Random Forest (RF):** Phương pháp Ensemble học máy dạng Bagging, xây dựng 100 cây quyết định độc lập song song để lấy biểu quyết đa số, giúp giảm thiểu hiện tượng quá khớp (Overfitting).
4. **XGBoost (Extreme Gradient Boosting):** Phương pháp Boosting tiên tiến, xây dựng các cây quyết định tuần tự, trong đó mỗi cây mới tập trung sửa lỗi phân loại sai của các cây trước đó dựa trên việc tối ưu hóa hàm mất mát. XGBoost nổi tiếng với tốc độ hội tụ nhanh và khả năng tự động xử lý tốt dữ liệu phi tuyến tính phức tạp.
5. **LightGBM:** Phiên bản nâng cấp thuật toán Boosting phát triển bởi Microsoft, chia nhánh cây theo chiều sâu lá (Leaf-wise) giúp tăng tốc độ huấn luyện tối đa trên tập dữ liệu lớn.

---

## 4. RESULT AND DISCUSSION (KẾT QUẢ VÀ THẢO LUẬN)

### A. Thiết lập Thực nghiệm
Toàn bộ quy trình thực nghiệm được triển khai trên ngôn ngữ lập trình Python 3.10, sử dụng các thư viện chuyên dụng: `scikit-learn` phiên bản 1.3, `xgboost` phiên bản 2.0, `lightgbm` phiên bản 4.0 và thư viện giải thích mô hình `shap`. Cấu hình phần cứng thử nghiệm sử dụng CPU Intel Core i7 và bộ nhớ RAM 16 GB.

### B. So sánh Hiệu năng Phân loại của các Mô hình (Objective 1.2)
Sau khi huấn luyện độc lập trên tập Train và đánh giá khách quan trên tập Test (không chứa rò rỉ dữ liệu), hiệu năng phân loại của 5 mô hình thu được chi tiết trong Bảng I dưới đây:

#### BẢNG I: BẢNG SO SÁNH HIỆU NĂNG 5 THUẬT TOÁN HỌC MÁY (LEAK-FREE)
| Thuật toán | Accuracy | Precision | Recall | F1-Score | AUC-ROC | Train Time (s) | Inference Time (s) |
|---|---|---|---|---|---|---|---|
| **KNN** | 88,98% | 91,01% | 75,64% | 82,61% | 0,9204 | 0,04s | 2,33s |
| **SVM (Linear)** | 84,48% | 88,03% | 63,84% | 74,00% | 0,8844 | 0,44s | 0,00s |
| **Random Forest** | 93,47% | 95,54% | 85,11% | 90,03% | 0,9743 | 0,49s | 0,12s |
| **XGBoost ⭐** | **94,10%** | **96,54%** | **86,04%** | **90,99%** | **0,9754** | **0,37s** | **0,02s** |
| **LightGBM** | 93,69% | **96,86%** | 84,51% | 90,27% | 0,9733 | 0,48s | 0,03s |

* Biểu đồ so sánh hiệu năng tổng thể của 5 mô hình được mô tả trực quan tại hình ảnh kết quả thực nghiệm: [model_comparison.png](file:///c:/Users/LOQ/Downloads/PROJ-NWC/plots/model_comparison.png).
* **Nhận xét về Độ chính xác thực tế:** Khi loại bỏ triệt để các đặc trưng rò rỉ thời gian, độ chính xác cao nhất đạt được là **94,10%** (XGBoost) chứ không phải 100% ảo. Đây mới là con số phản ánh năng lực phân loại thực tế của mô hình khi đối mặt với dữ liệu chưa từng thấy ngoài môi trường lab.
* **Sự vượt trội của mô hình Ensemble:** Các thuật toán dạng cây phức hợp (Random Forest, XGBoost, LightGBM) có điểm F1-Score vượt trội (>90%) so với hai mô hình truyền thống là KNN (82,61%) và SVM (74,00%). Điều này chứng minh ranh giới phân loại của các thuộc tính kỹ thuật Wi-Fi vô cùng phức tạp và mang tính phi tuyến tính cao, khiến các mô hình tuyến tính như SVM bị giới hạn khả năng học.
* **Độ trễ dự đoán (Inference Latency):** Đây là yếu tố quyết định khả năng triển khai thực tế. KNN tốn đến **2,33 giây** để dự đoán xong tập test vì độ phức tạp thuật toán tăng tuyến tính theo số mẫu. Trái lại, XGBoost chỉ mất **0,02 giây** và LightGBM mất **0,03 giây**, chứng minh tính khả thi cao để nhúng trực tiếp vào firmware của router để quét thời gian thực.

### C. Xác định các Đặc trưng Wi-Fi Cốt lõi (Objective 1.1)
Để giải quyết Mục tiêu 1.1, nghiên cứu sử dụng chỉ số độ quan trọng đặc trưng (Feature Importance) từ mô hình XGBoost tốt nhất kết hợp với phương pháp giải thích Shapley (SHAP Beeswarm) để chấm điểm tầm ảnh hưởng của các đặc trưng:

#### BẢNG II: TOP 5 ĐẶC TRƯNG QUAN TRỌNG NHẤT TRONG PHÂN LOẠI ROGUE AP
| Hạng | Đặc trưng | Độ quan trọng | Lý giải cơ chế hoạt động |
|---|---|---|---|
| 1 | `IsHidden` | 28,5% | AP giả mạo thường cố tình ẩn SSID để tránh sự chú ý của quản trị viên và quét định kỳ. |
| 2 | `Privacy` | 16,0% | Kẻ tấn công thường thiết lập mạng Open (không mật khẩu) để thu hút thiết bị nạn nhân tự động kết nối nhanh nhất. |
| 3 | `Is_WEP` | 9,7% | Chuẩn WEP cũ rất ít xuất hiện trên AP thật ngày nay nhưng lại là cấu hình mặc định trong các script giả lập AP tấn công. |
| 4 | `BSSID_LocalAdmin` | 6,9% | Vạch trần việc sử dụng phần mềm ngẫu nhiên hóa địa chỉ MAC (MAC randomization) của kẻ tấn công. |
| 5 | `HTStreams` | 6,7% | Phản ánh sự chênh lệch phần cứng: card USB của kẻ tấn công chỉ hỗ trợ 1 luồng phát, khác biệt với router thật (2-4 luồng). |

* Biểu đồ độ quan trọng đặc trưng đầy đủ của mô hình XGBoost được lưu trữ tại: [feature_importance.png](file:///c:/Users/LOQ/Downloads/PROJ-NWC/plots/feature_importance.png).
* Bản đồ đóng góp thuộc tính SHAP Beeswarm mô tả chiều hướng tác động của từng giá trị đặc trưng lên quyết định phân loại được lưu trữ tại: [shap_summary.png](file:///c:/Users/LOQ/Downloads/PROJ-NWC/plots/shap_summary.png). Phân tích SHAP chỉ ra rõ ràng rằng khi cờ `IsHidden = 1` and `BSSID_LocalAdmin = 1` đồng thời xuất hiện, mô hình sẽ bị đẩy mạnh quyết định về phía phân lớp là Rogue AP (nhãn 1).

---

## 5. CONCLUSION AND FUTURE WORK (KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN)

### A. Trả lời Câu hỏi Nghiên cứu thứ nhất (RQ1)
Thông qua kết quả thực nghiệm và các phân tích khoa học ở trên, nghiên cứu đưa ra câu trả lời cho RQ1:

> **Các mô hình học máy có giám sát hoàn toàn có thể tự động phân biệt chính xác AP hợp lệ và AP giả mạo/Evil Twin với độ chính xác thực tế đạt 94,10% và thời gian trễ cực thấp (0,02 giây) bằng cách trích xuất 25 đặc trưng kỹ thuật từ khung hình Beacon.**

* **Về Objective 1.1:** Các đặc trưng hiệu quả nhất để vạch trần Rogue AP không phải là các tham số tín hiệu dễ biến động vật lý như RSSI mà là **nhóm đặc trưng cấu hình bảo mật** (`IsHidden`, `Privacy`, `Is_WEP`) và **nhóm đặc trưng phản ánh năng lực phần cứng** (`BSSID_LocalAdmin`, `HTStreams`). Sự kết hợp đa chiều này giúp mô hình nhận diện chính xác các dấu vết phần mềm giả lập vốn không thể che giấu hoàn hảo.
* **Về Objective 1.2:** **XGBoost** là thuật toán tối ưu nhất nhờ khả năng tối ưu hóa hàm lỗi Gradient Boosting tuần tự giúp đạt độ chính xác cao nhất (94,10%), F1-Score cân bằng nhất (90,99%) và độ trễ dự đoán siêu nhỏ (0,02s).

### B. Hạn chế và Hướng phát triển Tương lai
Mặc dù đạt được kết quả ấn tượng, nghiên cứu vẫn tồn tại một số hạn chế cần khắc phục trong tương lai:
1. **Môi trường thu thập dữ liệu:** Tập dữ liệu hiện tại (`clean_dataset.csv`) được ghi nhận chủ yếu trong môi trường lab phòng thí nghiệm. Để tăng độ bền vững của mô hình trước các loại nhiễu thực tế, cần tiến hành huấn luyện mở rộng trên tập dữ liệu lớn hơn như **dataset_2** (gồm 35 file CSV, khoảng 1,75 triệu dòng) phản ánh đa dạng môi trường thực tế hơn.
2. **Độ ổn định của kết quả:** Nghiên cứu cần tích hợp thêm kỹ thuật kiểm thử chéo K-Fold (K-Fold Cross-Validation) để đưa ra khoảng tin cậy sai số (\(\pm\)) cho các chỉ số hiệu năng, đảm bảo tính khách quan tối đa.
3. **Triển khai thực địa:** Hướng phát triển tiếp theo là nhúng trực tiếp mô hình XGBoost đã huấn luyện (lưu dưới dạng file nhẹ `.pkl` hoặc chuyển đổi sang C++) lên bo mạch Raspberry Pi kết hợp với một card mạng Wi-Fi ngoài để tạo thành một thiết bị dò quét Rogue AP di động, giá thành thấp, phát cảnh báo thời gian thực qua giao diện web hoặc ứng dụng di động.

---

## TÀI LIỆU THAM KHẢO (REFERENCES)

* **[1] C. Lanze, A. Panchenko, B. Braatz, and D. Engel,** "Rogue access point detection in 802.11 wireless networks," *IEEE Communications Surveys & Tutorials*, vol. 17, no. 3, pp. 1651–1667, thirdquarter 2015. (Trích dẫn nhằm cụ thể hóa phân loại phương pháp dựa trên thuộc tính gói tin).
* **[2] S. Sheng, D. W. Oard, and M. I. Iorga,** "Detecting 802.11 MAC address spoofing using received signal strength," in *Proceedings of IEEE INFOCOM*, 2008, pp. 1768–1776. (Trích dẫn để thiết lập hệ thống chỉ số đo lường hiệu năng và biện giải thuộc tính RSSI).
* **[3] S. Glass, M. Portmann, and W. L. Tan,** "The feasibility of detecting rogue access points using packet inter-arrival time," in *Proceedings of the 2007 International Conference on Wireless Communications and Mobile Computing*, 2007, pp. 248–253. (Trích dẫn chứng minh tính khả thi của việc giám sát thụ động các đặc trưng khung hình Wi-Fi).
* **[4] M. Li, Y. Li, and Q. Wang,** "A survey of machine learning-based rogue access point detection," *IEEE Access*, vol. 6, pp. 56214–56228, 2018. (Trích dẫn chứng minh tính khả thi của các thuật toán học máy trong việc nhận diện bất thường không dây).
