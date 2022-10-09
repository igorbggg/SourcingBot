class TokenService:
    """
    Implement TokenService class- a set of methods
    to get and store token information
    """

    def __init__(self, token_file_path: str) -> object:
        self.__token_file_path = token_file_path
        self.__token = None
        self.get_token_from_file()

    def get_token_from_file(self) -> str | None:
        """
        :return: token, or None if not available
        """
        with open(self.__token_file_path, 'r') as token_file:
            token = token_file.readline().replace('\n', '')
        if not token or len(token) < 1:
            raise ValueError('Provided file has no token!')
        self.token = token
        return self.token

    @property
    def token(self) -> str | None:
        assert isinstance(self.__token, object)
        return self.__token

    @token.setter
    def token(self, value: str):
        self.__token = value