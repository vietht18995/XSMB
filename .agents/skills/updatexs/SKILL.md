---
name: updatexs
description: >-
  Đồng bộ tự động các kỳ quay XSMB còn thiếu từ xoso.com.vn vào data/xsmb_2014_2026_cache.json,
  tự động dựng lại bảng điều khiển index.html và cập nhật 2 ma trận theo dõi.
  Kích hoạt khi người dùng gõ /updatexs hoặc yêu cầu cập nhật kết quả xổ số.
---

# Skill `/updatexs` — Đồng Bộ Tự Động XSMB & Rebuild Dashboard HTML

Khi người dùng gọi `/updatexs` hoặc yêu cầu cập nhật dữ liệu XSMB:

1. **Chạy trình đồng bộ portable (tự động build lại `index.html`):**
   - Chế độ nhanh cho Cloud (chỉ cập nhật JSON + `index.html`, không cần `openpyxl`):
     ```bash
     python scripts/auto_update_xsmb.py --no-excel
     ```
   - Hoặc chế độ đầy đủ (cập nhật JSON + xuất 2 file Excel + `index.html`):
     ```bash
     python scripts/auto_update_xsmb.py
     ```
2. **Kiểm tra dữ liệu mới:** Đọc kết quả stdout (các ngày vừa tải thêm, Giải ĐB, Đề, Càng, Tổng, Giải Nhất, tổng số kỳ quay hiện tại).
3. **Trình bày bảng tóm tắt ngắn gọn** cho người dùng gồm: Ngày, Thứ/Đài, Giải ĐB, Đề, Càng, Tổng, Giải Nhất, tổng số kỳ và xác nhận đã cập nhật `index.html`.
4. **Cập nhật 2 tài liệu ma trận** (khi có kỳ quay mới):
   - Chạy `python scripts/xsmb_engine.py --section matrix` để lấy đúng hàng tuần mới, bảng Gan Càng/Tổng và tần suất thứ.
   - Cập nhật `docs/ma_tran_cang_3_lich_su.md` và `docs/so_do_tong_the_su_kien_trung_hop.md`.
