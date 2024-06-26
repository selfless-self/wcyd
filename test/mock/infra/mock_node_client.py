from typing import TypedDict
from src.abc.infra.inode_client import INodeClient
from src.type.alias import EndPoint, Identifier, PublicKey
from src.type.entity import Node
from src.type.exception import AlreadyAnswered, AlreadyExists, NotFound


class MockClientNodeObjectModel(TypedDict):
    endpoint: str
    public_key: str


class MockNodeClient(INodeClient):

    def __init__(self) -> None:
        self._mem_storage: dict[Identifier, dict[Identifier, MockClientNodeObjectModel]] = dict()

    async def get_neighbors(self, host: Node) -> list[Node]:
        try:
            return [
                Node(
                    identifier=k,
                    endpoint=v['endpoint'], # type: ignore
                    public_key=v['public_key']
                ) for k, v in self._mem_storage[host.identifier].items()
            ]
        except KeyError as e:
            raise Exception from e

    async def connect(self, host: Node, identifier: Identifier, endpoint: EndPoint, public_key: PublicKey) -> None:
        if host.identifier in self._mem_storage:
            raise AlreadyExists

        self._mem_storage[host.identifier] = dict()

    async def find(self, host: Node, questioners: set[Identifier], identifier: Identifier) -> Node:
        if host.identifier in questioners:
            raise AlreadyAnswered

        try:
            if (obj := self._mem_storage[host.identifier].get(identifier)) is None:
                raise NotFound
            return Node(identifier=identifier, endpoint=obj['endpoint'], public_key=obj['public_key']) # type: ignore
        except KeyError as e:
            raise Exception from e

