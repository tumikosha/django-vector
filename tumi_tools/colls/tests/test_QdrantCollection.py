from unittest import TestCase

from qdrant_client import models, QdrantClient
from qdrant_client.http.models import PointStruct
from sentence_transformers import SentenceTransformer

from tumi_tools.colls.QdrantCollection import QdrantCollection, QdrantMemoryCollection

encoder = SentenceTransformer("all-MiniLM-L6-v2")

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
    },
    {
        "name": "Brave New World",
        "description": "A dystopian society where people are genetically engineered and conditioned to conform to a strict social hierarchy.",
        "author": "Aldous Huxley",
        "year": 1932,
    },
    {
        "name": "The Hitchhiker's Guide to the Galaxy",
        "description": "A comedic science fiction series following the misadventures of an unwitting human and his alien friend.",
        "author": "Douglas Adams",
        "year": 1979,
    },
    {
        "name": "Dune",
        "description": "A desert planet is the site of political intrigue and power struggles.",
        "author": "Frank Herbert",
        "year": 1965,
    },
    {
        "name": "Foundation",
        "description": "A mathematician develops a science to predict the future of humanity and works to save civilization from collapse.",
        "author": "Isaac Asimov",
        "year": 1951,
    },
    {
        "name": "Snow Crash",
        "description": "A futuristic world where the internet has evolved into a virtual reality metaverse.",
        "author": "Neal Stephenson",
        "year": 1992,
    },
    {
        "name": "Neuromancer",
        "description": "A hacker is hired to pull off a near-impossible hack and gets pulled into a web of intrigue.",
        "author": "William Gibson",
        "year": 1984,
    },
    {
        "name": "The War of the Worlds",
        "description": "A Martian invasion of Earth throws humanity into chaos.",
        "author": "H.G. Wells",
        "year": 1898,
    },
    {
        "name": "The Hunger Games",
        "description": "A dystopian society where teenagers are forced to fight to the death in a televised spectacle.",
        "author": "Suzanne Collins",
        "year": 2008,
    },
    {
        "name": "The Andromeda Strain",
        "description": "A deadly virus from outer space threatens to wipe out humanity.",
        "author": "Michael Crichton",
        "year": 1969,
    },
    {
        "name": "The Left Hand of Darkness",
        "description": "A human ambassador is sent to a planet where the inhabitants are genderless and can change gender at will.",
        "author": "Ursula K. Le Guin",
        "year": 1969,
    },
    {
        "name": "The Three-Body Problem",
        "description": "Humans encounter an alien civilization that lives in a dying system.",
        "author": "Liu Cixin",
        "year": 2008,
    },
]


class TestQdrantCollection(TestCase):
    def setUp(self):
        # self.client = QdrantClient(":memory:")
        # self.client = client = QdrantClient("localhost", port=6333)
        # self.repo = QdrantRepository(host="localhost", port=6333)
        # self.coll = QdrantCollection(self.client, "my_coll")
        self.coll = QdrantMemoryCollection("my_coll", vector_size=4)

        self.points = [
            PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"city": "Berlin"}),
            PointStruct(id=2, vector=[0.19, 0.81, 0.75, 0.11], payload={"city": "London"}),
            PointStruct(id=3, vector=[0.36, 0.55, 0.47, 0.94], payload={"city": "Moscow"}),
            PointStruct(id=4, vector=[0.18, 0.01, 0.85, 0.80], payload={"city": "New York"}),
            PointStruct(id=5, vector=[0.24, 0.18, 0.22, 0.44], payload={"city": "Beijing"}),
            PointStruct(id=6, vector=[0.35, 0.08, 0.11, 0.44], payload={"city": "Mumbai"}),
            PointStruct(id=7, vector=[0.19, 0.81, 0.75, 0.1111], payload={"city": "London"}),
        ]
        print("------------")

    def test_create_collection(self):
        try:
            self.coll = QdrantCollection("my_coll")
            assert True
        except Exception as e:
            assert False

    def test_upsert(self):
        result = self.coll.upsert(records=self.points)
        print(result)
        assert True

    def test_find(self):
        result = self.coll.upsert(records=self.points)
        search_result = self.coll.find([0.2, 0.1, 0.9, 0.7], limit=3)
        assert len(search_result) == 3

    def test_count(self):
        self.coll.enable_indexing()
        upsert_result = self.coll.upsert(records=self.points)
        result = self.coll.upsert(records=self.points)
        total = self.coll.count()
        print(total)
        assert total == len(self.points)
        count = self.coll.count(query=self.coll.field_match("city", "London"))
        print(count)
        assert count == 2

    # def test_disable_indexing(self):
    #     self.fail()
    #
    # def test_enable_indexing(self):
    #     self.fail()

    # def test_set_threshold(self):
    #     self.fail()

    def test_delete(self):
        count_before = self.coll.count()
        self.coll.delete(QdrantCollection.field_match("id", 1))
        count_after = self.coll.count()
        assert count_before == count_after


class TestSematicQdrantCollection(TestCase):
    def setUp(self):
        self.client = QdrantClient(":memory:")
        # self.client = QdrantClient(host="127.0.0.1", port=6333)
        self.coll = QdrantCollection(self.client, "my_books", vector_size=encoder.get_sentence_embedding_dimension())
        self.client.recreate_collection(
            collection_name="my_books",
            vectors_config=models.VectorParams(
                size=encoder.get_sentence_embedding_dimension(),  # Vector size is defined by used model
                distance=models.Distance.COSINE,
            ),
        )

        self.records = [
            models.Record(
                id=idx, vector=encoder.encode(doc["description"]).tolist(), payload=doc
            )
            for idx, doc in enumerate(documents)
        ]

        print("Yess")

    def test_sem_upload_and_search_records(self):
        self.coll.upsert(self.records)
        print("encoder.get_sentence_embedding_dimension():", encoder.get_sentence_embedding_dimension())
        hits = self.coll.sem_search(query="alien invasion", limit=3)
        # print(hits)
        for hit in hits:
            print("score:", hit.score, hit.payload)
        assert self.coll.count() > 0
