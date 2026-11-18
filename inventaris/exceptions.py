"""Exception khusus aplikasi agar penanganan error spesifik dan jelas."""


class InventarisError(Exception):
    """Kelas dasar untuk semua error aplikasi ini."""


class DataFormatError(InventarisError):
    """Dilempar saat isi file / baris data tidak sesuai format."""


class ValidationError(InventarisError):
    """Dilempar saat satu nilai field gagal divalidasi."""
