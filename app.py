# Import necessary libraries from Flask, Crypto, os, and io
from flask import Flask, request, send_file, render_template
from Crypto.Cipher import AES  # The AES encryption algorithm
from Crypto.Random import get_random_bytes # For generating random nonces
import os     # To get environment variables and work with file paths
import io     # To send file data from memory

# Initialize the Flask application
app = Flask(__name__)

# --- Configuration ---
# WARNING: NEVER hardcode a key. Load from a secure environment variable.
# This key MUST be 32 bytes (32 characters) for AES-256.
# We fetch the key from the 'AES_KEY' environment variable.
MASTER_KEY = os.environ.get('AES_KEY')

# If the key is found, encode it to bytes, which is what the crypto library needs
if MASTER_KEY:
    MASTER_KEY = MASTER_KEY.encode('utf-8')

# Define the folder where encrypted files will be stored
UPLOAD_FOLDER = 'server_uploads'
# Create the folder if it doesn't already exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# --- End Configuration ---

@app.route('/')
def index():
    """
    This is the main route ('/').
    It just renders and displays the 'index.html' file from the 'templates' folder.
    """
    return render_template('index.html') 

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    This route handles file uploads (via HTTP POST).
    It encrypts the file and saves it to the server.
    """
    # Check if the 'file' part is in the request
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    
    # Check if the user selected a file
    if file.filename == '':
        return 'No selected file', 400

    if not file or not MASTER_KEY:
        if not file:
            return 'No file', 400
        if not MASTER_KEY:
            return 'Server Error: Encryption key is not configured', 500

    # Read the entire file into memory
    file_data = file.read()
    
    # --- Encryption ---
    # 1. Create a new AES cipher object using our MASTER_KEY in GCM mode.
    #    AES.MODE_GCM is an "authenticated" mode that provides both
    #    encryption (confidentiality) and integrity (prevents tampering).
    cipher = AES.new(MASTER_KEY, AES.MODE_GCM)
    
    # 2. Encrypt the data. This returns two things:
    #    - ciphertext: The encrypted data
    #    - tag: An authentication tag to verify integrity later
    ciphertext, tag = cipher.encrypt_and_digest(file_data)
    
    # 3. Get the 'nonce' (Number used once). This is like an IV (Initialization Vector)
    #    and is essential for decryption. It is generated automatically.
    nonce = cipher.nonce
    
    # --- Save Encrypted File ---
    # We must save all three parts to be able to decrypt later.
    # We save them in one file in this order: [nonce][tag][ciphertext]
    encrypted_filename = os.path.join(UPLOAD_FOLDER, file.filename + '.enc')
    with open(encrypted_filename, 'wb') as f:
        f.write(nonce)      # Write the 16-byte nonce
        f.write(tag)        # Write the 16-byte tag
        f.write(ciphertext) # Write the rest of the encrypted data
        
    return 'File encrypted and saved', 200

@app.route('/download/<filename>')
def download_file(filename):
    """
    This route handles file downloads.
    It reads the encrypted file, decrypts it in memory, and sends
    the original file back to the user.
    """
    if not MASTER_KEY:
        return 'Server Error: Encryption key is not configured', 500
        
    # Create the full path to the encrypted file
    encrypted_filename = os.path.join(UPLOAD_FOLDER, filename + '.enc')

    try:
        with open(encrypted_filename, 'rb') as f:
            # --- Read Encrypted File ---
            # We read the file back in the *exact* order we wrote it.
            nonce = f.read(16)      # Read the 16-byte nonce
            tag = f.read(16)        # Read the 16-byte tag
            ciphertext = f.read() # Read the rest of the encrypted data
            
        # --- Decryption ---
        # 1. Create a new cipher object, providing the *same key and nonce*.
        cipher = AES.new(MASTER_KEY, AES.MODE_GCM, nonce=nonce)
        
        # 2. Decrypt and verify. This checks the 'tag' to make sure
        #    the file wasn't tampered with. If the key is wrong or
        #    the file is corrupt, it will raise a ValueError.
        decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
        
        # --- Send Decrypted File ---
        # Send the decrypted data back to the user as a file attachment.
        return send_file(
            io.BytesIO(decrypted_data), # Send from memory
            mimetype='application/octet-stream', # A generic "file" type
            as_attachment=True,
            download_name=filename # The original (decrypted) file name
        )
    except (ValueError, KeyError):
        # This block catches decryption errors (e.g., wrong key, corrupt file)
        return 'Decryption failed. File may be corrupt or key is wrong.', 400
    except FileNotFoundError:
        return 'File not found.', 404

# This is the standard Python entry point
if __name__ == '__main__':
    # Make sure to set the AES_KEY environment variable before running
    if not MASTER_KEY:
        print("-------------------------------------------------------")
        print("Error: AES_KEY environment variable not set.")
        print("Please set it before running the app, e.g.:")
        print("set AES_KEY=E5B9A45B5F4932A88FF642F8C8A3A9C7")
        print("-------------------------------------------------------")
    else:
        # Run the Flask app in debug mode
        app.run(debug=True)