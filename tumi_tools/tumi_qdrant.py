from tumi_tools import tumi_parser as tp
import embeddings as emb
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from qdrant_client.http.models import Distance, VectorParams, PointIdsList

PATH = "/media/tumi/nvme/qdrant_storage/"

text = """
    That is a very happy Person!
    That is a Happy Dog.
    Today is a sunny day!!!
"""


# sentences = tp.text_2_lines_no_empty(text)
# # print(sentences)
# embeddings = emb.get_embeddings(sentences)
# # print(embeddings)
# s_and_e = zip(sentences, embeddings)
#
# client = QdrantClient(":memory:")
# client = QdrantClient("localhost", port=6333)


class QDrantCollection:
    def __init__(self, path=PATH, name="fixiegen"):
        self.path = path
        self.name = name
        # self.client = QdrantClient(path=path)  # Persists changes to disk
        try:
            self.client = QdrantClient("localhost", port=6333)  # Persists changes to disk
            # self.recreate_collection_if_need()
            self.recreate_collection_if_need()
            pass
        except Exception as e:
            print("Cant find QDrant server ", str(e))

        # Try to use qdrant client
        try:
            self.client = QdrantClient(path=path)  # Persists changes to disk
            # self.recreate_collection_if_need()
            self.recreate_collection_if_need()
            pass
        except Exception as e:
            print("Cant find QDrant server ", str(e))

    def existing_coll_names(self):
        return [c.name for c in self.client.get_collections().collections]

    def recreate_collection_if_need(self):
        full_path = self.path + "/collection/" + self.name + "/storage.sqlite"
        existing_colls = self.existing_coll_names()

        # print(client.get_collection("fixiegen11"))

        if self.name not in existing_colls:
            print("COLLECTION not exists")
            self.client.recreate_collection(
                collection_name=self.name,
                path=full_path,
                # vectors_config=VectorParams(size=4, distance=Distance.DOT),
                # vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                vectors_config=VectorParams(size=384, distance=Distance.EUCLID),
            )
            return True
        else:
            print("COLLECTION  exists")
            return False

    def save(self, d, text_field, **kwargs):
        d = d | kwargs
        embeddings_ = emb.get_embeddings([d[text_field]])
        operation_info = self.client.upsert(
            collection_name=self.name,
            points=[
                PointStruct(id=d['id'], vector=vector.tolist(), payload=d)
                for idx, vector in enumerate(embeddings_)
            ]
        )
        return operation_info

    def find(self, ids):
        return self.client.retrieve(
            collection_name=self.name,
            ids=ids,
        )

    @staticmethod
    def prepare_query(query):
        words = tuple(tp.just_words(query, tp.WORD_DELIMITERS))
        words = [word for word in words if word.lower() not in tp.THRASH_WORDS]
        return " ".join(words)

    def search(self, query, limit=10):
        p_query = QDrantCollection.prepare_query(query)
        query_vector = emb.get_embeddings(p_query)
        return self.client.search(
            collection_name=self.name,
            query_vector=query_vector,
            limit=limit
        )

    def delete(self, point_list):
        self.client.delete(
            collection_name=self.name,
            points_selector=PointIdsList(
                points=point_list,
            ),
        )

    def count(self):
        return self.client.count(
            collection_name=self.name,
            # count_filter=models.Filter(
            #     must=[
            #         models.FieldCondition(
            #             key="color",
            #
            #             match=models.MatchValue(value="red")
            #         ),
            #     ]
            # ),
            exact=True,
        ).count


# operation_info = client.upsert(
#     collection_name="test_collection",
#     points=[
#         PointStruct(id=idx, vector=vector.tolist(), payload={"line": sentences[idx]})
#         for idx, vector in enumerate(embeddings)
#     ]
# )

# print(operation_info)


if __name__ == '__main__':
    PATH = "/media/tumi/nvme/qdrant_storage/"
    coll = QDrantCollection(path=PATH, name="fixiegen")
    # coll.delete([1])
    # if coll.count() == 0:
    #     print("COLLECTION is Empty")
    #     coll.save({}, "intro", id=1, nick="arbuzzo", intro="That is a very happy Person!")
    coll.delete([37])
    for res in coll.search("Salvo", limit=1000):
        print(res)
        print(res.id, res.score, ":: ", res.payload['nick'], res.payload['intro'])
        # client.delete_vectors()
    print(coll.count())

    coll.client = None
