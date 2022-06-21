import requests


class ElasticIndex:
    def __init__(self, url: str, port: int):
        self.url = url
        self.port = port
        self.index = ''

    def create_index(self, index_name):
        requests.put(
            f"{self.url}:{self.port}/{index_name}",
            data=self.index,
            headers={'content-type': 'application/json', 'charset': 'UTF-8'}
        )


class MovieIndex(ElasticIndex):
    def __init__(self, url: str, port: int):
        super().__init__(url, port)
        self.index = """{
  "settings": {
    "refresh_interval": "1s",
    "analysis": {
      "filter": {
        "english_stop": {
          "type":       "stop",
          "stopwords":  "_english_"
        },
        "english_stemmer": {
          "type": "stemmer",
          "language": "english"
        },
        "english_possessive_stemmer": {
          "type": "stemmer",
          "language": "possessive_english"
        },
        "russian_stop": {
          "type":       "stop",
          "stopwords":  "_russian_"
        },
        "russian_stemmer": {
          "type": "stemmer",
          "language": "russian"
        }
      },
      "analyzer": {
        "ru_en": {
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "english_stop",
            "english_stemmer",
            "english_possessive_stemmer",
            "russian_stop",
            "russian_stemmer"
          ]
        }
      }
    }
  },
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "id": {
        "type": "keyword"
      },
      "imdb_rating": {
        "type": "float"
      },
      "genre": {
        "type": "keyword"
      },
      "title": {
        "type": "text",
        "analyzer": "ru_en",
        "fields": {
          "raw": {
            "type":  "keyword"
          }
        }
      },
      "description": {
        "type": "text",
        "analyzer": "ru_en"
      },
      "director": {
        "type": "text",
        "analyzer": "ru_en"
      },
      "actors_names": {
        "type": "text",
        "analyzer": "ru_en"
      },
      "writers_names": {
        "type": "text",
        "analyzer": "ru_en"
      },
      "actors": {
        "type": "nested",
        "dynamic": "strict",
        "properties": {
          "id": {
            "type": "keyword"
          },
          "name": {
            "type": "text",
            "analyzer": "ru_en"
          }
        }
      },
      "writers": {
        "type": "nested",
        "dynamic": "strict",
        "properties": {
          "id": {
            "type": "keyword"
          },
          "name": {
            "type": "text",
            "analyzer": "ru_en"
          }
        }
      }
    }
  }
}"""


class PersonIndex(ElasticIndex):
    def __init__(self, url: str, port: int):
        super().__init__(url, port)
        self.index = """{
            "mappings": {
                "properties": {
                    "id": {
                "type": "keyword"
                },
                "name": {
                "type": "text"}
                }
            }
        }"""


class GenresIndex(ElasticIndex):
    def __init__(self, url: str, port: int):
        super().__init__(url, port)
        self.index = """{
            "mappings": {
                "properties": {
                    "id": {
                "type": "keyword"
                },
                "name": {
                "type": "text"}
                }
            }
        }"""
