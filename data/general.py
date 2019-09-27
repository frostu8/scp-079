import sqlite3
from data import (
    server,
    user
)

from typing import (
    Optional,
    Tuple
)


class DataManager(object):
    SERVER_FLAGS = 0

    def __init__(self, db: str):
        self.filename = db

    # HELPERS

    @staticmethod
    def get_serial(user_id: int, server_id: int) -> str:
        return str(user_id) + '_' + str(server_id)

    @staticmethod
    def split_serial(serial: str) -> Tuple[int, int]:
        split_serial = serial.split('_')

        try:
            if len(split_serial) == 2:
                user_id = int(split_serial[0])
                server_id = int(split_serial[1])

                return user_id, server_id
        except ValueError:
            pass

        raise ValueError("Serial is malformed!")

    # ACCESSORS

    def get_server(self, id: int) -> server.Server:
        # get a connection
        conn = sqlite3.Connection(self.filename)

        # try to get the server
        serv = conn.execute('SELECT * FROM servers WHERE server_id=?', (id,)).fetchone()

        if serv is None:
            # create new server instance
            return self.create_server(id, conn)
        else:
            # found the server!
            return server.Server(conn, serv[0], serv[1], serv[2], serv[3], serv[4], serv[5])

    def create_server(self, id: int, conn: Optional[sqlite3.Connection]) -> server.Server:
        # get a connection if none has been passed
        if conn is None:
            conn = sqlite3.Connection(self.filename)

        # try to create a server object
        # use defaults
        allowed_channels = ''
        self_roles = ''
        level_roles = ''
        auto_role = 0
        flags = self.SERVER_FLAGS

        # add the entry
        conn.execute('INSERT INTO servers VALUES (?,?,?,?,?,?)',
                     (id, allowed_channels, self_roles, level_roles, auto_role, flags))

        # return a representation
        return server.Server(conn, id, allowed_channels, self_roles, level_roles, auto_role, flags)

    def get_server_user(self, server_id: int, user_id: int) -> user.ServerUser:
        # try to find the user
        # get a new connection
        conn = sqlite3.Connection(self.filename)  # MAGIC VALUE

        # find the user
        u = conn.execute('SELECT * FROM exp WHERE serial=?', (self.get_serial(server_id, user_id),)).fetchone()
        if u is None:
            # user does not exist! create a new user
            return self.create_server_user(server_id, user_id, conn)
        else:
            # separate the serial
            uid, sid = self.split_serial(u[0])

            # create a new user object!
            # warning! this is a hotfix, and should be changed immediately.
            return user.ServerUser(conn, uid, 'not implemented', 0, sid, u[1], u[2], u[3])

    def create_server_user(self, server_id: int, user_id: int, conn: Optional[sqlite3.Connection]) -> user.ServerUser:
        if conn is None:
            conn = sqlite3.Connection(self.filename)  # MAGIC VALUE

        # set some variables
        level = 0
        total_exp = 0
        cooldown = 0

        # create the user
        conn.execute('INSERT INTO exp VALUES (?,?,?,?)', (self.get_serial(server_id, user_id), level, total_exp, cooldown))

        conn.commit()

        # return a representation
        # warning! this is a hotfix, and should be changed immediately.
        return user.ServerUser(conn, user_id, 'not implemented', 0, server_id, level, total_exp, cooldown)
