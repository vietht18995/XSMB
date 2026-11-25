# XSMB Analytics Project — Quy Tắc & Ngữ Cảnh Cốt Lõi (Antigravity Rules)

Tài liệu này tự động kích hoạt trên mọi phiên hội thoại trong dự án. Tuân thủ nghiêm ngặt toàn bộ quy tắc dữ liệu, phương pháp luận v2 và kỷ luật đối soát bên dưới.

## Lệnh Nhanh Trong Chat
- **`/updatexs`** (hoặc *"cập nhật xs"*, *"cập nhật kết quả"*): Chạy ngay `python scripts/auto_update_xsmb.py --no-excel` (tự động đồng bộ JSON từ `xoso.com.vn` chuẩn giờ `UTC+7` + tự dựng lại `index.html`), sau đó đọc `.agents/skills/updatexs/SKILL.md` để tóm tắt kỳ mới và cập nhật 2 ma trận trong `docs/`.
- **`/xsmb-analyze`** (hoặc *"phân tích hôm nay"*, *"chốt số"*): Đọc `.agents/skills/xsmb-analyze/SKILL.md` và chạy `python scripts/xsmb_engine.py` để phân tích đủ 6 trụ cột v2.

---

## 1. Bảng Quy Đổi Tỷ Lệ Tham Chiếu (Khi Tính Vốn / Đánh Giá Hiệu Quả)
- Lô: `22.5k`/điểm ăn `80k`
- Đề: `1` ăn `84`
- Xiên 2: `1` ăn `14` | Xiên 3: `1` ăn `70` | Xiên 4: `1` ăn `200`
- 3 Càng: `1` ăn `800`

---

## 2. Kiến Trúc Tệp & Quy Ước Dữ Liệu (Bắt Buộc)
- **Nguồn dữ liệu chuẩn duy nhất:** `data/xsmb_2014_2026_cache.json` (JSON `dict` keyed by `YYYY-MM-DD`, lưu từ `01/01/2014` đến hiện tại).
- **Lọc kỳ quay hợp lệ (bắt buộc):** File JSON chứa cả các khóa ngày nghỉ Tết (`empty: True`). Luôn lọc:
  `isinstance(v, dict) and v.get('db') and len(str(v.get('db'))) == 5 and v.get('db') != '-----'` và sắp xếp tăng dần theo `date_iso`.
- **Cảnh báo Schema `p1`:** Trường `p1` (Giải Nhất) trong JSON là **chuỗi 5 ký tự (`str`)**, KHÔNG phải `list` như `p2..p7`. Luôn dùng helper an toàn:
  `get_p1(d) = d['p1'][0] if isinstance(d['p1'], list) else str(d['p1'])`.
- **Múi giờ chuẩn:** Luôn dùng **`UTC+7` (`Asia/Ho_Chi_Minh`)** trong mọi script và phân tích vì máy chủ cloud chạy mặc định `UTC+0`.
- **Lịch đài XSMB chuẩn theo thứ:** T2 Hà Nội | T3 Quảng Ninh | T4 Bắc Ninh | T5 Hà Nội | T6 Hải Phòng | T7 Nam Định | CN Thái Bình.
- **Công cụ chuẩn hóa:**
  - Đồng bộ kết quả mới: `python scripts/auto_update_xsmb.py` (thêm `--no-excel` nếu chỉ cần đồng bộ JSON nhanh).
  - Phân tích toàn diện (CLI): `python scripts/xsmb_engine.py` (hỗ trợ `--target YYYY-MM-DD`, `--events 42,75`, `--audit-picks 09,46`).
  - Xuất giao diện web đánh giá hằng ngày: `python scripts/build_dashboard.py` $\rightarrow$ tạo `index.html` độc lập 100%.
- **Ma trận theo dõi dài hạn (cập nhật đồng bộ mỗi khi `/updatexs`):**
  - `docs/ma_tran_cang_3_lich_su.md` (Ma trận Càng 3 năm 2026 + Gan Càng kèm Kỷ lục Max 13 năm).
  - `docs/so_do_tong_the_su_kien_trung_hop.md` (Ma trận Tổng Đề + Sơ đồ dòng chảy + Gan Tổng kèm Kỷ lục Max 13 năm).

---

## 3. Phương Pháp Luận Thực Chứng v2

### A. Nền Xác Suất Thực Tế (Không Thổi Phồng)
- Trung bình năm `2026` có `~23.75` số lô khác nhau/kỳ $\rightarrow$ Xác suất ngẫu nhiên: **BTL `~23.8%`**, **STL `~41.9%`**, **Đề 1 số `1%`**, **Đề dàn 10 số `10%`**, **3 Càng 1 số `0.1%`**.
- Mọi phân tích phải trình bày rõ **tỷ lệ lịch sử thực tế**, **số mẫu (`N`)**, và **rủi ro xác suất** — tuyệt đối không cam kết "chắc chắn nổ", "100% về" hay tạo ảo giác thắng tuyệt đối.

### B. 6 Trụ Cột Tín Hiệu Chấm Điểm
1. **Câm Đầu / Câm Đuôi kỳ liền trước:** Soi tỷ lệ bật lại trên 3 khung (`2014–2026`, riêng `2026`, và đúng cặp thứ `hôm qua -> hôm nay`).
2. **Pascal (`ĐB+G1`, `ĐB`) & Cầu kẹp `X-AB-X`:** Kiểm chứng tỷ lệ thực của Pascal `ĐB+G1` trong năm `2026` (`~46.4%`), ghép cặp với cầu chạy thông.
3. **Quét 107 vị trí giải (`ĐB[0..4]..G7.4[0..1]`):** Lọc đồng thời **chuỗi thông hiện tại** (STL `>=7d`, BTL `>=5d`, Chạm `>=4d`, Tổng `>=3d`, Càng `>=3d`) VÀ **hiệu suất cả năm `2026` / `30` ngày gần nhất** để loại cầu ăn may ngắn hạn.
4. **Bạc nhớ sau Đề `XX`:** Đối chiếu cả khung 13 năm (`2014–2026`) lẫn khung gần (`2023–2026`).
5. **Hồ sơ Đài theo Thứ trong tuần (`2026`):** Top Lô, Top STL, Top Xiên 2, Đầu/Đuôi/Tổng/Bộ/Càng mạnh nhất của đúng nhà đài quay hôm nay.
6. **Nhịp Gan – Nóng & Tránh Bẫy Đại Gan:**
   - **Lô:** Ưu tiên nhịp chín (`gan 2–7d`) và nóng `15d/30d`; trừ điểm mạnh và cảnh báo với **Lô gan `>=12` ngày** (chỉ lót nhỏ nếu có cầu cứng).
   - **Đề:** Nhịp Đề thực tế nghiêng về nhóm ấm (gan trung bình 30 ngày của Đề về dao động `~95–107` ngày). **KHÔNG ép Bạch thủ vào Đề đại gan (`>=280` ngày như `98`, `58`, `31`, `07`)**; chỉ xếp vào nhóm theo dõi / lót phụ nếu trùng Chạm & Tổng mạnh.
   - **Kỷ lục Gan 13 năm (mốc thật 2014–2026):** Gan Tổng tối đa thực tế `53–67` ngày (`Tổng 7 = 58d`, `Tổng 0 = 67d`, `Tổng 3 = 67d`); Gan Càng tối đa thực tế `48–80` ngày (`Càng 4 = 80d`, `Càng 2 = 78d`, `Càng 7 = 63d`). **Cấm tuyệt đối** gọi mức gan `20–40` ngày là "kỷ lục 13 năm" hay "vỡ đê chắc chắn".

### C. Quy Tắc Xử Lý Tin Tức / Số Tham Chiếu Trong Ngày
- Khi người dùng hỏi sự kiện thời sự trong ngày: dùng `search_web` kiểm chứng tin tức **đúng ngày hiện tại (`UTC+7`)**, có ngày giờ rõ ràng.
- Mọi bộ số tham chiếu theo sự kiện **CHỈ đóng vai trò lớp lọc phụ (tie-breaker)** khi trùng với nhóm có cầu thống kê từ `xsmb_engine.py`; không ép làm chủ lực nếu ngược thống kê.

---

## 4. Kỷ Luật Đạo Đức Dữ Liệu (Các Lỗi Cấm Lặp Lại)
1. **Cấm "nhận vơ":** Khi đối soát kết quả kỳ trước, CHỈ chấm trúng những con số thực sự đã chốt ở phiên trước. Nếu trượt phải ghi nhận thẳng thắn cả danh sách trượt và lý do.
2. **Cấm tái chế sự kiện ngày cũ:** Tuyệt đối không bê mốc sự kiện của ngày hôm qua/hôm kia sang làm luận điểm cho ngày hôm nay.
3. **Cấm ngụy tạo thống kê:** Mọi số liệu (`gan`, `max 13 năm`, `tỷ lệ %`, `số nháy`, `cầu vị trí`) phải chạy từ `python scripts/xsmb_engine.py` trên file JSON thực, không ước lượng bằng trí nhớ.
4. **Cấu trúc câu trả lời chuẩn khi chốt số:** Luôn rõ ràng, súc tích gồm: (1) Đối soát nhanh kỳ gần nhất (nếu có), (2) Tín hiệu kỹ thuật cốt lõi từ engine, (3) Bảng chốt tách bạch **Lô (BTL / STL / Xiên 2 / Lô nhiều nháy)** — **Đề (BTĐ–STĐ–Tứ thủ / Dàn 10–16 số / Đầu–Đuôi–Tổng)** — **3 Càng (5–10 số)**, (4) Cảnh báo bẫy Gan & lưu ý xác suất thực tế.
