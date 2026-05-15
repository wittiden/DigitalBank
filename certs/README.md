# JWT Certificates (RSA keys)

This document explains how to generate RSA keys for JWT authentication.

⚠️ **SECURITY WARNING:** Never commit `jwt-private.pem` to the repository. It must stay secret on the server.

## Generate RSA keys

```bash
# 1. Generate private key
cd certs
openssl genrsa -out access-private.pem 2048
openssl genrsa -out refresh-private.pem 2048

# 2. Generate public key
cd certs
openssl rsa -in access-private.pem -pubout -out access-public.pem
openssl rsa -in refresh-private.pem -pubout -out refresh-public.pem
