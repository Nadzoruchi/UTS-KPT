# Skrip Otomasi Eksperimen & Pembuatan Grafik Visualisasi UTS KPT

#==============================================
# Nama  : Muhammad Zaki Zaidan Binawan
# NPM   : 247006111134
# Kelas : E
#==============================================


import os
import sys
import time
import math
import csv
import matplotlib.pyplot as plt

# Import fungsi-fungsi pemrosesan dari fungsi utama
from hybrid_analyzer import (
    run_hybrid_file_analyzer,
    run_serial_baseline,
    DATASET_DIR,
    NAMA_MAHASISWA,
    NIM_MAHASISWA
)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hasil_eksperimen")


def get_dataset_files(data_count):
    all_files = sorted([os.path.join(DATASET_DIR, f) for f in os.listdir(DATASET_DIR) if f.endswith(".txt")])
    return all_files[:min(data_count, len(all_files))]


def run_benchmark():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 75)
    print("MEMULAI BENCHMARK EKSPERIMEN HYBRID COMPUTING UTS KPT")
    print(f"Mahasiswa : {NAMA_MAHASISWA} ({NIM_MAHASISWA})")
    print("=" * 75)

    # Mastiin data ada
    files_1340 = get_dataset_files(1340)
    if len(files_1340) < 1340:
        print(f"Error: File dataset tidak lengkap ({len(files_1340)}/1340). Jalankan generate_dataset.py dahulu.")
        sys.exit(1)

    # Nentuin Baseline Serial T1 untuk ukuran data yang diuji
    print("\n[1/3] Menghitung Baseline Serial (T1) untuk perhitungan Speedup & Efisiensi...")
    data_sizes = [670, 1340]
    t1_dict = {}
    for sz in data_sizes:
        sub_files = get_dataset_files(sz)
        times = []
        for _ in range(2):
            t_dur, _ = run_serial_baseline(sub_files)
            times.append(t_dur)
        avg_t1 = sum(times) / len(times)
        t1_dict[sz] = avg_t1
        print(f"  > Baseline Serial {sz} data: {avg_t1:.4f} detik")

    # 5 Konfigurasi Pengujian Sesuai Ketentuan Soal:
    # - No 1: Konfigurasi utama (4 Thread, 3 Process, 1340 Data)
    # - No 2 & 3: Variasi Jumlah Thread (2 dan 8 Thread)
    # - No 4: Variasi Jumlah Process (1 Process)
    # - No 5: Variasi Jumlah Data / File (670 Data / 50%)
    test_configs = [
        {"no": 1, "thread": 4, "process": 3, "data": 1340, "desc": "Konfigurasi Utama Sesuai Parameter NIM"},
        {"no": 2, "thread": 2, "process": 3, "data": 1340, "desc": "Variasi Thread Rendah (2 Thread, 3 Process)"},
        {"no": 3, "thread": 8, "process": 3, "data": 1340, "desc": "Variasi Thread Tinggi (8 Thread, 3 Process)"},
        {"no": 4, "thread": 4, "process": 1, "data": 1340, "desc": "Variasi Process Tunggal (4 Thread, 1 Process)"},
        {"no": 5, "thread": 4, "process": 3, "data": 670,  "desc": "Variasi Skala Data Separuh (670 File Teks)"},
    ]

    print("\n[2/3] Mengeksekusi 5 Konfigurasi Uji (Rata-rata 3 pengulangan per uji)...")
    results = []

    for cfg in test_configs:
        c_no = cfg["no"]
        t_count = cfg["thread"]
        p_count = cfg["process"]
        d_count = cfg["data"]
        sub_files = get_dataset_files(d_count)

        run_durations = []
        for _ in range(3):
            t_start = time.perf_counter()
            _ = run_hybrid_file_analyzer(sub_files, t_count, p_count)
            t_end = time.perf_counter()
            run_durations.append(t_end - t_start)

        avg_time = sum(run_durations) / len(run_durations)
        t1 = t1_dict[d_count]
        speedup = t1 / avg_time if avg_time > 0 else 1.0
        eff = (speedup / p_count) * 100.0 if p_count > 0 else 100.0

        res_entry = {
            "No": c_no,
            "Jumlah Thread": t_count,
            "Jumlah Process": p_count,
            "Data/Task": d_count,
            "Waktu (s)": round(avg_time, 4),
            "Speedup": round(speedup, 2),
            "Efisiensi (%)": round(eff, 2)
        }
        results.append(res_entry)
        print(f"  Konfigurasi {c_no:02d}: T={t_count}, P={p_count}, Data={d_count} | Waktu: {avg_time:.4f}s | Speedup: {speedup:.2f}x | Efisiensi: {eff:.1f}%")

    # Simpan Hasil ke CSV
    csv_file = os.path.join(OUTPUT_DIR, "tabel_hasil_eksperimen.csv")
    fieldnames = ["No", "Jumlah Thread", "Jumlah Process", "Data/Task", "Waktu (s)", "Speedup", "Efisiensi (%)"]
    try:
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"\nTabel CSV berhasil disimpan di: {csv_file}")
    except PermissionError:
        alt_csv = os.path.join(OUTPUT_DIR, "tabel_hasil_eksperimen_baru.csv")
        with open(alt_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"\n[PERHATIAN] File '{csv_file}' sedang dibuka di Microsoft Excel!")
        print(f"Data tabel tetap berhasil disimpan ke: '{alt_csv}' (Silakan tutup Excel untuk menimpa file utama).")

    # Cetak Tabel
    print("\n" + "=" * 90)
    print("TABEL HASIL EKSPERIMEN HYBRID COMPUTING (SESUAI FORMAT SOAL)")
    print("=" * 90)
    print(f"{'No':<4} | {'Jumlah Thread':<14} | {'Jumlah Process':<15} | {'Data/Task':<10} | {'Waktu (s)':<10} | {'Speedup':<8} | {'Efisiensi (%)':<14}")
    print("-" * 90)
    for r in results:
        is_nim = " (UTAMA)" if r["No"] == 1 else ""
        print(f"{r['No']:<4} | {r['Jumlah Thread']:<14} | {r['Jumlah Process']:<15} | {r['Data/Task']:<10} | {r['Waktu (s)']:<10.4f} | {r['Speedup']:<8.2f} | {r['Efisiensi (%)']:<14.2f}{is_nim}")
    print("=" * 90)

    # Buat dan Perbarui Visualisasi 3 Grafik Otomatis
    print("\n[3/3] Menghasilkan & Memperbarui 3 Grafik Perbandingan...")
    generate_charts(results)
    print(f"\nSemua file hasil eksperimen dan grafik telah otomatis diperbarui di: '{OUTPUT_DIR}'")


def generate_charts(results):
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

    # GRAFIK 1: Waktu vs Jumlah Thread (Data=1340, Process=3)
    # Konfigurasi No 2 (T=2), No 1 (T=4), No 3 (T=8)
    plt.figure(figsize=(8, 5))
    thread_cfgs = [r for r in results if r["Jumlah Process"] == 3 and r["Data/Task"] == 1340]
    thread_cfgs = sorted(thread_cfgs, key=lambda x: x["Jumlah Thread"])
    t_vals = [r["Jumlah Thread"] for r in thread_cfgs]
    t_times = [r["Waktu (s)"] for r in thread_cfgs]

    plt.plot(t_vals, t_times, marker='o', linewidth=2.5, markersize=8, color='#1f77b4', label='Process = 3, Data = 1340')
    for x, y in zip(t_vals, t_times):
        label_text = f"{y:.4f}s" + ("\n(NIM)" if x == 4 else "")
        plt.annotate(label_text, (x, y), textcoords="offset points", xytext=(0, 10), ha='center', fontweight='bold')

    plt.title("Grafik Perbandingan: Waktu Eksekusi vs Jumlah Thread (I/O Concurrency)", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Jumlah Thread", fontsize=11)
    plt.ylabel("Waktu Eksekusi (detik)", fontsize=11)
    plt.xticks(t_vals)
    plt.ylim(0, max(t_times) * 1.35)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(frameon=True)
    plt.tight_layout()
    chart1_path = os.path.join(OUTPUT_DIR, "grafik_waktu_vs_jumlah_thread.png")
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f"  > Grafik 1 tersimpan/terupdate: {chart1_path}")

    # GRAFIK 2: Waktu vs Jumlah Process (Data=1340, Thread=4)
    # Konfigurasi No 4 (P=1) dan No 1 (P=3)
    plt.figure(figsize=(8, 5))
    proc_cfgs = [r for r in results if r["Jumlah Thread"] == 4 and r["Data/Task"] == 1340]
    proc_cfgs = sorted(proc_cfgs, key=lambda x: x["Jumlah Process"])
    p_vals = [r["Jumlah Process"] for r in proc_cfgs]
    p_times = [r["Waktu (s)"] for r in proc_cfgs]

    plt.plot(p_vals, p_times, marker='s', linewidth=2.5, markersize=8, color='#ff7f0e', label='Thread = 4, Data = 1340')
    for x, y in zip(p_vals, p_times):
        label_text = f"{y:.4f}s" + ("\n(NIM)" if x == 3 else "")
        plt.annotate(label_text, (x, y), textcoords="offset points", xytext=(0, 10), ha='center', fontweight='bold')

    plt.title("Grafik Perbandingan: Waktu Eksekusi vs Jumlah Process (CPU Multiprocessing)", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Jumlah Process", fontsize=11)
    plt.ylabel("Waktu Eksekusi (detik)", fontsize=11)
    plt.xticks(p_vals)
    plt.ylim(0, max(p_times) * 1.35)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(frameon=True)
    plt.tight_layout()
    chart2_path = os.path.join(OUTPUT_DIR, "grafik_waktu_vs_jumlah_process.png")
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f"  > Grafik 2 tersimpan/terupdate: {chart2_path}")

    # GRAFIK 3: Speedup vs Konfigurasi
    # Bar chart perbandingan Speedup untuk seluruh 5 konfigurasi
    plt.figure(figsize=(10, 5.5))
    cfg_labels = [
        f"Cfg {r['No']} (Utama NIM)\n(T{r['Jumlah Thread']}/P{r['Jumlah Process']}/D{r['Data/Task']})" if r["No"] == 1
        else f"Cfg {r['No']}\n(T{r['Jumlah Thread']}/P{r['Jumlah Process']}/D{r['Data/Task']})"
        for r in results
    ]
    speedups = [r["Speedup"] for r in results]

    # No 1 (Utama NIM) diberi warna hijau terang, lainnya biru
    colors = ['#2ca02c' if r["No"] == 1 else '#1f77b4' for r in results]

    bars = plt.bar(cfg_labels, speedups, color=colors, width=0.55, edgecolor='black', linewidth=0.8)
    for bar in bars:
        h = bar.get_height()
        plt.annotate(f"{h:.2f}x", (bar.get_x() + bar.get_width() / 2, h),
                     textcoords="offset points", xytext=(0, 5), ha='center', fontweight='bold', fontsize=10)

    plt.axhline(1.0, color='red', linestyle='--', linewidth=1.2, label='Baseline Serial (1.0x)')
    plt.title("Grafik Perbandingan: Speedup vs Konfigurasi Pengujian (5 Variasi)", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Nomor Konfigurasi (Thread / Process / Data)", fontsize=11)
    plt.ylabel("Speedup ($S = T_{serial} / T_{hybrid}$)", fontsize=11)
    plt.ylim(0, max(max(speedups) * 1.35, 1.3))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(frameon=True)
    plt.tight_layout()
    chart3_path = os.path.join(OUTPUT_DIR, "grafik_speedup_vs_konfigurasi.png")
    plt.savefig(chart3_path, dpi=300)
    plt.close()
    print(f"  > Grafik 3 tersimpan/terupdate: {chart3_path}")


if __name__ == "__main__":
    run_benchmark()
