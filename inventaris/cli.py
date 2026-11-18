"""Antarmuka command line: argparse (mode batch) + menu interaktif."""

import argparse
import os
import sys

from . import analysis, report
from .exceptions import DataFormatError, InventarisError
from .io_utils import load_data, save_data, write_csv, write_json
from .validators import KOLOM_WAJIB, parse_int, validate_record

EXIT_OK, EXIT_FILE, EXIT_FORMAT, EXIT_LAIN = 0, 2, 3, 1


def build_parser():
    """Buat parser argumen CLI."""
    p = argparse.ArgumentParser(
        prog="main.py", description="Pengolah inventaris laboratorium komputer")
    p.add_argument("-i", "--input", default=os.path.join("data", "input", "inventaris.csv"),
                   help="file input .csv/.json (default: data/input/inventaris.csv)")
    p.add_argument("-o", "--output-dir", default=os.path.join("data", "output"),
                   help="folder hasil (default: data/output)")
    p.add_argument("--batch", action="store_true",
                   help="jalankan semua analisis otomatis lalu simpan hasil (tanpa menu)")
    p.add_argument("--batas-stok", type=int, default=2,
                   help="batas stok menipis (default: 2)")
    return p


def siapkan_data(path):
    """Muat file, buang duplikat, kembalikan data + laporan masalah.

    Returns:
        tuple: (records_unik, error_baris, kode_duplikat)
    """
    records, errors = load_data(path)
    unik, duplikat = analysis.remove_duplicates(records)
    return unik, errors, duplikat


def buat_laporan(records, batas_stok):
    """Susun dict laporan ringkasan (siap di-JSON-kan)."""
    return {
        "jumlah_jenis_barang": len(records),
        "total_nilai_aset": analysis.total_nilai_aset(records),
        "rata_rata_harga_satuan": round(analysis.rata_rata_harga(records), 2),
        "lokasi": sorted(analysis.unique_locations(records)),
        "rekap_per_kategori": analysis.recap_by_kategori(records),
        "stok_menipis": [r["kode_barang"] for r in analysis.low_stock(records, batas_stok)],
        "kondisi_rusak": [r["kode_barang"] for r in records if r["kondisi"] != "baik"],
    }


def simpan_hasil(records, laporan, batas_stok, folder):
    """Tulis 3 file keluaran ke `folder`; kembalikan daftar path-nya."""
    p_json = os.path.join(folder, "laporan_rekap.json")
    p_bersih = os.path.join(folder, "inventaris_bersih.csv")
    p_stok = os.path.join(folder, "stok_menipis.csv")
    write_json(p_json, laporan)
    write_csv(p_bersih, records, list(KOLOM_WAJIB))
    write_csv(p_stok, analysis.low_stock(records, batas_stok), list(KOLOM_WAJIB))
    return [p_json, p_bersih, p_stok]


def tampilkan_masalah(errors, duplikat):
    """Cetak ringkasan baris invalid & duplikat ke stderr/stdout."""
    for e in errors:
        print(f"[PERINGATAN] {e} -> dilewati", file=sys.stderr)
    if duplikat:
        print(f"[INFO] kode duplikat dibuang: {', '.join(sorted(duplikat))}")


def minta_angka(prompt, default=None):
    """Minta bilangan bulat >= 0; ulangi sampai valid (default dipakai bila kosong)."""
    while True:
        teks = input(prompt).strip()
        if not teks and default is not None:
            return default
        try:
            return parse_int(teks, "input")
        except InventarisError as e:
            print(f"  Input salah: {e}. Coba lagi.")


MENU = """
=== INVENTARIS LAB ===
1. Tampilkan semua barang
2. Cari barang (nama)
3. Filter (kondisi / kategori / lokasi)
4. Rekap per kategori
5. Stok menipis
6. Ringkasan (total aset, rata-rata, lokasi)
7. Tambah barang baru
8. Simpan data ke file
0. Keluar"""

PERTANYAAN_TAMBAH = (
    ("kode_barang", "Kode barang (mis. PC-010): "),
    ("nama_barang", "Nama barang: "),
    ("kategori", "Kategori: "),
    ("jumlah", "Jumlah (angka >= 0): "),
    ("kondisi", "Kondisi (baik/rusak ringan/rusak berat): "),
    ("lokasi", "Lokasi: "),
    ("harga_satuan", "Harga satuan (angka >= 0): "),
)


def tambah_barang(records):
    """Minta data barang baru lewat input, validasi, lalu tambahkan.

    Args:
        records (list[dict]): data saat ini.
    Returns:
        tuple[list[dict], bool]: (data terbaru, True bila berhasil menambah).
        Bila input tidak valid / kode ganda, data dikembalikan apa adanya.
    """
    mentah = {kolom: input(tanya) for kolom, tanya in PERTANYAAN_TAMBAH}
    try:
        baru = validate_record(mentah)
        records = analysis.add_record(records, baru)
    except InventarisError as e:
        print(f"  Gagal menambah: {e}")
        return records, False
    print(f"  Berhasil menambah {baru['kode_barang']} - {baru['nama_barang']}.")
    return records, True


def simpan_perubahan(records, path):
    """Simpan data ke `path`; kembalikan True bila sukses."""
    try:
        save_data(path, records)
    except (OSError, InventarisError) as e:
        print(f"  Gagal menyimpan: {e}")
        return False
    print(f"  Data ({len(records)} barang) tersimpan ke {path}")
    return True


def tanya_ya(prompt):
    """Tanya y/n; True bila jawaban diawali 'y'."""
    return input(prompt).strip().lower().startswith("y")


def jalankan_menu(records, batas_stok, path_data):
    """Loop menu interaktif; berhenti pada '0', Ctrl-D, atau Ctrl-C.

    Args:
        records (list[dict]): data awal.
        batas_stok (int): batas default stok menipis.
        path_data (str): file tujuan penyimpanan (menu 8).
    """
    belum_disimpan = False
    while True:
        print(MENU)
        try:
            pilihan = input("Pilih menu: ").strip()
            if pilihan == "0":
                if belum_disimpan and tanya_ya("Ada perubahan belum disimpan. Simpan sekarang? (y/n): "):
                    simpan_perubahan(records, path_data)
                print("Sampai jumpa.")
                return
            elif pilihan == "1":
                print(report.format_table(records))
            elif pilihan == "2":
                kata = input("Kata kunci nama: ")
                print(report.format_table(analysis.search_by_name(records, kata)))
            elif pilihan == "3":
                kond = input("Kondisi (baik/rusak ringan/rusak berat, kosong=semua): ")
                kat = input("Kategori (kosong=semua): ")
                lok = input("Lokasi (kosong=semua): ")
                print(report.format_table(
                    analysis.filter_records(records, kond or None, kat or None, lok or None)))
            elif pilihan == "4":
                print(report.format_recap(analysis.recap_by_kategori(records)))
            elif pilihan == "5":
                batas = minta_angka(f"Batas stok [{batas_stok}]: ", default=batas_stok)
                print(report.format_table(analysis.low_stock(records, batas)))
            elif pilihan == "6":
                print("Total nilai aset :", report.rupiah(analysis.total_nilai_aset(records)))
                print("Rata-rata harga  :", report.rupiah(round(analysis.rata_rata_harga(records))))
                print("Lokasi           :", ", ".join(sorted(analysis.unique_locations(records))) or "-")
            elif pilihan == "7":
                records, berhasil = tambah_barang(records)
                if berhasil:
                    belum_disimpan = True
                    if tanya_ya(f"Simpan ke {path_data} sekarang? (y/n): "):
                        belum_disimpan = not simpan_perubahan(records, path_data)
            elif pilihan == "8":
                belum_disimpan = not simpan_perubahan(records, path_data)
            else:
                print("Menu tidak dikenal, pilih 0-8.")
        except (EOFError, KeyboardInterrupt):
            print("\nKeluar.")
            return


def main(argv=None):
    """Titik masuk program. Mengembalikan exit code (0 = sukses)."""
    args = build_parser().parse_args(argv)
    try:
        records, errors, duplikat = siapkan_data(args.input)
    except FileNotFoundError:
        print(f"[ERROR] File tidak ditemukan: {args.input}", file=sys.stderr)
        return EXIT_FILE
    except DataFormatError as e:
        print(f"[ERROR] Format data salah: {e}", file=sys.stderr)
        return EXIT_FORMAT
    except OSError as e:
        print(f"[ERROR] Gagal membaca file: {e}", file=sys.stderr)
        return EXIT_LAIN

    tampilkan_masalah(errors, duplikat)
    print(f"Data dimuat: {len(records)} barang valid, {len(errors)} baris ditolak.")

    if args.batch:
        laporan = buat_laporan(records, args.batas_stok)
        try:
            for p in simpan_hasil(records, laporan, args.batas_stok, args.output_dir):
                print("Tersimpan:", p)
        except OSError as e:
            print(f"[ERROR] Gagal menyimpan hasil: {e}", file=sys.stderr)
            return EXIT_LAIN
        print(report.format_recap(laporan["rekap_per_kategori"]))
        return EXIT_OK

    jalankan_menu(records, args.batas_stok, args.input)
    return EXIT_OK
