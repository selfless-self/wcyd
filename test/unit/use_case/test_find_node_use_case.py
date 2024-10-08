from test.unit.mock.infra.mock_node_client import MockNodeClient
from test.unit.mock.infra.mock_node_repo import MockNodeRepo
from test.unit.utils import add_external_neighbor, add_internal_neighbor
from unittest import IsolatedAsyncioTestCase

from pydantic import AnyUrl

from src.settings import NodeSettings
from src.type.exception import AlreadyAnswered, DoesNotExist
from src.use_case.find_node import FindNode


class TestFindNodeUseCase(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self._settings = NodeSettings(IDENTIFIER="test-node", ENDPOINT=AnyUrl("http://localhost:44777"))
        self._mock_node_client = MockNodeClient()
        self._mock_node_repo = MockNodeRepo()
        self._use_case = FindNode(self._settings, self._mock_node_repo, self._mock_node_client)

    async def test_already_answered(self) -> None:
        with self.assertRaises(AlreadyAnswered):
            await self._use_case.execute("not-being-tested", {self._settings.IDENTIFIER})

    async def test_direct_neighbor(self) -> None:
        neighbor_identifier = "neighbor-identifier"
        endpoint = AnyUrl("http://neighbor:80")
        add_internal_neighbor(self._mock_node_repo, neighbor_identifier, endpoint)

        node = await self._use_case.execute(neighbor_identifier, {"not-being-tested"})

        self.assertEqual(node.identifier, neighbor_identifier)
        self.assertEqual(node.endpoint, endpoint)

    async def test_external_neighbor(self) -> None:
        direct_neighbor_identifier = "direct-neighbor-identifier"
        add_internal_neighbor(self._mock_node_repo, direct_neighbor_identifier, AnyUrl("http://not-bing-tested:80"))

        far_neighbor_identifier = "far-neighbor-identifier"
        far_neighbor_endpoint = AnyUrl("http://far-neighbor:80")
        add_external_neighbor(
            self._mock_node_client,
            direct_neighbor_identifier,
            far_neighbor_identifier,
            far_neighbor_endpoint,
        )

        node = await self._use_case.execute(far_neighbor_identifier, {"not-being-tested"})

        self.assertEqual(node.identifier, far_neighbor_identifier)
        self.assertEqual(node.endpoint, far_neighbor_endpoint)

    async def test_absent_identifier(self) -> None:
        with self.assertRaises(DoesNotExist):
            await self._use_case.execute("absent-identifier", {"not-being-tested"})
