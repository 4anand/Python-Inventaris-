"""Membaca & menulis file CSV/JSON. Hanya mengurus I/O, bukan analisis."""

import csv
import json
import os

from .exceptions import DataFormatError, ValidationError
from .validators import KOLOM_WAJIB, validate_record


def read_csv(path):
    """Baca CSV inventaris dan validasi tiap baris.

    Baris yang tidak valid TIDAK menghentikan program; baris itu dicatat
    di daftar error agar sisa data tetap diproses.

    Args:
        path (str): lokasi file CSV.
    Returns:
        tuple[list[dict], list[str]]: (record valid, pesan error per baris).
    Raises:
        FileNotFoundError: bila file tidak ada.
        DataFormatError: bila header tidak lengkap / file kosong.
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise DataFormatError(f"{path}: file kosong")
        kurang = [k for k in KOLOM_WAJIB if k not in reader.fieldnames]
        if kurang:
            raise DataFormatError(f"{path}: header kurang kolom {kurang}")
        records, errors = [], []
        for no, row in enumerate(reader, start=2):  # baris 1 = header
            try:
                records.append(validate_record(row))
            except ValidationError as e:
                errors.append(f"baris {no}: {e}")
    return records, errors


def read_json(path):
    """Baca JSON berisi list objek inventaris (format sama dengan CSV).

    Returns / Raises: sama seperti `read_csv`; JSON rusak -> DataFormatError.
    """
    with open(path, encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise DataFormatError(f"{path}: JSON tidak valid ({e})")
    if not isinstance(data, list):
        raise DataFormatError(f"{path}: isi JSON harus berupa list")
    records, errors = [], []
    for no, row in enumerate(data, start=1):
        try:
            records.append(validate_record(row if isinstance(row, dict) else {}))
        except ValidationError as e:
            errors.append(f"item {no}: {e}")
    return records, errors


def load_data(path):
    """Pilih pembaca berdasarkan ekstensi file (.csv / .json).

    Raises:
        DataFormatError: ekstensi tidak didukung.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return read_csv(path)
    if ext == ".json":
        return read_json(path)
    raise DataFormatError(f"ekstensi '{ext}' tidak didukung (gunakan .csv/.json)")


def write_json(path, data):
    """Simpan `data` (dict/list) ke JSON; folder tujuan dibuat bila belum ada."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def write_csv(path, rows, fieldnames):
    """Simpan list dict `rows` ke CSV dengan kolom `fieldnames`."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_data(path, records):
    """Simpan seluruh record ke `path` (.csv/.json) sesuai ekstensi.

    Raises:
        DataFormatError: ekstensi tidak didukung.
        OSError: gagal menulis file.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        write_csv(path, records, list(KOLOM_WAJIB))
    elif ext == ".json":
        write_json(path, records)
    else:
        raise DataFormatError(f"ekstensi '{ext}' tidak didukung (gunakan .csv/.json)")
