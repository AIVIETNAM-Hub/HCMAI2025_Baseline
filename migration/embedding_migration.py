import torch
import numpy as np
from pymilvus import Collection, connections, FieldSchema, CollectionSchema, DataType, utility
from typing import Optional
from tqdm import tqdm
import argparse

import sys
import os
ROOT_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)
sys.path.insert(0, ROOT_FOLDER)


from app.core.settings import KeyFrameIndexMilvusSetting


class MilvusEmbeddingInjector:
    def __init__(
        self,
        setting: KeyFrameIndexMilvusSetting,
        collection_name: str,
        host: str = "localhost",
        port: str = "19530",
        user: str = "",
        password: str = "",
        db_name: str = "default",
        alias: str = "default"

    ):
        self.setting = setting
        self.collection_name = collection_name
        self.alias = alias

        self._connect(host, port, user, password, db_name, alias)

    def _connect(self, host: str, port: str, user: str, password: str, db_name: str, alias: str):

        if connections.has_connection(alias):
            connections.remove_connection(alias)

        conn_params = {
            "host": host,
            "port": port,
            "db_name": db_name
        }

        if user and password:
            conn_params["user"] = user
            conn_params["password"] = password

        connections.connect(alias=alias, **conn_params)
        print(f"Connected to Milvus at {host}:{port}")



    def create_collection(self, embedding_dim: int, index_params: Optional[dict] = None):
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=embedding_dim)
        ]

        schema = CollectionSchema(fields, f"Collection for {self.collection_name} embeddings")

        collection = Collection(self.collection_name, schema, using=self.alias)
        print(f"Created collection '{self.collection_name}' with dimension {embedding_dim}")

        if index_params is None:
            index_params = {
                "metric_type": self.setting.METRIC_TYPE,
                "index_type": self.setting.INDEX_TYPE,
            }

        collection.create_index("embedding", index_params)
        print("Created index for embedding field")

        return collection

    def inject_embeddings(
        self,
        embedding_file_path: str,
        batch_size: int = 10000,
    ):
        print(f"Loading embeddings from {embedding_file_path}")
        embeddings = torch.load(embedding_file_path, weights_only=False)

        if isinstance(embeddings, torch.Tensor):
            embeddings = embeddings.cpu().numpy()

        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)

        num_vectors, embedding_dim = embeddings.shape
        print(f"Loaded {num_vectors} embeddings with dimension {embedding_dim}")



        if utility.has_collection(self.collection_name, using=self.alias):
            print(f"Dropping existing collection '{self.collection_name}' before creation...")
            utility.drop_collection(self.collection_name, using=self.alias)

        collection = self.create_collection(embedding_dim)



        print(f"Inserting {num_vectors} embeddings in batches of {batch_size}")

        for i in tqdm(range(0, num_vectors, batch_size), desc="Inserting batches"):
            end_idx = min(i + batch_size, num_vectors)
            batch_embeddings = embeddings[i:end_idx].tolist()

            batch_ids = list(range(i, end_idx))
            entities = [batch_ids, batch_embeddings]
            collection.insert(entities)

        collection.flush()
        print("Data flushed to disk")

        collection.load()
        print("Collection loaded for search")

        return collection

    def get_collection_info(self):

        collection = Collection(self.collection_name, using=self.alias)
        num_entities = collection.num_entities
        print(f"Collection '{self.collection_name}' has {num_entities} entities")
        return num_entities


    def disconnect(self):
        if connections.has_connection(self.alias):
            connections.remove_connection(self.alias)
            print("Disconnected from Milvus")


def inject_embeddings_simple(
    embedding_file_path: str,
    setting: KeyFrameIndexMilvusSetting
):
    injector = MilvusEmbeddingInjector(
        setting=setting,
        collection_name=setting.COLLECTION_NAME,
        host=setting.HOST,
        port=setting.PORT
    )


    injector.inject_embeddings(
        embedding_file_path=embedding_file_path,
        batch_size=setting.BATCH_SIZE
    )
    count = injector.get_collection_info()
    print(f"Successfully injected embeddings! Total entities: {count}")



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Migrate embedding to Milvus.")
    parser.add_argument(
        "--file_path", type=str, help="Path to embedding pt."
    )
    args = parser.parse_args()

    setting =  KeyFrameIndexMilvusSetting()
    inject_embeddings_simple(
        embedding_file_path=args.file_path,
        setting=setting
    )