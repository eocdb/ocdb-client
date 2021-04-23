def encrypt(txt: str, key: str) -> str:
    import hashlib
    import hmac

    if key is None:
        raise ValueError("password-key must be set: ocdb conf password-key [key].")

    h = hmac.new(key.encode(), txt.encode(), hashlib.sha512)
    return h.hexdigest()
