# Secure File Portal (Internship Task 3)

This is a secure web portal built with Python (Flask) that allows users to upload files, which are then encrypted at rest on the server using AES-256-GCM.

## Features

* **Secure File Upload:** Files uploaded via the web interface are encrypted on the server.
* **Secure File Download:** Files are decrypted on the fly before being sent to the user.
* **Strong Encryption:** Uses **AES-256-GCM** for high-level confidentiality and integrity (prevents tampering).
* **Secure Key Management:** The master encryption key is loaded from a secure environment variable, not hardcoded in the code.

## How It Works

1.  **Upload:**
    * A user selects a file in their browser and clicks "Upload".
    * The Flask server receives the raw file.
    * The server uses its `MASTER_KEY` to encrypt the file with AES-GCM.
    * The server saves the encrypted file as `[nonce][tag][ciphertext]` in the `server_uploads/` directory.

2.  **Download:**
    * A user requests a file via the download URL.
    * The server reads the encrypted file (`.enc`).
    * It separates the `nonce`, `tag`, and `ciphertext`.
    * It uses the `MASTER_KEY` and `nonce` to decrypt the data. The `tag` is used to verify the file has not been tampered with.
    * If successful, the server sends the *original, decrypted file* back to the user.

## How to Run This Project

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/RP1005/FUTURE_CS_03.git](https://github.com/RP1005/FUTURE_CS_03.git)
    cd FUTURE_CS_03
    ```

2.  **Install Dependencies:**
    ```bash
    pip install Flask pycryptodome
    ```

3.  **Set the Encryption Key:**
    You *must* set the `AES_KEY` environment variable. It must be a 32-character string.

    * **Windows (CMD):**
        ```cmd
        set AES_KEY=E5B9A45B5F4932A88FF642F8C8A3A9C7
        ```
    * **Mac/Linux:**
        ```bash
        export AES_KEY='E5B9A45B5F4932A88FF642F8C8A3A9C7'
        ```

4.  **Run the Server:**
    ```bash
    python app.py
    ```

5.  **Open the Portal:**
    Go to `http://127.0.0.1:5000` in your web browser.