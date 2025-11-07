# A conceptual example for a Flask backend (requires PyCryptodome)
# pip install flask pycryptodome

from flask import Flask, request, send_file, render_template
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os
import io

app = Flask(__name__)

# WARNING: NEVER hardcode a key. Load from a secure environment variable or KMS.
# This key MUST be 32 bytes (256-bit)
# You would set this in your terminal: export AES_KEY='your_32_byte_secret_key_here'
MASTER_KEY = os.environ.get('AES_KEY').encode('utf-8') 

UPLOAD_FOLDER = 'server_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    # This will find and show 'templates/index.html'
    return render_template('index.html') 

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    if not file:
        return 'No file', 400

    file_data = file.read()
    
    # Encrypt
    cipher = AES.new(MASTER_KEY, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(file_data)
    
    # Save the file as [nonce][tag][ciphertext]
    # (nonce is the same as IV)
    encrypted_filename = os.path.join(UPLOAD_FOLDER, file.filename + '.enc')
    with open(encrypted_filename, 'wb') as f:
        f.write(cipher.nonce)
        f.write(tag)
        f.write(ciphertext)
        
    return 'File encrypted and saved', 200

@app.route('/download/<filename>')
def download_file(filename):
    encrypted_filename = os.path.join(UPLOAD_FOLDER, filename + '.enc')

    try:
        with open(encrypted_filename, 'rb') as f:
            # Read the parts back
            nonce = f.read(16)
            tag = f.read(16)
            ciphertext = f.read()
            
        # Decrypt
        cipher = AES.new(MASTER_KEY, AES.MODE_GCM, nonce=nonce)
        decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
        
        # Send the decrypted data
        return send_file(
            io.BytesIO(decrypted_data),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=filename # The original name
        )
    except (ValueError, KeyError, FileNotFoundError):
        return 'Decryption failed or file not found', 400

if __name__ == '__main__':
    # Make sure to set the AES_KEY environment variable before running
    if not MASTER_KEY:
        print("Error: AES_KEY environment variable not set.")
        print("Please set it, e.g., export AES_KEY='your_32_byte_secret_key_here'")
    else:
        app.run(debug=True)