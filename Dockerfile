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
# PERHATIKAN: Pastikan nama file "requirements.txt" sudah benar (dengan 's').
COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt

# Tahap 4: Salin seluruh kode proyek Anda (app.py, folder model/, dll.) ke direktori kerja.
COPY . .

# Tahap 5: Perintah untuk menjalankan aplikasi saat container dimulai.
# Railway, sama seperti Render, akan menyediakan variabel lingkungan $PORT.
# Jadi, kita harus menggunakan perintah yang mengikat ke port dinamis tersebut.
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "1", "--threads", "8", "--timeout", "0", "app:app"]