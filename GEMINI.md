# WORKSPACE RULES — QUIZ TEST NMPP 2026

## QUY TẮC KIẾN TRÚC BẮT BUỘC
- **1 ứng dụng Web/PWA duy nhất cho toàn bộ bộ đề Nhà máy Thủy điện Nậm Má (NMPP):** Chạy qua link trên Máy tính/Laptop, điện thoại Android và iOS (Safari PWA offline). Tông màu chủ đạo **xanh dương nhạt** (`#38bdf8` / `#0ea5e9`).
- **Cô lập định danh lưu trữ:** Luôn giữ riêng `nmpp_2026_quiz_db` (IndexedDB), `nmpp_2026_settings_v1` (localStorage) và `quiz-nmpp-2026-v*` (Service Worker cache) để không xung đột với các ứng dụng trắc nghiệm khác.

## DANH SÁCH LỖI ĐÃ KHÓA
- **[2026-11-22] Lỗi mất nghĩa đáp án tham chiếu chéo ("Phương án A và C đúng", "Tất cả đều đúng") khi đảo đáp án (`src/quiz-engine.js`):**
  - *Nguyên nhân:* `prepareQuestion` xáo trộn toàn bộ mảng `options` nhưng giữ nguyên chữ cái tham chiếu trong văn bản đáp án (`Phương án A và C đúng`), hoặc đưa `"Tất cả đều đúng"` lên đầu.
  - *Cách khắc phục:* Ánh xạ lại chữ cái tham chiếu theo `labelMap` (`origLabel -> newLabel`) qua 1-pass `COMBINED_REF_RE` trong `remapOptionReferences`, giữ cố định phương án tổng hợp (`isAggregateOption`) ở cuối, và giữ nguyên thứ tự gốc nếu gặp tham chiếu vị trí tương đối (`phương án trên/dưới`). Đã khóa logic bằng `@FIXED`.
- **[2026-11-21] Lỗi xáo trộn lộn xộn các chuyên đề trong đề thi (`src/quiz-engine.js`):**
  - *Nguyên nhân:* Hàm `createSession` đã gọi `shuffleArray(sampled)` trên toàn bộ đề sau khi lấy câu hỏi từ các chuyên đề, làm thứ tự chuyên đề bị đảo lộn (`VII`, `I`, `V`...).
  - *Cách khắc phục:* Giữ nguyên thứ tự chuyên đề (`I` → `II` → `III`...) bằng `sectionOrderMap` ở cả chế độ `ratio` và `random`, chỉ xáo trộn câu hỏi bên trong từng chuyên đề. Đã khóa logic bằng `@FIXED`.
