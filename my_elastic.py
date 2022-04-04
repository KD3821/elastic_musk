from elasticsearch import Elasticsearch
import json


es = Elasticsearch("http://127.0.0.1:9200")


def load_json(file):
    with open(file) as f:
        data = json.load(f)
        return data


def add_to_index(file, index_name):
    es.indices.create(index=str(index_name))
    data = load_json(file)
    doc_id = 0
    for i in data:
        doc_id += 1
        es.index(index=str(index_name), id=doc_id, body=i)
    return 'index "'+str(index_name)+'" added!'


def show_res(index_name, search_body):
    total_res = []
    result = es.search(index=str(index_name), body=search_body)
    for i in range(len(result['hits']['hits'])):
        total_res.append([result['hits']['hits'][i]['_score'], result['hits']['hits'][i]['_source']])
    return total_res


# body = {
#     "from": 0,
#     "size": 18,
#     "query": {
#         "bool": {
#             "must": {
#                 "match": {
#                     "text": "doge"
#                 }
#             },
#             "must": {
#                 "match": {
#                     "text": "coin"
#                 }
#             }
#         }
#     }
# }
# body = {
#     "from":0,
#     "size":4,
#     "query": {
#         "bool": {
#             "must": {
#                 "match": {
#                     "text": "score"
#                 }
#             }
#         }
#     }
# }


# new_index = add_to_index('short-musk.json', '03apr')
# total = show_res('03apr', body)



# if __name__ == '__main__':
#     print(total)
