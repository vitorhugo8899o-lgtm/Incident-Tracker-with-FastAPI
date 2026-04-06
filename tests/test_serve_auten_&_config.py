import pytest


@pytest.mark.asyncio
async def test_not_token_in_authentication(client, user):
    req = await client.get(
        '/api/v1/user_incidents',
        headers={'Authorization': 'token_user'},
    )

    status = 401

    assert req.status_code == status
    assert req.json()['detail'] == 'Não autenticado.'


@pytest.mark.asyncio
async def test_no_sub_parameter_in_token(client):
    req = await client.get(
        '/api/v1/user_incidents',
        headers={
            'Authorization': 'Bearer ejasboapdbaphneqenp2asd.sadasdasdd123123.13adsadasdada2egmgmuytasdadadasd'  # noqa
        },
    )

    status = 401

    assert req.status_code == status
    assert 'detail' in req.json()


@pytest.mark.asyncio
async def test_schema_UserCreate_password_error(client):
    payload = {'email': 'emaillongo@gmail.com', 'password': '          '}

    req = await client.post('/api/v1/users', json=payload)

    status = 422

    mensagem = req.json()['detail'][0]['msg']

    assert req.status_code == status
    assert mensagem == 'Value error, Deve conter letra minúscula'


@pytest.mark.asyncio
async def test_schema_UserCreate_password_error_min(client):
    payload = {
        'email': 'emaillongo@gmail.com',
        'password': 'asbnchs',
        'cpf': '',
    }

    req = await client.post('/api/v1/users', json=payload)

    status = 422

    mensagem = req.json()['detail'][0]['msg']

    assert req.status_code == status
    assert mensagem == 'String should have at least 8 characters'
