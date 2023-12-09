from qdrant_client import models, QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
from tumi_tools.colls.AbstractCollections import AbstractCollection

__version__: str = '0.1'

encoder: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")
STD_VECTOR_SIZE = encoder.get_sentence_embedding_dimension()
print("STD_VECTOR_SIZE", STD_VECTOR_SIZE)


class QdrantCollection(AbstractCollection):
    client = None
    MEMORY = ":memory:"

    def __init__(self, client, name="test_collection", vector_size=STD_VECTOR_SIZE, distance=models.Distance.COSINE, shard_number=2):
        self.client = client
        self.name = name
        self.create_collection(name=name, vector_size=vector_size, distance=distance, shard_number=shard_number)

    @staticmethod
    def get_client(host: str = None, port=6333) -> QdrantClient:
        if host is None:
            return QdrantClient("127.0.0.1", port=port)
        if host.lower().find('memory') > -1:
            return QdrantClient(QdrantCollection.MEMORY)

        return QdrantClient(host, port=port)

    def create_collection(self, name: str, vector_size=4, distance=models.Distance.COSINE, shard_number=2):
        """
        :param vector_size:
        :param distance:
        :param shard_number: Parallel upload into multiple shards
        :return:
        """
        try:
            from qdrant_client.http.models import Distance, VectorParams

            res = self.client.create_collection(
                collection_name=self.name, vectors_config=VectorParams(size=vector_size, distance=distance),
                shard_number=shard_number
            )
            return True, res
        except Exception as e:
            return False, e

    def upsert(self, records=[]) -> bool:
        operation_info = self.client.upsert(
            collection_name=self.name,
            wait=True,
            # points=points if isinstance(points, list) else [points],  # wrap in list when need
            points=records
            # points=[
            #     PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"city": "Berlin"}),
            # ],
        )
        return operation_info

    def find(self, vector, query=None, limit=3, with_payload=True) -> list:
        if query is None:
            return self.client.search(collection_name=self.name, query_vector=vector, limit=limit)
        else:
            return self.client.search(
                collection_name=self.name,
                query_vector=vector,
                query_filter=query,
                with_payload=with_payload,
                limit=limit,
            )

    @staticmethod
    def field_match(key, value):
        return Filter(must=[FieldCondition(key=key, match=MatchValue(value=value))])

    def count(self, query=None):
        if filter is None:
            return self.client.count(collection_name=self.name, exact=True).count
        else:
            return self.client.count(collection_name=self.name, count_filter=query, exact=True).count

    def disable_indexing(self):
        print("# disable_indexing...", end="")
        self.client.update_collection(
            collection_name=self.name,
            optimizer_config=models.OptimizersConfigDiff(indexing_threshold=0))
        print("Ok")

    def enable_indexing(self):
        print("# enable_indexing...", end="")
        self.client.update_collection(
            collection_name=self.name,
            optimizer_config=models.OptimizersConfigDiff(indexing_threshold=20000))
        print("Ok")

    def set_threshold(self, threshold):
        self.client.update_collection(
            collection_name=self.name,
            optimizer_config=models.OptimizersConfigDiff(indexing_threshold=threshold))

    def sem_upload_records(self, records):
        self.client.upload_records(collection_name=self.name, records=records)

    def sem_search(self, query, limit):
        hits = self.client.search(collection_name=self.name, query_vector=encoder.encode(query).tolist(), limit=limit)
        # for hit in hits:
        #     print("score:", hit.score, hit.payload)
        return hits

    def delete_collection(self):
        self.client.delete_collection(collection_name=self.name)

    def get_collection(self, name: str):
        """
        If you insert the vectors into the collection, the status field may become yellow whilst it is optimizing. It will become green once all the points are successfully processed.

        The following color statuses are possible:

        🟢 green: collection is ready
        🟡 yellow: collection is optimizing
        🔴 red: an error occurred which the engine could not recover from
        There are some other attributes you might be interested in:

        points_count - total number of objects (vectors and their payloads) stored in the collection
        vectors_count - total number of vectors in a collection. If there are multiple vectors per object, it won’t be equal to points_count.
        indexed_vectors_count - total number of vectors stored in the HNSW index. Qdrant does not store all the vectors in the index, but only if an index segment might be created for a given configuration.
                :param name:
                :return:
        """
        if name is not None:
            return self.client.get_collection(collection_name=name)
        return None

    def delete(self, del_filter):
        """
        models.Filter(
                    must=[
                        models.FieldCondition(
                            key="color",
                            match=models.MatchValue(value="red"),
                        ),
                    ],
                )
        :param del_filterq:
        :return:
        """
        self.client.delete(
            collection_name=self.name,
            points_selector=models.FilterSelector(
                filter=del_filter
            ),
        )


class QdrantMemoryCollection(QdrantCollection):

    def __init__(self, name="test_collection", vector_size=STD_VECTOR_SIZE, distance=models.Distance.COSINE,
                 shard_number=2):
        client = QdrantClient(":memory:")
        super().__init__(client, name, vector_size, distance, shard_number)


class QdrantLocalCollection(QdrantCollection):

    def __init__(self, name="test_collection", vector_size=STD_VECTOR_SIZE,
                 distance=models.Distance.COSINE, shard_number=2):
        client = QdrantClient(host="localhost", port=6333)
        super().__init__(client, name, vector_size, distance, shard_number)


documents = [
    {
        "name": "The Time Machine",
        "description": "A man travels through time and witnesses the evolution of humanity.",
        "author": "H.G. Wells",
        "year": 1895,
    },
    {
        "name": "Ender's Game",
        "description": "A young boy is trained to become a military leader in a war against an alien race.",
        "author": "Orson Scott Card",
        "year": 1985,
    }
]
