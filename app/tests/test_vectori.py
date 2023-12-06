# -*- coding: utf-8 -*-
"""
File: test_snippet_api.py
Authors: Veaceslav Kunitki<tumikosha@fmail.com>
Description: tests for PG_Vector module
    https://github.com/pgvector/pgvector-python#django
    This test uses the sentense encoder "all-MiniLM-L6-v2"
"""
from django.db.models import Avg
from rest_framework.test import APITestCase
from app.models import Snippet, Company
from sentence_transformers import SentenceTransformer
from pgvector.django import L2Distance

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


class VectorTestCase(APITestCase):
    """  ... """

    def setUp(self):
        for doc in documents:
            vector = encoder.encode(doc['description']).tolist()
            company = Company.objects.create(title=doc['name'],
                                             summary=doc['description'],
                                             embedding=vector)
            company.save()

    def test_create_company(self):
        res = Company.objects.all()
        print("res", len(res), res)
        assert len(res) == len(documents)
        query = "alien invasion"
        vector = encoder.encode(query).tolist()
        result = Company.objects.order_by(L2Distance('embedding', vector))[:5]
        for row in result:
            print(row.title, row.summary)
        # print(res)
        assert True
        # assert len(res) == len(documents)

    def test_get_the_distance(self):
        # Also supports MaxInnerProduct and CosineDistance
        # Get the distance
        query = "alien invasion"
        query_vector = encoder.encode(query).tolist()
        result = Company.objects.annotate(
            distance=L2Distance('embedding', query_vector))[:5]
        for row in result:
            print("D::", row.distance, row.title, row.summary)
        # print(res)
        assert True

    def test_get_distance(self):
        query = "alien invasion"
        query_vector = encoder.encode(query).tolist()
        result = Company.objects.alias(distance=L2Distance('embedding', query_vector))\
            .filter(distance__lt=5)
        for row in result:
            print("D::", row.title, row.summary)
        # print(res)
        assert True

    def test_ordered_with_distance(self):
        # Also supports MaxInnerProduct and CosineDistance
        # Get the distance
        query = "alien invasion"
        query_vector = encoder.encode(query).tolist()
        result = Company.objects.annotate(
            distance=L2Distance('embedding', query_vector)
        ).order_by(L2Distance('embedding', query_vector))[:5]
        for row in result:
            print("D::", row.distance, row.title, row.summary)
        # print(res)
        assert True

    def test_average(self):
        # Also supports MaxInnerProduct and CosineDistance
        # Get the distance
        query = "alien invasion"
        query_vector = encoder.encode(query).tolist()
        result = Company.objects.aggregate(Avg('embedding'))
        print(result)
        # for row in result:
        #     print("D::", row.distance, row.title, row.summary)
        # print(res)
        assert True


# QDRANT Example
    # score: 0.5700933298008086 {'name': 'The War of the Worlds', 'description': 'A Martian invasion of Earth throws humanity into chaos.', 'author': 'H.G. Wells', 'year': 1898}
    # score: 0.5040467286968837 {'name': "The Hitchhiker's Guide to the Galaxy", 'description': 'A comedic science fiction series following the misadventures of an unwitting human and his alien friend.', 'author': 'Douglas Adams', 'year': 1979}
    # score: 0.4590294360605083 {'name': 'The Three-Body Problem', 'description': 'Humans encounter an alien civilization that lives in a dying system.', 'author': 'Liu Cixin', 'year': 2008}
# PGVector
#     The War of the Worlds A Martian invasion of Earth throws humanity into chaos.
#     The Hitchhiker's Guide to the Galaxy A comedic science fiction series following the misadventures of an unwitting human and his alien friend.
#     The Three-Body Problem Humans encounter an alien civilization that lives in a dying system.
