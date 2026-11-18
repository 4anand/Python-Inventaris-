"""Logika bisnis murni: pencarian, filter, pengelompokan, rekap, dedup.

Semua function bersifat murni (tidak mencetak / membaca file) sehingga
mudah diuji.
"""

from .exceptions import ValidationError


def remove_duplicates(records):
    """Hapus record yang kode_barang-nya sudah muncul (simpan yang pertama).

    Memakai `set` untuk mencatat kode yang sudah terlihat (lookup O(1)).

    Args:
        records (list[dict]): data bersih.
    Returns:
        tuple[list[dict], set[str]]: (data unik, himpunan kode yang duplikat).
    """
    terlihat, duplikat, unik = set(), set(), []
    for r in records:
        kode = r["kode_barang"]
        if kode in terlihat:
            duplikat.add(kode)
        else:
            terlihat.add(kode)
            unik.append(r)
    return unik, duplikat


def search_by_name(records, kata_kunci):
    """Cari barang yang namanya memuat `kata_kunci` (case-insensitive)."""
    kunci = kata_kunci.strip().lower()
    if not kunci:
        return []
    return [r for r in records if kunci in r["nama_barang"].lower()]


def filter_records(records, kondisi=None, kategori=None, lokasi=None):
    """Filter gabungan; parameter None berarti 'tidak difilter'."""
    hasil = records
    if kondisi:
        hasil = [r for r in hasil if r["kondisi"] == kondisi.lower()]
    if kategori:
        hasil = [r for r in hasil if r["kategori"].lower() == kategori.lower()]
    if lokasi:
        hasil = [r for r in hasil if r["lokasi"].lower() == lokasi.lower()]
    return hasil


def group_by_kategori(records):
    """Kelompokkan record per kategori -> dict {kategori: [record, ...]}."""
    grup = {}
    for r in records:
        grup.setdefault(r["kategori"], []).append(r)
    return grup


def nilai_aset(record):
    """Nilai aset satu record = jumlah x harga_satuan."""
    return record["jumlah"] * record["harga_satuan"]


def recap_by_kategori(records):
    """Rekap per kategori: jumlah jenis, total unit, total nilai aset.

    Returns:
        dict: {kategori: {"jenis": int, "total_unit": int, "nilai_aset": int}}
        (dict kosong bila records kosong -> edge case aman).
    """
    return {
        kat: {
            "jenis": len(items),
            "total_unit": sum(i["jumlah"] for i in items),
            "nilai_aset": sum(nilai_aset(i) for i in items),
        }
        for kat, items in group_by_kategori(records).items()
    }


def unique_locations(records):
    """Himpunan lokasi unik (set comprehension)."""
    return {r["lokasi"] for r in records}


def low_stock(records, batas=2):
    """Barang dengan jumlah <= batas (termasuk 0 = stok habis)."""
    return [r for r in records if r["jumlah"] <= batas]


def total_nilai_aset(records):
    """Total nilai seluruh aset; 0 bila data kosong."""
    return sum(nilai_aset(r) for r in records)


def rata_rata_harga(records):
    """Rata-rata harga satuan; 0.0 bila data kosong (cegah ZeroDivisionError)."""
    if not records:
        return 0.0
    return sum(r["harga_satuan"] for r in records) / len(records)


def add_record(records, record):
    """Tambah satu record baru dan kembalikan list baru (list asal tidak diubah).

    Args:
        records (list[dict]): data saat ini.
        record (dict): record yang sudah lolos `validate_record`.
    Returns:
        list[dict]: data lama + record baru di akhir.
    Raises:
        ValidationError: bila kode_barang sudah ada (cek memakai set).
    """
    ada = {r["kode_barang"] for r in records}
    if record["kode_barang"] in ada:
        raise ValidationError(f"kode '{record['kode_barang']}' sudah ada")
    return records + [record]
