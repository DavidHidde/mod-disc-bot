import mysql.connector

from ...mdb_cog import MDBCog


class MySQLCog(MDBCog):
    """Static MySQL connector provider"""
    _name: str = 'mysql'
    __conn = None

    @property
    def connection(self) -> mysql.connector:
        """Get or create a new buffered DB connection connection"""
        if not self.__conn:
            self.__conn = mysql.connector.connect(**self._settings)

        # Reconnect
        if not self.__conn.is_connected():
            self.__conn.close()
            self.__conn = mysql.connector.connect(**self._settings)

        return self.__conn

    @property
    def default_settings(self) -> dict:
        """Get all configurable settings of a cog"""
        return {
            **super().default_settings,
            'host': 'mysql-db',
            'user': None,
            'password': None,
            'db': None
        }

    def get_required_extensions(self) -> list[str]:
        """Get a list of extensions that are required to run this cog"""
        return []
