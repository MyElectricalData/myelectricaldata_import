from json import loads

from rauth import OAuth2Service


class ExampleOAuth2Client:
    def __init__(self, client_id, client_secret):
        self.access_token = None

        self.service = OAuth2Service(
            name="foo",
            client_id=client_id,
            client_secret=client_secret,
            access_token_url="http://api.example.com/oauth/access_token",
            authorize_url="http://api.example.com/oauth/access_token",
            base_url="http://api.example.com/",
        )

        self.get_access_token()

    def get_access_token(self):
        data = {
            "code": "bar",  # specific to my app
            "grant_type": "client_credentials",  # generally required!
        }

        session = self.service.get_auth_session(data=data, decoder=loads)

        self.access_token = session.access_token
