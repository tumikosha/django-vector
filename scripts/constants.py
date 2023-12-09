from scripts import proxies

MONGO_URI = "mongodb://admin:20_mongo_20#@127.0.0.1:27017/admin"
DENIED = ['Forbidden', "Website Builder", "hosting"]
proxy_nest = proxies.RotatingProxy("/home/tumi/instant.proxy")



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
