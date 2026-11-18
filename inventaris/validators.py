"""Validasi & normalisasi satu baris data (defensive programming)."""

from .exceptions import ValidationError

KOLOM_WAJIB = ("kode_barang", "nama_barang", "kategori", "jumlah",
               "kondisi", "lokasi", "harga_satuan")
KONDISI_VALID = {"baik", "rusak ringan", "rusak berat"}


def parse_int(nilai, nama_field, minimum=0):
    """Ubah `nilai` menjadi int >= minimum.

    Args:
        nilai: nilai mentah (str/int) dari file atau input pengguna.
        nama_field (str): nama field, dipakai untuk pesan error.
        minimum (int): batas bawah yang diizinkan.
    Returns:
        int: bilangan bulat hasil konversi.
    Raises:
        ValidationError: bila bukan angka bulat atau di bawah minimum.
    """
    try:
        hasil = int(str(nilai).strip())
    except (TypeError, ValueError):
        raise ValidationError(f"'{nama_field}' harus bilangan bulat, dapat: {nilai!r}")
    if hasil < minimum:
        raise ValidationError(f"'{nama_field}' minimal {minimum}, dapat: {hasil}")
    return hasil


def validate_record(row):
    """Validasi dan normalisasi satu baris (dict) menjadi record bersih.

    Args:
        row (dict): baris mentah dengan kunci sesuai KOLOM_WAJIB.
    Returns:
        dict: record dengan tipe data benar (jumlah:int, harga_satuan:int,
        teks di-strip, kondisi lowercase, kode uppercase).
    Raises:
        ValidationError: bila kolom hilang/kosong, kondisi tak dikenal,
        atau angka tidak valid.
    """
    hilang = [k for k in KOLOM_WAJIB if k not in row or row[k] is None]
    if hilang:
        raise ValidationError(f"kolom hilang: {', '.join(hilang)}")

    record = {k: str(row[k]).strip() for k in KOLOM_WAJIB}
    for k in ("kode_barang", "nama_barang", "kategori", "lokasi"):
        if not record[k]:
            raise ValidationError(f"'{k}' tidak boleh kosong")

    record["kode_barang"] = record["kode_barang"].upper()
    record["kondisi"] = record["kondisi"].lower()
    if record["kondisi"] not in KONDISI_VALID:
        raise ValidationError(
            f"kondisi '{record['kondisi']}' tidak valid, pilih: {sorted(KONDISI_VALID)}")

    record["jumlah"] = parse_int(record["jumlah"], "jumlah")
    record["harga_satuan"] = parse_int(record["harga_satuan"], "harga_satuan")
    return record
