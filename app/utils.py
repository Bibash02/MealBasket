import hmac
import hashlib
import base64

def generate_signature(total_amount, transaction_uuid, product_code, secret_key):
    total_amount = str(total_amount)

    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"

    secret_key_bytes = secret_key.encode("utf-8")
    message_bytes = message.encode("utf-8")

    digest = hmac.new(secret_key_bytes, message_bytes, hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode()

    return signature