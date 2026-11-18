"""Pemformatan teks keluaran untuk terminal (tanpa logika bisnis)."""


def rupiah(angka):
    """Format int menjadi 'Rp 1.234.567'."""
    return "Rp " + f"{angka:,}".replace(",", ".")


def format_table(records):
    """Ubah list record menjadi tabel teks rata-kiri.

    Returns:
        str: tabel; pesan 'Tidak ada data.' bila kosong.
    """
    if not records:
        return "Tidak ada data."
    kolom = ["kode_barang", "nama_barang", "kategori", "jumlah", "kondisi", "lokasi"]
    lebar = {k: max(len(k), *(len(str(r[k])) for r in records)) for k in kolom}
    garis = "-+-".join("-" * lebar[k] for k in kolom)
    baris = [" | ".join(k.ljust(lebar[k]) for k in kolom), garis]
    baris += [" | ".join(str(r[k]).ljust(lebar[k]) for k in kolom) for r in records]
    return "\n".join(baris)


def format_recap(recap):
    """Format hasil `recap_by_kategori` menjadi teks."""
    if not recap:
        return "Tidak ada data untuk direkap."
    baris = []
    for kat in sorted(recap):
        d = recap[kat]
        baris.append(f"{kat:<12} jenis={d['jenis']:<3} unit={d['total_unit']:<4} "
                     f"nilai={rupiah(d['nilai_aset'])}")
    return "\n".join(baris)
