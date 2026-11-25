import sys
import os

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import urllib.request
import re
from datetime import datetime, timedelta
import concurrent.futures
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from collections import Counter

def fetch_day(date_obj):
    date_str = date_obj.strftime("%d-%m-%Y")
    display_date = date_obj.strftime("%d/%m/%Y")
    date_iso = date_obj.strftime("%Y-%m-%d")
    url = f"https://xoso.com.vn/xsmb-{date_str}.html"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8')
            
        # Parse prizes
        sp = re.findall(r'class=special-prize>(\d+)<', html)
        if not sp:
            return None # Day without results (e.g. Tet holiday or future date)
            
        p1 = re.findall(r'class=prize1>(\d+)<', html)
        p2 = re.findall(r'class=prize2>\s*(\d+)\s*<', html)
        p3 = re.findall(r'class=prize3>\s*(\d+)\s*<', html)
        p4 = re.findall(r'class=prize4>\s*(\d+)\s*<', html)
        p5 = re.findall(r'class=prize5>\s*(\d+)\s*<', html)
        p6 = re.findall(r'class=prize6>\s*(\d+)\s*<', html)
        p7 = re.findall(r'class=prize7>\s*(\d+)\s*<', html)
        codes = re.findall(r'class=code-DB\d*>\s*([A-Za-z0-9]+)\s*<', html)
        
        station_m = re.search(r'\(([^)]+)\)', html)
        station = station_m.group(1) if station_m else ''
        
        # 27 raw prizes
        all_prizes_raw = []
        if sp: all_prizes_raw.extend(sp)
        if p1: all_prizes_raw.extend(p1)
        all_prizes_raw.extend(p2)
        all_prizes_raw.extend(p3)
        all_prizes_raw.extend(p4)
        all_prizes_raw.extend(p5)
        all_prizes_raw.extend(p6)
        all_prizes_raw.extend(p7)
        
        # 27 loto numbers
        loto_27 = [num[-2:] for num in all_prizes_raw if len(num) >= 2]
        
        # DB analysis
        db_num = sp[0] if sp else ''
        db_tail2 = db_num[-2:] if len(db_num) >= 2 else ''
        db_head2 = db_num[:2] if len(db_num) >= 2 else ''
        db_cang = db_num[2] if len(db_num) == 5 else ''
        db_sum = str((int(db_tail2[0]) + int(db_tail2[1])) % 10) if len(db_tail2) == 2 else ''
        
        weekday_map = {0: 'Thứ 2', 1: 'Thứ 3', 2: 'Thứ 4', 3: 'Thứ 5', 4: 'Thứ 6', 5: 'Thứ 7', 6: 'Chủ Nhật'}
        weekday_str = weekday_map[date_obj.weekday()]
        
        return {
            'date': display_date,
            'date_iso': date_iso,
            'weekday': weekday_str,
            'station': station,
            'db': db_num,
            'db_head2': db_head2,
            'db_cang': db_cang,
            'db_tail2': db_tail2,
            'db_sum': db_sum,
            'p1': p1[0] if p1 else '',
            'p2': p2,
            'p3': p3,
            'p4': p4,
            'p5': p5,
            'p6': p6,
            'p7': p7,
            'loto_27_str': ', '.join(sorted(loto_27)),
            'loto_list': loto_27,
            'codes': ' - '.join(codes)
        }
    except Exception as e:
        return None

def fetch_all_2026():
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 9, 6)
    
    dates = []
    curr = start_date
    while curr <= end_date:
        dates.append(curr)
        curr += timedelta(days=1)
        
    print(f"Tổng số ngày cần tải: {len(dates)} ngày (từ 01/01/2026 đến 15/08/2026)")
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(fetch_day, d): d for d in dates}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                results.append(res)
                
    results.sort(key=lambda x: x['date_iso'])
    print(f"Đã tải thành công: {len(results)}/{len(dates)} ngày có kết quả mở thưởng.")
    return results

def export_to_excel(all_days, output_path):
    print(f"Đang tiến hành tạo file Excel: {output_path} ...")
    wb = openpyxl.Workbook()
    
    font_header = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
    font_bold = Font(name='Segoe UI', size=10, bold=True)
    font_regular = Font(name='Segoe UI', size=10)
    font_red_bold = Font(name='Segoe UI', size=11, bold=True, color='C00000')
    
    fill_header_dark = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
    fill_header_blue = PatternFill(start_color='2F5597', end_color='2F5597', fill_type='solid')
    fill_header_green = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')
    fill_header_gold = PatternFill(start_color='C65911', end_color='C65911', fill_type='solid')
    fill_zebra = PatternFill(start_color='F2F5F9', end_color='F2F5F9', fill_type='solid')
    
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    
    # -------------------------------------------------------------
    # SHEET 1: TOÀN BỘ KẾT QUẢ 2026 (TỔNG HỢP THEO GIẢI)
    # -------------------------------------------------------------
    ws1 = wb.active
    ws1.title = "Toàn Bộ Kết Quả 2026"
    ws1.views.sheetView[0].showGridLines = True
    
    headers1 = [
        "STT", "Ngày", "Thứ", "Đài Quay", "Ký Hiệu ĐB", 
        "Giải Đặc Biệt", "Giải Nhất", "Giải Nhì (2 số)", "Giải Ba (6 số)", 
        "Giải Tư (4 số)", "Giải Năm (6 số)", "Giải Sáu (3 số)", "Giải Bảy (4 số)", 
        "27 Số Lô Tô"
    ]
    
    ws1.append(headers1)
    for col_idx in range(1, len(headers1) + 1):
        cell = ws1.cell(1, col_idx)
        cell.font = font_header
        cell.fill = fill_header_dark
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws1.row_dimensions[1].height = 28
    
    for idx, d in enumerate(all_days, 1):
        row_vals = [
            idx,
            d['date'],
            d['weekday'],
            d['station'],
            d['codes'],
            d['db'],
            d['p1'],
            ', '.join(d['p2']),
            ', '.join(d['p3']),
            ', '.join(d['p4']),
            ', '.join(d['p5']),
            ', '.join(d['p6']),
            ', '.join(d['p7']),
            d['loto_27_str']
        ]
        ws1.append(row_vals)
        r = idx + 1
        ws1.row_dimensions[r].height = 20
        for c in range(1, len(headers1) + 1):
            cell = ws1.cell(r, c)
            cell.font = font_regular
            cell.border = thin_border
            if c in [1, 2, 3, 4]:
                cell.alignment = Alignment(horizontal='center', vertical='center')
            elif c == 6: # DB
                cell.font = font_red_bold
                cell.alignment = Alignment(horizontal='center', vertical='center')
            elif c == 7: # P1
                cell.font = font_bold
                cell.alignment = Alignment(horizontal='center', vertical='center')
            else:
                cell.alignment = Alignment(horizontal='left', vertical='center')
                
            if r % 2 == 0:
                cell.fill = fill_zebra

    # -------------------------------------------------------------
    # SHEET 2: BẢNG TÁCH CHI TIẾT 27 GIẢI
    # -------------------------------------------------------------
    ws2 = wb.create_sheet(title="Chi Tiết 27 Giải Độc Lập")
    ws2.views.sheetView[0].showGridLines = True
    
    headers2 = [
        "STT", "Ngày", "Thứ", "Đài", 
        "ĐB", "G1", 
        "G2_1", "G2_2", 
        "G3_1", "G3_2", "G3_3", "G3_4", "G3_5", "G3_6",
        "G4_1", "G4_2", "G4_3", "G4_4",
        "G5_1", "G5_2", "G5_3", "G5_4", "G5_5", "G5_6",
        "G6_1", "G6_2", "G6_3",
        "G7_1", "G7_2", "G7_3", "G7_4"
    ]
    ws2.append(headers2)
    for col_idx in range(1, len(headers2) + 1):
        cell = ws2.cell(1, col_idx)
        cell.font = font_header
        cell.fill = fill_header_blue
        cell.alignment = Alignment(horizontal='center', vertical='center')
    ws2.row_dimensions[1].height = 28
    
    for idx, d in enumerate(all_days, 1):
        p2 = d['p2'] + [''] * (2 - len(d['p2']))
        p3 = d['p3'] + [''] * (6 - len(d['p3']))
        p4 = d['p4'] + [''] * (4 - len(d['p4']))
        p5 = d['p5'] + [''] * (6 - len(d['p5']))
        p6 = d['p6'] + [''] * (3 - len(d['p6']))
        p7 = d['p7'] + [''] * (4 - len(d['p7']))
        
        row_vals = [
            idx, d['date'], d['weekday'], d['station'],
            d['db'], d['p1'],
            p2[0], p2[1],
            p3[0], p3[1], p3[2], p3[3], p3[4], p3[5],
            p4[0], p4[1], p4[2], p4[3],
            p5[0], p5[1], p5[2], p5[3], p5[4], p5[5],
            p6[0], p6[1], p6[2],
            p7[0], p7[1], p7[2], p7[3]
        ]
        ws2.append(row_vals)
        r = idx + 1
        ws2.row_dimensions[r].height = 19
        for c in range(1, len(headers2) + 1):
            cell = ws2.cell(r, c)
            cell.font = font_regular
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='center', vertical='center')
            if c == 5:
                cell.font = font_red_bold
            elif c in [6, 7, 8]:
                cell.font = font_bold
            if r % 2 == 0:
                cell.fill = fill_zebra

    # -------------------------------------------------------------
    # SHEET 3: THỐNG KÊ GIẢI ĐẶC BIỆT
    # -------------------------------------------------------------
    ws3 = wb.create_sheet(title="Thống Kê Giải Đặc Biệt")
    ws3.views.sheetView[0].showGridLines = True
    
    headers3 = [
        "STT", "Ngày", "Thứ", "Giải ĐB (5 số)", "2 Số Đầu", "Càng (Giữa)", 
        "Đề (2 Số Cuối)", "Đầu Đề", "Đuôi Đề", "Tổng Đề", "Chẵn / Lẻ", "Tài / Xỉu"
    ]
    ws3.append(headers3)
    for col_idx in range(1, len(headers3) + 1):
        cell = ws3.cell(1, col_idx)
        cell.font = font_header
        cell.fill = fill_header_gold
        cell.alignment = Alignment(horizontal='center', vertical='center')
    ws3.row_dimensions[1].height = 28
    
    for idx, d in enumerate(all_days, 1):
        de_val = int(d['db_tail2']) if d['db_tail2'].isdigit() else 0
        chan_le = "Chẵn Chẵn" if (int(d['db_tail2'][0])%2==0 and int(d['db_tail2'][1])%2==0) else \
                  "Lẻ Lẻ" if (int(d['db_tail2'][0])%2!=0 and int(d['db_tail2'][1])%2!=0) else \
                  "Chẵn Lẻ" if int(d['db_tail2'][0])%2==0 else "Lẻ Chẵn"
        tai_xiu = "Tài (>=50)" if de_val >= 50 else "Xỉu (<50)"
        
        row_vals = [
            idx, d['date'], d['weekday'], d['db'], d['db_head2'], d['db_cang'],
            d['db_tail2'], d['db_tail2'][0], d['db_tail2'][1], d['db_sum'],
            chan_le, tai_xiu
        ]
        ws3.append(row_vals)
        r = idx + 1
        ws3.row_dimensions[r].height = 19
        for c in range(1, len(headers3) + 1):
            cell = ws3.cell(r, c)
            cell.font = font_regular
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='center', vertical='center')
            if c == 4:
                cell.font = font_bold
            elif c == 7:
                cell.font = font_red_bold
            if r % 2 == 0:
                cell.fill = fill_zebra

    # -------------------------------------------------------------
    # SHEET 4: BẢNG TẦN SUẤT 100 CẶP SỐ LÔ TÔ (00 -> 99)
    # -------------------------------------------------------------
    ws4 = wb.create_sheet(title="Tần Suất Lô Tô 00-99")
    ws4.views.sheetView[0].showGridLines = True
    
    all_loto_flat = [num for d in all_days for num in d['loto_list']]
    loto_counter = Counter(all_loto_flat)
    
    de_flat = [d['db_tail2'] for d in all_days if d['db_tail2']]
    de_counter = Counter(de_flat)
    
    headers4 = [
        "Số Lô Tô", "Tổng Số Lần Về (27 Giải)", "Số Lần Về Giải ĐB (Đề)", 
        "Lần Về Gần Nhất", "Số Ngày Chưa Về (Gan)"
    ]
    ws4.append(headers4)
    for col_idx in range(1, len(headers4) + 1):
        cell = ws4.cell(1, col_idx)
        cell.font = font_header
        cell.fill = fill_header_green
        cell.alignment = Alignment(horizontal='center', vertical='center')
    ws4.row_dimensions[1].height = 28
    
    reversed_days = list(reversed(all_days))
    
    for i in range(100):
        num_str = f"{i:02d}"
        count_27 = loto_counter.get(num_str, 0)
        count_de = de_counter.get(num_str, 0)
        
        last_date = "Chưa về 2026"
        days_gan = len(all_days)
        for d_idx, d in enumerate(reversed_days):
            if num_str in d['loto_list']:
                last_date = d['date']
                days_gan = d_idx
                break
                
        row_vals = [num_str, count_27, count_de, last_date, days_gan]
        ws4.append(row_vals)
        r = i + 2
        ws4.row_dimensions[r].height = 19
        for c in range(1, len(headers4) + 1):
            cell = ws4.cell(r, c)
            cell.font = font_regular
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='center', vertical='center')
            if c == 1:
                cell.font = font_bold
            elif c == 2:
                cell.font = font_bold
            elif c == 5 and days_gan >= 10:
                cell.font = font_red_bold
            if r % 2 == 0:
                cell.fill = fill_zebra

    # Auto-adjust column widths
    for ws in [ws1, ws2, ws3, ws4]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = str(cell.value or '')
                if '\n' in val:
                    val = max(val.split('\n'), key=len)
                if len(val) > max_len:
                    max_len = len(val)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 11)
            
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    print(f"XUẤT THÀNH CÔNG: {output_path}")

if __name__ == '__main__':
    all_data = fetch_all_2026()
    dest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "XSMB_2026_Toan_Bo_Giai_Chi_Tiet.xlsx")
    export_to_excel(all_data, dest_path)
