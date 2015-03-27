from PySide import QtNetwork
import pytest
import mock

from src.games_service import GamesService
from src.lobbyconnection import LobbyConnection, PlayersOnline
from src.FaLobbyServer import FALobbyServer


@pytest.fixture()
def test_game_info():
    return {
        'title': 'Test game',
        'gameport': '8000',
        'access': 'public',
        'mod': 'faf',
        'version': None,
        'mapname': 'scmp_007',
        'password': None,
        'lobby_rating': 1,
        'options':  []
    }

@pytest.fixture()
def test_game_info_invalid():
    return {
        'title': 'Tittle with non ASCI char \xc3',
        'gameport': '8000',
        'access': 'public',
        'mod': 'faf',
        'version': None,
        'mapname': 'scmp_007',
        'password': None,
        'lobby_rating': 1,
        'options':  []
    }


@pytest.fixture(scope='function')
def connected_socket():
    sock = mock.Mock(spec=QtNetwork.QTcpSocket)
    sock.state = mock.Mock(return_value=3)
    sock.isValid = mock.Mock(return_value=True)
    return sock


@pytest.fixture
def mock_lobby_server(db):
    users = PlayersOnline()
    hyper_container = GamesService(users, db)
    return FALobbyServer(users, hyper_container, db)


def test_command_game_host_calls_host_game(connected_socket,
                                           mock_lobby_server,
                                           test_game_info,
                                           players):
    mock_lobby_server.games.create_game = mock.Mock()
    server_thread = LobbyConnection(connected_socket, mock_lobby_server)
    server_thread.player = players.hosting
    server_thread.command_game_host(test_game_info)
    mock_lobby_server.games.create_game\
        .assert_called_with(test_game_info['access'],
                            test_game_info['mod'],
                            server_thread.player,
                            test_game_info['title'],
                            test_game_info['gameport'],
                            test_game_info['mapname'],
                            test_game_info['version'])


def test_command_game_host_calls_host_game_invalid_title(connected_socket,
                                           mock_lobby_server,
                                           test_game_info_invalid):
    server_thread = LobbyConnection(connected_socket, mock_lobby_server)
    server_thread.sendJSON = mock.Mock()
    mock_lobby_server.games.create_game = mock.Mock()
    server_thread.command_game_host(test_game_info_invalid)
    assert mock_lobby_server.games.create_game.mock_calls == []
    server_thread.sendJSON.assert_called_with(dict(command="notice", style="error", text="Non-ascii characters in game name detected."))

# ModVault
# TODO: check outcome of the test, nut only running code
def test_mod_vault_start(connected_socket,
                         mock_lobby_server):
    server_thread = LobbyConnection(connected_socket, mock_lobby_server)
    server_thread.command_modvault({'type': 'start'})

# database releaed
def test_mod_vault_like(connected_socket,
                         mock_lobby_server):
    server_thread = LobbyConnection(connected_socket, mock_lobby_server)
    server_thread.command_modvault({'type': 'like',
                                    'uid': 'something_invalid'})

def test_mod_vault_like(connected_socket,
                         mock_lobby_server):
    server_thread = LobbyConnection(connected_socket, mock_lobby_server)
    server_thread.command_modvault({'type': 'download',
                                    'uid': None})

def test_mod_vault_addcomment(connected_socket,
                        mock_lobby_server):
    server_thread = LobbyConnection(connected_socket, mock_lobby_server)
    server_thread.command_modvault({'type': 'addcomment'})

def test_mod_vault_invalid_type(connected_socket,
                        mock_lobby_server):
    server_thread = LobbyConnection(connected_socket, mock_lobby_server)
    server_thread.command_modvault({'type': 'DragonfireNegativeTest'})

def test_mod_vault_no_type(connected_socket,
                         mock_lobby_server):
    server_thread = LobbyConnection(connected_socket, mock_lobby_server)
    server_thread.command_modvault({'invalidKey': None}
