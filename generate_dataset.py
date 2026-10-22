# Generator Dataset File Teks untuk Ujian Tengah Semester (UTS)

#==============================================
# Nama  : Muhammad Zaki Zaidan Binawan
# NPM   : 247006111134
# Kelas : E
#==============================================


import os
import random

# Parameter Khusus NIM
NIM = "247006111134"
TOTAL_FILES = 1340  # Tiga digit terakhir NIM (134) * 10
DATASET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")

# Kosakata sampel untuk membentuk teks realistis
SAMPLE_WORDS = [
    "komputasi", "paralel", "terdistribusi", "prosesor", "thread", "multiprocessing",
    "kinerja", "algoritma", "arsitektur", "memori", "jaringan", "skalabilitas",
    "sinkronisasi", "throughput", "latency", "optimasi", "eksekusi", "frekuensi",
    "pipeline", "concurrency", "distributed", "system", "cluster", "performance",
    "amdahl", "speedup", "efisiensi", "analisis", "dataset", "workload", "simulasi"
]

SAMPLE_TEMPLATES = [
    "Sistem {word1} modern memerlukan {word2} yang efisien untuk mencapai {word3} optimal.",
    "Dalam lingkungan {word1}, penanganan {word2} dan {word3} sangat krusial bagi sistem.",
    "Peningkatan {word1} berbanding lurus dengan alokasi {word2} pada beban {word3}.",
    "Model {word1} membagi komputasi menjadi beberapa unit {word2} guna mempercepat {word3}.",
    "Evaluasi metrik {word1} menunjukkan bahwa {word2} mampu mereduksi {word3} secara signifikan."
]


def generate_content(rng, num_paragraphs=6):
    paragraphs = []
    for _ in range(num_paragraphs):
        sentences = []
        for _ in range(rng.randint(4, 8)):
            template = rng.choice(SAMPLE_TEMPLATES)
            w1 = rng.choice(SAMPLE_WORDS)
            w2 = rng.choice(SAMPLE_WORDS)
            w3 = rng.choice(SAMPLE_WORDS)
            sentence = template.format(word1=w1, word2=w2, word3=w3)
            # Tambahkan variasi angka dan karakter simbol secara deterministik
            if rng.random() > 0.4:
                num = rng.randint(10, 9999)
                sentence += f" (ID-{num} val: {rng.random():.4f}#@!)"
            sentences.append(sentence)
        paragraphs.append(" ".join(sentences))
    return "\n\n".join(paragraphs)


def main():
    print(f"=== GENERATOR DATASET FILE TEKS ===")
    print(f"NIM: {NIM}")
    print(f"Jumlah file target: {TOTAL_FILES}")
    print(f"Lokasi folder: {DATASET_DIR}")

    # Set random seed sesuai ketentuan soal
    random.seed(int(NIM))

    os.makedirs(DATASET_DIR, exist_ok=True)

    print("Sedang membuat file teks...")
    for i in range(1, TOTAL_FILES + 1):
        filename = f"file_{i:04d}.txt"
        filepath = os.path.join(DATASET_DIR, filename)
        content = generate_content(random, num_paragraphs=random.randint(5, 8))
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        if i % 200 == 0 or i == TOTAL_FILES:
            print(f"Progress: {i}/{TOTAL_FILES} file berhasil dibuat...")

    print(f"Selesai! Berhasil membuat {TOTAL_FILES} file teks di '{DATASET_DIR}'.")


if __name__ == "__main__":
    main()
