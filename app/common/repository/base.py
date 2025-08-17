from typing import TypeVar, Any, Generic, Type, List, Optional
from abc import ABC, abstractmethod
from beanie import Document
import torch
import numpy as np
from pydantic import BaseModel, Field
from pymilvus import connections
from pymilvus import Collection as MilvusCollection


BeanieDocument = TypeVar('BeanieDocument', bound=Document)
class MongoBaseRepository(Generic[BeanieDocument]):
    def __init__(self, collection: Type[BeanieDocument]):
        self.collection = collection

    async def find(self, *args, **kwargs) -> list[BeanieDocument]:
        """
        Find documents in the collection.
        """
        return await self.collection.find(*args, **kwargs).to_list(length=None)


    async def find_pipeline(self, pipeline: list[dict[str, Any]]) -> list[BeanieDocument]:
        """
        Find documents using an aggregation pipeline.
        """
        result = await self.collection.aggregate(aggregation_pipeline=pipeline).to_list(length=None)

        return [self.collection(**item) for item in result]

    async def get_all(self) -> list[BeanieDocument]:
        """
        Get all documents in the collection.
        """
        return await self.collection.find_all().to_list(length=None)


class MilvusBaseRepository(ABC):

    def __init__(
        self,
        collection: MilvusCollection,
    ):

        self.collection = collection
