import os

from util.common import string_2_uuid

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "general.settings")
# import django
# django.setup()
from app import setup

setup()

from app.models import Company
from sentence_transformers import SentenceTransformer

encoder = SentenceTransformer("all-MiniLM-L6-v2")

dummy_list = [
    {"domain": "microsoft.com", "title": "Microsoft",
     "summary": " Operating systems and office software"},
    {"domain": "ibm.com", "title": "IBM",
     "summary": "International Business Machines & Database Management Systems"},
    {"domain": "apple.com", "title": "Apple",
     "summary": "gadgets and computers manufacturer "},
    {"domain": "tesla.com", "title": "Tesla",
     "summary": "cars & spaceships, also crypto-fraud"},
    {"domain": "renaultgroup.com", "title": "Tesla",
     "summary": "cars manufacturer"},
    {"domain": "SINGULARIS.AI", "title": "SINGULARIS.AI",
     "summary": "Community of ML/DL/AI professionals"},
    {"domain": "perplexity.ai", "title": "Perplexity.ai - AI Companion",
     "summary": "The world is full of noise, and we believe people need a way to sift through it to find what's truly relevant. We fill this gap by offering a more engaging, reliable, and intelligent way to search and discover information. By pioneering in-house AI technology, we deliver answers quickly and reliably."},
    {"domain": "lakera.ai", "title": "The AI Security Company.",
     "summary": "Lakera empowers developers to confidently build secure AI applications and deploy them at scale."},


]

for doc in dummy_list:
    vector = encoder.encode(doc['summary']).tolist()
    company, created = Company.objects.update_or_create(
        id=string_2_uuid(doc['domain']),
        defaults={
            "title": doc['title'],
            "domain": doc['domain'],
            "summary": doc['summary'],
            "embedding": vector
        }
    )
    company.save()
print("Companies count in DB:", Company.objects.count())
print("Done...")

