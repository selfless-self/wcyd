from blacksheep import FromJSON, FromQuery, FromRoute, Response
from blacksheep.server.authorization import allow_anonymous
from blacksheep.server.controllers import get, post
from blacksheep.server.openapi.common import ContentInfo, ResponseInfo

from src.abc.use_case.connect_node_use_case import ConnectNodeUseCase
from src.abc.use_case.find_node_use_case import FindNodeUseCase
from src.api.controller.base_controller import BaseController
from src.api.docs import docs, unsecure_handler
from src.api.io_type.node_io import NodeCreationRequest, NodeModel


class NodeController(BaseController):

    ROUTE = "/nodes"

    def __init__(self, connect_use_case: ConnectNodeUseCase, find_node_use_case: FindNodeUseCase) -> None:
        self._connect_use_case = connect_use_case
        self._find_use_case = find_node_use_case

    @docs(
        tags=["nodes"],
        summary="register provided node as neighbor",
        responses={201: "registeration done successfully", 409: "already connected"},
        on_created=unsecure_handler,
    )
    @allow_anonymous()
    @post("/")
    async def register_node(self, request_body: FromJSON[NodeCreationRequest]) -> Response:

        await self._connect_use_case.execute(request_body.value.identifier, request_body.value.endpoint)

        return self.created()

    @docs(
        tags=["nodes"],
        summary="get information of a node within the network which this node is a part of",
        responses={
            200: ResponseInfo("information of the queried node", content=[ContentInfo(NodeModel)]),
            404: "not found",
            409: "already answered",
        },
        on_created=unsecure_handler,
    )
    @allow_anonymous()
    @get("/{node_identifier}")
    async def get_node(self, node_identifier: FromRoute[str], questioners: FromQuery[set[str]]) -> Response:

        node = await self._find_use_case.execute(node_identifier.value, questioners.value)

        return self.ok(NodeModel(identifier=node.identifier, endpoint=str(node.endpoint)))
