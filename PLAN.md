# KẾ HOẠCH TRIỂN KHAI: QUIZ TEST NMPP 2026

## 1. Mục tiêu & Phạm vi (Scope)
- **Mục đích:** Xây dựng **1 ứng dụng Web/PWA duy nhất** phục vụ ôn tập và thi trắc nghiệm chuyên môn cho nhân sự **Nhà máy Thủy điện Nậm Má (NMPP)**, chạy mượt qua đường link trên **Máy tính/Laptop** và **Smartphone (Android & iOS — hỗ trợ cài ra màn hình chính & thi Offline)**.
- **Dữ liệu nguồn ban đầu:** File `Câu hỏi chuyên môn ôn tập năm 2026.xlsx` (6 bộ đề chức danh — 1.586 câu, tự động bỏ qua sheet `Tổng hợp câu hỏi`) kết hợp 2 bộ đề dùng chung (`data/extra-decks.json` — 485 câu), tổng cộng **8 bộ đề / 2.071 câu hỏi**:
  1. `ĐIỀU HÀNH VIÊN B3` (7 chuyên đề — 208 câu)
  2. `ĐIỀU HÀNH VIÊN B4` (7 chuyên đề — 213 câu)
  3. `ĐIỀU HÀNH VIÊN B5` (7 chuyên đề — 217 câu)
  4. `TRƯỞNG KÍP B5` (9 chuyên đề — 334 câu)
  5. `TRƯỞNG KÍP B4` (9 chuyên đề — 318 câu)
  6. `TRƯỞNG KÍP B3` (9 chuyên đề — 296 câu)
  7. `Bộ đề An toàn` (`AN TOAN`, 2 phần — 457 câu)
  8. `Văn hóa Doanh nghiệp` (`VHDN`, 1 phần — 28 câu, hỗ trợ nhiều đáp án)
- **Nhận diện & Kế thừa từ ứng dụng mẫu `bhpp-2026`:**
  - Tên ứng dụng: **Quiz Test NMPP 2026** (màu chủ đạo **xanh dương nhạt** — Sky Blue `#38bdf8` / `#0ea5e9`).
  - Giữ nguyên toàn bộ trải nghiệm, tính năng và các bản vá đã khóa (`@FIXED`) từ `bhpp-2026` (không thêm tính năng thừa, không cần đóng gói `.apk` Android).
- **Luồng hoạt động cốt lõi:**
  1. Chọn bộ đề theo chức danh/bậc từ danh sách thả xuống (`#deck-select`).
  2. Chọn chế độ **Thi thử** (mặc định 40 câu / 30 phút, Đạt ≥ 80%, nộp bài mới chấm) hoặc **Ôn tập** (xem đáp án đúng/sai ngay lập tức); hỗ trợ cả câu **1 đáp án** và **nhiều đáp án (`A–L`)**.
  3. Cấu hình tổng số câu trong 1 đề và phân bổ theo **tỷ lệ (%) từng chương** (*Tỷ lệ thực tế* hoặc *Chia đều*, thuật toán Hamilton `computeRatioCounts`), giữ nguyên thứ tự chuyên đề `I → II → III...`.
  4. Xáo trộn câu hỏi trong từng chuyên đề & xáo trộn đáp án an toàn (tự động ánh xạ chữ cái tham chiếu chéo `Phương án A và C đúng`, giữ phương án tổng hợp `Tất cả đều đúng/sai` ở cuối, giữ nguyên thứ tự khi gặp `phương án trên/dưới`).
  5. Ôn nhanh **Câu hay sai** / **Đã đánh dấu**, lưu lịch sử làm bài và **Xuất/Nhập sao lưu JSON** cá nhân (bỏ chức năng Import đề cục bộ trên giao diện người dùng để quản lý tập trung qua GitHub).

---

## 2. Ràng buộc kỹ thuật (Technical Constraints — Trường hợp B: Website / Web App)
- **Stack công nghệ:**
  - **Frontend:** HTML5 + Tailwind CSS + Vanilla JavaScript (ES6+), thiết kế **Mobile-First Responsive** (thanh điều hướng cố định đáy màn hình & Drawer bảng câu hỏi trên điện thoại, phím tắt `A–D`/`1–4`/`←/→` trên PC, Dark Mode, đổi cỡ chữ `Aa`).
  - **Đọc Excel phía trình duyệt:** SheetJS (`xlsx` v0.20.3) hỗ trợ import file nhiều sheet trên cả PC và Smartphone.
  - **PWA Offline (Android/iOS/PC):** `manifest.json`, bộ icon PNG (`apple-touch-icon.png` 180×180, `icon-192.png`, `icon-512.png` tông xanh dương nhạt) và Service Worker `sw.js` (`quiz-nmpp-2026-v1`).
  - **Data Pipeline:** Python 3 (`openpyxl`, `Pillow`) trích xuất dữ liệu từ Excel gốc với chuẩn `encoding="utf-8"` / ghi file nguyên tử (`.tmp` → rename) và sinh bộ icon PWA.
- **Lưu trữ & Cô lập định danh:**
  - **IndexedDB riêng:** `nmpp_2026_quiz_db` (stores: `custom_decks`, `exam_history`, `bookmarks`, `wrong_stats`) để lưu bộ đề import tùy chỉnh, lịch sử thi, câu đánh dấu và thống kê câu sai; hỗ trợ Export/Import JSON.
  - **localStorage riêng:** `nmpp_2026_settings_v1` cho cấu hình nhẹ (Dark Mode, cỡ chữ, số câu, tỷ lệ `%` từng chương, bộ đề đang chọn).
- **Bảo mật & Độ ổn định:**
  - Không hardcode API Key hay thông tin nhạy cảm; không phụ thuộc backend server.
  - Mọi tác vụ I/O (IndexedDB, đọc file Excel/JSON) bọc `try-catch-finally` kèm timeout (10 giây) và fallback an toàn về dữ liệu mặc định.
  - Dọn dẹp `setInterval` (timer đếm ngược) ngay khi nộp bài hoặc thoát màn hình làm bài (Zero Memory Leak).
  - Bảo toàn các logic quan trọng bằng comment `@FIXED` và ghi nhận trong `GEMINI.md` tại thư mục dự án.

---

## 3. Cấu trúc thư mục & File tác động
```text
e:\app trac nghiem\nmpp\
├── Câu hỏi chuyên môn ôn tập năm 2026.xlsx   # [Hiện có] File nguồn đề thi gốc (chỉ đọc)
├── PLAN.md                                   # [Mới] Kế hoạch triển khai dự án
├── GEMINI.md                                 # [Mới] Workspace Rules & Danh sách lỗi đã khóa (@FIXED)
├── .gitignore                                # [Mới] Bỏ qua file tạm/cache (__pycache__/, *.tmp, ...)
├── index.html                                # [Mới] Giao diện chính Responsive PC/Android/iOS (tông xanh dương nhạt)
├── manifest.json                             # [Mới] Cấu hình PWA (Quiz Test NMPP 2026, theme #38bdf8)
├── sw.js                                     # [Mới] Service Worker hỗ trợ chạy Offline
├── icons/
│   ├── apple-touch-icon.png                  # [Mới] Icon 180×180 cho iOS Safari
│   ├── icon-192.png                          # [Mới] Icon 192×192 PWA
│   └── icon-512.png                          # [Mới] Icon 512×512 PWA
├── scripts/
│   ├── build_nmpp_data.py                    # [Mới] Script Python parse 6 sheet Excel -> data/nmpp-2026.json & .js
│   └── generate_icons.py                     # [Mới] Script Python (Pillow) sinh bộ icon tông xanh dương nhạt
├── data/
│   ├── nmpp-2026.json                        # [Mới] Ngân hàng đề chuẩn hóa (6 bộ đề / 1.586 câu)
│   └── nmpp-2026.js                          # [Mới] Bản đóng gói window.NMPP_DATA (chạy được cả qua file://)
└── src/
    ├── styles.css                            # [Mới] CSS tùy chỉnh (cỡ chữ, nút chạm >= 48px, safe-area iOS, Toast)
    ├── db.js                                 # [Mới] Lớp quản lý IndexedDB (NmppDB) & Sao lưu JSON
    ├── excel-parser.js                       # [Mới] Bộ đọc file .xlsx nhiều sheet phía trình duyệt (NmppExcelParser)
    ├── quiz-engine.js                        # [Mới] Bộ máy trộn đề/đáp án (@FIXED), Hamilton ratio, Timer & Chấm điểm
    └── app.js                                # [Mới] Điều phối UI 5 màn hình, sự kiện PC/Mobile, Import & Lịch sử
```

---

## 4. Kế hoạch triển khai từng bước (Checklist)
- [x] **Task 1: Khởi tạo cấu hình dự án, bộ icon PWA và script trích xuất dữ liệu (`scripts/generate_icons.py`, `scripts/build_nmpp_data.py`, `GEMINI.md`, `.gitignore`)**
  - *Đầu vào:* File `Câu hỏi chuyên môn ôn tập năm 2026.xlsx`.
  - *Hành động:*
    - Viết `scripts/build_nmpp_data.py` tương thích chuẩn cấu trúc file NMPP: tự động bỏ qua sheet không có dòng tiêu đề `CÂU HỎI` (`Tổng hợp câu hỏi`), chuẩn hóa tên sheet thừa khoảng trắng (`TRƯỞNG KÍP  B4` → `TRƯỞNG KÍP B4`), nhận diện tiêu đề chuyên đề (cả dạng có số La Mã ở cột A lẫn dạng cột A trống + cột B ghi tên chuyên đề như `MÁY PHÁT ĐIỆN`, `MÁY BIẾN ÁP`... rồi tự gán mã `I, II, III...`), bỏ qua dòng `0` thừa ở cuối sheet, và ghi file nguyên tử ra `data/nmpp-2026.json` & `data/nmpp-2026.js`.
    - Viết `scripts/generate_icons.py` sinh 3 icon PNG tông xanh dương nhạt với nhãn `NMPP`.
    - Tạo `GEMINI.md` khóa sẵn 2 logic `@FIXED` kế thừa từ `bhpp` và tạo `.gitignore`.
  - *Tiêu chí hoàn thành:* Chạy script không lỗi, sinh đủ 6 bộ đề với đúng số chuyên đề (7 cho ĐHV, 9 cho Trưởng kíp) và 1.586 câu hỏi; báo cáo rõ trạng thái cảnh báo đáp án.

- [x] **Task 2: Xây dựng lõi xử lý bài thi, lưu trữ IndexedDB và bộ đọc Excel trình duyệt (`src/quiz-engine.js`, `src/db.js`, `src/excel-parser.js`)**
  - *Đầu vào:* Mã nguồn lõi ổn định từ `bhpp-2026` và đặc tả định danh `nmpp`.
  - *Hành động:*
    - Tạo `src/quiz-engine.js` giữ nguyên 100% logic đã khóa `@FIXED` (thứ tự chuyên đề `I → II → ...`, bảo toàn tham chiếu chéo `COMBINED_REF_RE`, phương án tổng hợp, thuật toán Hamilton `computeRatioCounts`, hỗ trợ 1 & nhiều đáp án, quản lý Timer an toàn).
    - Tạo `src/db.js` (`window.NmppDB`) với `DB_NAME = "nmpp_2026_quiz_db"`, `SETTINGS_KEY = "nmpp_2026_settings_v1"`, timeout 10s và Export/Import JSON.
    - Tạo `src/excel-parser.js` (`window.NmppExcelParser`) đồng bộ đúng quy tắc parse chuyên đề/sheet của NMPP để người dùng có thể tự import lại file Excel cập nhật ngay trên trình duyệt.
  - *Tiêu chí hoàn thành:* Các module chạy sạch không lỗi cú pháp, đồng nhất kết quả parse giữa Python script và SheetJS trên trình duyệt.

- [x] **Task 3: Xây dựng giao diện Responsive & PWA tông xanh dương nhạt (`index.html`, `manifest.json`, `sw.js`, `src/styles.css`, `src/app.js`)**
  - *Đầu vào:* Dữ liệu `data/nmpp-2026.js` và các module ở Task 2.
  - *Hành động:*
    - Xây dựng `index.html` mang thương hiệu **Quiz Test NMPP 2026** với bảng màu **xanh dương nhạt chủ đạo** (logo `NMPP`, nút bấm, thẻ chọn, thanh tiến độ, `theme-color: #38bdf8` / `#0ea5e9`), bố cục 5 màn hình (*Trang chủ*, *Làm bài*, *Kết quả*, *Import đề*, *Lịch sử & Sao lưu*) tương thích PC, Android & iOS.
    - Cấu hình `manifest.json` và `sw.js` (`quiz-nmpp-2026-v1`) cache toàn bộ tài nguyên cốt lõi để dùng Offline.
    - Xây dựng `src/app.js` kết nối đầy đủ sự kiện chọn bộ đề, cấu hình tỷ lệ `%`, Thi thử/Ôn tập, phím tắt PC, Drawer Mobile, Import Excel/JSON và Export/Import sao lưu.
  - *Tiêu chí hoàn thành:* Mở ứng dụng hiển thị đúng 6 bộ đề, bảng màu xanh dương nhạt hài hòa cả Light/Dark Mode, toàn bộ luồng chức năng hoạt động trơn tru.

- [x] **Task 4: Kiểm thử toàn diện trên Desktop & Mobile Viewport và chuẩn bị xuất bản Link**
  - *Đầu vào:* Toàn bộ ứng dụng đã hoàn thiện.
  - *Hành động:*
    - Kiểm tra dữ liệu đã sinh (số bộ đề, số chuyên đề, số câu hỏi, kiểm tra không có lỗi runtime JS/Console).
    - Kiểm tra giao diện trên kích thước PC và Smartphone, kiểm tra luồng chọn bộ đề, chia tỷ lệ `%`, Thi thử/Ôn tập, Import lại chính file `Câu hỏi chuyên môn ôn tập năm 2026.xlsx`, và Export/Import JSON.
    - Hướng dẫn/hỗ trợ đẩy lên GitHub Pages (khi người dùng yêu cầu `/push`) để lấy link chạy trực tiếp trên PC, Android và iOS.
  - *Tiêu chí hoàn thành:* Toàn bộ kiểm thử đạt, 0 lỗi Console, sẵn sàng xuất bản đường link sử dụng ngay.

---

## 5. Rủi ro & Cách phòng tránh
1. **Dữ liệu Excel gốc có 2 câu bị lệch/thiếu dấu `ĐA` trên cả 6 sheet:**
   - *Phát hiện thực tế khi khảo sát file `Câu hỏi chuyên môn ôn tập năm 2026.xlsx`:*
     - **Câu 21** (chuyên đề *QUY TRÌNH VẬN HÀNH NHÀ MÁY* — kích thước kênh dẫn nước): Cột ĐÁP ÁN ở phương án `A` bị gõ là `A` thay vì `ĐA`.
     - **Câu 45** (chuyên đề *QUY TRÌNH VẬN HÀNH NHÀ MÁY* — *dòng điện định mức của máy phát H2 là* `173,3 A / 183,3 A / 193,3 A / 203,3 A`): **chưa đánh dấu `ĐA` ở cả 4 phương án**.
   - *Phòng tránh:* Báo rõ để người dùng xác nhận đáp án đúng (hoặc sửa thẳng trong file Excel gốc) trước khi chốt dữ liệu; đồng thời bộ `excel-parser.js` sẽ hiển thị hộp **Cảnh báo** rõ ràng mỗi khi import file mới.
2. **Dòng chuyên đề của NMPP để trống Cột A & sheet `Tổng hợp câu hỏi` không phải đề thi:**
   - *Phòng tránh:* Viết luật nhận diện trong cả `build_nmpp_data.py` và `excel-parser.js` để bỏ qua sheet không có dòng `CÂU HỎI`, bỏ qua dòng `0` thừa ở cuối sheet, và tự nhận diện tiêu đề chuyên đề ở Cột B (khi Cột A trống và dòng kế tiếp là câu hỏi số chứ không phải phương án `A`), tự đánh số La Mã `I → IX`.
3. **Cache cũ trên điện thoại Android/iOS sau khi cập nhật đề:**
   - *Phòng tránh:* Dùng cơ chế phiên bản `CACHE_NAME` trong `sw.js` (tăng `v1 → v2...` mỗi lần cập nhật bộ đề mới) và hỗ trợ nút Import trực tiếp ngay trong ứng dụng.
4. **Mất nghĩa khi đảo đáp án hoặc xáo trộn thứ tự chuyên đề:**
   - *Phòng tránh:* Giữ nguyên 100% logic đã khóa `@FIXED` (`sectionOrderMap`, `isAggregateOption`, `COMBINED_REF_RE`) từ `bhpp-2026` và khóa trong `GEMINI.md`.
