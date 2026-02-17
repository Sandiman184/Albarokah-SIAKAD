# Panduan Pengujian (Testing Guide)

Proyek ini menggunakan `pytest` untuk pengujian otomatis.

## Persyaratan
Pastikan Anda telah menginstal dependensi pengembangan:
```bash
pip install pytest pytest-flask pytest-cov
```

## Menjalankan Test
Untuk menjalankan seluruh rangkaian tes pada aplikasi `siakad_app`:

1. Masuk ke direktori aplikasi:
   ```bash
   cd siakad_app
   ```

2. Jalankan perintah pytest:
   ```bash
   pytest
   ```

## Struktur Test
- `tests/conftest.py`: Konfigurasi fixture (database, client).
- `tests/unit/`: Pengujian unit (model, helper).
- `tests/integration/`: Pengujian integrasi (route, flow autentikasi).

## Cakupan Test (Coverage)
Untuk melihat laporan cakupan kode:
```bash
pytest --cov=app tests/
```
