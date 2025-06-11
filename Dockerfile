# Tahap 1: Pilih base image resmi Python yang ringan.
# python:3.9-slim adalah pilihan yang bagus karena ukurannya kecil dan stabil.
FROM python:3.9-slim

# Menetapkan variabel lingkungan untuk Python agar tidak membuat file .pyc
# dan berjalan dalam mode unbuffered, yang baik untuk logging di container.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Tahap 2: Buat dan tetapkan direktori kerja di dalam container.
WORKDIR /app

# Tahap 3: Salin file requirements.txt dan install dependensi.
# Langkah ini dipisah agar Docker dapat menggunakan cache layer. Jika kode Anda berubah
# tetapi requirements.txt tidak, Docker tidak perlu menginstall ulang semua library.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tahap 4: Salin seluruh kode proyek Anda (app.py, folder model/, dll.) ke direktori kerja.
COPY . .

# Tahap 5: Perintah untuk menjalankan aplikasi saat container dimulai.
# Platform hosting (seperti Render/Cloud Run) akan menyediakan variabel $PORT.
# Kita menggunakan Gunicorn sebagai server produksi, bukan server development Flask.
#
# Penjelasan Perintah:
# - gunicorn: Server WSGI untuk produksi.
# - --bind 0.0.0.0:$PORT: Mengikat server ke semua antarmuka jaringan pada port yang disediakan oleh platform.
# - --workers 1: Jumlah proses worker. Untuk free-tier dengan CPU terbatas, 1 sudah cukup.
# - --threads 8: Jumlah thread per worker untuk menangani beberapa request secara bersamaan.
# - --timeout 0: Menonaktifkan timeout. SANGAT PENTING untuk model ML, karena request pertama
#   atau request yang kompleks bisa memakan waktu lebih dari 30 detik (default timeout).
# - app:app: Menjalankan objek 'app' dari file 'app.py'.
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "1", "--threads", "8", "--timeout", "0", "app:app"]