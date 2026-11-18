# Inventaris Lab — Aplikasi CLI Pengolahan Data Inventaris Laboratorium

UTS Pemrograman Dasar (TK091) — Universitas AMIKOM Yogyakarta, TA 2026/2027
Dosen: Muhammad Koprawi, S.Kom., M.Eng
Mahasiswa: Ananda Nur Rohman (NIM 25.83.1196) — S1 Teknik Komputer

## Deskripsi
Aplikasi command line untuk membaca data inventaris lab komputer (CSV/JSON), memvalidasi,
membuang duplikat, mencari/memfilter, merekap per kategori, lalu menyimpan hasil ke file.

## Persyaratan & Dependency
- Python 3.9+ (diuji pada 3.12)
- **Hanya standard library** (`csv`, `json`, `argparse`, `os`, `sys`, `unittest`, `tempfile`).
  Tidak perlu `pip install`. `requirements.txt` sengaja kosong.

## Struktur Program
```
inventaris-lab/
├── main.py                  # entry point
├── inventaris/              # package buatan sendiri
│   ├── __init__.py          # dokumentasi alur dependensi
│   ├── exceptions.py        # exception khusus
│   ├── validators.py        # validasi & normalisasi 1 baris
│   ├── io_utils.py          # baca/tulis CSV & JSON
│   ├── analysis.py          # cari, filter, grup, rekap, dedup
│   ├── report.py            # format teks keluaran
│   └── cli.py               # argparse + menu interaktif
├── data/input/              # inventaris.csv, inventaris.json, header_salah.csv, rusak.json
├── data/output/             # hasil: laporan_rekap.json, inventaris_bersih.csv, stok_menipis.csv
├── tests/test_app.py        # 17 unit test
└── docs/                    # debug_demo.py, log_*.txt
```
Dependensi: `main -> cli -> {io_utils, analysis, report, validators}`;
`io_utils -> validators -> exceptions`. Tidak ada import melingkar.

## Cara Menjalankan
```bash
# 1. Mode batch (otomatis, hasil disimpan ke data/output/)
python main.py --batch

# 2. Mode menu interaktif
python main.py

# 3. Input/Output kustom (CSV atau JSON)
python main.py -i data/input/inventaris.json -o hasil --batch --batas-stok 3

# 4. Unit test
python -m unittest -v

# 5. Demo debugging
python docs/debug_demo.py
```
Exit code: `0` sukses, `2` file tidak ditemukan, `3` format data salah, `1` error I/O lain.

## Menambah Barang Baru
Jalankan `python main.py`, pilih **menu 7 (Tambah barang baru)**, isi 7 field (kode, nama, kategori,
jumlah, kondisi, lokasi, harga). Data divalidasi (angka >= 0, kondisi valid) dan kode yang sudah ada
ditolak. Setelah berhasil, program menawarkan menyimpan ke file input (.csv/.json); **menu 8** menyimpan
kapan saja, dan saat keluar (menu 0) program mengingatkan bila ada perubahan belum disimpan.
Catatan: saat menyimpan, baris invalid/duplikat yang sudah dibuang tidak ikut tertulis (file jadi bersih).

## Format Data
Kolom wajib: `kode_barang, nama_barang, kategori, jumlah, kondisi, lokasi, harga_satuan`.
`kondisi` ∈ {baik, rusak ringan, rusak berat}; `jumlah` dan `harga_satuan` bilangan bulat ≥ 0.
Baris invalid dilewati dan dilaporkan; kode barang duplikat dibuang (yang pertama dipertahankan).

## Penanganan Error (ringkas)
File tidak ada, header kurang, JSON rusak, ekstensi tak didukung, baris invalid, data kosong
(rata-rata/rekap aman), input menu salah (diulang), Ctrl-C/Ctrl-D (keluar rapi).

## Referensi, Library, dan Bantuan AI
- Dokumentasi Python: docs.python.org (modul csv, json, argparse, unittest).
- Library: hanya standard library Python.
- **Bantuan AI:** kerangka kode, data contoh, unit test, dan draf dokumentasi dibuat dengan
  bantuan Claude (Anthropic). Seluruh kode dijalankan, diuji, dan dipelajari oleh mahasiswa.

## Link Demo
URL repository: **(isi URL GitHub di sini)**
