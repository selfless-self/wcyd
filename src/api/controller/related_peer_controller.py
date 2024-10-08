from blacksheep import FromRoute, Response
from blacksheep.server.authorization import allow_anonymous
from blacksheep.server.controllers import get
from blacksheep.server.openapi.common import ContentInfo, ResponseInfo

from src.abc.use_case.add_peer_use_case import AddPeerUseCase
from src.abc.use_case.find_peer_use_case import FindPeerUseCase
from src.api.controller.base_controller import BaseController
from src.api.docs import docs, unsecure_handler
from src.api.io_type.peer_io import PeerModel
from src.type.internal import UniversalPeerIdentifier


class RelatedPeerController(BaseController):

    ROUTE = "nodes/{node_identifier}/peers"

    def __init__(self, add_use_case: AddPeerUseCase, find_use_case: FindPeerUseCase) -> None:
        self._add_use_case = add_use_case
        self._find_peer_use_case = find_use_case

    @docs(
        tags=["peers"],
        summary="get information of a peer within the network which this node is a part of",
        responses={
            200: ResponseInfo("information of the queried peer", content=[ContentInfo(PeerModel)]),
            404: "not found",
        },
        on_created=unsecure_handler,
    )
    @allow_anonymous()
    @get("/{peer_identifier}")
    async def get_peer(self, node_identifier: FromRoute[str], peer_identifier: FromRoute[str]) -> Response:

        peer = await self._find_peer_use_case.execute(
            UniversalPeerIdentifier(node=node_identifier.value, peer=peer_identifier.value)
        )

        return self.ok(PeerModel(identifier=peer.identifier, keyring=peer.keyring))
