Security Overview: Secure File Portal

1. Introduction

This document outlines the security measures, cryptographic methods, and key handling procedures for the Secure File Portal project. The primary security objective is to ensure the confidentiality and integrity of user-uploaded files at rest.

2. Encryption Algorithm

Algorithm: AES (Advanced Encryption Standard)

Key Size: 256 bits

Mode: GCM (Galois/Counter Mode)

Justification: AES-256 is the industry standard for strong symmetric encryption. GCM is an "authenticated encryption" mode (AEAD), which provides both confidentiality (encryption) and integrity (protection against tampering). If an encrypted file is modified, the GCM algorithm will detect it, and decryption will fail, preventing the use of a corrupted or malicious file.

3. File Integrity

File integrity is guaranteed by the choice of AES-GCM. The tag (or authentication tag) generated during encryption ensures that the ciphertext has not been altered. Any attempt to modify the encrypted file will cause the decrypt_and_verify step to fail.

4. Key Management

Securely managing the encryption key is the most critical part of this system.

4.1. Prototype Key Handling (Client-Side)

The index.html prototype uses a user-provided password to derive a key.

Method: PBKDF2 (Password-Based Key Derivation Function 2)

Salt: A new 16-byte random salt is generated for every encryption. This prevents "rainbow table" attacks.

Iterations: 100,000 iterations are used to make brute-force attacks on the password slow.

Security Limitation: This method is suitable for a user encrypting their own files. It is unsuitable for a multi-user server system, as the server would have no way to know the user's password to decrypt a file for another user (or even the same user later).

4.2. Recommended Production Key Handling (Server-Side)

A production-grade system must manage keys itself. The recommended approach is Envelope Encryption.

Master Key:

A single, high-entropy, 256-bit Master Key is generated.

This key must be stored in a secure, non-public location.

Good: A "secrets manager" (like AWS KMS, Google Cloud KMS, or HashiCorp Vault).

Okay (for this task): A secure Environment Variable on the server (e.g., export AES_KEY=...).

Bad (NEVER DO THIS): Hardcoding the key in the source code.

Server Encryption Process (Envelope Encryption):

When a user uploads a file, the server does the following:

Generates a new, unique Data Key (e.g., 256-bit) for this file only.

Encrypts the file using this new Data Key (e.g., AES-GCM).

Encrypts the Data Key using the Master Key. This is the "envelope."

Stores the encrypted file and the encrypted data key together.

The unencrypted Data Key is discarded from memory.

Server Decryption Process:

When a user requests a file:

The server retrieves the encrypted file and the encrypted data key.

It uses its Master Key to decrypt the encrypted data key.

It now has the (unencrypted) Data Key.

It uses the Data Key to decrypt the file.

It sends the original, decrypted file to the user.

Advantage: This method allows you to "re-key" the system by only re-encrypting the data keys, not all the files. It also limits the exposure of any single key, as each file has its own. For the scope of this internship task, using a single Master Key loaded from an environment variable (as shown in the README.md Flask example) is a solid, secure, and basic implementation.