from abc import ABC


class AbstractCollection(ABC):
    def __init__(self, client, name: str, *args, **kwargs):
        pass

    def count(self, query: str = None) -> int:
        pass

    def upsert(self, records: list = []) -> bool:
        pass

    def find(self, vector: list[float], query=None, limit: int = 3, with_payload: bool = True) -> list:
        pass

    def sem_upload_records(self, records: list) -> bool:
        pass

    def sem_search(self, query: str, limit: int) -> list:
        pass
