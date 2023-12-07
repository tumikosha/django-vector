import hashlib
import uuid

from sentence_transformers import SentenceTransformer

encoder = SentenceTransformer("all-MiniLM-L6-v2")


def string_2_uuid(val: str) -> uuid.UUID:
    """ generates uuid from random string """
    hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
    return uuid.UUID(hex=hex_string)
