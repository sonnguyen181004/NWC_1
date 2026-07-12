import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import os

def set_cell_background(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=120, bottom=120, left=180, right=180):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_feature_description(doc, name, concept, role, bt_example, k_bt_example):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.2)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    
    # Feature Title
    run_title = p.add_run(f"★ {name}\n")
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    run_title.font.size = Pt(11)
    
    # Concept
    run_concept_lbl = p.add_run(" - Khái niệm: ")
    run_concept_lbl.font.bold = True
    p.add_run(concept + "\n")
    
    # Role
    run_role_lbl = p.add_run(" - Vai trò trong phân loại: ")
    run_role_lbl.font.bold = True
    p.add_run(role + "\n")
    
    # Examples (bt vs k bt)
    run_bt_lbl = p.add_run("   + Bình thường (bt): ")
    run_bt_lbl.font.italic = True
    run_bt_lbl.font.bold = True
    p.add_run(bt_example + "\n")
    
    run_k_bt_lbl = p.add_run("   + Bất thường/Giả mạo (k bt): ")
    run_k_bt_lbl.font.italic = True
    run_k_bt_lbl.font.bold = True
    run_k_bt_text = p.add_run(k_bt_example)
    run_k_bt_text.font.color.rgb = RGBColor(0x99, 0x00, 0x00) # Dark red for abnormal

def create_document():
    doc = docx.Document()
    
    # Configure styles
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(12)
    style_normal.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    
    # ------------------ COVER TITLE ------------------
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.add_run("BÁO CÁO NGHIÊN CỨU THỰC NGHIỆM CHI TIẾT (RQ1)\nPHÁT HIỆN ACCESS POINT GIẢ MẠO (ROGUE AP) BẰNG HỌC MÁY\n")
    title_run.font.name = 'Times New Roman'
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = subtitle.add_run("Đánh giá 5 Thuật toán Học máy & Phân tích các Đặc trưng Wi-Fi Cốt lõi (Không Rò rỉ Dữ liệu)\n")
    sub_run.font.name = 'Times New Roman'
    sub_run.font.size = Pt(12)
    sub_run.font.italic = True
    sub_run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    
    doc.add_paragraph("\n" * 1)
    
    # ------------------ SECTION 1 ------------------
    h1 = doc.add_heading(level=1)
    h1_run = h1.add_run("1. Tổng quan Nghiên cứu và Câu hỏi Nghiên cứu 1 (RQ1)")
    h1_run.font.name = 'Times New Roman'
    h1_run.font.size = Pt(14)
    h1_run.font.bold = True
    h1_run.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    
    doc.add_paragraph(
        "Trong lĩnh vực an ninh mạng không dây, phát hiện Access Point giả mạo (Rogue AP) và cuộc tấn công giả danh "
        "mạng hợp pháp (Evil Twin) là một bài toán vô cùng quan trọng. Báo cáo thực nghiệm này tập trung giải quyết "
        "chi tiết câu hỏi nghiên cứu cốt lõi đầu tiên (RQ1):\n\n"
        "RQ1: Làm thế nào các mô hình học máy phân biệt chính xác AP hợp pháp và AP giả mạo/evil twin "
        "bằng các đặc trưng lưu lượng và cường độ tín hiệu Wi-Fi?\n"
    )
    
    doc.add_paragraph(
        "Nghiên cứu triển khai các thực nghiệm nhằm đạt được hai mục tiêu học thuật chính:\n"
        "- Objective 1.1: Xác định các đặc trưng (features) lưu lượng và tín hiệu Wi-Fi đóng vai trò quan trọng nhất trong việc phân biệt AP thật và giả mạo.\n"
        "- Objective 1.2: So sánh hiệu năng của 5 mô hình học máy có giám sát (KNN, SVM, Random Forest, XGBoost, LightGBM) để chọn ra thuật toán phân loại tối ưu."
    )
    
    doc.add_paragraph(
        "Lưu ý về tính thực tế và chống kết quả ảo (Leakage Prevention): Trong các thực nghiệm trước, mô hình đạt độ chính xác giả lập ~100% "
        "do học được các đặc trưng rò rỉ thời gian (LowTSF, BeaconTimestamp...) từ môi trường lab. Để đảm bảo mô hình hoạt động thực tế, "
        "chúng tôi đã loại bỏ hoàn toàn 5 cột rò rỉ (Timestamp_ms, BeaconTimestamp, LowTSF, Timestamp_Ratio, time_delta). "
        "Kết quả trong báo cáo này phản ánh độ chính xác thực tế của mô hình."
    )
    
    # ------------------ SECTION 2: FEATURE CONCEPTS ------------------
    h2 = doc.add_heading(level=1)
    h2_run = h2.add_run("2. Mô tả Chi tiết Khái niệm và Ví dụ Đối chứng của 25 Đặc trưng Wi-Fi")
    h2_run.font.name = 'Times New Roman'
    h2_run.font.size = Pt(14)
    h2_run.font.bold = True
    h2_run.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    
    doc.add_paragraph(
        "Dưới đây là mô tả chi tiết khái niệm, vai trò phân loại, kèm ví dụ đối chứng giữa hành vi Bình thường (bt) "
        "của thiết bị hợp pháp và hành vi Bất thường/Giả mạo (k bt) của kẻ tấn công cho toàn bộ 25 đặc trưng:"
    )
    
    features_list = [
        ("RSSI", 
         "Received Signal Strength Indicator: Chỉ số cường độ tín hiệu nhận được từ thiết bị phát sóng, đo bằng dBm.",
         "Giúp phát hiện sự thay đổi bất thường về vị trí vật lý hoặc khoảng cách của thiết bị phát sóng.",
         "RSSI dao động cực nhỏ quanh mức -50 dBm đến -53 dBm đối với AP thật được gắn cố định trên tường.",
         "RSSI dao động cực kỳ mạnh từ -45 dBm xuống -85 dBm trong vài giây (kẻ tấn công cầm thiết bị di động di chuyển) hoặc RSSI đột ngột cực mạnh (thiết bị phát đặt sát card mạng nạn nhân)."),
        
        ("Channel", 
         "Kênh tần số Wi-Fi vật lý mà gói tin được phát sóng (ví dụ các kênh từ 1 đến 13 ở băng tần 2.4 GHz).",
         "Phát hiện việc AP phát sóng sai kênh so với quy hoạch thiết lập của hệ thống mạng gốc.",
         "AP thật hoạt động cố định trên kênh 6 theo đúng quy hoạch cấu hình mạng nội bộ.",
         "Thiết bị giả mạo phát sóng trên kênh 8 (kênh không tiêu chuẩn gây nhiễu chéo) để thu hút kết nối mà không bị trùng trực tiếp kênh phát của AP thật."),
        
        ("SequenceNumber", 
         "Số thứ tự gói tin (từ 0 đến 4095) do bộ đếm phần cứng trên card mạng tự động tăng dần tuần tự theo thời gian.",
         "Phát hiện sự nhảy vọt số sequence khi kẻ tấn công chèn gói tin giả mạo vào luồng dữ liệu.",
         "Số sequence tăng đều đặn liên tục từng đơn vị: 100 -> 101 -> 102 -> 103.",
         "Số sequence nhảy lộn xộn hoặc lùi số bất ngờ (ví dụ: 100 -> 15 -> 101 -> 16) do card mạng thu được gói tin của cả AP thật và AP giả mạo phát trùng địa chỉ MAC song song."),
        
        ("BeaconInterval", 
         "Khoảng thời gian định kỳ giữa các gói tin quảng bá Beacon thông báo mạng (mặc định của chuẩn IEEE 802.11 là 102.4 ms).",
         "Phát hiện cấu hình sai lệch mặc định của các công cụ giả lập phần mềm so với router chuyên dụng.",
         "Gói tin beacon được phát đều đặn chuẩn xác mỗi 102.4 ms.",
         "Beacon được phát ra lệch chuẩn ở mức tròn chĩnh 100.0 ms hoặc 200.0 ms do kẻ tấn công dùng cấu hình mặc định lỗi thời của công cụ giả lập Airbase-ng."),
        
        ("Privacy", 
         "Cờ nhị phân chỉ định xem AP có yêu cầu mật khẩu kết nối bảo mật hay không.",
         "Nhận diện hành vi dụ dỗ người dùng kết nối vào mạng không mật khẩu.",
         "Mạng doanh nghiệp hoặc nhà riêng luôn khóa bằng mật khẩu (Privacy = 1).",
         "AP giả mạo thiết lập mạng mở (Open - Privacy = 0) để lừa thiết bị người dùng tự động kết nối (tự động bắt tay Wi-Fi)."),
        
        ("ShortPreamble", 
         "Cờ vật lý chỉ định việc sử dụng tiền tố (Preamble) ngắn để tăng tốc độ đồng bộ gói tin.",
         "Chỉ ra sự khác biệt cấu hình driver/phần cứng của card mạng tấn công.",
         "Thiết lập ShortPreamble = 1 phổ biến trên các thiết bị định tuyến hiện đại.",
         "Thiết lập ShortPreamble = 0 do card USB Wi-Fi rẻ tiền của kẻ tấn công sử dụng driver lỗi thời không bật cấu hình này."),
        
        ("ShortSlot", 
         "Cờ vật lý chỉ định slot time ngắn (9 micro giây thay vì 20 micro giây) để tăng hiệu suất truyền sóng.",
         "Đặc trưng nhận diện cấu hình khe thời gian vật lý của phần cứng phát.",
         "ShortSlot = 1 (9 micro giây) được bật mặc định trên toàn bộ hệ thống AP thật.",
         "ShortSlot = 0 (20 micro giây) xuất hiện trên thiết bị giả lập do card mạng tấn công không hỗ trợ tối ưu khe truyền dẫn."),
        
        ("RateCount", 
         "Số lượng tốc độ truyền tải dữ liệu cơ bản (Basic Rates) mà AP hỗ trợ quảng bá trong gói tin Beacon.",
         "Phát hiện sự nghèo nàn hoặc sai lệch trong driver giả lập tốc độ truyền dẫn.",
         "AP thật hỗ trợ đầy đủ 8 mức tốc độ cơ bản (1, 2, 5.5, 11, 6, 9, 12, 18 Mbps).",
         "AP giả mạo chỉ hỗ trợ 4 mức tốc độ cơ bản do driver thô sơ không khai báo đủ dải tốc độ truyền."),
        
        ("ExtRateCount", 
         "Số lượng tốc độ truyền tải dữ liệu mở rộng (Extended Rates) được AP hỗ trợ quảng bá.",
         "Đặc trưng cấu hình phần cứng truyền dẫn mở rộng.",
         "Hỗ trợ đầy đủ dải tốc độ mở rộng (ví dụ ExtRateCount = 4 hoặc 8).",
         "ExtRateCount = 0 (không hỗ trợ tốc độ mở rộng) do phần cứng USB Wi-Fi của kẻ tấn công quá cũ."),
        
        ("DSChannel", 
         "Trường thông tin kênh truyền trực tiếp được quảng bá bên trong nội dung gói tin Beacon.",
         "Phát hiện sự không đồng nhất giữa kênh vật lý thực tế phát sóng và kênh khai báo trong gói tin.",
         "Thiết bị phát trên kênh thực tế là 6 và DSChannel ghi nhận trong gói tin cũng là 6.",
         "Thiết bị phát trên kênh thực tế là 11 nhưng trường DSChannel trong gói tin vẫn ghi là 6 (do kẻ tấn công sao chép cấu hình AP thật từ xa nhưng quên sửa thông số này)."),
        
        ("HasHT", 
         "Cờ nhị phân cho biết AP có hỗ trợ chuẩn High Throughput (802.11n - Wi-Fi 4) hay không.",
         "Nhận diện phần cứng Wi-Fi đời cũ hoặc giả lập thô sơ không bật HT.",
         "HasHT = 1 được bật trên toàn bộ AP thật để hỗ trợ truyền tải tốc độ cao.",
         "HasHT = 0 do kẻ tấn công dùng card Wi-Fi USB đời cũ chỉ hỗ trợ 802.11g hoặc phần mềm giả lập không kích hoạt HT."),
        
        ("HTChannelWidth", 
         "Độ rộng băng thông kênh truyền HT (0 ứng với 20MHz, 1 ứng với 40MHz).",
         "Đặc trưng kỹ thuật truyền dẫn vật lý của ăng-ten phát sóng.",
         "HTChannelWidth = 1 (sử dụng băng thông rộng 40MHz để tối ưu hiệu năng).",
         "HTChannelWidth = 0 (bị giới hạn ở 20MHz) do card mạng của kẻ tấn công bị hạn chế về phần cứng phát sóng."),
        
        ("HTStreams", 
         "Số lượng luồng không gian truyền dẫn HT tối đa (MIMO 1x1, 2x2, 3x3).",
         "Phát hiện sự chênh lệch lớn về năng lực phần cứng giữa Router thương mại và card mạng cá nhân.",
         "Router thật cao cấp hỗ trợ MIMO 2x2 hoặc 3x3 (HTStreams = 2 hoặc 3 luồng phát).",
         "Thiết bị của kẻ tấn công chỉ hỗ trợ 1 luồng phát (HTStreams = 1) do sử dụng card USB Wi-Fi nhỏ gọn chỉ có 1 anten phát sóng."),
        
        ("HasExtCap", 
         "Cờ cho biết AP có hỗ trợ các tính năng mở rộng đặc biệt (Extended Capabilities) của chuẩn 802.11 hay không.",
         "Đặc trưng nhận diện cấu hình phần mềm điều khiển (firmware) của nhà sản xuất.",
         "HasExtCap = 1 (Router thật của Cisco/Aruba bật để hỗ trợ các tính năng doanh nghiệp nâng cao).",
         "HasExtCap = 0 (thiết bị giả lập bỏ trống trường này để giảm tải cấu trúc gói tin phát sóng)."),
        
        ("IsHidden", 
         "Cờ cho biết mạng Wi-Fi có bị ẩn tên mạng (SSID) đối với các thiết bị thông thường hay không.",
         "Phát hiện hành vi ẩn danh trộm thông tin hoặc giả lập mạng ẩn của kẻ tấn công.",
         "Mạng Wi-Fi công cộng luôn hiển thị tên rõ ràng (IsHidden = 0).",
         "AP giả mạo thiết lập ẩn SSID (IsHidden = 1) để dụ dỗ các thiết bị nạn nhân tự động phát gói tin Probe Request tìm mạng, từ đó thu thập thông tin thiết bị."),
        
        ("FrameLength", 
         "Kích thước khung gói tin Beacon vật lý bắt được trên card mạng (tính bằng bytes).",
         "Nhận diện các tag thông tin bất thường được thêm/bớt bởi phần mềm giả lập.",
         "Kích thước gói tin Beacon của hãng Cisco luôn cố định ở mức 128 bytes.",
         "Kích thước gói tin Beacon bất thường ở mức 142 bytes hoặc 90 bytes do phần mềm giả lập (Airbase-ng) tự động chèn thêm/bớt các tag định danh của công cụ hack."),
        
        ("SSID_Length", 
         "Độ dài chuỗi ký tự của tên mạng Wi-Fi (SSID).",
         "Giúp phát hiện các tên mạng trống hoặc tên mạng quá dài để tấn công tràn bộ đệm.",
         "Độ dài SSID hợp lý tương ứng với tên mạng đăng ký (ví dụ: SSID 'Wifi_Nha_Khach' có SSID_Length = 14).",
         "SSID_Length = 0 (tên mạng trống hoàn toàn) xuất hiện liên tục trên gói tin giả mạo."),
        
        ("EmptySSID", 
         "Cờ nhị phân kiểm tra xem tên Wi-Fi (SSID) có bị để trống hay không (0 là không trống, 1 là trống).",
         "Phát hiện các gói tin Probe Response giả lập không tên.",
         "Mạng Wi-Fi phát sóng bình thường luôn có tên (EmptySSID = 0).",
         "EmptySSID = 1 xuất hiện hàng loạt do kẻ tấn công giả lập phản hồi gói tin Probe request mà chưa cấu hình tên mạng."),
        
        ("BSSID_LocalAdmin", 
         "Cờ địa chỉ MAC quản trị nội bộ. Nếu địa chỉ MAC được sinh ngẫu nhiên bằng phần mềm, cờ này sẽ mang giá trị 1.",
         "Đặc trưng cực kỳ quan trọng vạch trần địa chỉ MAC giả lập bằng phần mềm của kẻ tấn công.",
         "BSSID_LocalAdmin = 0 (địa chỉ MAC vật lý gốc của nhà sản xuất Router như Cisco, Linksys bắt đầu bằng 00:0c:29...).",
         "BSSID_LocalAdmin = 1 (địa chỉ MAC giả lập bắt đầu bằng 02:1a:11... do kẻ tấn công dùng phần mềm ngẫu nhiên hóa MAC để ẩn danh)."),
        
        ("UnusualChannel", 
         "Cờ nhị phân kiểm tra xem AP có hoạt động trên các kênh phát không phổ thông hoặc bị hạn chế tại khu vực hay không.",
         "Nhận diện việc AP phát sóng bất thường ngoài quy hoạch.",
         "Hoạt động trên các kênh thông dụng 1, 6, 11 (UnusualChannel = 0).",
         "Hoạt động trên kênh 14 (kênh bị hạn chế ở hầu hết các nước trừ Nhật Bản) để ẩn mình (UnusualChannel = 1)."),
        
        ("Is_WEP", 
         "Cờ nhị phân cho biết AP có sử dụng mã hóa WEP cũ (đã bị bẻ khóa hoàn toàn) hay không.",
         "Phát hiện các cấu hình mã hóa yếu bất thường phục vụ tấn công thử nghiệm.",
         "Mạng hiện đại dùng chuẩn mã hóa an toàn WPA2 hoặc WPA3 (Is_WEP = 0).",
         "Is_WEP = 1 (sử dụng mã hóa yếu WEP) do phần mềm giả lập của kẻ tấn công thiết lập làm cấu hình mặc định."),
        
        ("Is_Open", 
         "Cờ nhị phân cho biết mạng hoàn toàn mở (không mã hóa, không mật khẩu).",
         "Phát hiện bẫy Wi-Fi miễn phí do kẻ tấn công dựng lên.",
         "Mạng doanh nghiệp hoặc nhà riêng được bảo mật bằng mật khẩu mã hóa (Is_Open = 0).",
         "Is_Open = 1 (mạng mở hoàn toàn không có mật khẩu) được kẻ tấn công dựng lên ở nơi công cộng để dụ dỗ người dùng truy cập."),
        
        ("LowSeqNumber", 
         "Cờ chỉ định số sequence của gói tin nhỏ bất thường (thường là bé hơn 10).",
         "Phát hiện hành vi thiết bị giả mạo liên tục khởi động lại hoặc công cụ tấn công vừa kích hoạt.",
         "Số sequence lớn chạy liên tục và tuần hoàn lên tới hàng ngàn (LowSeqNumber = 0).",
         "Số sequence liên tục lặp lại xung quanh các giá trị nhỏ hơn 10 (LowSeqNumber = 1) do công cụ hack của kẻ tấn công liên tục bị đặt lại hoặc crash."),
        
        ("seq_delta", 
         "Độ chênh lệch Sequence Number giữa hai gói tin liên tiếp từ cùng một nguồn phát sóng (MAC).",
         "Đặc trưng cốt lõi để vạch trần Evil Twin phát trùng địa chỉ MAC song song với AP thật.",
         "Hiệu số sequence luôn ổn định ở mức +1 (hoặc +2, +3 khi bị mất gói tin vật lý).",
         "Hiệu số sequence nhảy vọt cực lớn (ví dụ +2500) hoặc âm (ví dụ -1500) do card mạng của nạn nhân bắt xen kẽ gói tin từ cả AP thật và AP giả mạo đang chạy song song."),
        
        ("rssi_std", 
         "Độ lệch chuẩn đo lường mức độ biến động của cường độ tín hiệu RSSI trong một cửa sổ thời gian.",
         "Nhận diện sự không ổn định về khoảng cách vật lý của thiết bị tấn công di động.",
         "rssi_std cực nhỏ (dưới 1.5 dB) do AP thật được lắp cố định chắc chắn trên trần nhà.",
         "rssi_std rất lớn (trên 5.0 dB) do kẻ tấn công xách tay thiết bị phát giả mạo di chuyển liên tục để dò quét hoặc thay đổi công suất phát sóng để dụ dỗ nạn nhân.")
    ]
    
    # Write feature descriptions in the document
    for name, concept, role, bt_example, k_bt_example in features_list:
        add_feature_description(doc, name, concept, role, bt_example, k_bt_example)
        
    doc.add_paragraph("\n" * 1)
    
    # ------------------ SECTION 3: MODEL COMPARISON ------------------
    h3 = doc.add_heading(level=1)
    h3_run = h3.add_run("3. Đánh giá Thực nghiệm & So sánh 5 thuật toán (Objective 1.2)")
    h3_run.font.name = 'Times New Roman'
    h3_run.font.size = Pt(14)
    h3_run.font.bold = True
    h3_run.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    
    doc.add_paragraph(
        "Thực nghiệm tiến hành huấn luyện độc lập 5 mô hình học máy trên tập dữ liệu sạch [clean_dataset.csv](file:///c:/Users/LOQ/Downloads/PROJ-NWC/dataset/clean_dataset.csv) "
        "đã loại bỏ rò rỉ thời gian. Phân chia Train/Test theo tỷ lệ 80/20 chuẩn. Kết quả thu được như sau:"
    )
    
    # Table Results
    results_data = [
        ["Thuật toán", "Accuracy", "Precision", "Recall", "F1-Score", "AUC-ROC", "Train Time (s)", "Inference Time (s)"],
        ["KNN", "88.98%", "91.01%", "75.64%", "82.61%", "0.9204", "0.04s", "2.33s"],
        ["SVM", "84.48%", "88.03%", "63.84%", "74.00%", "0.8844", "0.44s", "0.00s"],
        ["Random Forest", "93.47%", "95.54%", "85.11%", "90.03%", "0.9743", "0.49s", "0.12s"],
        ["XGBoost", "94.10%", "96.54%", "86.04%", "90.99%", "0.9754", "0.37s", "0.02s"],
        ["LightGBM", "93.69%", "96.86%", "84.51%", "90.27%", "0.9733", "0.48s", "0.03s"]
    ]
    
    t_res = doc.add_table(rows=len(results_data), cols=len(results_data[0]))
    t_res.style = 'Light Shading Accent 1'
    
    for row_idx, row in enumerate(results_data):
        hdr_cells = t_res.rows[row_idx].cells
        for col_idx, text in enumerate(row):
            hdr_cells[col_idx].text = text
            set_cell_margins(hdr_cells[col_idx])
            if row_idx == 0:
                set_cell_background(hdr_cells[col_idx], "003366")
                hdr_cells[col_idx].paragraphs[0].runs[0].font.bold = True
                hdr_cells[col_idx].paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                hdr_cells[col_idx].paragraphs[0].runs[0].font.size = Pt(10)
            else:
                hdr_cells[col_idx].paragraphs[0].runs[0].font.size = Pt(10)
                if row_idx % 2 == 0:
                    set_cell_background(hdr_cells[col_idx], "F2F2F2")
                    
    doc.add_paragraph("\nPhân tích khoa học về kết quả thực nghiệm:")
    p_an1 = doc.add_paragraph(style='List Bullet')
    p_an1.add_run("Độ chính xác thực tế: ").bold = True
    p_an1.add_run("Sau khi loại bỏ rò rỉ dữ liệu, kết quả chính xác cao nhất đạt 94.10% (XGBoost) thay vì 100% như ban đầu. Đây là số liệu phản ánh đúng bản chất học tập của mô hình trên các đặc trưng thực tế của gói tin Wi-Fi.")
    
    p_an2 = doc.add_paragraph(style='List Bullet')
    p_an2.add_run("Sự vượt trội của mô hình Ensemble: ").bold = True
    p_an2.add_run("Các thuật toán Boosting (XGBoost, LightGBM) và Bagging (Random Forest) đạt F1-Score vượt trội (>90%) so với các thuật toán truyền thống như KNN (82.61%) hay SVM (74.00%). Điều này do ranh giới phân lớp của các thuộc tính cấu hình Wi-Fi là phi tuyến tính và phức tạp.")
    
    p_an3 = doc.add_paragraph(style='List Bullet')
    p_an3.add_run("Độ trễ dự đoán (Inference Latency): ").bold = True
    p_an3.add_run("KNN tốn tới 2.33 giây để dự đoán trên tập test do phải tính khoảng cách Euclidean với toàn bộ mẫu. XGBoost chỉ tốn 0.02 giây, chứng minh tính khả thi cao khi triển khai thời gian thực trên Router.")

    # Insert Model Comparison Image
    img_path1 = "plots/model_comparison.png"
    if os.path.exists(img_path1):
        doc.add_picture(img_path1, width=Inches(5.5))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("Hình 1: So sánh hiệu năng các mô hình KNN, SVM, RF, XGBoost và LightGBM (Leak-free)").alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph("\n" * 1)
    
    # ------------------ SECTION 4: FEATURE IMPORTANCE ------------------
    h4 = doc.add_heading(level=1)
    h4_run = h4.add_run("4. Phân tích các Đặc trưng Wi-Fi Cốt lõi (Objective 1.1)")
    h4_run.font.name = 'Times New Roman'
    h4_run.font.size = Pt(14)
    h4_run.font.bold = True
    h4_run.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    
    doc.add_paragraph(
        "Thông qua phương pháp tính Feature Importance của XGBoost và phân tích SHAP (SHapley Additive exPlanations), "
        "nghiên cứu đã xác định được các đặc trưng cốt lõi nhất đóng vai trò quyết định trong việc phân loại Rogue AP:"
    )
    
    p_det1 = doc.add_paragraph(style='List Bullet')
    p_det1.add_run("IsHidden (Độ quan trọng 28.5%): ").bold = True
    p_det1.add_run("Đây là đặc trưng quan trọng nhất. AP giả mạo thường thiết lập ẩn SSID để hoạt động bí mật hoặc tránh sự quét của quản trị viên, trong khi hầu hết AP thật trong môi trường capture đều phát sóng công khai.")
    
    p_det2 = doc.add_paragraph(style='List Bullet')
    p_det2.add_run("Privacy (Độ quan trọng 16.0%): ").bold = True
    p_det2.add_run("Cờ bảo mật. AP giả mạo thường để chế độ Open (không mật khẩu) để thu hút thiết bị của nạn nhân tự động kết nối (tấn công Evil Twin tự động).")
    
    p_det3 = doc.add_paragraph(style='List Bullet')
    p_det3.add_run("Is_WEP (Độ quan trọng 9.7%): ").bold = True
    p_det3.add_run("Cờ WEP. Chuẩn mã hóa cũ rất ít khi được AP thật sử dụng ngày nay, nhưng thường xuyên xuất hiện ở các công cụ giả lập AP giả mạo phục vụ tấn công thử nghiệm.")
    
    p_det4 = doc.add_paragraph(style='List Bullet')
    p_det4.add_run("BSSID_LocalAdmin (Độ quan trọng 6.9%): ").bold = True
    p_det4.add_run("Cờ địa chỉ MAC quản trị nội bộ. Kẻ tấn công tạo địa chỉ MAC ngẫu nhiên bằng phần mềm (macchanger) sẽ làm thay đổi bit thứ 2 của địa chỉ MAC, dẫn đến cờ này bị bật.")
    
    p_det5 = doc.add_paragraph(style='List Bullet')
    p_det5.add_run("HTStreams (Độ quan trọng 6.7%) & RateCount (Độ quan trọng 4.8%): ").bold = True
    p_det5.add_run("Năng lực phần cứng. Router Wi-Fi thương mại thật thường hỗ trợ đa luồng phát (MIMO 2x2 hoặc 4x4) và có danh sách tốc độ hỗ trợ đầy đủ. Card mạng giả lập (Wi-Fi Pineapple hoặc card USB) thường bị giới hạn về luồng (1 stream) và có tập tốc độ truyền dẫn nghèo nàn hơn.")

    # Insert Feature Importance Image
    img_path2 = "plots/feature_importance.png"
    if os.path.exists(img_path2):
        doc.add_picture(img_path2, width=Inches(5.5))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("Hình 2: Phân tích độ quan trọng của đặc trưng Wi-Fi trong mô hình XGBoost").alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Insert SHAP Summary Image
    img_path3 = "plots/shap_summary.png"
    if os.path.exists(img_path3):
        doc.add_picture(img_path3, width=Inches(5.5))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("Hình 3: Biểu đồ phân tích SHAP Beeswarm giải thích cơ chế ra quyết định của mô hình").alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph("\n" * 1)
    
    # ------------------ SECTION 5: CONCLUSION ------------------
    h5 = doc.add_heading(level=1)
    h5_run = h5.add_run("5. Kết luận khoa học cho RQ1")
    h5_run.font.name = 'Times New Roman'
    h5_run.font.size = Pt(14)
    h5_run.font.bold = True
    h5_run.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    
    doc.add_paragraph(
        "1. Các mô hình học máy có giám sát (đặc biệt là XGBoost) hoàn toàn có thể phân biệt chính xác AP giả mạo "
        "với độ chính xác thực tế đạt 94.10% khi đã loại bỏ rò rỉ dữ liệu.\n"
        "2. Nhóm đặc trưng cấu hình mạng Wi-Fi (IsHidden, Privacy, Is_WEP) và đặc trưng phần cứng (BSSID_LocalAdmin, HTStreams) "
        "là những chỉ số hiệu quả nhất để xác định Rogue AP, thay vì dựa vào các tham số thời gian chụp gói tin dễ biến động."
    )
    
    doc.save("Rogue_AP_Detection_Report.docx")
    print("Report saved successfully as Rogue_AP_Detection_Report.docx")

if __name__ == "__main__":
    create_document()
