import mysql.connector


class AMSQL:
    """Class that provides static methods for mysql connectors"""
    settings: dict = {}
    conn = None

    @staticmethod
    def get_conn():
        """Get or create a new buffered DB cursor connection"""
        if not AMSQL.conn:
            AMSQL.conn = mysql.connector.connect(**AMSQL.settings)

        if not AMSQL.conn.is_connected():
            AMSQL.conn.close()
            AMSQL.conn = mysql.connector.connect(**AMSQL.settings)

        return AMSQL.conn

    @staticmethod
    def set_settings(settings: dict):
        """Set the global settings for the class"""
        AMSQL.settings = {
            'host': settings.get('host', 'mysql-db'),
            'user': settings.get('user', 'root'),
            'password': settings.get('password', ''),
            'db': settings.get('db', None)
        }