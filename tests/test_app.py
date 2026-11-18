"""Unit test (unittest, standard library). Jalankan: python -m unittest -v"""
import json
import os
import tempfile
import unittest

from inventaris import analysis, io_utils
from inventaris.exceptions import DataFormatError, ValidationError
from inventaris.validators import validate_record

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "input")


def rec(kode="A-1", nama="Barang", kat="K", jml=1, kond="baik", lok="L", harga=100):
    return {"kode_barang": kode, "nama_barang": nama, "kategori": kat,
            "jumlah": jml, "kondisi": kond, "lokasi": lok, "harga_satuan": harga}


class TestAnalysis(unittest.TestCase):
    def test_dedup(self):
        unik, dup = analysis.remove_duplicates([rec("A"), rec("B"), rec("A")])
        self.assertEqual(len(unik), 2)
        self.assertEqual(dup, {"A"})

    def test_search_case_insensitive(self):
        data = [rec(nama="Monitor LED"), rec("B", nama="Mouse")]
        self.assertEqual(len(analysis.search_by_name(data, "mon")), 1)
        self.assertEqual(analysis.search_by_name(data, "   "), [])

    def test_recap(self):
        data = [rec("A", kat="X", jml=2, harga=10), rec("B", kat="X", jml=3, harga=5)]
        self.assertEqual(analysis.recap_by_kategori(data),
                         {"X": {"jenis": 2, "total_unit": 5, "nilai_aset": 35}})

    def test_edge_data_kosong(self):
        self.assertEqual(analysis.recap_by_kategori([]), {})
        self.assertEqual(analysis.rata_rata_harga([]), 0.0)
        self.assertEqual(analysis.total_nilai_aset([]), 0)

    def test_edge_stok_nol(self):
        self.assertEqual(len(analysis.low_stock([rec(jml=0), rec("B", jml=9)], 2)), 1)


class TestTambah(unittest.TestCase):
    def test_tambah_berhasil_tanpa_ubah_list_asal(self):
        asal = [rec("A")]
        baru = analysis.add_record(asal, rec("B"))
        self.assertEqual([r["kode_barang"] for r in baru], ["A", "B"])
        self.assertEqual(len(asal), 1)

    def test_tambah_kode_ganda_ditolak(self):
        with self.assertRaises(ValidationError):
            analysis.add_record([rec("A")], rec("A"))

    def test_simpan_lalu_baca_kembali(self):
        with tempfile.TemporaryDirectory() as d:
            for nama in ("x.csv", "x.json"):
                p = os.path.join(d, nama)
                io_utils.save_data(p, [rec("A-1", jml=3)])
                records, errors = io_utils.load_data(p)
                self.assertEqual((len(records), errors), (1, []))
                self.assertEqual(records[0]["jumlah"], 3)

    def test_simpan_ekstensi_salah(self):
        with self.assertRaises(DataFormatError):
            io_utils.save_data("x.txt", [])


class TestValidation(unittest.TestCase):
    def test_normalisasi(self):
        r = validate_record({**rec(kode=" pc-1 ", kond="BAIK"), "jumlah": " 5 "})
        self.assertEqual((r["kode_barang"], r["kondisi"], r["jumlah"]), ("PC-1", "baik", 5))

    def test_input_salah(self):
        for bad in ({"jumlah": "abc"}, {"jumlah": -1}, {"kondisi": "hancur"}, {"kode_barang": ""}):
            with self.assertRaises(ValidationError):
                validate_record({**rec(), **bad})

    def test_kolom_hilang(self):
        with self.assertRaises(ValidationError):
            validate_record({"kode_barang": "A"})


class TestIO(unittest.TestCase):
    def test_csv_contoh(self):
        records, errors = io_utils.read_csv(os.path.join(BASE, "inventaris.csv"))
        self.assertEqual(len(records), 12)   # 11 unik + 1 duplikat (belum dibuang)
        self.assertEqual(len(errors), 4)

    def test_file_tidak_ada(self):
        with self.assertRaises(FileNotFoundError):
            io_utils.load_data("tidak_ada.csv")

    def test_header_salah_dan_json_rusak(self):
        with self.assertRaises(DataFormatError):
            io_utils.load_data(os.path.join(BASE, "header_salah.csv"))
        with self.assertRaises(DataFormatError):
            io_utils.load_data(os.path.join(BASE, "rusak.json"))

    def test_ekstensi_tak_didukung(self):
        with self.assertRaises(DataFormatError):
            io_utils.load_data("data.xml")

    def test_roundtrip_json(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "sub", "x.json")
            io_utils.write_json(p, {"a": 1})
            with open(p, encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"a": 1})


if __name__ == "__main__":
    unittest.main()
