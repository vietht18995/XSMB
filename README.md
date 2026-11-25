# XSMB Analytics — Antigravity Cloud Project

Dự án phân tích dữ liệu Xổ Số Kiến Thiết Miền Bắc (XSMB) giai đoạn **2014 – 2026** (`4.637` kỳ quay lịch sử, `324` kỳ năm `2026` tính đến `24/11/2026`), đóng gói sạch theo chuẩn **Antigravity Cloud Project** (tương thích 100% **Linux Cloud** & **Windows Local**, không chứa thông tin cá nhân) kèm **bảng điều khiển HTML (`index.html`)** để xem và tự đánh giá phân tích mỗi ngày.

---

## 1. Cấu Trúc Thư Mục

```text
xsmb-cloud-project/
├── index.html                               # Dashboard HTML độc lập 100% để xem & đánh giá mỗi ngày
├── GEMINI.md                                # Quy tắc dự án tự động nạp (Phương pháp v2, Schema, Kỷ luật)
├── README.md                                # Tài liệu hướng dẫn sử dụng & triển khai Cloud
├── requirements.txt                         # Phụ thuộc tùy chọn (chỉ cần openpyxl nếu xuất Excel)
├── .gitignore
├── .agents/
│   └── skills/
│       ├── updatexs/SKILL.md                # Skill tự động đồng bộ XSMB + rebuild index.html (/updatexs)
│       └── xsmb-analyze/SKILL.md            # Skill phân tích 6 trụ cột & cập nhật ma trận
├── scripts/
│   ├── auto_update_xsmb.py                  # Trình đồng bộ tự động (UTC+7, --no-excel, tự gọi build_dashboard)
│   ├── build_dashboard.py                   # Trình sinh giao diện HTML độc lập từ cache JSON (100% Python stdlib)
│   ├── xsmb_engine.py                       # Engine phân tích hợp nhất CLI (100% Python stdlib)
│   ├── crawl_2014_2026.py                   # Module xuất Excel 13 năm
│   └── export_xsmb_full.py                  # Module xuất Excel năm 2026
├── data/
│   └── xsmb_2014_2026_cache.json            # Cơ sở dữ liệu lõi 2014–2026 (~3.69 MB)
└── docs/
    ├── xsmb_knowledge_base.md               # Tổng hợp phương pháp luận v2, đối soát & thống kê 7 đài
    ├── ma_tran_cang_3_lich_su.md            # Ma trận Càng 3 năm 2026 & Kỷ lục Gan 13 năm
    └── so_do_tong_the_su_kien_trung_hop.md  # Ma trận Tổng Đề 2026 & Sơ đồ dòng chảy tín hiệu
```

---

## 2. Xem Giao Diện HTML Trên Cloud & Local

File **`index.html`** được build hoàn toàn độc lập (nhúng sẵn CSS, JS và dữ liệu phân tích mới nhất, không cần backend hay CDN ngoài):

- **Xem trên GitHub Pages (khuyên dùng trên Cloud / điện thoại):**
  1. Đẩy repo lên GitHub.
  2. Vào **Settings → Pages → Source: Deploy from a branch → `main` / `/ (root)` → Save**.
  3. Mở URL `https://<username>.github.io/<repo>/` — mỗi lần chạy `/updatexs` và `git push`, trang web tự cập nhật theo kỳ quay mới nhất.
- **Xem trực tiếp trong Antigravity Cloud / Local Workspace:**
  ```bash
  python -m http.server 8000
  ```
  Sau đó mở `http://localhost:8000` (hoặc mở trực tiếp file `index.html` bằng trình duyệt trên máy).

---

## 3. Các Lệnh Vận Hành Hằng Ngày

```bash
# 1. Cập nhật kết quả mới nhất + tự động build lại index.html (nhanh, không cần openpyxl)
python scripts/auto_update_xsmb.py --no-excel

# 2. Cập nhật đầy đủ (JSON + 2 file Excel + rebuild index.html)
python scripts/auto_update_xsmb.py

# 3. Tự build lại dashboard HTML bất kỳ lúc nào (tùy chọn --target YYYY-MM-DD)
python scripts/build_dashboard.py

# 4. Chạy phân tích chuyên sâu dạng text trên terminal
python scripts/xsmb_engine.py
python scripts/xsmb_engine.py --events 42,75 --audit-picks 06,60,32
```

### Tùy chọn đường dẫn dữ liệu qua biến môi trường
```bash
export XSMB_DATA_DIR="/path/to/data"
python scripts/auto_update_xsmb.py --no-excel
python scripts/build_dashboard.py
```
