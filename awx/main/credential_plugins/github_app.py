import base64
import collections
import json
import time

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.hashes import SHA256


# É necessário adicionar a seguinte linha no ficheiro setup.cfg
#     github_app = awx.main.credential_plugins.github_app:github_plugin
# em [options.entry_points]
#    awx.credential_plugins =
# para que o plugin seja reconhecido pelo AWX.


# Esta é uma classe que representa um plugin de credencial;
# Faz uso da função namedtuple do módulo collections.
CredentialPlugin = collections.namedtuple('CredentialPlugin', ['name', 'inputs', 'backend'])


def generate_jwt(app_id, rsa_key):  # noqa: WPS210
    """
    Função para gerar um JSON Web Token (JWT) com base no arquivo de chave privada.

    Parameters
    ----------
    app_id : string
        Identificador da Github App
    rsa_key : string
        Chave Privada da Github App

    Returns
    -------
    string
        JWT Token
    """

    # Carrega a chave privada
    private_key = serialization.load_pem_private_key(
        bytes(rsa_key, 'utf-8'),
        password=None,
        backend=default_backend(),
    )

    now = int(time.time())
    iat = now - 60  # Define o tempo de emissão do token 60 segundos no passado.
    # Define o tempo de expiração do token 10 minutos no futuro.
    exp = now + 300  # noqa: WPS432

    # Cria o cabeçalho e o payload do JWT.
    header = {'typ': 'JWT', 'alg': 'RS256'}
    payload = {'iat': iat, 'exp': exp, 'iss': app_id}

    # Codifica o cabeçalho e o payload em base64.
    header_enc = (
        base64.urlsafe_b64encode(
            json.dumps(header).encode(),
        )
        .decode()
        .strip('=')
    )
    payload_enc = (
        base64.urlsafe_b64encode(
            json.dumps(payload).encode(),
        )
        .decode()
        .strip('=')
    )

    # Combina o cabeçalho e o payload codificados.
    header_payload = f'{header_enc}.{payload_enc}'

    # Assina o JWT usando a chave privada.
    signature = private_key.sign(
        header_payload.encode(),
        padding.PKCS1v15(),
        SHA256(),
    )
    signature_enc = base64.urlsafe_b64encode(signature).decode().strip('=')

    # Retorna o JWT completo.
    return f'{header_payload}.{signature_enc}'


def get_installation_access_token(jwt, installation_id):
    """
    Função para obter um token de acesso à instalação usando JWT.

    Parameters
    ----------
    jwt : string
        JWT da Github App
    installation_id : string
        Identificador da Instalação da Github App

    Returns
    -------
    string
        Token
    """

    headers = {
        'Authorization': f'Bearer {jwt}',
        'Accept': 'application/vnd.github.v3+json',
    }

    response = requests.post(
        f'https://api.github.com/app/installations/{installation_id}/access_tokens',
        headers=headers,
        timeout=5,
    )

    if response.status_code == 201:  # noqa: WPS432
        return response.json().get('token')

    # Tratar erros de solicitação
    print(f'Error: {response.status_code}')
    return None


def some_lookup_function(**kwargs):

    installation_id = kwargs.get('installation_id')
    app_id = kwargs.get('app_id')
    rsa_key = kwargs.get('private_key')

    jwt = generate_jwt(app_id, rsa_key)  # Gera um JWT.
    # Obtém um token de acesso à instalação.
    return get_installation_access_token(jwt, installation_id)


# Cria o objeto "CredentialPlugin", plugin de credencial do GitHub.
github_plugin = CredentialPlugin(
    'GitHub App Credential',  # Nome do plugin.
    inputs={  # Definição dos campos de entrada do plugin.
        'fields': [
            {
                'id': 'app_id',
                'label': 'GitHub App ID',
                'type': 'string',
                'help_text': 'dddd',
            },
            {
                'id': 'private_key',
                'label': 'GitHub App RSA PRIVATE KEY',
                'type': 'string',
                'secret': True,
                'multiline': True,
                'help_text': 'Private key',
            },
            {
                'id': 'installation_id',
                'label': 'Installation Identifier',
                'type': 'string',
                'help_text': 'The unique identifier of the installation.',
            },
        ],
        'metadata': [],
        'required': ['app_id', 'installation_id', 'private_key'],  # Campos obrigatórios.
    },
    backend=some_lookup_function,  # Função de backend.
)
