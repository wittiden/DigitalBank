# JWT Certificates (RSA keys)

This document explains how to generate RSA keys for JWT authentication.

⚠️ **SECURITY WARNING:** Never commit `jwt-private.pem` to the repository. It must stay secret on the server.

## Generate RSA keys

```bash
# 1. Generate private key
openssl genrsa -out jwt-private.pem 2048

# 2. Generate public key
openssl rsa -in jwt-private.pem -pubout -out jwt-public.pem