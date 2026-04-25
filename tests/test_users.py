import pytest


@pytest.mark.asyncio
async def test_create_user(client):
    payload = {
        'email': 'uber@gmail.com',
        'cpf': '02871143170',
        'password': 'Senha12@#',
    }

    req = await client.post('/api/v1/users', json=payload)

    response = req.json()

    status = 201

    assert req.status_code == status
    assert response['id'] == 1
    assert response['email'] == 'uber@gmail.com'
    assert response['cpf'] == '02871143170'
    assert response['is_active'] is True
    assert 'created_at' in response


@pytest.mark.asyncio
async def test_user_email_alredy_in_use(client, user):
    payload = {
        'email': 'emailfoda@gmail.com',
        'cpf': '82965919104',
        'password': 'Senha12@#',
    }

    req = await client.post('/api/v1/users', json=payload)

    response = req.json()

    status = 409

    assert req.status_code == status
    assert response['detail'] == 'Email ou CPF já cadastrado no sistema.'


@pytest.mark.asyncio
async def test_user_cpf_alredy_in_use(client, user):
    payload = {
        'email': 'emailfoda@gmail.com',
        'cpf': '82965919104',
        'password': 'Senha12@#',
    }

    req = await client.post('/api/v1/users', json=payload)

    response = req.json()

    status = 409

    assert req.status_code == status
    assert response['detail'] == 'Email ou CPF já cadastrado no sistema.'


@pytest.mark.asyncio
async def test_login_user(client, user):
    data = {'username': 'emailfoda@gmail.com', 'password': 'Senha12@#'}

    req = await client.post('/api/v1/Login', data=data)

    response = req.json()

    status = 200

    assert req.status_code == status
    assert 'access_token' in response
    assert 'token_type' in response


@pytest.mark.asyncio
async def test_user_disable_try_login(client, user_disable):
    user_disable, raw_password = user_disable

    data = {'username': user_disable.email, 'password': f'{raw_password}'}

    req = await client.post('/api/v1/Login', data=data)

    status = 409

    response = req.json()

    assert req.status_code == status
    assert response['detail'] == 'Usuário desativado'


@pytest.mark.asyncio
async def test_error_password(client, user):
    data = {'username': 'emailfoda@gmail.com', 'password': 'Senhaerrada12@#'}

    req = await client.post('/api/v1/Login', data=data)

    response = req.json()

    status = 401

    assert req.status_code == status
    assert response['detail'] == 'Credenciais inválidas'


@pytest.mark.asyncio
async def test_user_disable_account(client, token_user):
    req = await client.post(
        '/api/v1/users/disable',
        headers={'Authorization': f'Bearer {token_user}'},
    )

    status = 200

    response = req.json()

    assert req.status_code == status
    assert response == 'Conta deletada com sucesso!\nMuito Obrigado por usar o NexusTracker' #noqa


@pytest.mark.asyncio
async def test_user_disable_account_but_have_incidents(
    client, incident_user, token_user
):
    req = await client.post(
        '/api/v1/users/disable',
        headers={'Authorization': f'Bearer {token_user}'},
    )

    status = 200

    response = req.json()

    assert req.status_code == status
    assert response == 'Conta desativada, como você ainda possui chamados em aberto ou que foram resolvidos recentemente sua conta será deletada dentre os proximos 3 meses.' #noqa


@pytest.mark.asyncio
async def test_get_user_incidents(client, incident_user, token_user):
    req = await client.get(
        '/api/v1/user_incidents',
        headers={'Authorization': f'Bearer {token_user}'},
    )

    response = req.json()

    status = 200

    assert req.status_code == status
    assert 'description' in response[0]
    assert 'status' in response[0]
    assert 'created_at' in response[0]
    assert 'technician_id' in response[0]
    assert 'title' in response[0]
    assert 'id' in response[0]
    assert 'priority' in response[0]
    assert 'creator_id' in response[0]
