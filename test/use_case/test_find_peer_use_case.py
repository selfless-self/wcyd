from unittest import IsolatedAsyncioTestCase

from pydantic import AnyUrl

from src.settings import NodeSettings
from src.type.enum import AsymmetricCryptographyProvider
from src.type.internal import PublicKey, UniversalPeerIdentifier
from src.use_case.find_node import FindNode
from src.use_case.find_peer import FindPeer
from test.mock.infra.mock_node_client import MockNodeClient
from test.mock.infra.mock_node_repo import MockNodeRepo
from test.mock.infra.mock_peer_repo import MockPeerRepo
from test.utils import add_external_peer, add_internal_peer, add_internal_neighbor


class TestFindPeerUseCase(IsolatedAsyncioTestCase):

    SAMPLE_PUBLIC_KEY_VALUE = 'Ov4eCC6vqpcBbswXLfn0aRD9TvafYB+BVprg7eyv03o='

    def setUp(self) -> None:
        self._settings = NodeSettings(
            IDENTIFIER='test-node',
            ENDPOINT=AnyUrl('http://localhost:44777')
        )
        self._mock_node_client = MockNodeClient()
        self._mock_peer_repo = MockPeerRepo(self._settings)
        self._mock_node_repo = MockNodeRepo()
        self._find_node_use_case = FindNode(self._settings, self._mock_node_repo, self._mock_node_client)
        self._use_case = FindPeer(
            self._settings,
            self._mock_node_client,
            self._mock_peer_repo,
            self._find_node_use_case
        )

    async def test_normal(self) -> None:
        existing_peer_identifier = 'existing-peer-identifier'
        add_internal_peer(
            self._mock_peer_repo,
            existing_peer_identifier,
            PublicKey(provider=AsymmetricCryptographyProvider.NACL, value=TestFindPeerUseCase.SAMPLE_PUBLIC_KEY_VALUE)
        )

        peer = await self._use_case.execute(
            UniversalPeerIdentifier(node=self._settings.IDENTIFIER, peer=existing_peer_identifier)
        )

        self.assertEqual(peer.identifier.peer, existing_peer_identifier)
        self.assertEqual(peer.identifier.node, self._settings.IDENTIFIER)

    async def test_external(self) -> None:
        neighbor_identifier = 'neighbor-identifier'
        add_internal_neighbor(self._mock_node_repo, neighbor_identifier, AnyUrl('http://not-being-tested:80'))

        external_peer_identifier = 'external-peer-identifier'
        add_external_peer(
            self._mock_node_client,
            neighbor_identifier,
            external_peer_identifier,
            PublicKey(provider=AsymmetricCryptographyProvider.NACL, value=TestFindPeerUseCase.SAMPLE_PUBLIC_KEY_VALUE)
        )

        peer = await self._use_case.execute(
            UniversalPeerIdentifier(node=neighbor_identifier, peer=external_peer_identifier)
        )

        self.assertEqual(peer.identifier.node, neighbor_identifier)
        self.assertEqual(peer.identifier.peer, external_peer_identifier)
