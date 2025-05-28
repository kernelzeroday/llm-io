import hashlib
import base64
import json
import secrets
import string

def crypto_utils(operation: str, data: str, **kwargs) -> str:
    """
    Cryptographic utilities for hashing, encoding, and basic crypto operations.
    
    Supported operations:
    - hash: Generate various hash types (md5, sha1, sha256, sha512)
    - encode: Base64 encoding
    - decode: Base64 decoding
    - generate_key: Generate random keys/tokens
    - password_hash: Secure password hashing
    - verify_hash: Verify data against hash
    
    Args:
        operation (str): The crypto operation to perform
        data (str): The input data
        **kwargs: Additional parameters (algorithm, length, etc.)
        
    Returns:
        str: JSON string with operation results
    """
    operations = {
        'hash': _hash_data,
        'encode': _encode_data,
        'decode': _decode_data,
        'generate_key': _generate_key,
        'password_hash': _password_hash,
        'verify_hash': _verify_hash
    }
    
    if operation not in operations:
        available_ops = list(operations.keys())
        return json.dumps({
            "error": f"Unknown operation '{operation}'",
            "available_operations": available_ops
        })
    
    try:
        result = operations[operation](data, **kwargs)
        return json.dumps({
            "operation": operation,
            "input_data": data[:50] + "..." if len(data) > 50 else data,
            "result": result
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Operation failed: {str(e)}"})

def _hash_data(data: str, algorithm: str = "sha256", **kwargs) -> Dict[str, Any]:
    """Generate hash of data using specified algorithm"""
    algorithms = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512
    }
    
    if algorithm not in algorithms:
        return {
            "error": f"Unsupported algorithm '{algorithm}'",
            "supported": list(algorithms.keys())
        }
    
    hash_obj = algorithms[algorithm]()
    hash_obj.update(data.encode('utf-8'))
    
    return {
        "algorithm": algorithm,
        "hash": hash_obj.hexdigest(),
        "length": len(hash_obj.hexdigest())
    }

def _encode_data(data: str, encoding: str = "base64", **kwargs) -> Dict[str, Any]:
    """Encode data using specified encoding"""
    if encoding == "base64":
        encoded = base64.b64encode(data.encode('utf-8')).decode('utf-8')
        return {
            "encoding": encoding,
            "encoded": encoded,
            "original_length": len(data),
            "encoded_length": len(encoded)
        }
    else:
        return {"error": f"Unsupported encoding '{encoding}'"}

def _decode_data(data: str, encoding: str = "base64", **kwargs) -> Dict[str, Any]:
    """Decode data using specified encoding"""
    if encoding == "base64":
        try:
            decoded = base64.b64decode(data.encode('utf-8')).decode('utf-8')
            return {
                "encoding": encoding,
                "decoded": decoded,
                "original_length": len(data),
                "decoded_length": len(decoded)
            }
        except Exception as e:
            return {"error": f"Invalid base64 data: {str(e)}"}
    else:
        return {"error": f"Unsupported encoding '{encoding}'"}

def _generate_key(data: str = "", length: int = 32, key_type: str = "hex", **kwargs) -> Dict[str, Any]:
    """Generate random cryptographic keys"""
    if key_type == "hex":
        key = secrets.token_hex(length // 2)
    elif key_type == "url_safe":
        key = secrets.token_urlsafe(length)
    elif key_type == "alphanumeric":
        chars = string.ascii_letters + string.digits
        key = ''.join(secrets.choice(chars) for _ in range(length))
    elif key_type == "password":
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        key = ''.join(secrets.choice(chars) for _ in range(length))
    else:
        return {
            "error": f"Unsupported key type '{key_type}'",
            "supported": ["hex", "url_safe", "alphanumeric", "password"]
        }
    
    return {
        "key_type": key_type,
        "key": key,
        "length": len(key),
        "entropy_bits": length * 4 if key_type == "hex" else length * 6
    }

def _password_hash(data: str, algorithm: str = "sha256", salt_length: int = 16, **kwargs) -> Dict[str, Any]:
    """Generate secure password hash with salt"""
    salt = secrets.token_hex(salt_length)
    salted_password = salt + data
    
    algorithms = {
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512
    }
    
    if algorithm not in algorithms:
        return {
            "error": f"Unsupported algorithm '{algorithm}'",
            "supported": list(algorithms.keys())
        }
    
    hash_obj = algorithms[algorithm]()
    hash_obj.update(salted_password.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    
    return {
        "algorithm": algorithm,
        "salt": salt,
        "hash": password_hash,
        "combined": f"{salt}:{password_hash}",
        "salt_length": salt_length
    }

def _verify_hash(data: str, hash_to_verify: str, algorithm: str = "sha256", **kwargs) -> Dict[str, Any]:
    """Verify data against a hash (supports both simple and salted hashes)"""
    algorithms = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512
    }
    
    if algorithm not in algorithms:
        return {
            "error": f"Unsupported algorithm '{algorithm}'",
            "supported": list(algorithms.keys())
        }
    
    # Check if it's a salted hash (contains colon)
    if ':' in hash_to_verify:
        salt, stored_hash = hash_to_verify.split(':', 1)
        salted_data = salt + data
        hash_obj = algorithms[algorithm]()
        hash_obj.update(salted_data.encode('utf-8'))
        computed_hash = hash_obj.hexdigest()
        is_match = computed_hash == stored_hash
        
        return {
            "algorithm": algorithm,
            "hash_type": "salted",
            "salt": salt,
            "is_match": is_match,
            "computed_hash": computed_hash,
            "stored_hash": stored_hash
        }
    else:
        # Simple hash verification
        hash_obj = algorithms[algorithm]()
        hash_obj.update(data.encode('utf-8'))
        computed_hash = hash_obj.hexdigest()
        is_match = computed_hash == hash_to_verify
        
        return {
            "algorithm": algorithm,
            "hash_type": "simple",
            "is_match": is_match,
            "computed_hash": computed_hash,
            "stored_hash": hash_to_verify
        } 