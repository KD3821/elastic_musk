configurations = {
    "settings": {
        "index": {"number_of_replicas": 2},
        "analysis": {
            "filter": {
                "ngram_filter": {
                    "type": "edge_ngram",
                    "min_gram": 2,
                    "max_gram": 15,
                },
            },
            "analyzer": {
                "ngram_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "ngram_filter"],
                },
            },
        },
    },
    "mappings": {
        "properties": {
            "text": {
                "type": "text",
                "analyzer": "standard",
                "fields": {
                    "keyword": {"type": "keyword"},
                    "ngrams": {"type": "text", "analyzer": "ngram_analyzer"},
                },
            },
            "author": {"type": "text"},
        },
    },
}