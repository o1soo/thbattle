# -*- coding: utf-8 -*-
from __future__ import absolute_import

# -- stdlib --
from collections import defaultdict
from weakref import WeakSet
import logging

# -- third party --
from gevent import Greenlet, Timeout
from gevent.queue import Queue

# -- own --
from account import Account
from endpoint import Endpoint, EndpointDied
from game import Gamedata
from options import options
from server.core.state import ServerState
from utils import BatchList, log_failure


# -- code --
log = logging.getLogger('server.core.endpoint')


def _record_gamedata(client, tag, data):
    from server.core.game_manager import GameManager
    manager = GameManager.get_by_user(client)
    manager.record_user_gamedata(client, tag, data)


class Client(Endpoint, Greenlet):
    def __init__(self, sock, addr):
        Endpoint.__init__(self, sock, addr)
        Greenlet.__init__(self)
        self.observers = BatchList()
        self.gamedata = Gamedata()
        self.cmd_listeners = defaultdict(WeakSet)
        self.current_game = None

    @log_failure(log)
    def _run(self):
        self.account = None

        # ----- Banner -----
        from settings import VERSION
        self.write(['thbattle_greeting', (options.node, VERSION)])
        # ------------------

        self.state = 'connected'
        while True:
            try:
                hasdata = False
                with Timeout(90, False):
                    cmd, data = self.read()
                    hasdata = True

                if not hasdata:
                    self.close()
                    # client should send heartbeat periodically
                    raise EndpointDied

                if cmd == 'gamedata':
                    self.gamedata.feed(data)
                else:
                    self.handle_command(cmd, data)

            except EndpointDied:
                self.gbreak()
                break

            except Exception:
                log.exception("Error occurred when handling client command")

        # client died, do clean ups
        self.handle_drop()

    def close(self):
        Endpoint.close(self)
        self.kill(EndpointDied)

    def __repr__(self):
        acc = self.account
        if not acc:
            return Endpoint.__repr__(self)

        return '%s:%s:%s' % (
            self.__class__.__name__,
            self.address[0],
            acc.username.encode('utf-8'),
        )

    def __data__(self):
        return dict(
            account=self.account,
            state=self.state,
        )

    def __eq__(self, other):
        return self.account is other.account

    def listen_command(self, *cmds):
        listeners_set = self.cmd_listeners
        q = Queue(100)
        for cmd in cmds:
            listeners_set[cmd].add(q)

        return q

    def handle_command(self, cmd, data):
        f = getattr(self, 'command_' + str(cmd), None)
        if not f:
            listeners = self.cmd_listeners[cmd]
            if listeners:
                [l.put(data) for l in listeners]
                return

            log.debug('No command %s', cmd)
            self.write(['invalid_command', [cmd, data]])
            return

        if not isinstance(data, (list, tuple)):
            log.error('Malformed command: %s %s', cmd, data)
            return

        n = f.__code__.co_argcount - 1
        if n != len(data):
            log.error(
                'Command "%s" argcount mismatch, expect %s, got %s',
                cmd, n, len(data)
            )
        else:
            f(*data)

    def handle_drop(self):
        if self.state not in ('connected', 'hang'):
            ServerState.lobby.exit_game(self, is_drop=True)

        if self.state != 'connected':
            ServerState.lobby.user_leave(self)

    def gexpect(self, tag, blocking=True):
        tag, data = self.gamedata.gexpect(tag, blocking)
        tag and _record_gamedata(self, tag, data)
        return tag, data

    def gwrite(self, tag, data):
        log.debug('GAME_WRITE: %s -> %s', self.account.username, repr([tag, data]))

        _record_gamedata(self, tag, data)

        encoded = self.encode(['gamedata', [tag, data]])
        self.raw_write(encoded)
        self.observers and self.observers.raw_write(encoded)

    def gbreak(self):
        return self.gamedata.gbreak()

    def gclear(self):
        self.gamedata = Gamedata()

    # --------- Handlers ---------
    def command_auth(self, login, password):
        if self.state != 'connected' or self.account:
            self.write(['invalid_command', ['auth', '']])
            return

        acc = Account.authenticate(login, password)
        if acc:
            self.account = acc
            if not acc.available():
                self.write(['auth_result', 'not_available'])
                self.close()
            else:
                self.write(['auth_result', 'success'])
                self.account = acc
                ServerState.lobby.user_join(self)

        else:
            self.write(['auth_result', 'invalid_credential'])

    def command_lobby(self, cmd, args):
        ServerState.lobby.process_lobby_command(self, cmd, args)

    def command_heartbeat(self):
        pass

    # --------- End handlers ---------


class DroppedClient(Client):
    read = write = raw_write = gclear = lambda *a, **k: None

    def __init__(self, client=None):
        client and self.__dict__.update(client.__dict__)

    def __data__(self):
        return dict(
            account=self.account,
            state='left',
        )

    def gwrite(self, tag, data):
        _record_gamedata(self, tag, data)

    def gexpect(self, tag, blocking=True):
        raise EndpointDied

    @property
    def state(self):
        return 'dropped'

    @state.setter
    def state(self, val):
        pass


class NPCClient(Client):
    read = write = raw_write = gclear = lambda *a, **k: None
    state = property(lambda: 'ingame')

    def __init__(self, name):
        acc = Account.build_npc_account(name)
        self.account = acc

    def __data__(self):
        return dict(
            account=self.account,
            state='ingame',
        )

    def gwrite(self, tag, data):
        pass

    def gexpect(self, tag, blocking=True):
        raise Exception('Should not be called!')