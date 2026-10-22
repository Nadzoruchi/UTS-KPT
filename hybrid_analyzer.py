# Program Utama Proyek Hybrid Computing - Parallel File Analyzer

#==============================================
# Nama  : Muhammad Zaki Zaidan Binawan
# NPM   : 247006111134
# Kelas : E
#==============================================


import os
import sys
import time
import math
import re
import hashlib
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


# Hitungan Parameter:
# - Dua digit terakhir (34) mod 4 + 2 = 2 + 2 = 4
DEFAULT_THREADS = (34 % 4) + 2

# - Dua digit tengah (61) mod 3 + 2 = 1 + 2 = 3
DEFAULT_PROCESSES = (61 % 3) + 2

# - Tiga digit terakhir (134) * 10 = 1340
DEFAULT_DATA_COUNT = 134 * 10

DATASET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")


# TUGAS KOMPUTASI CPU-BOUND (Dijalankan oleh ProcessPoolExecutor)
def cpu_task_analyze_chunk(file_data_list):
    """
    Fungsi CPU-bound untuk memproses sekumpulan teks file.
    Dijalankan di tingkat prosesor terpisah agar terbebas dari GIL Python.
    """
    vowel_pattern = re.compile(r'[aeiouAEIOU]')
    consonant_pattern = re.compile(r'[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]')
    digit_pattern = re.compile(r'[0-9]')
    symbol_pattern = re.compile(r'[^a-zA-Z0-9\s]')
    word_pattern = re.compile(r'\b\w+\b')

    chunk_total_words = 0
    chunk_total_vowels = 0
    chunk_total_consonants = 0
    chunk_total_digits = 0
    chunk_total_symbols = 0
    chunk_hash_checksum = 0

    for filename, content in file_data_list:
        words = word_pattern.findall(content)
        chunk_total_words += len(words)
        chunk_total_vowels += len(vowel_pattern.findall(content))
        chunk_total_consonants += len(consonant_pattern.findall(content))
        chunk_total_digits += len(digit_pattern.findall(content))
        chunk_total_symbols += len(symbol_pattern.findall(content))

        # Komputasi hashing berulang untuk mensimulasikan intensitas CPU-bound yang terukur
        # Menghitung hash SHA-256 integritas konten
        h = hashlib.sha256(content.encode('utf-8')).hexdigest()
        chunk_hash_checksum += int(h[:4], 16)

    return {
        "files_count": len(file_data_list),
        "total_words": chunk_total_words,
        "total_vowels": chunk_total_vowels,
        "total_consonants": chunk_total_consonants,
        "total_digits": chunk_total_digits,
        "total_symbols": chunk_total_symbols,
        "hash_checksum": chunk_hash_checksum
    }


# TUGAS I/O-BOUND (Dijalankan oleh ThreadPoolExecutor)
def io_task_read_file(filepath):
    """
    Fungsi I/O-bound untuk membaca konten file dari media penyimpanan (disk).
    Python melepaskan GIL saat operasi I/O, sehingga Thread sangat efisien.
    """
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return filename, content


# ARSITEKTUR HYBRID PIPELINE
def run_hybrid_file_analyzer(file_paths, num_threads, num_processes):
    """
    Menjalankan analisis dengan paradigma Hybrid:
    1. Lapisan I/O (Thread): Membaca file secara paralel dari disk ke RAM.
    2. Lapisan CPU (ProcessPool): Menganalisis token dan statistik teks secara paralel multi-core.
    """

    # Baca File (I/O-Bound dengan ThreadPool)
    t_io_start = time.perf_counter()
    if num_threads <= 1:
        loaded_files = [io_task_read_file(fp) for fp in file_paths]
    else:
        with ThreadPoolExecutor(max_workers=num_threads) as t_pool:
            loaded_files = list(t_pool.map(io_task_read_file, file_paths))
    t_io_end = time.perf_counter()
    io_duration = t_io_end - t_io_start


    # Bagia Beban (Chunking Data)
    total_files = len(loaded_files)
    effective_processes = max(1, num_processes)
    chunk_size = math.ceil(total_files / effective_processes)
    chunks = [loaded_files[i:i + chunk_size] for i in range(0, total_files, chunk_size)]


    # Proses Komputasi (CPU-Bound dengan ProcessPool)
    t_cpu_start = time.perf_counter()
    if effective_processes <= 1:
        chunk_results = [cpu_task_analyze_chunk(ch) for ch in chunks]
    else:
        with ProcessPoolExecutor(max_workers=effective_processes) as p_pool:
            chunk_results = list(p_pool.map(cpu_task_analyze_chunk, chunks))
    t_cpu_end = time.perf_counter()
    cpu_duration = t_cpu_end - t_cpu_start

    # Agregasi Hasil (Reducer)
    aggregated = {
        "files_count": sum(r["files_count"] for r in chunk_results),
        "total_words": sum(r["total_words"] for r in chunk_results),
        "total_vowels": sum(r["total_vowels"] for r in chunk_results),
        "total_consonants": sum(r["total_consonants"] for r in chunk_results),
        "total_digits": sum(r["total_digits"] for r in chunk_results),
        "total_symbols": sum(r["total_symbols"] for r in chunk_results),
        "hash_checksum": sum(r["hash_checksum"] for r in chunk_results),
        "io_duration": io_duration,
        "cpu_duration": cpu_duration
    }
    return aggregated


def run_serial_baseline(file_paths):
    """
    Menjalankan eksekusi serial murni (1 Thread, 1 Process) sebagai acuan T1.
    """
    t_start = time.perf_counter()
    # Membaca serial
    loaded_files = [io_task_read_file(fp) for fp in file_paths]
    # Analisis serial (1 chunk)
    res = cpu_task_analyze_chunk(loaded_files)
    t_end = time.perf_counter()
    return (t_end - t_start), res


# Program Main utama 
def main():
    threads = DEFAULT_THREADS
    processes = DEFAULT_PROCESSES
    data_count = DEFAULT_DATA_COUNT

    # Izinin passing argumen via CLI jika ada: python hybrid_analyzer.py [threads] [processes] [data_count]
    if len(sys.argv) > 1:
        threads = int(sys.argv[1])
    if len(sys.argv) > 2:
        processes = int(sys.argv[2])
    if len(sys.argv) > 3:
        data_count = int(sys.argv[3])

    # Periksa ketersediaan dataset
    if not os.path.exists(DATASET_DIR):
        print(f"Error: Folder dataset '{DATASET_DIR}' tidak ditemukan.")
        print("Silakan jalankan 'generate_dataset.py' terlebih dahulu.")
        sys.exit(1)

    all_files = sorted([os.path.join(DATASET_DIR, f) for f in os.listdir(DATASET_DIR) if f.endswith(".txt")])
    if len(all_files) < data_count:
        print(f"Peringatan: File yang tersedia ({len(all_files)}) kurang dari permintaan ({data_count}).")
        target_files = all_files
    else:
        target_files = all_files[:data_count]

    actual_data_count = len(target_files)

    # Jalanin pengukuran Serial Baseline untuk mendapatkan T1 (jika belum ada)
    # Agar Speedup dan Efisiensi dihitung secara nyata dan valid
    t_serial_baseline, _ = run_serial_baseline(target_files)

    # Jalanin Mode Hybrid
    t_hybrid_start = time.perf_counter()
    analysis_results = run_hybrid_file_analyzer(target_files, threads, processes)
    t_hybrid_end = time.perf_counter()
    total_time = t_hybrid_end - t_hybrid_start

    # Hitung Metrik Kinerja
    # Speedup S = T_serial / T_hybrid
    speedup = t_serial_baseline / total_time if total_time > 0 else 1.0

    # Total unit worker aktif
    total_workers = processes
    # Efisiensi E = (Speedup / n) * 100%
    efficiency = (speedup / total_workers) * 100.0 if total_workers > 0 else 100.0

    # Throughput (file per detik)
    throughput = actual_data_count / total_time if total_time > 0 else 0.0


    print("\n" + "=" * 72)
    print(f"Hybrid Project by: Muhammad Zaki Zaidan Binawan (247006111134)")
    print(f"Threads: {threads} | Processes: {processes} | Data: {actual_data_count}")
    print(f"Total Time: {total_time:.2f} s | Speedup: {speedup:.2f} | Efficiency: {efficiency:.1f}%")
    print("=" * 72)
    print("Hasil Analisis Karakteristik File Teks:")
    print(f"  - Total File Diproses      : {analysis_results['files_count']:,} file")
    print(f"  - Total Kata Ditemukan     : {analysis_results['total_words']:,} kata")
    print(f"  - Total Huruf Vokal        : {analysis_results['total_vowels']:,}")
    print(f"  - Total Huruf Konsonan     : {analysis_results['total_consonants']:,}")
    print(f"  - Total Angka (Digits)     : {analysis_results['total_digits']:,}")
    print(f"  - Total Simbol & Tanda Baca: {analysis_results['total_symbols']:,}")
    print(f"  - Throughput Pemrosesan    : {throughput:.2f} file/detik")
    print(f"  - Rincian Durasi I/O (Disk): {analysis_results['io_duration']:.4f} detik")
    print(f"  - Rincian Durasi CPU (Anal): {analysis_results['cpu_duration']:.4f} detik")
    print("=" * 72 + "\n")


if __name__ == "__main__":
    main()
