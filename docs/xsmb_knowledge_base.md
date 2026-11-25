# TÀI LIỆU TRI THỨC HỆ THỐNG PHÂN TÍCH XSMB (2014 – 2026)
### *Dữ liệu cập nhật đến **24/11/2026** (`4.637` kỳ quay `2014–2026` | `324` kỳ năm `2026`) — Phiên bản sạch chuẩn Cloud*

---

## 1. CỘT MỐC XÂY DỰNG HỆ THỐNG

| Giai đoạn | Nâng cấp kỹ thuật & phương pháp luận |
| :--- | :--- |
| **`08/2026`** | Xây dựng bộ thu thập tự động toàn bộ kết quả XSMB 13 năm (`01/01/2014 – nay`) từ `xoso.com.vn`, lưu trữ chuẩn hóa trên JSON cache + Excel 4 sheet. |
| **`09/2026`** | Tự động hóa đồng bộ bằng lệnh `/updatexs`; thiết lập kỷ luật không tái chế dữ liệu sự kiện ngày cũ. |
| **`10/2026`** | Thiết lập kỷ luật đối soát trung thực (ghi đủ Trúng & Trượt); xây dựng 2 ma trận theo dõi trực quan (`ma_tran_cang_3_lich_su.md` và `so_do_tong_the_su_kien_trung_hop.md`). |
| **`13/11/2026`** | **Cải tổ Phương pháp luận v2:** Loại bỏ hoàn toàn bẫy gan cực đại giả định, thay bằng hệ thống quét **107 vị trí giải + Kỷ lục Max 13 năm thật + Nhịp Đề ấm + Cảnh báo bẫy Đại Gan**. |
| **`25/11/2026`** | Chuẩn hóa thành **Antigravity Cloud Project** gọn nhẹ (`scripts/xsmb_engine.py`, `scripts/auto_update_xsmb.py` chuẩn `UTC+7`, và giao diện đánh giá hằng ngày `index.html` sinh từ `scripts/build_dashboard.py`). |

---

## 2. PHƯƠNG PHÁP LUẬN THỰC CHỨNG v2 & KỶ LUẬT CỐT LÕI

### 2.1. Xác suất nền & Mốc Gan 13 năm thực tế (`2014 – 2026`, `4.637` kỳ)
- **Nền ngẫu nhiên năm `2026` (`324` kỳ):** Trung bình **`23.75`** số lô khác nhau mỗi kỳ $\rightarrow$ xác suất ngẫu nhiên: **BTL `23.75%`**, **STL `41.86%`**, **Đề 1 số `1.0%`**, **Đề dàn 10 số `10.0%`**, **3 Càng 1 số `0.1%`**.
- **Hiệu suất thực chứng Pascal `ĐB+G1` năm `2026`:** **`150/323` (`46.44%`)** — cao hơn nền STL ngẫu nhiên `+4.58%`.
- **Tỷ lệ quy đổi chuẩn dùng cho module tự đánh giá lãi/lỗ:** Lô `22.5k`/điểm ăn `80k`; Đề `1` ăn `84`; Xiên 2 `1` ăn `14`; Xiên 3 `1` ăn `70`; Xiên 4 `1` ăn `200`; 3 Càng `1` ăn `800`.
- **Kỷ lục Max Gan 13 năm (mốc thật `2014–2026`):**
  - **Tổng Đề (`53 – 67` ngày):** Tổng 0 (`67d`), Tổng 3 (`67d`), Tổng 6 (`66d`), Tổng 2 (`64d`), Tổng 1 (`63d`), Tổng 8 (`59d`), Tổng 5 (`58d`), Tổng 7 (`58d`), Tổng 4 (`56d`), Tổng 9 (`53d`).
  - **Càng Đề (`48 – 80` ngày):** Càng 4 (`80d`), Càng 2 (`78d`), Càng 9 (`69d`), Càng 6 (`63d`), Càng 7 (`63d`), Càng 5 (`62d`), Càng 0 (`59d`), Càng 3 (`56d`), Càng 1 (`50d`), Càng 8 (`48d`).
- **Nhịp Đề ấm thực tế:** Trong `30` kỳ gần nhất đến `24/11/2026`, gan trung bình của Đề về là **`106.6` ngày** (`19/30` kỳ `<=100` ngày; chỉ `5/30` kỳ `>=200` ngày). Không ép Bạch thủ Đề vào nhóm đại gan `>=280` ngày (`98` đang `641d`, `58` đang `546d`, `31` đang `436d`, `07` đang `432d`).

### 2.2. Bộ 6 trụ cột chấm điểm (`scripts/xsmb_engine.py` & `scripts/build_dashboard.py`)
1. **Câm Đầu / Đuôi kỳ liền trước:** Đo tỷ lệ bật lại trên cả 3 khung (`2014–2026`, riêng `2026`, và đúng cặp thứ `hôm qua -> hôm nay`).
2. **Pascal (`ĐB+G1`, `ĐB`) & Cầu kẹp `X-AB-X` (`ĐB..G5`).**
3. **Quét 107 vị trí giải (`ĐB[0..4]..G7.4[0..1]`):** Lọc đồng thời chuỗi thông (`STL >=7d`, `BTL >=5d`, `Chạm >=4d`, `Tổng >=3d`, `Càng >=3d`) **VÀ** hiệu suất cả năm `2026` + `30` ngày gần nhất.
4. **Bạc nhớ sau Đề `XX`** (`2014–2026` & `2023–2026`).
5. **Hồ sơ Nhà Đài theo Thứ (`2026`):** T2/T5 Hà Nội, T3 Quảng Ninh, T4 Bắc Ninh, T6 Hải Phòng, T7 Nam Định, CN Thái Bình.
6. **Chấm điểm đa yếu tố + Trừ điểm bẫy Gan (`Lô >=12d`, `Đề >=280d`)**.

### 2.3. 3 Kỷ luật dữ liệu bắt buộc
1. **Đối soát minh bạch:** Ghi đủ cả số Trúng và số Trượt đúng theo danh sách đã chốt, không nhận vơ.
2. **Không tái chế dữ liệu cũ:** Tin tức/mốc tham chiếu chỉ dùng đúng ngày phát sinh.
3. **100% số liệu trích từ mã nguồn:** Mọi số liệu gan, cầu vị trí và tần suất phải chạy trực tiếp từ `data/xsmb_2014_2026_cache.json`.

---

## 3. LỊCH SỬ ĐỐI SOÁT HIỆU SUẤT THÁNG 11 (`01/11 – 24/11/2026`)

| Giai đoạn / Kỳ | Diễn biến & Kết quả thực tế | Đánh giá thẳng thắn |
| :--- | :--- | :--- |
| **`01/11 – 12/11`** *(Trước cải tổ)* | Sai hệ thống do ép Bạch thủ đại gan `98` và đánh giá nhầm mốc gan Tổng `7` (`38–40d`). | **`0/10` Đề** — Nguyên nhân trực tiếp dẫn đến cải tổ v2 ngày `13/11`. |
| **`14/11` (T7)** | Trúng `STL 48–84` (`48 x2`), `04–40` (`40`), chuẩn `Chạm 3` & `Càng 8`. Trượt BTL `52` (nổ bù `25 x2 + ĐB 61225` ngày `15/11`). | Khởi đầu ổn định theo chuẩn v2. |
| **`19/11` (T5)** | Trúng lớn `STL 29–92` cả đôi (`29 x2` + `92`), `BTL 62` G1, `57, 32, 33, 17`, chuẩn `Chạm 7`. Trượt `24` & `06–60` (câm Đầu `0`). | Hiệu suất Lô rất cao. |
| **`20/11` (T6)** | **Đỉnh cao hiệu suất:** Trúng thẳng **BTL `09`**, **Xiên 2 số 1 `09–46`**, **`46`**, **`02–20` cả đôi**, **`26`**, **`44`**, **Tứ thủ Đề `60` (`60 x2`)** và **trúng chính xác 3 Càng `760` (`ĐB 10760`)** trong 6 số chốt. Trượt `14–41`. | Hội tụ đầy đủ các trụ cột v2. |
| **`21/11` (T7)** | Trúng lót `67, 28`, chuẩn `Càng 8` (lần `10` T7) & Tổng lót `4`. Trượt chủ lực `35–53`, `34–43` và dàn Đề chính (`04`). | Ngày âm nhẹ. |
| **`22/11` (CN)** | Trúng `Pascal 08 x3`, `59` (cầu thông `12d`), `61, 69`, chuẩn `Chạm 8`. Trượt `09–90` và dàn Đề chính (xả đại gan `86` `299d`). | Ổn định dàn Lô cầu dài & Pascal. |
| **`23/11` (T2)** | **ĐB `94495` (Đề `95`, Càng `4`, Tổng `4`), G1 `61045`.** Trúng **`5` số Lô** (`45` G1, `52`, `24`, `57`, `75` — ăn cả đôi `57–75`), trúng **`3` cặp Xiên 2** (`24–57`, `45–24`, `45–75`), đúng **Càng `4`**. Trượt BTL `29`, `13–31`, `83` và dàn Đề chính (bệt Tổng `4` ngày thứ 3). | Tích cực ở dàn STL & Xiên 2. |
| **`24/11` (T3)** | **ĐB `17489` (Đề `89`, bệt Càng `4`, Tổng `7`, Bộ `34`), G1 `26330`.** `>1` nháy: `49 x2, 53 x2`. **Câm Đuôi `2` & Đuôi `6`**. | Dữ liệu chuẩn bị cho kỳ Thứ Tư `25/11`. |

---

## 4. ẢNH CHỤP THỐNG KÊ 7 NHÀ ĐÀI & GAN – NÓNG ĐẾN `24/11/2026`

### 4.1. Tổng quan 7 nhà đài theo thứ năm `2026` (`324` kỳ)
| Thứ & Nhà đài | Số kỳ | Vua Càng `2026` | Vua Tổng `2026` | Top 5 Lô hay về nhất `2026` |
| :--- | :---: | :--- | :--- | :--- |
| **Thứ Hai** — Hà Nội | `46` | **Càng 2** (`8`), Càng 4 (`7`) | **Tổng 8** (`7`), Tổng 5/6/9 (`6`) | `83` (`43.5%`), `45` (`39.1%`), `57` (`37.0%`), `89` (`37.0%`), `31` (`34.8%`) |
| **Thứ Ba** — Quảng Ninh | `46` | **Càng 0** (`7`), Càng 4/6 (`6`) | **Tổng 9, 0** (`8`), Tổng 1 (`7`) | `62` (`39.1%`), `10` (`34.8%`), `91` (`34.8%`), `47` (`32.6%`), `63` (`32.6%`) |
| **Thứ Tư** — Bắc Ninh | `45` | **Càng 1** (`9`), Càng 3/5 (`6`) | **Tổng 6** (`8`), Tổng 8/4 (`6`) | `48` (`37.8%`), `95` (`35.6%`), `60` (`35.6%`), `02` (`35.6%`), `20` (`35.6%`) |
| **Thứ Năm** — Hà Nội | `46` | **Càng 1** (`7`), Càng 0/5/6 (`6`) | **Tổng 2** (`9`), Tổng 5 (`8`) | `96` (`39.1%`), `99` (`37.0%`), `94` (`37.0%`), `06` (`37.0%`), `60` (`34.8%`) |
| **Thứ Sáu** — Hải Phòng | `47` | **Càng 1** (`9`), Càng 7 (`8`), Càng 4 (`7`) | **Tổng 1** (`8`), Tổng 4 (`7`) | `09` (`46.8%`), `46` (`40.4%`), `54` (`40.4%`), `81` (`36.2%`), `77` (`36.2%`) |
| **Thứ Bảy** — Nam Định | `47` | **Càng 8** (`10`), Càng 4 (`7`) | **Tổng 5** (`8`), Tổng 4 (`7`) | `68` (`42.6%`), `48` (`40.4%`), `52` (`38.3%`), `94` (`38.3%`), `14` (`38.3%`) |
| **Chủ Nhật** — Thái Bình | `47` | **Càng 9** (`8`), Càng 3/4/2 (`6`) | **Tổng 0** (`8`), Tổng 6/1 (`6`) | `38` (`40.4%`), `17` (`38.3%`), `03` (`38.3%`), `69` (`34.0%`), `09` (`34.0%`) |

### 4.2. Trạng thái Gan & Nóng hiện hành (`24/11/2026`)
- **Top Gan Tổng Đề:** Tổng `0` (`20d` / max `67d`), Tổng `8` (`16d` / max `59d`), Tổng `9` (`12d` / max `53d`), Tổng `2` (`10d` / max `64d`).
- **Top Gan Càng Đề:** Càng `5` (`19d` / max `62d`), Càng `0` (`17d` / max `59d`), Càng `3` (`15d` / max `56d`), Càng `6` (`14d` / max `63d`).
- **Top Gan Đầu / Đuôi Đề:** Đầu `3` (`31d`), Đầu `4` (`20d`), Đầu `5` (`11d`) | Đuôi `7` (`18d`), Đuôi `2` (`15d`), Đuôi `1` (`11d`).
- **Top 10 Đề Đại Gan (chỉ theo dõi, không ép Bạch thủ):** `98` (`641d`), `58` (`546d`), `31` (`436d`), `07` (`432d`), `27` (`311d`), `62` (`300d`), `74` (`298d`), `30` (`279d`), `49` (`263d`), `24` (`249d`).
- **Top Lô Gan (`>=10d`, cảnh báo bẫy):** `37` (`22d`), `55` (`21d`), `18` (`14d`), `81` (`12d`), `16` (`10d`), `77` (`10d`), `90` (`10d`).
- **Top Lô Nóng `15` ngày:** `92` (`9x`), `00` (`9x`), `14` (`9x`), `06` (`8x`), `12` (`8x`), `32` (`8x`), `45` (`8x`).
- **Top Lô Nóng `30` ngày:** `06` (`16x`), `34` (`15x`), `17` (`15x`), `14` (`15x`), `52` (`14x`), `04` (`13x`), `92` (`13x`), `24` (`13x`), `00` (`13x`).
