#!/usr/bin/env python3
"""
Trình đồng bộ tự động dữ liệu XSMB (Cloud & Local Portable Edition).
- Tương thích cả Linux (Antigravity Cloud) và Windows (Local).
- Chuẩn múi giờ UTC+7 (Việt Nam) để tránh lệch ngày trên máy chủ Cloud UTC.
- Mặc định lưu dữ liệu tại <repo_root>/data/ (hoặc biến môi trường XSMB_DATA_DIR).
- Hỗ trợ --no-excel để đồng bộ JSON siêu nhanh (<2s) mà không cần cài openpyxl.
"""

import argparse
import concurrent.futures
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

VN_TZ = timezone(timedelta(hours=7))
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DEFAULT_DATA_DIR = os.environ.get("XSMB_DATA_DIR") or os.path.join(REPO_ROOT, "data")

WEEKDAY_MAP = {
    0: "Thứ 2",
    1: "Thứ 3",
    2: "Thứ 4",
    3: "Thứ 5",
    4: "Thứ 6",
    5: "Thứ 7",
    6: "Chủ Nhật",
}

STATION_BY_WEEKDAY = {
    0: "Hà Nội",
    1: "Quảng Ninh",
    2: "Bắc Ninh",
    3: "Hà Nội",
    4: "Hải Phòng",
    5: "Nam Định",
    6: "Thái Bình",
}

VALID_STATIONS = {"Hà Nội", "Quảng Ninh", "Bắc Ninh", "Hải Phòng", "Nam Định", "Thái Bình"}


def fetch_single_day(date_obj):
    date_str = date_obj.strftime("%d-%m-%Y")
    display_date = date_obj.strftime("%d/%m/%Y")
    date_iso = date_obj.strftime("%Y-%m-%d")
    url = f"https://xoso.com.vn/xsmb-{date_str}.html"

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            )
        },
    )
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                html = resp.read().decode("utf-8", errors="ignore")

            sp = re.findall(r"class=[\"']?special-prize[\"']?[^>]*>\s*(\d+)\s*<", html)
            if not sp:
                return None

            p1 = re.findall(r"class=[\"']?prize1[\"']?[^>]*>\s*(\d+)\s*<", html)
            p2 = re.findall(r"class=[\"']?prize2[\"']?[^>]*>\s*(\d+)\s*<", html)
            p3 = re.findall(r"class=[\"']?prize3[\"']?[^>]*>\s*(\d+)\s*<", html)
            p4 = re.findall(r"class=[\"']?prize4[\"']?[^>]*>\s*(\d+)\s*<", html)
            p5 = re.findall(r"class=[\"']?prize5[\"']?[^>]*>\s*(\d+)\s*<", html)
            p6 = re.findall(r"class=[\"']?prize6[\"']?[^>]*>\s*(\d+)\s*<", html)
            p7 = re.findall(r"class=[\"']?prize7[\"']?[^>]*>\s*(\d+)\s*<", html)
            codes = re.findall(r"class=[\"']?code-DB\d*[\"']?[^>]*>\s*([A-Za-z0-9]+)\s*<", html)

            wd = date_obj.weekday()
            station = STATION_BY_WEEKDAY[wd]
            for cand in re.findall(r"\(([^)]{2,30})\)", html):
                cleaned = cand.strip()
                if cleaned in VALID_STATIONS:
                    station = cleaned
                    break

            all_prizes_raw = []
            all_prizes_raw.extend(sp)
            all_prizes_raw.extend(p1)
            all_prizes_raw.extend(p2)
            all_prizes_raw.extend(p3)
            all_prizes_raw.extend(p4)
            all_prizes_raw.extend(p5)
            all_prizes_raw.extend(p6)
            all_prizes_raw.extend(p7)

            loto_27 = [num[-2:] for num in all_prizes_raw if len(num) >= 2]

            db_num = sp[0]
            db_tail2 = db_num[-2:] if len(db_num) >= 2 else ""
            db_head2 = db_num[:2] if len(db_num) >= 2 else ""
            db_cang = db_num[2] if len(db_num) == 5 else ""
            db_sum = str((int(db_tail2[0]) + int(db_tail2[1])) % 10) if len(db_tail2) == 2 else ""

            return {
                "date": display_date,
                "date_iso": date_iso,
                "weekday": WEEKDAY_MAP[wd],
                "station": station,
                "db": db_num,
                "db_head2": db_head2,
                "db_cang": db_cang,
                "db_tail2": db_tail2,
                "db_sum": db_sum,
                "p1": p1[0] if p1 else "",
                "p2": p2,
                "p3": p3,
                "p4": p4,
                "p5": p5,
                "p6": p6,
                "p7": p7,
                "loto_27_str": ", ".join(sorted(loto_27)),
                "loto_list": loto_27,
                "codes": " - ".join(codes),
            }
        except Exception:
            time.sleep(0.3)
    return None


def run_update(data_dir: str, export_excel: bool = True, fix_stations: bool = True, build_html: bool = True):
    os.makedirs(data_dir, exist_ok=True)
    checkpoint_file = os.path.join(data_dir, "xsmb_2014_2026_cache.json")
    excel_2026 = os.path.join(data_dir, "XSMB_2026_Toan_Bo_Giai_Chi_Tiet.xlsx")
    excel_13y = os.path.join(data_dir, "XSMB_2014_2026_Toan_Bo_Giai_Chi_Tiet.xlsx")

    print("=================================================================")
    print("      LỆNH CẬP NHẬT TỰ ĐỘNG XSMB (/updatexs — CLOUD EDITION)     ")
    print("=================================================================")
    print(f"[*] Thư mục dữ liệu: {data_dir}")

    cached_data = {}
    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
            print(f"[*] Đã nạp {len(cached_data)} ngày từ cache JSON.")
        except Exception as e:
            print(f"[!] Lỗi đọc cache: {e}")

    fixed_count = 0
    if fix_stations:
        for d_iso, rec in cached_data.items():
            if isinstance(rec, dict) and not rec.get("empty") and rec.get("db"):
                if rec.get("station") not in VALID_STATIONS:
                    try:
                        wd = datetime.strptime(d_iso, "%Y-%m-%d").weekday()
                        rec["station"] = STATION_BY_WEEKDAY[wd]
                        fixed_count += 1
                    except Exception:
                        pass

    start_date = datetime(2014, 1, 1).date()
    now_vn = datetime.now(VN_TZ)
    end_date = now_vn.date()

    dates_to_fetch = []
    curr = start_date
    while curr <= end_date:
        d_iso = curr.strftime("%Y-%m-%d")
        if d_iso not in cached_data:
            dates_to_fetch.append(curr)
        curr += timedelta(days=1)

    print(f"[*] Giờ Việt Nam (UTC+7): {now_vn.strftime('%Y-%m-%d %H:%M')} | Cần kiểm tra: {len(dates_to_fetch)} ngày.")

    newly_fetched = []
    cache_dirty = fixed_count > 0
    if dates_to_fetch:
        print("[*] Đang tải dữ liệu từ xoso.com.vn...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            future_to_date = {
                executor.submit(fetch_single_day, datetime.combine(d, datetime.min.time())): d
                for d in dates_to_fetch
            }
            for future in concurrent.futures.as_completed(future_to_date):
                d_obj = future_to_date[future]
                d_iso = d_obj.strftime("%Y-%m-%d")
                res = future.result()
                if res:
                    cached_data[d_iso] = res
                    newly_fetched.append(res)
                    cache_dirty = True
                else:
                    if d_obj < end_date:
                        cached_data[d_iso] = {"empty": True, "date_iso": d_iso}
                        cache_dirty = True

    if cache_dirty:
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(cached_data, f, ensure_ascii=False)
        if fixed_count:
            print(f"[*] Đã chuẩn hóa tên đài cho {fixed_count} bản ghi cũ.")

    valid_days = [
        v for v in cached_data.values()
        if isinstance(v, dict) and not v.get("empty") and v.get("db") and len(str(v.get("db"))) == 5 and v.get("db") != "-----"
    ]
    valid_days.sort(key=lambda x: x["date_iso"])
    current_year = str(end_date.year)
    valid_cur_year = [v for v in valid_days if v["date_iso"].startswith(f"{current_year}-")]

    if export_excel:
        try:
            sys.path.insert(0, SCRIPT_DIR)
            import export_xsmb_full
            import crawl_2014_2026

            print(f"\n[*] Đang xuất file Excel {current_year} ({len(valid_cur_year)} kỳ)...")
            export_xsmb_full.export_to_excel(valid_cur_year, excel_2026)

            print(f"[*] Đang xuất file Excel 13 năm ({len(valid_days)} kỳ)...")
            crawl_2014_2026.export_huge_excel(valid_days, excel_13y)
        except ImportError:
            print("[!] Bỏ qua xuất Excel vì chưa cài openpyxl (chạy `pip install openpyxl` nếu cần Excel).")

    if build_html:
        try:
            sys.path.insert(0, SCRIPT_DIR)
            import build_dashboard

            html_out = os.path.join(REPO_ROOT, "index.html")
            build_dashboard.generate_dashboard(checkpoint_file, html_out)
        except Exception as e:
            print(f"[!] Không thể sinh index.html tự động: {e}")

    print("\n=================================================================")
    if newly_fetched:
        newly_fetched.sort(key=lambda x: x["date_iso"])
        print(f"  ĐÃ CẬP NHẬT THÊM {len(newly_fetched)} KỲ QUAY MỚI NHẤT:")
        for r in newly_fetched:
            print(f"  + Ngày {r['date']} ({r['weekday']} - {r['station']}):")
            print(f"    - Ký hiệu: {r['codes']}")
            print(f"    - Giải ĐB: [{r['db']}] -> Đề [{r['db_tail2']}], Càng [{r['db_cang']}], Tổng [{r['db_sum']}]")
            print(f"    - Giải Nhất: [{r['p1']}]")
    else:
        latest = valid_days[-1]
        print("  DỮ LIỆU ĐÃ Ở TRẠNG THÁI MỚI NHẤT!")
        print(
            f"  + Kỳ mới nhất: {latest['date']} ({latest['weekday']} - {latest['station']}): "
            f"ĐB [{latest['db']}] (Đề {latest['db_tail2']}, Càng {latest['db_cang']}, Tổng {latest['db_sum']}) | G1 [{latest['p1']}]"
        )
    print(f"  + Tổng kho dữ liệu: {len(valid_days)} kỳ (2014–{current_year}) | {len(valid_cur_year)} kỳ năm {current_year}")
    print("=================================================================")


def main():
    parser = argparse.ArgumentParser(description="Đồng bộ tự động kết quả XSMB từ xoso.com.vn")
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR, help="Thư mục lưu JSON cache & Excel")
    parser.add_argument("--no-excel", action="store_true", help="Chỉ cập nhật cache JSON, bỏ qua xuất Excel")
    parser.add_argument("--no-html", action="store_true", help="Bỏ qua tự động dựng lại index.html")
    parser.add_argument("--no-fix-stations", action="store_true", help="Không chuẩn hóa lại tên đài cũ")
    args = parser.parse_args()
    run_update(
        args.data_dir,
        export_excel=not args.no_excel,
        fix_stations=not args.no_fix_stations,
        build_html=not args.no_html,
    )


if __name__ == "__main__":
    main()
