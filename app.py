# app.py

import os
import torch
from flask import Flask, request, jsonify
# Kita akan menggunakan T5Tokenizer secara spesifik karena cocok untuk SentencePiece
from transformers import T5Tokenizer, AutoModelForSeq2SeqLM

# --- 1. Inisialisasi Aplikasi Flask ---
app = Flask(__name__)

# --- 2. Muat Model dan Tokenizer (Hanya sekali saat aplikasi dimulai) ---

# Ganti nama file .pt Anda menjadi 'model.pt' untuk kemudahan,
# atau sesuaikan path di bawah ini.
MODEL_PATH = os.path.join('model', 'model.pt')
# File .model adalah file utama untuk tokenizer SentencePiece
TOKENIZER_FILE = os.path.join('model', 'indo_minang_bpe.model')

# Ganti 't5-small' dengan nama model dasar yang Anda gunakan untuk fine-tuning
# Ini penting untuk memuat ARSITEKTUR yang benar sebelum menimpa bobotnya.
BASE_MODEL_NAME = "t5-small"

try:
    # Muat tokenizer SentencePiece dari file .model
    tokenizer = T5Tokenizer(vocab_file=TOKENIZER_FILE)

    # Muat arsitektur model dari base model
    model = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL_NAME)

    # Muat bobot (weights) yang sudah Anda latih dari file .pt
    model.load_state_dict(torch.load(
        MODEL_PATH, map_location=torch.device('cpu')))

    # Set model ke mode evaluasi (penting untuk inferensi)
    model.eval()
    print(">>> Model dan Tokenizer berhasil dimuat.")

except Exception as e:
    print(f"Error memuat model atau tokenizer: {e}")
    model = None
    tokenizer = None

# --- 3. Buat Fungsi Logika Translasi ---


def terjemahkan(teks_indonesia):
    if not model or not tokenizer:
        raise Exception(
            "Model tidak berhasil dimuat, translasi tidak dapat dilakukan.")

    # Model T5 tidak selalu butuh prefix, tapi ini adalah praktik yang baik.
    # Sesuaikan jika Anda tidak menggunakan prefix saat training.
    input_text = f"terjemahkan Indonesia ke Minang: {teks_indonesia}"

    # Tokenisasi input
    inputs = tokenizer(input_text, return_tensors="pt",
                       padding=True, truncation=True, max_length=512)

    # Lakukan inferensi/prediksi tanpa menghitung gradien
    with torch.no_grad():
        outputs = model.generate(inputs.input_ids, max_length=128)

    # Decode hasil prediksi menjadi teks
    teks_minang = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return teks_minang

# --- 4. Definisikan Endpoint API (Bagian ini sama persis seperti sebelumnya) ---


@app.route('/translate', methods=['POST'])
def handle_translation():
    if not model:
        return jsonify({"error": "Model sedang tidak tersedia"}), 503

    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Request tidak valid. Harap sediakan JSON dengan key 'text'."}), 400

    input_text = data['text']
    if not input_text.strip():
        return jsonify({"error": "Teks tidak boleh kosong."}), 400

    try:
        hasil_terjemahan = terjemahkan(input_text)
        return jsonify({
            "source_text": input_text,
            "translation": hasil_terjemahan
        })
    except Exception as e:
        return jsonify({"error": f"Terjadi kesalahan internal: {str(e)}"}), 500


@app.route('/')
def index():
    return "API Translasi Indo-Minang Aktif! Gunakan endpoint /translate dengan method POST."


# Bagian ini hanya untuk testing lokal
if __name__ == '__main__':
    # Pastikan port yang digunakan tidak bentrok dengan service lain
    app.run(host='0.0.0.0', port=os.environ.get("PORT", 5000), debug=True)
