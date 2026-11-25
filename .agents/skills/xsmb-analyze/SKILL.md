---
name: xsmb-analyze
description: >-
  Chạy quy trình phân tích XSMB thực chứng v2 (6 trụ cột thống kê + đối soát kỳ trước + kiểm chứng sự kiện thời sự ngày hiện tại)
  bằng scripts/xsmb_engine.py và cập nhật giao diện index.html để đưa ra báo cáo Lô, STL, Xiên 2, Đề, Đầu/Đuôi/Tổng và 3 Càng.
  Kích hoạt khi người dùng yêu cầu phân tích, chốt số, soi cầu, xem đề gan hoặc đối chiếu sự kiện hôm nay.
---

# Skill `xsmb-analyze` — Quy Trình Phân Tích Thực Chứng v2

## Bước 1 — Đảm Bảo Dữ Liệu & Dashboard Mới Nhất
- Kiểm tra ngày quay gần nhất trong `data/xsmb_2014_2026_cache.json`. Nếu còn thiếu kỳ đã mở thưởng (sau `18h35` giờ `UTC+7`), chạy `python scripts/auto_update_xsmb.py --no-excel` trước (lệnh này tự build lại `index.html`).

## Bước 2 — Chạy Engine Phân Tích Hợp Nhất
- Chạy một lệnh duy nhất:
  ```bash
  python scripts/xsmb_engine.py
  ```
- Nếu người dùng cung cấp thêm các con số tham chiếu trong ngày (ví dụ `42,75`), truyền thêm `--events 42,75`.
- Nếu có dàn chốt của kỳ trước cần đối soát công khai, truyền thêm `--audit-picks <danh_sách_số>`.

## Bước 3 — Kiểm Chứng Sự Kiện Thời Sự (Nếu Được Yêu Cầu)
- Dùng `search_web` tìm sự kiện nổi bật trong nước & quốc tế **đúng ngày hiện tại (`UTC+7`)**.
- Chỉ dùng con số sự kiện làm lớp lọc phụ (tie-breaker) khi trùng với nhóm ứng viên có điểm thống kê cao từ `xsmb_engine.py`. **Tuyệt đối không dùng lại sự kiện ngày cũ** và **không ép số sự kiện làm chủ lực nếu ngược cầu**.

## Bước 4 — Trình Bày Kết Quả Theo Chuẩn Kỷ Luật v2
1. **Đối soát kỳ trước** (nếu có): ghi rõ cả Trúng và Trượt, không "nhận vơ".
2. **Tín hiệu kỹ thuật cốt lõi:** Câm Đầu/Đuôi, Pascal `ĐB+G1`, Cầu kẹp, Cầu 107 vị trí (kèm tỷ lệ 2026), Bạc nhớ sau Đề gần nhất, Hồ sơ Đài theo Thứ.
3. **Chốt số phân tầng rõ ràng:**
   - **Lô:** BTL, 2–3 cặp STL chủ lực, 2–4 cặp Xiên 2, ứng viên `>=2` nháy.
   - **Đề:** BTĐ / STĐ / Tứ thủ, Dàn `10–16` số, Top 2–3 Tổng, Đầu/Đuôi trọng tâm.
   - **3 Càng:** Top 3–4 Càng chủ lực & `5–10` số 3 Càng ghép từ dàn Đề.
4. **Cảnh báo bẫy Gan & xác suất nền:** Nêu rõ Lô gan `>=12d`, Đề đại gan `>=280d` (kèm mốc Max 13 năm thực tế) và xác suất ngẫu nhiên nền (`BTL ~23.8%`, `STL ~41.9%`, `Đề 10 số = 10%`).
