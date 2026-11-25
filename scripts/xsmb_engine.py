#!/usr/bin/env python3
"""
XSMB Unified Analytics Engine (v2 — Cloud & Local Portable, 100% Python Stdlib).
Thay thế toàn bộ các script phân tích đơn lẻ bằng một CLI duy nhất chạy chuẩn theo 6 trụ cột v2:
  1. Đối soát kỳ gần nhất & Bật lại sau Câm Đầu/Đuôi (3 khung: 2014-nay, năm hiện tại, cặp thứ).
  2. Pascal (ĐB+G1, ĐB) & Cầu kẹp X-AB-X.
  3. Quét toàn bộ 107 vị trí giải (Cầu STL, BTL, Chạm, Tổng, Càng kèm hiệu suất năm & 30 ngày).
  4. Bạc nhớ sau Đề kỳ trước (2014-nay & 2023-nay).
  5. Hồ sơ Đài quay theo Thứ trong tuần (Top Lô, >=2 nháy, STL, Xiên 2, Đầu/Đuôi/Tổng/Bộ/Càng).
  6. Bảng Gan & Nóng kèm Kỷ lục Max 13 năm thật + Chấm điểm đa yếu tố Lô/Đề (tránh bẫy đại gan).
"""

import argparse
import datetime
import json
import os
import sys
from collections import Counter

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DEFAULT_DATA_DIR = os.environ.get("XSMB_DATA_DIR") or os.path.join(REPO_ROOT, "data")
DEFAULT_CACHE = os.path.join(DEFAULT_DATA_DIR, "xsmb_2014_2026_cache.json")

WEEKDAY_NAMES = [
    ("Thứ Hai", "Hà Nội"),
    ("Thứ Ba", "Quảng Ninh"),
    ("Thứ Tư", "Bắc Ninh"),
    ("Thứ Năm", "Hà Nội"),
    ("Thứ Sáu", "Hải Phòng"),
    ("Thứ Bảy", "Nam Định"),
    ("Chủ Nhật", "Thái Bình"),
]


def get_p1(d):
    return d["p1"][0] if isinstance(d["p1"], list) else str(d["p1"])


def get_digit_map(d):
    m = {}
    for idx, ch in enumerate(str(d["db"])):
        m[f"ĐB[{idx}]"] = ch
    for idx, ch in enumerate(get_p1(d)):
        m[f"G1[{idx}]"] = ch
    for gname, gkey in [("G2", "p2"), ("G3", "p3"), ("G4", "p4"), ("G5", "p5"), ("G6", "p6"), ("G7", "p7")]:
        for gi, num in enumerate(d[gkey], 1):
            for idx, ch in enumerate(str(num)):
                m[f"{gname}.{gi}[{idx}]"] = ch
    return m


def pascal(num_str):
    s = [int(c) for c in num_str if c.isdigit()]
    while len(s) > 2:
        s = [(s[i] + s[i + 1]) % 10 for i in range(len(s) - 1)]
    return f"{s[0]}{s[1]}"


def get_bo(s):
    a, b = int(s[0]), int(s[1])
    sa, sb = (a + 5) % 10, (b + 5) % 10
    return min(
        f"{x}{y}"
        for x, y in [(a, b), (b, a), (sa, b), (b, sa), (a, sb), (sb, a), (sa, sb), (sb, sa)]
    )


def load_draws(cache_path):
    with open(cache_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    draws = [
        v
        for v in raw.values()
        if isinstance(v, dict) and v.get("db") and len(str(v.get("db"))) == 5 and v.get("db") != "-----"
    ]
    draws.sort(key=lambda x: x["date_iso"])
    return draws


def compute_gan_with_max(draws, fn, keys):
    n = len(draws)
    last_idx = {}
    max_gap = {k: (0, "", "") for k in keys}
    for i, d in enumerate(draws):
        val = fn(d)
        if val in last_idx:
            gap = i - last_idx[val] - 1
            if gap > max_gap[val][0]:
                max_gap[val] = (gap, draws[last_idx[val]]["date"], d["date"])
        else:
            if i > max_gap[val][0]:
                max_gap[val] = (i, "đầu chuỗi", d["date"])
        last_idx[val] = i

    res = []
    for k in keys:
        cur = n - 1 - last_idx[k] if k in last_idx else n
        if cur > max_gap[k][0]:
            max_gap[k] = (cur, draws[last_idx[k]]["date"], "hiện tại")
        ld = draws[last_idx[k]]["date"] if k in last_idx else "-"
        ldb = draws[last_idx[k]]["db"] if k in last_idx else "-"
        res.append((k, cur, max_gap[k][0], max_gap[k][1], max_gap[k][2], ld, ldb))
    return sorted(res, key=lambda r: -r[1])


def scan_107_bridges(draws, start_yr):
    n = len(draws)
    dmaps = [get_digit_map(d) for d in draws]
    pos_keys = sorted(dmaps[0].keys())
    lo_sets = [set(d["loto_list"]) for d in draws]
    de_list = [d["db_tail2"] for d in draws]
    sum_list = [d["db_sum"] for d in draws]
    cang_list = [d["db_cang"] for d in draws]

    stl_b, stl_rate, btl_b, cham_b, tong_b, cang_b = [], [], [], [], [], []
    for ia, pa in enumerate(pos_keys):
        for ib in range(ia, len(pos_keys)):
            pb = pos_keys[ib]

            st = 0
            for k in range(n - 2, max(-1, n - 35), -1):
                a, b = dmaps[k][pa], dmaps[k][pb]
                if (a + b) in lo_sets[k + 1] or (b + a) in lo_sets[k + 1]:
                    st += 1
                else:
                    break
            if st >= 5:
                h_yr = sum(
                    1
                    for k in range(start_yr, n - 1)
                    if (dmaps[k][pa] + dmaps[k][pb]) in lo_sets[k + 1]
                    or (dmaps[k][pb] + dmaps[k][pa]) in lo_sets[k + 1]
                )
                la, lb = dmaps[-1][pa], dmaps[-1][pb]
                pair = f"{min(la + lb, lb + la)}-{max(la + lb, lb + la)}"
                if st >= 7:
                    h30 = sum(
                        1
                        for k in range(n - 31, n - 1)
                        if (dmaps[k][pa] + dmaps[k][pb]) in lo_sets[k + 1]
                        or (dmaps[k][pb] + dmaps[k][pa]) in lo_sets[k + 1]
                    )
                    stl_b.append((st, h_yr, h30, pair, pa, pb))
                if h_yr >= int(0.46 * (n - 1 - start_yr)):
                    stl_rate.append((h_yr, st, pair, pa, pb))

            for first, second in ([(pa, pb), (pb, pa)] if pa != pb else [(pa, pb)]):
                stb = 0
                for k in range(n - 2, max(-1, n - 25), -1):
                    if (dmaps[k][first] + dmaps[k][second]) in lo_sets[k + 1]:
                        stb += 1
                    else:
                        break
                if stb >= 5:
                    h_yr = sum(1 for k in range(start_yr, n - 1) if (dmaps[k][first] + dmaps[k][second]) in lo_sets[k + 1])
                    h30 = sum(1 for k in range(n - 31, n - 1) if (dmaps[k][first] + dmaps[k][second]) in lo_sets[k + 1])
                    btl_b.append((stb, h_yr, h30, dmaps[-1][first] + dmaps[-1][second], first, second))

            stc = 0
            for k in range(n - 2, max(-1, n - 20), -1):
                if str((int(dmaps[k][pa]) + int(dmaps[k][pb])) % 10) in de_list[k + 1]:
                    stc += 1
                else:
                    break
            if stc >= 4:
                h30 = sum(1 for k in range(n - 31, n - 1) if str((int(dmaps[k][pa]) + int(dmaps[k][pb])) % 10) in de_list[k + 1])
                h_yr = sum(1 for k in range(start_yr, n - 1) if str((int(dmaps[k][pa]) + int(dmaps[k][pb])) % 10) in de_list[k + 1])
                cham_b.append((stc, h30, h_yr, str((int(dmaps[-1][pa]) + int(dmaps[-1][pb])) % 10), pa, pb))

            stt = 0
            for k in range(n - 2, max(-1, n - 20), -1):
                if str((int(dmaps[k][pa]) + int(dmaps[k][pb])) % 10) == sum_list[k + 1]:
                    stt += 1
                else:
                    break
            if stt >= 3:
                h30 = sum(1 for k in range(n - 31, n - 1) if str((int(dmaps[k][pa]) + int(dmaps[k][pb])) % 10) == sum_list[k + 1])
                h_yr = sum(1 for k in range(start_yr, n - 1) if str((int(dmaps[k][pa]) + int(dmaps[k][pb])) % 10) == sum_list[k + 1])
                tong_b.append((stt, h30, h_yr, str((int(dmaps[-1][pa]) + int(dmaps[-1][pb])) % 10), pa, pb))

            stcg = 0
            for k in range(n - 2, max(-1, n - 20), -1):
                if str((int(dmaps[k][pa]) + int(dmaps[k][pb])) % 10) == cang_list[k + 1]:
                    stcg += 1
                else:
                    break
            if stcg >= 3:
                h30 = sum(1 for k in range(n - 31, n - 1) if str((int(dmaps[k][pa]) + int(dmaps[k][pb])) % 10) == cang_list[k + 1])
                h_yr = sum(1 for k in range(start_yr, n - 1) if str((int(dmaps[k][pa]) + int(dmaps[k][pb])) % 10) == cang_list[k + 1])
                cang_b.append((stcg, h30, h_yr, str((int(dmaps[-1][pa]) + int(dmaps[-1][pb])) % 10), pa, pb))

    c1pos = sorted(
        [
            (
                sum(1 for k in range(n - 31, n - 1) if dmaps[k][p] in de_list[k + 1]),
                sum(1 for k in range(start_yr, n - 1) if dmaps[k][p] in de_list[k + 1]),
                dmaps[-1][p],
                p,
            )
            for p in pos_keys
        ],
        reverse=True,
    )

    stl_b.sort(key=lambda r: (-r[0], -r[1], -r[2]))
    stl_rate.sort(reverse=True)
    btl_b.sort(key=lambda r: (-r[0], -r[1], -r[2]))
    cham_b.sort(key=lambda r: (-r[0], -r[1], -r[2]))
    tong_b.sort(key=lambda r: (-r[0], -r[1], -r[2]))
    cang_b.sort(key=lambda r: (-r[0], -r[1], -r[2]))
    return stl_b, stl_rate, btl_b, cham_b, tong_b, cang_b, c1pos


def run_analysis(cache_path, target_str=None, events_str=None, audit_str=None, section="all"):
    draws = load_draws(cache_path)
    n = len(draws)
    last = draws[-1]
    last_date = datetime.date.fromisoformat(last["date_iso"])

    target_date = (
        datetime.date.fromisoformat(target_str)
        if target_str
        else last_date + datetime.timedelta(days=1)
    )
    target_wd = target_date.weekday()
    wd_name, station_name = WEEKDAY_NAMES[target_wd]

    cur_year = last["date_iso"][:4]
    d_yr = [d for d in draws if d["date_iso"].startswith(f"{cur_year}-")]
    n_yr = len(d_yr)
    start_yr = n - n_yr

    c_last = Counter(last["loto_list"])
    mult_last = [f"{k}x{v}" for k, v in sorted(c_last.items()) if v > 1]
    cam_dau = [str(i) for i in range(10) if not any(x.startswith(str(i)) for x in c_last)]
    cam_duoi = [str(i) for i in range(10) if not any(x.endswith(str(i)) for x in c_last)]

    avg_uniq = sum(len(set(d["loto_list"])) for d in d_yr) / n_yr
    p_btl = avg_uniq / 100.0
    p_stl = 1 - (1 - p_btl) ** 2

    p_dbg1 = pascal(str(last["db"]) + get_p1(last))
    p_db = pascal(str(last["db"]))
    stl_p_dbg1 = "-".join(sorted({p_dbg1, p_dbg1[::-1]}))
    stl_p_db = "-".join(sorted({p_db, p_db[::-1]}))
    p_hits_yr = sum(
        1
        for i in range(start_yr, n - 1)
        if (
            pascal(str(draws[i]["db"]) + get_p1(draws[i])) in draws[i + 1]["loto_list"]
            or pascal(str(draws[i]["db"]) + get_p1(draws[i]))[::-1] in draws[i + 1]["loto_list"]
        )
    )

    keps = []
    for gname, vals in [
        ("ĐB", [last["db"]]),
        ("G1", [get_p1(last)]),
        ("G2", last["p2"]),
        ("G3", last["p3"]),
        ("G4", last["p4"]),
        ("G5", last["p5"]),
    ]:
        for idx, s in enumerate(vals, 1):
            s = str(s)
            for j in range(len(s) - 3):
                if s[j] == s[j + 3]:
                    ab = s[j + 1 : j + 3]
                    keps.append((f"{gname}.{idx}", s, f"{min(ab, ab[::-1])}-{max(ab, ab[::-1])}"))

    need_bridges = section in ("all", "bridges", "score", "matrix")
    if need_bridges:
        stl_b, stl_rate, btl_b, cham_b, tong_b, cang_b, c1pos = scan_107_bridges(draws, start_yr)
    else:
        stl_b = stl_rate = btl_b = cham_b = tong_b = cang_b = c1pos = []

    after_de = [draws[i + 1] for i in range(n - 1) if draws[i]["db_tail2"] == last["db_tail2"]]
    after_de_rec = [d for d in after_de if d["date_iso"] >= "2023-01-01"]

    wd_draws = [d for d in d_yr if datetime.date.fromisoformat(d["date_iso"]).weekday() == target_wd]
    w_lo, w_mult, w_stl, w_pairs = Counter(), Counter(), Counter(), Counter()
    for d in wd_draws:
        c = Counter(d["loto_list"])
        u = sorted(c.keys())
        for k in c:
            w_lo[k] += 1
            if c[k] >= 2:
                w_mult[k] += 1
        for p in {f"{min(x, x[::-1])}-{max(x, x[::-1])}" for x in c}:
            w_stl[p] += 1
        for i in range(len(u)):
            for j in range(i + 1, len(u)):
                w_pairs[(u[i], u[j])] += 1

    tong_stats = compute_gan_with_max(draws, lambda d: d["db_sum"], [str(x) for x in range(10)])
    cang_stats = compute_gan_with_max(draws, lambda d: d["db_cang"], [str(x) for x in range(10)])
    dau_stats = compute_gan_with_max(draws, lambda d: d["db_tail2"][0], [str(x) for x in range(10)])
    duoi_stats = compute_gan_with_max(draws, lambda d: d["db_tail2"][1], [str(x) for x in range(10)])
    de_stats = compute_gan_with_max(draws, lambda d: d["db_tail2"], [f"{x:02d}" for x in range(100)])

    lo_li = {}
    for i, d in enumerate(draws):
        for x in set(d["loto_list"]):
            lo_li[x] = i
    lo_gan = {f"{x:02d}": n - 1 - lo_li[f"{x:02d}"] for x in range(100)}
    lo15, lo30 = Counter(), Counter()
    for d in draws[-15:]:
        for x in d["loto_list"]:
            lo15[x] += 1
    for d in draws[-30:]:
        for x in d["loto_list"]:
            lo30[x] += 1

    # --- SECTION: SUMMARY ---
    if section in ("all", "summary"):
        print(f"==========================================================================")
        print(f" XSMB ENGINE v2 | MỤC TIÊU: {target_date.strftime('%d/%m/%Y')} ({wd_name} — {station_name})")
        print(f" Dữ liệu: {n} kỳ (2014–{cur_year}) | {n_yr} kỳ năm {cur_year} | Mới nhất: {last['date']}")
        print(f" Nền ngẫu nhiên {cur_year}: TB {avg_uniq:.2f} số/kỳ -> BTL={p_btl*100:.2f}% | STL={p_stl*100:.2f}%")
        print(f"==========================================================================")
        print(f"Kỳ gần nhất ({last['date']} - {last['weekday']}): ĐB={last['db']} (Đề {last['db_tail2']}, Càng {last['db_cang']}, Tổng {last['db_sum']}, Bộ {get_bo(last['db_tail2'])}) | G1={get_p1(last)}")
        print(f"  >1 nháy: {mult_last} | Đầu câm: {cam_dau} | Đuôi câm: {cam_duoi}")
        if audit_str:
            picks = [x.strip().zfill(2) for x in audit_str.split(",") if x.strip()]
            hits = {p: c_last[p] for p in picks if c_last[p] > 0}
            misses = [p for p in picks if c_last[p] == 0]
            print(f"  [AUDIT KỲ TRƯỚC] Trúng ({len(hits)}/{len(picks)}): {hits} | Trượt: {misses}")

        for kind, c_list in [("Đầu", cam_dau), ("Đuôi", cam_duoi)]:
            for ch in c_list:
                idx_pos = 0 if kind == "Đầu" else 1
                all_c, yr_c, wd_c = [], [], []
                for i in range(n - 1):
                    ss = {x[idx_pos] for x in draws[i]["loto_list"]}
                    if ch not in ss:
                        all_c.append(draws[i + 1])
                        if draws[i]["date_iso"].startswith(f"{cur_year}-"):
                            yr_c.append(draws[i + 1])
                        if datetime.date.fromisoformat(draws[i + 1]["date_iso"]).weekday() == target_wd:
                            wd_c.append(draws[i + 1])
                print(f"\n--- BẬT LẠI SAU CÂM {kind.upper()} {ch} ---")
                for sub, lbl in [(all_c, f"2014-{cur_year}"), (yr_c, f"Riêng {cur_year}"), (wd_c, f"-> {wd_name}")]:
                    if not sub:
                        continue
                    hits = [sum(1 for x in d["loto_list"] if x[idx_pos] == ch) for d in sub]
                    cn, cs = Counter(), Counter()
                    for d in sub:
                        for x in set(d["loto_list"]):
                            cn[x] += 1
                        for k in range(10):
                            p1s, p2s = (f"{ch}{k}", f"{k}{ch}") if idx_pos == 0 else (f"{k}{ch}", f"{ch}{k}")
                            if p1s in d["loto_list"] or p2s in d["loto_list"]:
                                cs[f"{min(p1s, p2s)}-{max(p1s, p2s)}"] += 1
                    nums = [f"{ch}{k}" if idx_pos == 0 else f"{k}{ch}" for k in range(10)]
                    top_n = sorted([(num, cn[num], f"{cn[num]/len(sub)*100:.1f}%") for num in nums], key=lambda r: -r[1])
                    print(f"  [{lbl} (N={len(sub)})] Về: {sum(1 for h in hits if h > 0)}/{len(sub)} (TB={sum(hits)/len(sub):.2f}) | Top: {top_n[:5]}")
                    print(f"    Top STL: {[(k, v, f'{v/len(sub)*100:.1f}%') for k, v in cs.most_common(5)]}")

        print(f"\n--- PASCAL & CẦU KẸP ({last['date']}) ---")
        print(f"  Pascal ĐB+G1 ({last['db']}+{get_p1(last)}) -> {p_dbg1} (STL {stl_p_dbg1}) | {cur_year}={p_hits_yr}/{n_yr-1} ({p_hits_yr/(n_yr-1)*100:.1f}%)")
        print(f"  Pascal ĐB ({last['db']}) -> {p_db} (STL {stl_p_db})")
        print(f"  Cầu kẹp X-AB-X: {keps}")

    # --- SECTION: BRIDGES ---
    if section in ("all", "bridges"):
        print(f"\n=== CẦU 107 VỊ TRÍ ĐANG THÔNG (SAU KỲ {last['date']}) ===")
        print("Top Cầu STL thông >= 7d:")
        for r in stl_b[:10]:
            print(f"  STL {r[3]}: thông {r[0]}d | {r[4]}+{r[5]} | 30d={r[2]}/30 | {cur_year}={r[1]}/{n_yr-1} ({r[1]/(n_yr-1)*100:.1f}%)")
        print(f"Top Cầu STL thông >= 5d & Hiệu suất {cur_year} cao nhất:")
        for r in stl_rate[:8]:
            print(f"  STL {r[2]}: {cur_year}={r[0]}/{n_yr-1} ({r[0]/(n_yr-1)*100:.1f}%) | thông {r[1]}d | {r[3]}+{r[4]}")
        print("Top Cầu BTL thông >= 5d:")
        for r in btl_b[:10]:
            print(f"  BTL {r[3]}: thông {r[0]}d | {r[4]}->{r[5]} | 30d={r[2]}/30 | {cur_year}={r[1]}/{n_yr-1} ({r[1]/(n_yr-1)*100:.1f}%)")
        print("Top Cầu Chạm >= 4d:")
        for r in cham_b[:10]:
            print(f"  Chạm {r[3]}: thông {r[0]}d | ({r[4]}+{r[5]})%10 | 30d={r[1]}/30 | {cur_year}={r[2]}/{n_yr-1}")
        print("  Phân bố Chạm >=4d:", Counter(r[3] for r in cham_b).most_common())
        print("  Cầu Chạm 1 vị trí >= 11/30d:", [x for x in c1pos if x[0] >= 11][:8])
        print("Cầu Tổng >= 3d:")
        for r in tong_b[:10]:
            print(f"  Tổng {r[3]}: thông {r[0]}d | ({r[4]}+{r[5]})%10 | 30d={r[1]}/30 | {cur_year}={r[2]}/{n_yr-1}")
        print("Cầu Càng >= 3d:")
        for r in cang_b[:10]:
            print(f"  Càng {r[3]}: thông {r[0]}d | ({r[4]}+{r[5]})%10 | 30d={r[1]}/30 | {cur_year}={r[2]}/{n_yr-1}")

    # --- SECTION: BAC NHO ---
    if section in ("all", "bacnho"):
        print(f"\n=== BẠC NHỚ SAU ĐỀ {last['db_tail2']} ===")
        for sub, lbl in [(after_de, f"2014-{cur_year}"), (after_de_rec, f"2023-{cur_year}")]:
            if not sub:
                continue
            lc, sc = Counter(), Counter()
            for d in sub:
                for x in set(d["loto_list"]):
                    lc[x] += 1
                for p in {f"{min(x, x[::-1])}-{max(x, x[::-1])}" for x in d["loto_list"]}:
                    sc[p] += 1
            print(f"  [{lbl} (N={len(sub)})]:")
            print("    Top Lô:", [(k, v, f"{v/len(sub)*100:.1f}%") for k, v in lc.most_common(8)])
            print("    Top STL:", [(k, v, f"{v/len(sub)*100:.1f}%") for k, v in sc.most_common(6)])
            print(
                "    Đầu:", Counter(d["db_tail2"][0] for d in sub).most_common(5),
                "| Đuôi:", Counter(d["db_tail2"][1] for d in sub).most_common(5),
            )
            print(
                "    Tổng:", Counter(d["db_sum"] for d in sub).most_common(5),
                "| Bộ:", Counter(get_bo(d["db_tail2"]) for d in sub).most_common(5),
                "| Càng:", Counter(d["db_cang"] for d in sub).most_common(5),
            )

    # --- SECTION: WEEKDAY ---
    if section in ("all", "weekday"):
        print(f"\n=== HỒ SƠ ĐÀI {station_name.upper()} — {wd_name.upper()} {cur_year} (N={len(wd_draws)}) ===")
        print("  Top Lô:", [(k, v, f"{v/len(wd_draws)*100:.1f}%") for k, v in w_lo.most_common(10)])
        print("  Top >=2 nháy:", w_mult.most_common(8))
        print("  Top STL:", [(k, v, f"{v/len(wd_draws)*100:.1f}%") for k, v in w_stl.most_common(8)])
        print("  Top Xiên 2:", [(f"{a}-{b}", c, f"{c/len(wd_draws)*100:.1f}%") for (a, b), c in w_pairs.most_common(8)])
        print("  Đầu Đề:", Counter(d["db_tail2"][0] for d in wd_draws).most_common())
        print("  Đuôi Đề:", Counter(d["db_tail2"][1] for d in wd_draws).most_common())
        print("  Tổng Đề:", Counter(d["db_sum"] for d in wd_draws).most_common())
        print("  Bộ Đề:", Counter(get_bo(d["db_tail2"]) for d in wd_draws).most_common(8))
        print("  Càng Đề:", Counter(d["db_cang"] for d in wd_draws).most_common())
        print("  10 kỳ gần nhất:", [(d["date"][:5], d["db"]) for d in wd_draws[-10:]])

    # --- SECTION: GAN ---
    if section in ("all", "gan"):
        hit_gans_30 = []
        for idx in range(n - 30, n):
            t = draws[idx]["db_tail2"]
            prev = -1
            for j in range(idx - 1, -1, -1):
                if draws[j]["db_tail2"] == t:
                    prev = j
                    break
            hit_gans_30.append(idx - prev - 1 if prev != -1 else idx)

        print(f"\n=== GAN & NÓNG (KÈM KỶ LỤC MAX 13 NĂM THẬT — ĐẾN {last['date']}) ===")
        print("  Tổng Gan (cur / max13y):", [(r[0], f"{r[1]}d/{r[2]}d") for r in tong_stats])
        print("  Càng Gan (cur / max13y):", [(r[0], f"{r[1]}d/{r[2]}d") for r in cang_stats])
        print("  Đầu Đề Gan:", [(r[0], f"{r[1]}d/{r[2]}d") for r in dau_stats[:6]])
        print("  Đuôi Đề Gan:", [(r[0], f"{r[1]}d/{r[2]}d") for r in duoi_stats[:6]])
        print("  Top 12 Đề Gan:", [(r[0], f"{r[1]}d", r[5]) for r in de_stats[:12]])
        print(
            f"  Nhịp Đề 30 kỳ gần nhất: TB gan={sum(hit_gans_30)/len(hit_gans_30):.1f}d "
            f"(<=50d: {sum(1 for g in hit_gans_30 if g <= 50)}/30 | <=100d: {sum(1 for g in hit_gans_30 if g <= 100)}/30 | >=200d: {sum(1 for g in hit_gans_30 if g >= 200)}/30)"
        )
        print("  Top 10 Lô Gan:", sorted(lo_gan.items(), key=lambda r: -r[1])[:10])
        print("  Top 10 Lô Nóng 15d:", lo15.most_common(10))
        print("  Top 10 Lô Nóng 30d:", lo30.most_common(10))

    # --- SECTION: SCORE ---
    if section in ("all", "score"):
        br_stl_n = Counter()
        for r in stl_b[:15]:
            a, b = r[3].split("-")
            br_stl_n[a] = max(br_stl_n[a], r[0])
            br_stl_n[b] = max(br_stl_n[b], r[0])
        br_btl_n = {r[3]: (r[0], r[1] / (n_yr - 1) * 100) for r in btl_b}

        ad_cnt, adr_cnt = Counter(), Counter()
        for d in after_de:
            for x in set(d["loto_list"]):
                ad_cnt[x] += 1
        for d in after_de_rec:
            for x in set(d["loto_list"]):
                adr_cnt[x] += 1

        lo_scores = []
        for x in range(100):
            s = f"{x:02d}"
            gl = lo_gan[s]
            wpct = w_lo[s] / len(wd_draws) * 100 if wd_draws else 0
            adp = ad_cnt[s] / len(after_de) * 100 if after_de else 0
            adrp = adr_cnt[s] / len(after_de_rec) * 100 if after_de_rec else 0
            sc, tags = 0.0, []
            if wpct >= 35.0:
                sc += 3.0; tags.append(f"Vua {wd_name} {w_lo[s]}/{len(wd_draws)} ({wpct:.1f}%)")
            elif wpct >= 28.0:
                sc += 1.5; tags.append(f"{wd_name} tốt ({wpct:.1f}%)")
            if s in br_btl_n:
                sc += 2.5; tags.append(f"BTL cầu {br_btl_n[s][0]}d ({br_btl_n[s][1]:.1f}%)")
            if br_stl_n[s] >= 7:
                sc += 2.0; tags.append(f"STL cầu {br_stl_n[s]}d")
            if s in (p_dbg1, p_dbg1[::-1]):
                sc += 2.0; tags.append(f"Pascal ĐB+G1 ({p_dbg1})")
            if any(s in k[2].split("-") for k in keps):
                sc += 1.5; tags.append("Cầu kẹp")
            if adp >= 34.0:
                sc += 2.0; tags.append(f"Sau {last['db_tail2']} 13y ({adp:.1f}%)")
            if adrp >= 40.0:
                sc += 2.0; tags.append(f"Sau {last['db_tail2']} 23+ ({adrp:.1f}%)")
            if s[0] in cam_dau:
                sc += 1.5; tags.append(f"Bật Đầu câm {s[0]}")
            if s[1] in cam_duoi:
                sc += 1.5; tags.append(f"Bật Đuôi câm {s[1]}")
            if 2 <= gl <= 7:
                sc += 1.5; tags.append(f"Nhịp chín ({gl}d)")
            elif gl == 1:
                sc += 0.5; tags.append("gan 1d")
            elif gl >= 12:
                sc -= 2.0; tags.append(f"Bẫy Lô Gan ({gl}d)")
            if lo30[s] >= 10:
                sc += 1.0; tags.append(f"Nóng 30d ({lo30[s]}x)")
            lo_scores.append((sc, s, gl, lo15[s], lo30[s], w_lo[s], tags))
        lo_scores.sort(key=lambda r: (-r[0], -r[5]))

        print(f"\n=== CHẤM ĐIỂM TOP 15 LÔ ({target_date.strftime('%d/%m/%Y')} — {wd_name}) ===")
        for r in lo_scores[:15]:
            print(f"  Lô {r[1]} (gan {r[2]:2d}d | 15d={r[3]:2d} | 30d={r[4]:2d} | {wd_name}={r[5]:2d}/{len(wd_draws)}): {r[0]:4.1f} | {r[6]}")

        cham_cnt = Counter(r[3] for r in cham_b)
        cham_max = {}
        for r in cham_b:
            cham_max[r[3]] = max(cham_max.get(r[3], 0), r[0])
        c1_d = Counter(x[2] for x in c1pos if x[0] >= 11)
        tong_bc = Counter(r[3] for r in tong_b)

        w_dau = Counter(d["db_tail2"][0] for d in wd_draws)
        w_duoi = Counter(d["db_tail2"][1] for d in wd_draws)
        w_tong = Counter(d["db_sum"] for d in wd_draws)
        w_bo = Counter(get_bo(d["db_tail2"]) for d in wd_draws)
        ad_tong = Counter(d["db_sum"] for d in after_de)
        ad_bo = Counter(get_bo(d["db_tail2"]) for d in after_de)
        adr_tong = Counter(d["db_sum"] for d in after_de_rec)
        adr_bo = Counter(get_bo(d["db_tail2"]) for d in after_de_rec)

        dau_g = {r[0]: r[1] for r in dau_stats}
        duoi_g = {r[0]: r[1] for r in duoi_stats}
        tong_g = {r[0]: r[1] for r in tong_stats}
        de_g_map = {r[0]: r[1] for r in de_stats}

        de_scores = []
        for x in range(100):
            s = f"{x:02d}"
            d0, d1 = s[0], s[1]
            t = str((int(d0) + int(d1)) % 10)
            bo = get_bo(s)
            gan = de_g_map[s]
            cyr = sum(1 for d in d_yr if d["db_tail2"] == s)
            cwd = sum(1 for d in wd_draws if d["db_tail2"] == s)
            sc, tags = 0.0, []
            for ch in set(s):
                if cham_max.get(ch, 0) >= 5:
                    sc += 2.5; tags.append(f"Chạm {ch} (cầu {cham_max[ch]}d)")
                elif cham_cnt.get(ch, 0) >= 2:
                    sc += 2.0; tags.append(f"Chạm {ch} ({cham_cnt[ch]} cầu 4d)")
                elif cham_cnt.get(ch, 0) == 1:
                    sc += 1.0; tags.append(f"Chạm {ch} (4d)")
                if c1_d[ch] >= 1:
                    sc += 1.0; tags.append(f"1-pos Chạm {ch}")
            if dau_g[d0] >= 15:
                sc += 1.5; tags.append(f"Đầu {d0} gan {dau_g[d0]}d")
            if duoi_g[d1] >= 12:
                sc += 1.5; tags.append(f"Đuôi {d1} gan {duoi_g[d1]}d")
            if w_dau[d0] >= 6:
                sc += 1.0; tags.append(f"Đầu {d0} {wd_name} ({w_dau[d0]})")
            if w_duoi[d1] >= 6:
                sc += 1.0; tags.append(f"Đuôi {d1} {wd_name} ({w_duoi[d1]})")
            if tong_bc[t] >= 1:
                sc += 2.0; tags.append(f"Tổng {t} ({tong_bc[t]} cầu 3d)")
            if tong_g[t] >= 12:
                sc += 1.5; tags.append(f"Tổng {t} gan {tong_g[t]}d")
            if w_tong[t] >= 6:
                sc += 1.5; tags.append(f"Tổng {t} {wd_name} ({w_tong[t]})")
            if ad_tong[t] >= 6 or adr_tong[t] >= 3:
                sc += 1.0; tags.append(f"Tổng {t} sau {last['db_tail2']}")
            if w_bo[bo] >= 5:
                sc += 1.5; tags.append(f"Bộ {bo} {wd_name} ({w_bo[bo]})")
            if ad_bo[bo] >= 5 or adr_bo[bo] >= 3:
                sc += 1.0; tags.append(f"Bộ {bo} sau {last['db_tail2']}")
            if gan <= 160:
                sc += 1.0
            elif gan >= 280:
                sc -= 1.0; tags.append(f"Bẫy Đại Gan ({gan}d)")
            de_scores.append((sc, s, t, bo, gan, cyr, cwd, tags))
        de_scores.sort(key=lambda r: (-r[0], r[4]))

        print(f"\n=== CHẤM ĐIỂM TOP 16 ĐỀ ({target_date.strftime('%d/%m/%Y')} — {wd_name}) ===")
        for r in de_scores[:16]:
            print(f"  Đề {r[1]} (T{r[2]}, Bộ {r[3]}, gan {r[4]:3d}d, {cur_year}={r[5]}x, {wd_name}={r[6]}x): {r[0]:4.1f} | {r[7]}")

        if events_str:
            ev_nums = [x.strip().zfill(2) for x in events_str.split(",") if x.strip().isdigit()]
            lo_map = {r[1]: r for r in lo_scores}
            de_map = {r[1]: r for r in de_scores}
            print(f"\n=== ĐỐI CHIẾU SỐ SỰ KIỆN ({', '.join(ev_nums)}) VỚI THỐNG KÊ ===")
            for num in ev_nums:
                if num in lo_map and num in de_map:
                    lr, dr = lo_map[num], de_map[num]
                    print(f"  Số {num}: Lô score={lr[0]:.1f} (gan {lr[2]}d) {lr[6]} || Đề score={dr[0]:.1f} (T{dr[2]}, gan {dr[4]}d) {dr[7]}")

    # --- SECTION: MATRIX ---
    if section in ("all", "matrix"):
        print(f"\n=== DỮ LIỆU CẬP NHẬT MA TRẬN (ĐẾN {last['date']}) ===")
        # Current week draws (Monday..Sunday containing latest draw)
        monday = last_date - datetime.timedelta(days=last_date.weekday())
        week_draws = [d for d in draws if datetime.date.fromisoformat(d["date_iso"]) >= monday]
        print(f"  Tuần hiện tại (từ {monday.strftime('%d/%m')}):", [(d["date"][:5], d["db"], f"C{d['db_cang']}", f"T{d['db_sum']}") for d in week_draws])
        print("  Tần suất Càng theo Thứ năm", cur_year + ":")
        for w, (wn, stn) in enumerate(WEEKDAY_NAMES):
            sub = [d for d in d_yr if datetime.date.fromisoformat(d["date_iso"]).weekday() == w]
            print(f"    {wn} ({stn}, N={len(sub)}): {Counter(d['db_cang'] for d in sub).most_common()}")


def main():
    parser = argparse.ArgumentParser(description="XSMB Unified Analytics Engine v2")
    parser.add_argument("--data", default=DEFAULT_CACHE, help="Đường dẫn file xsmb_2014_2026_cache.json")
    parser.add_argument("--target", default=None, help="Ngày phân tích mục tiêu (YYYY-MM-DD)")
    parser.add_argument("--events", default=None, help="Danh sách số sự kiện cần đối chiếu (vd: 42,75,87)")
    parser.add_argument("--audit-picks", default=None, help="Danh sách số đã chốt kỳ trước để đối soát (vd: 29,45,54)")
    parser.add_argument(
        "--section",
        default="all",
        choices=["all", "summary", "bridges", "weekday", "bacnho", "gan", "score", "matrix"],
        help="Chọn nhóm phân tích cần xuất",
    )
    args = parser.parse_args()
    run_analysis(args.data, args.target, args.events, args.audit_picks, args.section)


if __name__ == "__main__":
    main()
