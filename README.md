# Quiz Test NMPP 2026 — Ứng Dụng Thi Trắc Nghiệm Nhà Máy Thủy Điện Nậm Má

Ứng dụng Web/PWA thi và ôn tập trắc nghiệm chuyên môn cho nhân sự **Nhà máy Thủy điện Nậm Má (NMPP)**, hoạt động mượt mà qua đường link trên **Máy tính/Laptop**, điện thoại **Android** và **iOS** (hỗ trợ cài ra màn hình chính & thi Offline).

## 1. Chức năng chính
- **6 bộ đề chuyên môn (1.586 câu hỏi):** Chọn nhanh theo chức danh & bậc (`ĐIỀU HÀNH VIÊN B3–B5`, `TRƯỞNG KÍP B3–B5`).
- **2 chế độ làm bài:**
  - **Thi thử:** Đếm ngược thời gian (mặc định 40 câu / 30 phút, Đạt ≥ 80%), nộp bài mới chấm điểm.
  - **Ôn tập:** Xem đáp án đúng/sai ngay lập tức sau khi chọn.
- **Phân bổ câu hỏi thông minh:** Tùy chỉnh tổng số câu và tỷ lệ `%` từng chương (*Tỷ lệ thực tế* hoặc *Chia đều*, thuật toán Hamilton), giữ đúng thứ tự chuyên đề (`I → II → III...`).
- **Đảo đáp án an toàn:** Tự động ánh xạ lại chữ cái tham chiếu chéo (`Phương án A và C đúng`), giữ cố định phương án tổng hợp (`Tất cả đều đúng/sai`) ở cuối.
- **Import cập nhật đề trực tiếp từ Excel:** Đọc file `.xlsx` nhiều sheet ngay trên trình duyệt bằng SheetJS để cập nhật ngân hàng đề mới.
- **Lưu trữ & Sao lưu:** Lưu lịch sử thi, câu hay sai, câu đã đánh dấu trong **IndexedDB** (`nmpp_2026_quiz_db`), hỗ trợ **Xuất/Nhập sao lưu JSON**, Dark Mode và đổi cỡ chữ `Aa`.

## 2. Công nghệ sử dụng
- **Frontend:** HTML5, Tailwind CSS, Vanilla JavaScript (ES6+, Mobile-First Responsive, tông xanh dương nhạt).
- **PWA Offline:** Web App Manifest (`manifest.json`), bộ icon PNG và Service Worker (`sw.js`).
- **Đọc Excel phía trình duyệt:** SheetJS (`xlsx`).
- **Trích xuất dữ liệu gốc & sinh icon:** Python 3 (`openpyxl`, `Pillow`).

## 3. Cấu trúc thư mục
```text
nmpp/
├── index.html                                # Giao diện chính (Desktop, Android, iOS)
├── manifest.json                             # Cấu hình PWA
├── sw.js                                     # Service Worker hỗ trợ chạy Offline
├── Câu hỏi chuyên môn ôn tập năm 2026.xlsx   # File nguồn ngân hàng câu hỏi gốc
├── icons/                                    # Icon PWA (180x180, 192x192, 512x512)
├── data/
│   ├── nmpp-2026.json                        # Dữ liệu 6 bộ đề chuẩn hóa (1.586 câu)
│   └── nmpp-2026.js                          # Bản đóng gói JS mở trực tiếp không cần server
├── scripts/
│   ├── build_nmpp_data.py                    # Script trích xuất Excel -> JSON/JS
│   └── generate_icons.py                     # Script sinh bộ icon tông xanh dương nhạt
└── src/
    ├── styles.css                            # CSS tùy chỉnh PC & Mobile
    ├── db.js                                 # Quản lý IndexedDB & Sao lưu JSON
    ├── excel-parser.js                       # Phân tích file .xlsx nhiều sheet trên trình duyệt
    ├── quiz-engine.js                        # Trộn đề/đáp án, phân bổ tỷ lệ %, Timer & Chấm điểm
    └── app.js                                # Điều phối giao diện & sự kiện
```

## 4. Hướng dẫn sử dụng & Cập nhật dữ liệu
- **Chạy trực tiếp trên Web (PC / Android / iOS):** Truy cập link GitHub Pages sau khi bật Pages: `https://thanhbb86.github.io/namma2026/`
  - *Cài ra màn hình chính iPhone/iPad:* Mở bằng **Safari** → bấm nút **Chia sẻ** → **Thêm vào MH chính**.
  - *Cài ra màn hình chính Android:* Mở bằng **Chrome** → menu `⋮` → **Thêm vào màn hình chính** / **Cài đặt ứng dụng**.
- **Chạy cục bộ trên máy tính:** Mở trực tiếp file `index.html` bằng trình duyệt Chrome/Edge.
- **Cập nhật lại dữ liệu từ file Excel mới:** Chạy `python scripts/build_nmpp_data.py` (hoặc dùng nút **📥 Import đề** ngay trong ứng dụng).
