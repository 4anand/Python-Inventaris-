"""Demo debugging: reproduksi bug -> traceback -> akar masalah -> perbaikan.

Jalankan: python docs/debug_demo.py
"""
import os
import sys
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from inventaris import analysis


def rata_rata_harga_BUGGY(records):
    """Versi awal (SEBELUM perbaikan): tidak mengecek data kosong."""
    return sum(r["harga_satuan"] for r in records) / len(records)


print("=== 1. Reproduksi bug: filter menghasilkan list kosong ===")
data_kosong = analysis.filter_records([], kondisi="rusak berat")
try:
    rata_rata_harga_BUGGY(data_kosong)
except ZeroDivisionError:
    traceback.print_exc(file=sys.stdout)

print("\n=== 2. Langkah debugging ===")
print("len(records) di baris pembagi =", len(data_kosong), "-> pembagi 0")

print("\n=== 3. Setelah perbaikan (guard 'if not records') ===")
print("rata_rata_harga([]) =", analysis.rata_rata_harga(data_kosong))
