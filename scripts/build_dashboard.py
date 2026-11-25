#!/usr/bin/env python3
"""
Trình sinh giao diện HTML đánh giá & phân tích XSMB hằng ngày (index.html).
- 100% Python stdlib, tái sử dụng trực tiếp thuật toán từ scripts/xsmb_engine.py.
- Xuất ra 1 file HTML độc lập hoàn toàn (inline CSS + JS + JSON dữ liệu), không phụ thuộc CDN hay backend.
- Xem mượt trên GitHub Pages, Antigravity Preview / Cloud Workspace, hoặc mở trực tiếp trên trình duyệt.
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
DEFAULT_OUT = os.path.join(REPO_ROOT, "index.html")
VN_TZ = datetime.timezone(datetime.timedelta(hours=7))

sys.path.insert(0, SCRIPT_DIR)
import xsmb_engine as eng


def build_payload(cache_path: str, target_str: str = None) -> dict:
    draws = eng.load_draws(cache_path)
    n = len(draws)
    last = draws[-1]
    last_date = datetime.date.fromisoformat(last["date_iso"])
    target_date = (
        datetime.date.fromisoformat(target_str)
        if target_str
        else last_date + datetime.timedelta(days=1)
    )
    target_wd = target_date.weekday()
    wd_name, station_name = eng.WEEKDAY_NAMES[target_wd]

    cur_year = last["date_iso"][:4]
    d_yr = [d for d in draws if d["date_iso"].startswith(f"{cur_year}-")]
    n_yr = len(d_yr)
    start_yr = n - n_yr

    c_last = Counter(last["loto_list"])
    mult_last = [{"num": k, "cnt": v} for k, v in sorted(c_last.items()) if v > 1]
    cam_dau = [str(i) for i in range(10) if not any(x.startswith(str(i)) for x in c_last)]
    cam_duoi = [str(i) for i in range(10) if not any(x.endswith(str(i)) for x in c_last)]

    avg_uniq = sum(len(set(d["loto_list"])) for d in d_yr) / n_yr
    p_btl = avg_uniq / 100.0
    p_stl = 1 - (1 - p_btl) ** 2

    p_dbg1 = eng.pascal(str(last["db"]) + eng.get_p1(last))
    p_db = eng.pascal(str(last["db"]))
    stl_p_dbg1 = "-".join(sorted({p_dbg1, p_dbg1[::-1]}))
    stl_p_db = "-".join(sorted({p_db, p_db[::-1]}))
    p_hits_yr = sum(
        1
        for i in range(start_yr, n - 1)
        if (
            eng.pascal(str(draws[i]["db"]) + eng.get_p1(draws[i])) in draws[i + 1]["loto_list"]
            or eng.pascal(str(draws[i]["db"]) + eng.get_p1(draws[i]))[::-1] in draws[i + 1]["loto_list"]
        )
    )

    keps = []
    for gname, vals in [
        ("ĐB", [last["db"]]),
        ("G1", [eng.get_p1(last)]),
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
                    keps.append(
                        {
                            "pos": f"{gname}.{idx}",
                            "raw": s,
                            "pair": f"{min(ab, ab[::-1])}-{max(ab, ab[::-1])}",
                        }
                    )

    cam_rebound = []
    for kind, c_list in [("Đầu", cam_dau), ("Đuôi", cam_duoi)]:
        idx_pos = 0 if kind == "Đầu" else 1
        for ch in c_list:
            all_c, yr_c, wd_c = [], [], []
            for i in range(n - 1):
                ss = {x[idx_pos] for x in draws[i]["loto_list"]}
                if ch not in ss:
                    all_c.append(draws[i + 1])
                    if draws[i]["date_iso"].startswith(f"{cur_year}-"):
                        yr_c.append(draws[i + 1])
                    if datetime.date.fromisoformat(draws[i + 1]["date_iso"]).weekday() == target_wd:
                        wd_c.append(draws[i + 1])
            frames = []
            for sub, lbl in [(all_c, f"2014–{cur_year}"), (yr_c, f"Riêng {cur_year}"), (wd_c, f"-> {wd_name}")]:
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
                top_n = sorted(
                    [{"num": num, "cnt": cn[num], "pct": round(cn[num] / len(sub) * 100, 1)} for num in nums],
                    key=lambda r: -r["cnt"],
                )[:5]
                top_stl = [
                    {"pair": k, "cnt": v, "pct": round(v / len(sub) * 100, 1)}
                    for k, v in cs.most_common(5)
                ]
                frames.append(
                    {
                        "label": lbl,
                        "n": len(sub),
                        "hit_days": sum(1 for h in hits if h > 0),
                        "avg": round(sum(hits) / len(sub), 2),
                        "top_nums": top_n,
                        "top_stl": top_stl,
                    }
                )
            cam_rebound.append({"kind": kind, "digit": ch, "frames": frames})

    stl_b, stl_rate, btl_b, cham_b, tong_b, cang_b, c1pos = eng.scan_107_bridges(draws, start_yr)

    after_de = [draws[i + 1] for i in range(n - 1) if draws[i]["db_tail2"] == last["db_tail2"]]
    after_de_rec = [d for d in after_de if d["date_iso"] >= "2023-01-01"]
    bacnho = []
    for sub, lbl in [(after_de, f"2014–{cur_year}"), (after_de_rec, f"2023–{cur_year}")]:
        if not sub:
            continue
        lc, sc = Counter(), Counter()
        for d in sub:
            for x in set(d["loto_list"]):
                lc[x] += 1
            for p in {f"{min(x, x[::-1])}-{max(x, x[::-1])}" for x in d["loto_list"]}:
                sc[p] += 1
        bacnho.append(
            {
                "label": lbl,
                "n": len(sub),
                "top_lo": [{"num": k, "cnt": v, "pct": round(v / len(sub) * 100, 1)} for k, v in lc.most_common(8)],
                "top_stl": [{"pair": k, "cnt": v, "pct": round(v / len(sub) * 100, 1)} for k, v in sc.most_common(6)],
                "dau": Counter(d["db_tail2"][0] for d in sub).most_common(5),
                "duoi": Counter(d["db_tail2"][1] for d in sub).most_common(5),
                "tong": Counter(d["db_sum"] for d in sub).most_common(5),
                "bo": Counter(eng.get_bo(d["db_tail2"]) for d in sub).most_common(5),
                "cang": Counter(d["db_cang"] for d in sub).most_common(5),
            }
        )

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

    tong_stats = eng.compute_gan_with_max(draws, lambda d: d["db_sum"], [str(x) for x in range(10)])
    cang_stats = eng.compute_gan_with_max(draws, lambda d: d["db_cang"], [str(x) for x in range(10)])
    dau_stats = eng.compute_gan_with_max(draws, lambda d: d["db_tail2"][0], [str(x) for x in range(10)])
    duoi_stats = eng.compute_gan_with_max(draws, lambda d: d["db_tail2"][1], [str(x) for x in range(10)])
    de_stats = eng.compute_gan_with_max(draws, lambda d: d["db_tail2"], [f"{x:02d}" for x in range(100)])

    hit_gans_30 = []
    for idx in range(n - 30, n):
        t = draws[idx]["db_tail2"]
        prev = -1
        for j in range(idx - 1, -1, -1):
            if draws[j]["db_tail2"] == t:
                prev = j
                break
        hit_gans_30.append(idx - prev - 1 if prev != -1 else idx)

    lo_li = {}
    for i, d in enumerate(draws):
        for x in set(d["loto_list"]):
            lo_li[x] = i
    lo_gan = {f"{x:02d}": n - 1 - lo_li[f"{x:02d}"] for x in range(100)}
    lo_last_date = {f"{x:02d}": draws[lo_li[f"{x:02d}"]]["date"] for x in range(100)}
    lo15, lo30 = Counter(), Counter()
    for d in draws[-15:]:
        for x in d["loto_list"]:
            lo15[x] += 1
    for d in draws[-30:]:
        for x in d["loto_list"]:
            lo30[x] += 1

    # Multi-factor Lô scoring (same exact formula as xsmb_engine.py)
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
        if any(s in k["pair"].split("-") for k in keps):
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
        lo_scores.append(
            {
                "num": s,
                "score": round(sc, 1),
                "gan": gl,
                "c15": lo15[s],
                "c30": lo30[s],
                "c_wd": w_lo[s],
                "wd_n": len(wd_draws),
                "trap": gl >= 12,
                "tags": tags,
            }
        )
    lo_scores.sort(key=lambda r: (-r["score"], -r["c_wd"], r["gan"]))

    # Multi-factor Đề scoring (same exact formula as xsmb_engine.py)
    cham_cnt = Counter(r[3] for r in cham_b)
    cham_max = {}
    for r in cham_b:
        cham_max[r[3]] = max(cham_max.get(r[3], 0), r[0])
    c1_d = Counter(x[2] for x in c1pos if x[0] >= 11)
    tong_bc = Counter(r[3] for r in tong_b)

    w_dau = Counter(d["db_tail2"][0] for d in wd_draws)
    w_duoi = Counter(d["db_tail2"][1] for d in wd_draws)
    w_tong = Counter(d["db_sum"] for d in wd_draws)
    w_bo = Counter(eng.get_bo(d["db_tail2"]) for d in wd_draws)
    ad_tong = Counter(d["db_sum"] for d in after_de)
    ad_bo = Counter(eng.get_bo(d["db_tail2"]) for d in after_de)
    adr_tong = Counter(d["db_sum"] for d in after_de_rec)
    adr_bo = Counter(eng.get_bo(d["db_tail2"]) for d in after_de_rec)

    dau_g = {r[0]: r[1] for r in dau_stats}
    duoi_g = {r[0]: r[1] for r in duoi_stats}
    tong_g = {r[0]: r[1] for r in tong_stats}
    de_g_map = {r[0]: r[1] for r in de_stats}

    de_scores = []
    for x in range(100):
        s = f"{x:02d}"
        d0, d1 = s[0], s[1]
        t = str((int(d0) + int(d1)) % 10)
        bo = eng.get_bo(s)
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
        de_scores.append(
            {
                "num": s,
                "score": round(sc, 1),
                "tong": t,
                "bo": bo,
                "gan": gan,
                "c_yr": cyr,
                "c_wd": cwd,
                "trap": gan >= 280,
                "tags": tags,
            }
        )
    de_scores.sort(key=lambda r: (-r["score"], r["gan"]))

    weekday_matrix = []
    for w, (wn, stn) in enumerate(eng.WEEKDAY_NAMES):
        sub = [d for d in d_yr if datetime.date.fromisoformat(d["date_iso"]).weekday() == w]
        lc = Counter()
        for d in sub:
            for x in set(d["loto_list"]):
                lc[x] += 1
        weekday_matrix.append(
            {
                "weekday": wn,
                "station": stn,
                "n": len(sub),
                "top_cang": Counter(d["db_cang"] for d in sub).most_common(3),
                "top_tong": Counter(d["db_sum"] for d in sub).most_common(3),
                "top_lo": [{"num": k, "cnt": v, "pct": round(v / len(sub) * 100, 1)} for k, v in lc.most_common(5)],
                "is_target": w == target_wd,
            }
        )

    recent_30 = [
        {
            "date": d["date"],
            "date_iso": d["date_iso"],
            "weekday": d["weekday"],
            "station": d.get("station", ""),
            "db": d["db"],
            "de": d["db_tail2"],
            "cang": d["db_cang"],
            "tong": d["db_sum"],
            "bo": eng.get_bo(d["db_tail2"]),
            "p1": eng.get_p1(d),
            "loto": d["loto_list"],
        }
        for d in reversed(draws[-30:])
    ]

    return {
        "meta": {
            "generated_at": datetime.datetime.now(VN_TZ).strftime("%d/%m/%Y %H:%M UTC+7"),
            "total_draws": n,
            "year": cur_year,
            "year_draws": n_yr,
            "latest_date": last["date"],
            "target_date": target_date.strftime("%d/%m/%Y"),
            "target_weekday": wd_name,
            "target_station": station_name,
            "baseline_btl": round(p_btl * 100, 2),
            "baseline_stl": round(p_stl * 100, 2),
            "avg_uniq": round(avg_uniq, 2),
            "pascal_hits": p_hits_yr,
            "pascal_total": n_yr - 1,
            "pascal_pct": round(p_hits_yr / (n_yr - 1) * 100, 2),
        },
        "latest": {
            "date": last["date"],
            "weekday": last["weekday"],
            "station": last.get("station", ""),
            "db": last["db"],
            "de": last["db_tail2"],
            "cang": last["db_cang"],
            "tong": last["db_sum"],
            "bo": eng.get_bo(last["db_tail2"]),
            "p1": eng.get_p1(last),
            "multi_hits": mult_last,
            "cam_dau": cam_dau,
            "cam_duoi": cam_duoi,
            "pascal_dbg1": p_dbg1,
            "stl_pascal_dbg1": stl_p_dbg1,
            "pascal_db": p_db,
            "stl_pascal_db": stl_p_db,
            "keps": keps,
            "loto": last["loto_list"],
        },
        "cam_rebound": cam_rebound,
        "bridges": {
            "stl_streak": [
                {"pair": r[3], "streak": r[0], "h_yr": r[1], "yr_pct": round(r[1] / (n_yr - 1) * 100, 1), "h30": r[2], "pos": f"{r[4]} + {r[5]}"}
                for r in stl_b[:12]
            ],
            "stl_rate": [
                {"pair": r[2], "h_yr": r[0], "yr_pct": round(r[0] / (n_yr - 1) * 100, 1), "streak": r[1], "pos": f"{r[3]} + {r[4]}"}
                for r in stl_rate[:10]
            ],
            "btl": [
                {"num": r[3], "streak": r[0], "h_yr": r[1], "yr_pct": round(r[1] / (n_yr - 1) * 100, 1), "h30": r[2], "pos": f"{r[4]} → {r[5]}"}
                for r in btl_b[:12]
            ],
            "cham": [
                {"digit": r[3], "streak": r[0], "h30": r[1], "h_yr": r[2], "pos": f"({r[4]} + {r[5]}) % 10"}
                for r in cham_b[:12]
            ],
            "cham_dist": Counter(r[3] for r in cham_b).most_common(),
            "tong": [
                {"digit": r[3], "streak": r[0], "h30": r[1], "h_yr": r[2], "pos": f"({r[4]} + {r[5]}) % 10"}
                for r in tong_b[:10]
            ],
            "cang": [
                {"digit": r[3], "streak": r[0], "h30": r[1], "h_yr": r[2], "pos": f"({r[4]} + {r[5]}) % 10"}
                for r in cang_b[:10]
            ],
        },
        "bacnho": bacnho,
        "weekday": {
            "name": wd_name,
            "station": station_name,
            "n": len(wd_draws),
            "top_lo": [{"num": k, "cnt": v, "pct": round(v / len(wd_draws) * 100, 1)} for k, v in w_lo.most_common(10)],
            "top_mult": w_mult.most_common(8),
            "top_stl": [{"pair": k, "cnt": v, "pct": round(v / len(wd_draws) * 100, 1)} for k, v in w_stl.most_common(8)],
            "top_xien": [{"pair": f"{a}-{b}", "cnt": c, "pct": round(c / len(wd_draws) * 100, 1)} for (a, b), c in w_pairs.most_common(8)],
            "dau": Counter(d["db_tail2"][0] for d in wd_draws).most_common(),
            "duoi": Counter(d["db_tail2"][1] for d in wd_draws).most_common(),
            "tong": Counter(d["db_sum"] for d in wd_draws).most_common(),
            "bo": Counter(eng.get_bo(d["db_tail2"]) for d in wd_draws).most_common(8),
            "cang": Counter(d["db_cang"] for d in wd_draws).most_common(),
        },
        "gan": {
            "tong": [{"digit": r[0], "cur": r[1], "max13": r[2], "last_date": r[5], "last_db": r[6]} for r in tong_stats],
            "cang": [{"digit": r[0], "cur": r[1], "max13": r[2], "last_date": r[5], "last_db": r[6]} for r in cang_stats],
            "dau": [{"digit": r[0], "cur": r[1], "max13": r[2], "last_date": r[5]} for r in dau_stats],
            "duoi": [{"digit": r[0], "cur": r[1], "max13": r[2], "last_date": r[5]} for r in duoi_stats],
            "de_top15": [{"num": r[0], "cur": r[1], "last_date": r[5]} for r in de_stats[:15]],
            "warm_30": {
                "avg": round(sum(hit_gans_30) / len(hit_gans_30), 1),
                "le50": sum(1 for g in hit_gans_30 if g <= 50),
                "le100": sum(1 for g in hit_gans_30 if g <= 100),
                "ge200": sum(1 for g in hit_gans_30 if g >= 200),
            },
            "lo_top12": [
                {"num": k, "cur": v, "last_date": lo_last_date[k]}
                for k, v in sorted(lo_gan.items(), key=lambda r: -r[1])[:12]
            ],
            "lo_hot15": lo15.most_common(12),
            "lo_hot30": lo30.most_common(12),
        },
        "scores_lo_all": lo_scores,
        "scores_de_all": de_scores,
        "weekday_matrix": weekday_matrix,
        "recent_30": recent_30,
    }


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>XSMB Analytics Dashboard v2 — Phân Tích & Đánh Giá Mỗi Ngày</title>
<style>
  :root {
    --bg: #0b1120;
    --panel: #111827;
    --panel2: #172033;
    --border: #243047;
    --text: #e5edf8;
    --muted: #93a4be;
    --accent: #38bdf8;
    --green: #22c55e;
    --amber: #f59e0b;
    --red: #ef4444;
    --purple: #a78bfa;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.5;
  }
  header {
    position: sticky;
    top: 0;
    z-index: 20;
    background: rgba(11, 17, 32, 0.94);
    backdrop-filter: blur(8px);
    border-bottom: 1px solid var(--border);
    padding: 14px 20px;
  }
  .header-inner {
    max-width: 1320px;
    margin: 0 auto;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    justify-content: space-between;
  }
  .brand h1 {
    margin: 0;
    font-size: 1.15rem;
    letter-spacing: 0.2px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .brand .sub { font-size: 0.82rem; color: var(--muted); margin-top: 2px; }
  .pills { display: flex; flex-wrap: wrap; gap: 8px; }
  .pill {
    font-size: 0.78rem;
    padding: 4px 10px;
    border-radius: 999px;
    border: 1px solid var(--border);
    background: var(--panel2);
    color: var(--text);
  }
  .pill.accent { border-color: rgba(56,189,248,0.45); color: #7dd3fc; }
  .pill.green { border-color: rgba(34,197,94,0.45); color: #86efac; }
  .pill.amber { border-color: rgba(245,158,11,0.45); color: #fcd34d; }
  .pill.red { border-color: rgba(239,68,68,0.5); color: #fca5a5; }
  nav.tabs {
    max-width: 1320px;
    margin: 12px auto 0;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  .tab-btn {
    cursor: pointer;
    background: var(--panel);
    color: var(--muted);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 0.88rem;
    font-weight: 600;
    transition: all .15s;
  }
  .tab-btn:hover { color: var(--text); border-color: var(--accent); }
  .tab-btn.active {
    background: linear-gradient(135deg, #0284c7, #2563eb);
    color: #fff;
    border-color: transparent;
  }
  main {
    max-width: 1320px;
    margin: 18px auto 48px;
    padding: 0 20px;
  }
  .tab-panel { display: none; }
  .tab-panel.active { display: block; }
  .grid { display: grid; gap: 16px; }
  .g-4 { grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
  .g-2 { grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); }
  .g-3 { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
  @media (max-width: 640px) {
    .g-2, .g-3 { grid-template-columns: 1fr; }
  }
  .card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
  }
  .card h2 {
    margin: 0 0 12px;
    font-size: 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
  }
  .card h3 { margin: 12px 0 8px; font-size: 0.9rem; color: #bae6fd; }
  .kpi-val { font-size: 1.55rem; font-weight: 800; letter-spacing: 0.5px; }
  .kpi-lbl { font-size: 0.78rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }
  .kpi-sub { font-size: 0.82rem; color: var(--muted); margin-top: 4px; }
  table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
  th, td {
    text-align: left;
    padding: 7px 8px;
    border-bottom: 1px solid rgba(36, 48, 71, 0.7);
    vertical-align: top;
  }
  th { color: var(--muted); font-weight: 600; font-size: 0.78rem; text-transform: uppercase; }
  tr:hover td { background: rgba(56, 189, 248, 0.04); }
  .num-badge {
    display: inline-block;
    min-width: 32px;
    text-align: center;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 6px;
    background: rgba(56, 189, 248, 0.14);
    color: #7dd3fc;
    border: 1px solid rgba(56, 189, 248, 0.35);
    font-variant-numeric: tabular-nums;
  }
  .num-badge.top { background: rgba(34, 197, 94, 0.18); color: #86efac; border-color: rgba(34, 197, 94, 0.45); }
  .num-badge.trap { background: rgba(239, 68, 68, 0.18); color: #fca5a5; border-color: rgba(239, 68, 68, 0.45); }
  .tag {
    display: inline-block;
    font-size: 0.73rem;
    padding: 2px 6px;
    margin: 2px 3px 2px 0;
    border-radius: 5px;
    background: var(--panel2);
    border: 1px solid var(--border);
    color: #cbd5e1;
  }
  .tag.warn { border-color: rgba(239,68,68,0.5); color: #fca5a5; background: rgba(239,68,68,0.1); }
  .bar-wrap {
    width: 100%;
    height: 8px;
    background: #1e293b;
    border-radius: 99px;
    overflow: hidden;
    margin-top: 4px;
  }
  .bar-fill { height: 100%; border-radius: 99px; background: linear-gradient(90deg, #38bdf8, #22c55e); }
  .bar-fill.amber { background: linear-gradient(90deg, #f59e0b, #ef4444); }
  .input-row { display: flex; flex-wrap: wrap; gap: 10px; align-items: flex-end; margin-bottom: 12px; }
  .field { display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 150px; }
  .field label { font-size: 0.78rem; color: var(--muted); font-weight: 600; }
  input, select, textarea {
    background: #0f172a;
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 10px;
    font-size: 0.88rem;
    font-family: inherit;
  }
  input:focus, select:focus, textarea:focus { outline: none; border-color: var(--accent); }
  .btn {
    cursor: pointer;
    border: none;
    border-radius: 8px;
    padding: 9px 14px;
    font-weight: 700;
    font-size: 0.86rem;
    background: #0284c7;
    color: #fff;
  }
  .btn:hover { background: #0369a1; }
  .btn.secondary { background: var(--panel2); color: var(--text); border: 1px solid var(--border); }
  .btn.danger { background: rgba(239,68,68,0.18); color: #fca5a5; border: 1px solid rgba(239,68,68,0.45); }
  .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
  .note-box {
    margin-top: 14px;
    padding: 10px 14px;
    border-radius: 8px;
    background: rgba(245, 158, 11, 0.08);
    border: 1px solid rgba(245, 158, 11, 0.35);
    font-size: 0.82rem;
    color: #fde68a;
  }
  .profit-pos { color: #4ade80; font-weight: 800; }
  .profit-neg { color: #f87171; font-weight: 800; }
  .scroll-x { overflow-x: auto; }
  footer {
    max-width: 1320px;
    margin: 0 auto 30px;
    padding: 0 20px;
    color: var(--muted);
    font-size: 0.78rem;
    text-align: center;
  }
</style>
</head>
<body>

<header>
  <div class="header-inner">
    <div class="brand">
      <h1>📊 XSMB Analytics Dashboard <span class="pill accent">v2 Cloud</span></h1>
      <div class="sub" id="hdr-sub"></div>
    </div>
    <div class="pills" id="hdr-pills"></div>
  </div>
  <nav class="tabs">
    <button class="tab-btn active" data-tab="overview">🎯 Tổng Quan & Chấm Điểm</button>
    <button class="tab-btn" data-tab="bridges">🔗 Cầu 107 Vị Trí & Bạc Nhớ</button>
    <button class="tab-btn" data-tab="gan">📉 Ma Trận Gan & 7 Nhà Đài</button>
    <button class="tab-btn" data-tab="evaluate">✅ Tra Cứu & Tự Đánh Giá Mỗi Ngày</button>
  </nav>
</header>

<main>
  <!-- TAB 1: OVERVIEW -->
  <section id="tab-overview" class="tab-panel active">
    <div class="grid g-4" id="kpi-cards"></div>

    <div class="grid g-2" style="margin-top:16px">
      <div class="card">
        <h2>🔥 Top 15 Ứng Viên Lô <span class="pill accent" id="lo-target-badge"></span></h2>
        <div class="scroll-x">
          <table>
            <thead>
              <tr><th>#</th><th>Số</th><th>Điểm</th><th>Gan</th><th>15d/30d</th><th>Đài</th><th>Tín hiệu hội tụ</th></tr>
            </thead>
            <tbody id="tbl-top-lo"></tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <h2>💎 Top 16 Ứng Viên Đề <span class="pill green" id="de-target-badge"></span></h2>
        <div class="scroll-x">
          <table>
            <thead>
              <tr><th>#</th><th>Số</th><th>Điểm</th><th>Tổng/Bộ</th><th>Gan Đề</th><th>Tín hiệu hội tụ</th></tr>
            </thead>
            <tbody id="tbl-top-de"></tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="grid g-3" style="margin-top:16px">
      <div class="card">
        <h2>🧭 Khung Càng & Tổng Trọng Tâm</h2>
        <div id="quick-tong-cang"></div>
      </div>
      <div class="card">
        <h2>📐 Pascal & Cầu Kẹp Kỳ Gần Nhất</h2>
        <div id="quick-pascal"></div>
      </div>
      <div class="card">
        <h2>⚠️ Cảnh Báo Bẫy Gan & Nhịp Đề 30 Kỳ</h2>
        <div id="quick-traps"></div>
      </div>
    </div>

    <div class="note-box">
      <strong>Lưu ý xác suất thực chứng (Kỷ luật v2):</strong>
      Nền ngẫu nhiên năm <span id="note-year"></span> đạt <strong>BTL <span id="note-btl"></span>%</strong> và <strong>STL <span id="note-stl"></span>%</strong>; Đề dàn 10 số = <strong>10%</strong>; 3 Càng 1 số = <strong>0.1%</strong>.
      Hệ thống chỉ tổng hợp tín hiệu thống kê lịch sử — không cam kết chắc chắn thắng và luôn trừ điểm cảnh báo với bẫy Lô gan ≥ 12 ngày, Đề đại gan ≥ 280 ngày.
    </div>
  </section>

  <!-- TAB 2: BRIDGES & BAC NHO -->
  <section id="tab-bridges" class="tab-panel">
    <div class="grid g-2" id="cam-rebound-container"></div>

    <div class="grid g-2" style="margin-top:16px">
      <div class="card">
        <h2>⚡ Top Cầu STL Thông ≥ 7 Ngày (107 Vị Trí)</h2>
        <div class="scroll-x">
          <table>
            <thead><tr><th>Cặp STL</th><th>Thông</th><th>30d</th><th>Năm nay</th><th>Vị trí ghép</th></tr></thead>
            <tbody id="tbl-stl-streak"></tbody>
          </table>
        </div>
        <h3>🏆 Top Cầu STL Thông ≥ 5 Ngày & Tỷ Lệ Năm Cao Nhất</h3>
        <div class="scroll-x">
          <table>
            <thead><tr><th>Cặp STL</th><th>Năm nay</th><th>Thông</th><th>Vị trí ghép</th></tr></thead>
            <tbody id="tbl-stl-rate"></tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <h2>🎯 Top Cầu BTL Thông ≥ 5 Ngày</h2>
        <div class="scroll-x">
          <table>
            <thead><tr><th>BTL</th><th>Thông</th><th>30d</th><th>Năm nay</th><th>Vị trí</th></tr></thead>
            <tbody id="tbl-btl"></tbody>
          </table>
        </div>
        <h3>🎲 Cầu Chạm (≥4d) · Cầu Tổng (≥3d) · Cầu Càng (≥3d)</h3>
        <div id="box-de-bridges"></div>
      </div>
    </div>

    <div class="grid g-2" style="margin-top:16px">
      <div class="card">
        <h2>🏛️ Hồ Sơ Nhà Đài Mục Tiêu <span class="pill accent" id="wd-title-badge"></span></h2>
        <div id="box-weekday-profile"></div>
      </div>
      <div class="card">
        <h2>🧠 Bạc Nhớ Sau Đề <span class="pill amber" id="bn-de-badge"></span></h2>
        <div id="box-bacnho"></div>
      </div>
    </div>
  </section>

  <!-- TAB 3: GAN & 7 WEEKDAYS -->
  <section id="tab-gan" class="tab-panel">
    <div class="grid g-2">
      <div class="card">
        <h2>📊 Gan Tổng Đề vs Kỷ Lục Max 13 Năm</h2>
        <div class="scroll-x">
          <table>
            <thead><tr><th>Tổng</th><th>Hiện tại</th><th>Max 13 năm</th><th>Tỷ lệ so Max</th><th>Gần nhất</th></tr></thead>
            <tbody id="tbl-gan-tong"></tbody>
          </table>
        </div>
      </div>
      <div class="card">
        <h2>📊 Gan Càng Đề vs Kỷ Lục Max 13 Năm</h2>
        <div class="scroll-x">
          <table>
            <thead><tr><th>Càng</th><th>Hiện tại</th><th>Max 13 năm</th><th>Tỷ lệ so Max</th><th>Gần nhất</th></tr></thead>
            <tbody id="tbl-gan-cang"></tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="grid g-3" style="margin-top:16px">
      <div class="card">
        <h2>🚨 Top 15 Đề Gan Sâu Nhất</h2>
        <table>
          <thead><tr><th>Đề</th><th>Số ngày</th><th>Lần cuối</th></tr></thead>
          <tbody id="tbl-de-gan15"></tbody>
        </table>
      </div>
      <div class="card">
        <h2>🧊 Top 12 Lô Gan & Đầu/Đuôi Đề Gan</h2>
        <table>
          <thead><tr><th>Lô</th><th>Gan</th><th>Lần cuối</th></tr></thead>
          <tbody id="tbl-lo-gan12"></tbody>
        </table>
        <h3>Đầu / Đuôi Đề Gan Nhất</h3>
        <div id="box-dau-duoi-gan"></div>
      </div>
      <div class="card">
        <h2>🔥 Top 12 Lô Nóng (15 Ngày & 30 Ngày)</h2>
        <div id="box-lo-hot"></div>
      </div>
    </div>

    <div class="card" style="margin-top:16px">
      <h2>📅 Ma Trận 7 Nhà Đài Theo Thứ Trong Tuần (Năm <span id="wm-year"></span>)</h2>
      <div class="scroll-x">
        <table>
          <thead><tr><th>Thứ & Nhà Đài</th><th>Số kỳ</th><th>Top 3 Càng</th><th>Top 3 Tổng</th><th>Top 5 Lô Nổi Bật</th></tr></thead>
          <tbody id="tbl-weekday-matrix"></tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- TAB 4: LOOKUP & DAILY EVALUATOR -->
  <section id="tab-evaluate" class="tab-panel">
    <div class="card">
      <h2>🔎 Tra Cứu & Chấm Điểm Tức Thì Bất Kỳ Số Nào (00–99)</h2>
      <div class="input-row">
        <div class="field">
          <label for="lookup-input">Nhập các số cần kiểm tra (cách nhau bởi dấu phẩy hoặc khoảng trắng, vd: 06 42 60 98)</label>
          <input id="lookup-input" type="text" placeholder="Ví dụ: 06, 42, 60, 32, 98" />
        </div>
        <button class="btn" id="btn-lookup">Kiểm tra điểm</button>
      </div>
      <div id="lookup-results"></div>
    </div>

    <div class="card" style="margin-top:16px">
      <h2>✅ Công Cụ Tự Đánh Giá & Đối Soát Dàn Chốt Hằng Ngày</h2>
      <div class="input-row">
        <div class="field" style="max-width:260px">
          <label for="eval-draw-select">Chọn kỳ quay để đối soát (30 kỳ gần nhất)</label>
          <select id="eval-draw-select"></select>
        </div>
        <div class="field">
          <label for="eval-lo">Dàn Lô (vd: 06 60 32)</label>
          <input id="eval-lo" type="text" placeholder="06 60 32" />
        </div>
        <div class="field" style="max-width:130px">
          <label for="eval-lo-pts">Điểm/con Lô</label>
          <input id="eval-lo-pts" type="number" min="0" value="5" />
        </div>
        <div class="field">
          <label for="eval-de">Dàn Đề (vd: 42 60 08)</label>
          <input id="eval-de" type="text" placeholder="42 60 08" />
        </div>
        <div class="field" style="max-width:130px">
          <label for="eval-de-k">Tiền Đề (k/con)</label>
          <input id="eval-de-k" type="number" min="0" value="10" />
        </div>
      </div>
      <div class="input-row">
        <div class="field">
          <label for="eval-xien">Xiên 2 (vd: 06-60, 32-02)</label>
          <input id="eval-xien" type="text" placeholder="06-60, 32-02" />
        </div>
        <div class="field" style="max-width:140px">
          <label for="eval-xien-k">Tiền X2 (k/cặp)</label>
          <input id="eval-xien-k" type="number" min="0" value="20" />
        </div>
        <div class="field">
          <label for="eval-3c">3 Càng (vd: 142 560 908)</label>
          <input id="eval-3c" type="text" placeholder="142 560 908" />
        </div>
        <div class="field" style="max-width:140px">
          <label for="eval-3c-k">Tiền 3C (k/số)</label>
          <input id="eval-3c-k" type="number" min="0" value="5" />
        </div>
        <button class="btn" id="btn-eval-run">Đối soát & Tính lãi/lỗ</button>
        <button class="btn secondary" id="btn-eval-save">Lưu vào Nhật ký</button>
      </div>
      <div id="eval-output"></div>

      <h3>📒 Nhật Ký Tự Đánh Giá Hiệu Suất (Lưu trên trình duyệt — localStorage)</h3>
      <div class="input-row">
        <button class="btn secondary" id="btn-export-log">Xuất JSON nhật ký</button>
        <button class="btn danger" id="btn-clear-log">Xóa nhật ký</button>
      </div>
      <div class="scroll-x">
        <table>
          <thead><tr><th>Kỳ đối soát</th><th>ĐB</th><th>Lô trúng</th><th>Đề / 3C</th><th>Xiên 2</th><th>Vốn (k)</th><th>Thu (k)</th><th>Lãi/Lỗ (k)</th></tr></thead>
          <tbody id="tbl-eval-log"></tbody>
        </table>
      </div>
    </div>

    <div class="card" style="margin-top:16px">
      <h2>📜 Lịch Sử 30 Kỳ Quay Gần Nhất</h2>
      <div class="input-row">
        <div class="field" style="max-width:300px">
          <label for="hist-filter">Lọc theo ngày hoặc số (vd: 89 hoặc 24/11)</label>
          <input id="hist-filter" type="text" placeholder="Nhập số hoặc ngày..." />
        </div>
      </div>
      <div class="scroll-x">
        <table>
          <thead><tr><th>Ngày</th><th>Thứ / Đài</th><th>ĐB</th><th>Đề</th><th>Càng</th><th>Tổng</th><th>G1</th><th>27 Số Lô Tô</th></tr></thead>
          <tbody id="tbl-history"></tbody>
        </table>
      </div>
    </div>
  </section>
</main>

<footer>
  XSMB Analytics Dashboard v2 · Dữ liệu chuẩn hóa từ <span class="mono">data/xsmb_2014_2026_cache.json</span> · Không lưu thông tin cá nhân · Sinh tự động bằng <span class="mono">scripts/build_dashboard.py</span>
</footer>

<script>
const DATA = __PAYLOAD_JSON__;

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

// Tab switching
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    $("tab-" + btn.dataset.tab).classList.add("active");
  });
});

function renderAll() {
  const m = DATA.meta;
  const L = DATA.latest;

  $("hdr-sub").textContent = `Cập nhật lúc ${m.generated_at} · Mục tiêu: ${m.target_weekday} ${m.target_date} (Đài ${m.target_station})`;
  $("hdr-pills").innerHTML = `
    <span class="pill accent">Kho: ${m.total_draws.toLocaleString("vi-VN")} kỳ (2014–${m.year})</span>
    <span class="pill green">${m.year}: ${m.year_draws} kỳ</span>
    <span class="pill amber">Nền BTL ${m.baseline_btl}% · STL ${m.baseline_stl}%</span>
  `;

  $("note-year").textContent = m.year;
  $("note-btl").textContent = m.baseline_btl;
  $("note-stl").textContent = m.baseline_stl;
  $("lo-target-badge").textContent = `${m.target_weekday} ${m.target_date}`;
  $("de-target-badge").textContent = `Đài ${m.target_station}`;
  $("wd-title-badge").textContent = `${DATA.weekday.name} — ${DATA.weekday.station} (N=${DATA.weekday.n})`;
  $("bn-de-badge").textContent = `Đề ${L.de}`;
  $("wm-year").textContent = m.year;

  // KPI cards
  const camTxt = [
    L.cam_dau.length ? `Đầu câm: ${L.cam_dau.join(", ")}` : "Không câm Đầu",
    L.cam_duoi.length ? `Đuôi câm: ${L.cam_duoi.join(", ")}` : "Không câm Đuôi",
  ].join(" · ");
  const multTxt = L.multi_hits.length ? L.multi_hits.map((x) => `${x.num}×${x.cnt}`).join(", ") : "Không có";

  $("kpi-cards").innerHTML = `
    <div class="card">
      <div class="kpi-lbl">Kỳ Gần Nhất (${esc(L.date)} — ${esc(L.weekday)})</div>
      <div class="kpi-val" style="color:#f87171">${esc(L.db)}</div>
      <div class="kpi-sub">Đề <strong>${esc(L.de)}</strong> · Càng <strong>${esc(L.cang)}</strong> · Tổng <strong>${esc(L.tong)}</strong> · Bộ <strong>${esc(L.bo)}</strong> · G1 <span class="mono">${esc(L.p1)}</span></div>
    </div>
    <div class="card">
      <div class="kpi-lbl">Biến Cố Kỳ Trước</div>
      <div class="kpi-val" style="font-size:1.15rem;color:#fcd34d">${esc(camTxt)}</div>
      <div class="kpi-sub">&gt;1 nháy: <strong>${esc(multTxt)}</strong></div>
    </div>
    <div class="card">
      <div class="kpi-lbl">Pascal ĐB+G1 (${m.year}: ${m.pascal_pct}%)</div>
      <div class="kpi-val" style="color:#7dd3fc">${esc(L.pascal_dbg1)} <span style="font-size:.95rem;color:var(--muted)">(STL ${esc(L.stl_pascal_dbg1)})</span></div>
      <div class="kpi-sub">Hiệu suất năm ${m.year}: <strong>${m.pascal_hits}/${m.pascal_total}</strong> · Pascal ĐB: <strong>${esc(L.pascal_db)}</strong></div>
    </div>
    <div class="card">
      <div class="kpi-lbl">Nhịp Đề 30 Kỳ Gần Nhất</div>
      <div class="kpi-val" style="color:#86efac">TB ${DATA.gan.warm_30.avg}d</div>
      <div class="kpi-sub">≤50d: <strong>${DATA.gan.warm_30.le50}/30</strong> · ≤100d: <strong>${DATA.gan.warm_30.le100}/30</strong> · ≥200d: <strong>${DATA.gan.warm_30.ge200}/30</strong></div>
    </div>
  `;

  // Top 15 Lo
  $("tbl-top-lo").innerHTML = DATA.scores_lo_all.slice(0, 15).map((r, i) => `
    <tr>
      <td>${i + 1}</td>
      <td><span class="num-badge ${r.trap ? "trap" : i < 5 ? "top" : ""}">${r.num}</span></td>
      <td><strong>${r.score.toFixed(1)}</strong></td>
      <td>${r.gan}d</td>
      <td>${r.c15} / ${r.c30}</td>
      <td>${r.c_wd}/${r.wd_n}</td>
      <td>${r.tags.map((t) => `<span class="tag ${t.includes("Bẫy") ? "warn" : ""}">${esc(t)}</span>`).join("")}</td>
    </tr>
  `).join("");

  // Top 16 De
  $("tbl-top-de").innerHTML = DATA.scores_de_all.slice(0, 16).map((r, i) => `
    <tr>
      <td>${i + 1}</td>
      <td><span class="num-badge ${r.trap ? "trap" : i < 5 ? "top" : ""}">${r.num}</span></td>
      <td><strong>${r.score.toFixed(1)}</strong></td>
      <td>T${r.tong} / B${r.bo}</td>
      <td>${r.gan}d</td>
      <td>${r.tags.map((t) => `<span class="tag ${t.includes("Bẫy") ? "warn" : ""}">${esc(t)}</span>`).join("")}</td>
    </tr>
  `).join("");

  // Quick cards
  const topTongGan = DATA.gan.tong.slice(0, 3).map((x) => `T${x.digit} (${x.cur}d)`).join(", ");
  const topCangGan = DATA.gan.cang.slice(0, 3).map((x) => `C${x.digit} (${x.cur}d)`).join(", ");
  const topTongWd = DATA.weekday.tong.slice(0, 3).map((x) => `T${x[0]} (${x[1]}x)`).join(", ");
  const topCangWd = DATA.weekday.cang.slice(0, 3).map((x) => `C${x[0]} (${x[1]}x)`).join(", ");
  const topCham = DATA.bridges.cham_dist.slice(0, 4).map((x) => `Chạm ${x[0]} (${x[1]} cầu)`).join(", ");
  $("quick-tong-cang").innerHTML = `
    <p><strong>Vua Tổng ${esc(DATA.weekday.name)}:</strong> ${esc(topTongWd)}</p>
    <p><strong>Top Gan Tổng:</strong> ${esc(topTongGan)}</p>
    <p><strong>Vua Càng ${esc(DATA.weekday.name)}:</strong> ${esc(topCangWd)}</p>
    <p><strong>Top Gan Càng:</strong> ${esc(topCangGan)}</p>
    <p><strong>Phân bố Cầu Chạm ≥4d:</strong> ${esc(topCham || "Chưa có")}</p>
  `;

  $("quick-pascal").innerHTML = `
    <p><strong>Pascal ĐB+G1:</strong> <span class="num-badge top">${esc(L.pascal_dbg1)}</span> (STL ${esc(L.stl_pascal_dbg1)})</p>
    <p><strong>Pascal ĐB:</strong> <span class="num-badge">${esc(L.pascal_db)}</span> (STL ${esc(L.stl_pascal_db)})</p>
    <p><strong>Cầu kẹp X-AB-X (${esc(L.date)}):</strong></p>
    <div>${L.keps.length ? L.keps.map((k) => `<span class="tag">${esc(k.pos)}: ${esc(k.raw)} → <strong>${esc(k.pair)}</strong></span>`).join("") : '<span class="tag">Không có cầu kẹp kỳ này</span>'}</div>
  `;

  const loTraps = DATA.gan.lo_top12.filter((x) => x.cur >= 12);
  const deTraps = DATA.gan.de_top15.filter((x) => x.cur >= 280);
  $("quick-traps").innerHTML = `
    <p><strong>Lô Gan ≥ 12 ngày (tránh ép BTL):</strong><br/>${loTraps.length ? loTraps.map((x) => `<span class="tag warn">${x.num} (${x.cur}d)</span>`).join("") : "Không có"}</p>
    <p><strong>Đề Đại Gan ≥ 280 ngày (chỉ theo dõi):</strong><br/>${deTraps.map((x) => `<span class="tag warn">${x.num} (${x.cur}d)</span>`).join("")}</p>
  `;

  // Tab 2: Cam Rebound
  $("cam-rebound-container").innerHTML = DATA.cam_rebound.length
    ? DATA.cam_rebound.map((blk) => `
      <div class="card">
        <h2>🔔 Bật Lại Sau Câm ${esc(blk.kind)} ${esc(blk.digit)}</h2>
        ${blk.frames.map((f) => `
          <h3>${esc(f.label)} (N=${f.n} · Về ${f.hit_days}/${f.n}, TB ${f.avg} nháy)</h3>
          <div><strong>Top số:</strong> ${f.top_nums.map((x) => `<span class="tag"><strong>${x.num}</strong> ${x.cnt} (${x.pct}%)</span>`).join("")}</div>
          <div style="margin-top:4px"><strong>Top STL:</strong> ${f.top_stl.map((x) => `<span class="tag">${x.pair} (${x.pct}%)</span>`).join("")}</div>
        `).join("")}
      </div>
    `).join("")
    : `<div class="card"><h2>🔔 Câm Đầu / Đuôi</h2><p style="color:var(--muted)">Kỳ gần nhất (${esc(L.date)}) không có Đầu câm hoặc Đuôi câm.</p></div>`;

  // Bridges tables
  $("tbl-stl-streak").innerHTML = DATA.bridges.stl_streak.map((r) => `
    <tr><td><span class="num-badge top">${esc(r.pair)}</span></td><td><strong>${r.streak}d</strong></td><td>${r.h30}/30</td><td>${r.h_yr} (${r.yr_pct}%)</td><td class="mono">${esc(r.pos)}</td></tr>
  `).join("") || '<tr><td colspan="5">Không có cầu ≥7d</td></tr>';

  $("tbl-stl-rate").innerHTML = DATA.bridges.stl_rate.map((r) => `
    <tr><td><span class="num-badge">${esc(r.pair)}</span></td><td><strong>${r.h_yr} (${r.yr_pct}%)</strong></td><td>${r.streak}d</td><td class="mono">${esc(r.pos)}</td></tr>
  `).join("") || '<tr><td colspan="4">Không có cầu đạt ngưỡng</td></tr>';

  $("tbl-btl").innerHTML = DATA.bridges.btl.map((r) => `
    <tr><td><span class="num-badge top">${esc(r.num)}</span></td><td><strong>${r.streak}d</strong></td><td>${r.h30}/30</td><td>${r.h_yr} (${r.yr_pct}%)</td><td class="mono">${esc(r.pos)}</td></tr>
  `).join("") || '<tr><td colspan="5">Không có cầu ≥5d</td></tr>';

  $("box-de-bridges").innerHTML = `
    <p><strong>Cầu Chạm ≥4d:</strong><br/>${DATA.bridges.cham.map((r) => `<span class="tag">Chạm <strong>${r.digit}</strong> (${r.streak}d · năm ${r.h_yr})</span>`).join("") || "Không có"}</p>
    <p><strong>Cầu Tổng ≥3d:</strong><br/>${DATA.bridges.tong.map((r) => `<span class="tag">Tổng <strong>${r.digit}</strong> (${r.streak}d · năm ${r.h_yr})</span>`).join("") || "Không có"}</p>
    <p><strong>Cầu Càng ≥3d:</strong><br/>${DATA.bridges.cang.map((r) => `<span class="tag">Càng <strong>${r.digit}</strong> (${r.streak}d · năm ${r.h_yr})</span>`).join("") || "Không có"}</p>
  `;

  // Weekday Profile
  const W = DATA.weekday;
  $("box-weekday-profile").innerHTML = `
    <p><strong>Top Lô:</strong> ${W.top_lo.map((x) => `<span class="tag"><strong>${x.num}</strong> ${x.cnt}/${W.n} (${x.pct}%)</span>`).join("")}</p>
    <p><strong>Top STL:</strong> ${W.top_stl.map((x) => `<span class="tag"><strong>${x.pair}</strong> (${x.pct}%)</span>`).join("")}</p>
    <p><strong>Top Xiên 2:</strong> ${W.top_xien.map((x) => `<span class="tag">${x.pair} (${x.pct}%)</span>`).join("")}</p>
    <p><strong>Top ≥2 nháy:</strong> ${W.top_mult.map((x) => `<span class="tag">${x[0]} (${x[1]}x)</span>`).join("")}</p>
    <p><strong>Đầu Đề:</strong> ${W.dau.slice(0,5).map((x) => `Đ${x[0]}(${x[1]})`).join(", ")} · <strong>Đuôi Đề:</strong> ${W.duoi.slice(0,5).map((x) => `Đ${x[0]}(${x[1]})`).join(", ")}</p>
    <p><strong>Tổng Đề:</strong> ${W.tong.slice(0,5).map((x) => `T${x[0]}(${x[1]})`).join(", ")} · <strong>Bộ:</strong> ${W.bo.slice(0,5).map((x) => `B${x[0]}(${x[1]})`).join(", ")}</p>
    <p><strong>Càng Đề:</strong> ${W.cang.slice(0,5).map((x) => `C${x[0]}(${x[1]})`).join(", ")}</p>
  `;

  // Bac nho
  $("box-bacnho").innerHTML = DATA.bacnho.map((b) => `
    <h3>${esc(b.label)} (N=${b.n})</h3>
    <p><strong>Top Lô:</strong> ${b.top_lo.map((x) => `<span class="tag"><strong>${x.num}</strong> (${x.pct}%)</span>`).join("")}</p>
    <p><strong>Top STL:</strong> ${b.top_stl.map((x) => `<span class="tag">${x.pair} (${x.pct}%)</span>`).join("")}</p>
    <p><strong>Tổng:</strong> ${b.tong.map((x) => `T${x[0]}(${x[1]})`).join(", ")} · <strong>Bộ:</strong> ${b.bo.map((x) => `B${x[0]}(${x[1]})`).join(", ")} · <strong>Càng:</strong> ${b.cang.map((x) => `C${x[0]}(${x[1]})`).join(", ")}</p>
  `).join("");

  // Tab 3: Gan tables
  const renderGanRows = (arr) => arr.map((r) => {
    const pct = Math.min(100, Math.round((r.cur / Math.max(1, r.max13)) * 100));
    return `<tr>
      <td><span class="num-badge ${r.cur >= 15 ? "trap" : ""}">${r.digit}</span></td>
      <td><strong>${r.cur}d</strong></td>
      <td>${r.max13}d</td>
      <td style="min-width:120px">${pct}%<div class="bar-wrap"><div class="bar-fill ${pct >= 30 ? "amber" : ""}" style="width:${pct}%"></div></div></td>
      <td class="mono">${esc(r.last_date)} (${esc(r.last_db)})</td>
    </tr>`;
  }).join("");
  $("tbl-gan-tong").innerHTML = renderGanRows(DATA.gan.tong);
  $("tbl-gan-cang").innerHTML = renderGanRows(DATA.gan.cang);

  $("tbl-de-gan15").innerHTML = DATA.gan.de_top15.map((r) => `
    <tr><td><span class="num-badge ${r.cur >= 280 ? "trap" : ""}">${r.num}</span></td><td><strong>${r.cur} ngày</strong></td><td class="mono">${esc(r.last_date)}</td></tr>
  `).join("");

  $("tbl-lo-gan12").innerHTML = DATA.gan.lo_top12.map((r) => `
    <tr><td><span class="num-badge ${r.cur >= 12 ? "trap" : ""}">${r.num}</span></td><td><strong>${r.cur} ngày</strong></td><td class="mono">${esc(r.last_date)}</td></tr>
  `).join("");

  $("box-dau-duoi-gan").innerHTML = `
    <p><strong>Đầu gan:</strong> ${DATA.gan.dau.slice(0,5).map((r) => `<span class="tag ${r.cur >= 15 ? "warn" : ""}">Đầu ${r.digit}: ${r.cur}d/${r.max13}d</span>`).join("")}</p>
    <p><strong>Đuôi gan:</strong> ${DATA.gan.duoi.slice(0,5).map((r) => `<span class="tag ${r.cur >= 15 ? "warn" : ""}">Đuôi ${r.digit}: ${r.cur}d/${r.max13}d</span>`).join("")}</p>
  `;

  $("box-lo-hot").innerHTML = `
    <h3>15 ngày gần nhất</h3>
    <div>${DATA.gan.lo_hot15.map((x) => `<span class="tag"><strong>${x[0]}</strong> ×${x[1]}</span>`).join("")}</div>
    <h3>30 ngày gần nhất</h3>
    <div>${DATA.gan.lo_hot30.map((x) => `<span class="tag"><strong>${x[0]}</strong> ×${x[1]}</span>`).join("")}</div>
  `;

  $("tbl-weekday-matrix").innerHTML = DATA.weekday_matrix.map((w) => `
    <tr style="${w.is_target ? "background:rgba(56,189,248,0.1)" : ""}">
      <td><strong>${esc(w.weekday)}</strong> — ${esc(w.station)} ${w.is_target ? '<span class="pill accent">Hôm nay</span>' : ""}</td>
      <td>${w.n}</td>
      <td>${w.top_cang.map((x) => `C${x[0]}(${x[1]})`).join(", ")}</td>
      <td>${w.top_tong.map((x) => `T${x[0]}(${x[1]})`).join(", ")}</td>
      <td>${w.top_lo.map((x) => `<span class="tag"><strong>${x.num}</strong> ${x.pct}%</span>`).join("")}</td>
    </tr>
  `).join("");

  // Tab 4: Select draws & history
  $("eval-draw-select").innerHTML = DATA.recent_30.map((d, idx) =>
    `<option value="${idx}">${d.date} (${d.weekday}) — ĐB ${d.db}</option>`
  ).join("");

  renderHistory("");
  renderEvalLog();
}

// Instant lookup 00-99
const loMap = Object.fromEntries(DATA.scores_lo_all.map((r) => [r.num, r]));
const deMap = Object.fromEntries(DATA.scores_de_all.map((r) => [r.num, r]));

function runLookup() {
  const raw = $("lookup-input").value;
  const nums = [...new Set((raw.match(/\d{1,2}/g) || []).map((x) => x.padStart(2, "0")))];
  if (!nums.length) {
    $("lookup-results").innerHTML = '<p style="color:var(--muted)">Hãy nhập ít nhất một số từ 00 đến 99.</p>';
    return;
  }
  $("lookup-results").innerHTML = `
    <div class="scroll-x">
      <table>
        <thead><tr><th>Số</th><th>Điểm Lô</th><th>Gan Lô</th><th>Tín hiệu Lô</th><th>Điểm Đề</th><th>Gan Đề</th><th>Tổng / Bộ</th><th>Tín hiệu Đề</th></tr></thead>
        <tbody>
          ${nums.map((num) => {
            const lr = loMap[num], dr = deMap[num];
            if (!lr || !dr) return "";
            return `<tr>
              <td><span class="num-badge ${lr.trap || dr.trap ? "trap" : "top"}">${num}</span></td>
              <td><strong>${lr.score.toFixed(1)}</strong></td>
              <td>${lr.gan}d</td>
              <td>${lr.tags.map((t) => `<span class="tag ${t.includes("Bẫy") ? "warn" : ""}">${esc(t)}</span>`).join("") || "-"}</td>
              <td><strong>${dr.score.toFixed(1)}</strong></td>
              <td>${dr.gan}d</td>
              <td>T${dr.tong} / B${dr.bo}</td>
              <td>${dr.tags.map((t) => `<span class="tag ${t.includes("Bẫy") ? "warn" : ""}">${esc(t)}</span>`).join("") || "-"}</td>
            </tr>`;
          }).join("")}
        </tbody>
      </table>
    </div>
  `;
}
$("btn-lookup").addEventListener("click", runLookup);
$("lookup-input").addEventListener("keydown", (e) => { if (e.key === "Enter") runLookup(); });

// Evaluator & P/L calculator (Lô 22.5 ăn 80 | Đề 1 ăn 84 | X2 1 ăn 14 | 3C 1 ăn 800)
const LOG_KEY = "xsmb_v2_eval_log";
function parseNums(str, len = 2) {
  const re = new RegExp(`\\d{1,${len}}`, "g");
  return [...new Set((str.match(re) || []).map((x) => x.padStart(len, "0")))];
}
function parsePairs(str) {
  const matches = str.match(/\d{2}\s*[-–/]\s*\d{2}/g) || [];
  return matches.map((m) => m.replace(/\s+/g, "").replace(/[–/]/g, "-"));
}

function evaluateCurrent() {
  const draw = DATA.recent_30[Number($("eval-draw-select").value) || 0];
  const lotoCounts = {};
  draw.loto.forEach((x) => { lotoCounts[x] = (lotoCounts[x] || 0) + 1; });

  const los = parseNums($("eval-lo").value, 2);
  const loPts = Number($("eval-lo-pts").value) || 0;
  const des = parseNums($("eval-de").value, 2);
  const deK = Number($("eval-de-k").value) || 0;
  const xiens = parsePairs($("eval-xien").value);
  const xienK = Number($("eval-xien-k").value) || 0;
  const c3s = parseNums($("eval-3c").value, 3);
  const c3K = Number($("eval-3c-k").value) || 0;

  let loHits = [], totalNhay = 0;
  los.forEach((n) => {
    if (lotoCounts[n]) {
      loHits.push(`${n}×${lotoCounts[n]}`);
      totalNhay += lotoCounts[n];
    }
  });
  const deHit = des.includes(draw.de);
  const c3Target = draw.db.slice(-3);
  const c3Hit = c3s.includes(c3Target);
  const xienHits = xiens.filter((p) => {
    const [a, b] = p.split("-");
    return lotoCounts[a] > 0 && lotoCounts[b] > 0;
  });

  const cost = los.length * loPts * 22.5 + des.length * deK + xiens.length * xienK + c3s.length * c3K;
  const win = totalNhay * loPts * 80 + (deHit ? deK * 84 : 0) + xienHits.length * xienK * 14 + (c3Hit ? c3K * 800 : 0);
  const net = win - cost;

  const summary = {
    date: draw.date,
    db: draw.db,
    lo_str: loHits.length ? loHits.join(", ") : `0/${los.length}`,
    de_3c: `${deHit ? "Trúng Đề " + draw.de : "Trượt Đề"}${c3s.length ? (c3Hit ? " · Trúng 3C " + c3Target : " · Trượt 3C") : ""}`,
    xien_str: xiens.length ? `${xienHits.length}/${xiens.length} (${xienHits.join(", ") || "-"})` : "-",
    cost: Math.round(cost * 10) / 10,
    win: Math.round(win * 10) / 10,
    net: Math.round(net * 10) / 10,
  };

  $("eval-output").innerHTML = `
    <div class="grid g-4" style="margin-top:8px">
      <div class="card"><div class="kpi-lbl">Kỳ Đối Soát</div><div class="kpi-val" style="font-size:1.15rem">${draw.date} · ĐB ${draw.db}</div><div class="kpi-sub">Đề ${draw.de} · 3 Càng ${c3Target}</div></div>
      <div class="card"><div class="kpi-lbl">Kết Quả Trúng</div><div class="kpi-val" style="font-size:1.05rem">${esc(summary.lo_str)}</div><div class="kpi-sub">${esc(summary.de_3c)} · X2: ${esc(summary.xien_str)}</div></div>
      <div class="card"><div class="kpi-lbl">Tổng Vốn / Tiền Thu</div><div class="kpi-val" style="font-size:1.15rem">${summary.cost.toLocaleString("vi-VN")}k / ${summary.win.toLocaleString("vi-VN")}k</div><div class="kpi-sub">Tỷ lệ: Lô 22.5→80 · Đề 84 · X2 14 · 3C 800</div></div>
      <div class="card"><div class="kpi-lbl">Lãi / Lỗ Ròng</div><div class="kpi-val ${net >= 0 ? "profit-pos" : "profit-neg"}">${net >= 0 ? "+" : ""}${summary.net.toLocaleString("vi-VN")}k</div></div>
    </div>
  `;
  return summary;
}

function getEvalLog() {
  try { return JSON.parse(localStorage.getItem(LOG_KEY) || "[]"); } catch { return []; }
}
function renderEvalLog() {
  const logs = getEvalLog();
  if (!logs.length) {
    $("tbl-eval-log").innerHTML = '<tr><td colspan="8" style="color:var(--muted)">Chưa có bản ghi đối soát nào. Nhập dàn ở trên rồi bấm "Lưu vào Nhật ký".</td></tr>';
    return;
  }
  const totalNet = logs.reduce((acc, x) => acc + (x.net || 0), 0);
  $("tbl-eval-log").innerHTML = logs.map((r) => `
    <tr>
      <td class="mono">${esc(r.date)}</td>
      <td class="mono"><strong>${esc(r.db)}</strong></td>
      <td>${esc(r.lo_str)}</td>
      <td>${esc(r.de_3c)}</td>
      <td>${esc(r.xien_str)}</td>
      <td>${r.cost}</td>
      <td>${r.win}</td>
      <td class="${r.net >= 0 ? "profit-pos" : "profit-neg"}">${r.net >= 0 ? "+" : ""}${r.net}</td>
    </tr>
  `).join("") + `
    <tr style="background:rgba(56,189,248,0.08)">
      <td colspan="7"><strong>TỔNG CỘNG (${logs.length} phiên đã lưu)</strong></td>
      <td class="${totalNet >= 0 ? "profit-pos" : "profit-neg"}">${totalNet >= 0 ? "+" : ""}${Math.round(totalNet * 10) / 10}k</td>
    </tr>
  `;
}

$("btn-eval-run").addEventListener("click", evaluateCurrent);
$("btn-eval-save").addEventListener("click", () => {
  const s = evaluateCurrent();
  const logs = getEvalLog();
  logs.unshift(s);
  localStorage.setItem(LOG_KEY, JSON.stringify(logs.slice(0, 120)));
  renderEvalLog();
});
$("btn-clear-log").addEventListener("click", () => {
  localStorage.removeItem(LOG_KEY);
  renderEvalLog();
});
$("btn-export-log").addEventListener("click", () => {
  const blob = new Blob([JSON.stringify(getEvalLog(), null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "xsmb_eval_log.json";
  a.click();
});

// History filter
function renderHistory(q) {
  const s = q.trim().toLowerCase();
  const rows = DATA.recent_30.filter((d) =>
    !s || d.date.toLowerCase().includes(s) || d.db.includes(s) || d.loto.includes(s.padStart(2, "0"))
  );
  $("tbl-history").innerHTML = rows.map((d) => `
    <tr>
      <td class="mono">${esc(d.date)}</td>
      <td>${esc(d.weekday)} (${esc(d.station)})</td>
      <td class="mono" style="color:#f87171;font-weight:700">${esc(d.db)}</td>
      <td><span class="num-badge top">${esc(d.de)}</span></td>
      <td>${esc(d.cang)}</td>
      <td>${esc(d.tong)}</td>
      <td class="mono">${esc(d.p1)}</td>
      <td class="mono" style="font-size:0.78rem;color:var(--muted)">${esc([...d.loto].sort().join(", "))}</td>
    </tr>
  `).join("");
}
$("hist-filter").addEventListener("input", (e) => renderHistory(e.target.value));

renderAll();
</script>
</body>
</html>
"""


def generate_dashboard(cache_path: str = DEFAULT_CACHE, out_path: str = DEFAULT_OUT, target_str: str = None):
    payload = build_payload(cache_path, target_str)
    payload_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    html = HTML_TEMPLATE.replace("__PAYLOAD_JSON__", payload_json)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[*] Đã sinh dashboard HTML thành công: {out_path} ({len(html.encode('utf-8')):,} bytes)")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Sinh giao diện HTML đánh giá & phân tích XSMB mỗi ngày")
    parser.add_argument("--data", default=DEFAULT_CACHE, help="Đường dẫn file xsmb_2014_2026_cache.json")
    parser.add_argument("--out", default=DEFAULT_OUT, help="Đường dẫn file HTML đầu ra (mặc định: index.html)")
    parser.add_argument("--target", default=None, help="Ngày mục tiêu (YYYY-MM-DD)")
    args = parser.parse_args()
    generate_dashboard(args.data, args.out, args.target)


if __name__ == "__main__":
    main()
