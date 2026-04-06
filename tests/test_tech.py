import pytest


@pytest.mark.asyncio
async def test_tech_resolve_incident(client, token_tech, incident_user):
    payload = {
        'status': 'closed',
        'priority': 'high',
        'comment': 'Comentario sobre o chamado',
    }

    req = await client.put(
        f'/api/v1/incident/{1}',
        headers={'Authorization': f'Bearer {token_tech}'},
        json=payload,
    )

    status = 200

    response = req.json()

    assert req.status_code == status
    assert 'id' in response
    assert 'status' in response
    assert 'description' in response
    assert 'priority' in response
    assert 'created_at' in response


@pytest.mark.asyncio
async def test_none_change_in_incident(client, token_tech, incident_user):
    payload = {
        'status': 'open',
        'priority': 'low',
    }

    req = await client.put(
        f'/api/v1/incident/{1}',
        headers={'Authorization': f'Bearer {token_tech}'},
        json=payload,
    )

    status = 200

    response = req.json()

    assert req.status_code == status
    assert response['status'] == 'open'
    assert response['priority'] == 'low'


@pytest.mark.asyncio
async def test_tech_tries_to_solve_incident_not_encouraged(client, token_tech):  # noqa
    payload = {
        'status': 'closed',
        'priority': 'high',
        'comment': 'Comentario sobre o chamado',
    }

    req = await client.put(
        f'/api/v1/incident/{1}',
        headers={'Authorization': f'Bearer {token_tech}'},
        json=payload,
    )

    status = 404

    response = req.json()

    assert req.status_code == status
    assert response['detail'] == 'Incidente não encontrado'


@pytest.mark.asyncio
async def test_user_tries_to_solve_incident(client, token_user, incident_user):  # noqa
    payload = {
        'status': 'closed',
        'priority': 'high',
        'comment': 'Comentario sobre o chamado',
    }

    req = await client.put(
        f'/api/v1/incident/{1}',
        headers={'Authorization': f'Bearer {token_user}'},
        json=payload,
    )

    status = 403

    response = req.json()

    assert req.status_code == status
    assert response['detail'] == (
        'Você não possui permisão para realizar essa acão'
    )


@pytest.mark.asyncio
async def test_incident_is_already_closed(client, token_tech, incident_closed):
    payload = {
        'status': 'open',
        'priority': 'low',
        'comment': 'Comentario sobre o chamado',
    }

    req = await client.put(
        f'/api/v1/incident/{1}',
        headers={'Authorization': f'Bearer {token_tech}'},
        json=payload,
    )

    status = 409

    reponse = req.json()

    assert req.status_code == status
    assert reponse['detail'] == 'Chamado já finalizado'


@pytest.mark.asyncio
async def test_supervisor_disable_user_or_worker(
    client, token_user, token_supervisor
):
    req = await client.put(
        f'/api/v1/disable/user/or/worker/{1}',
        headers={'Authorization': f'Bearer {token_supervisor}'},
    )

    response = req.json()

    status = 200

    assert req.status_code == status
    assert response['id'] == 1
    assert response['email'] == 'emailfoda@gmail.com'
    assert response['cpf'] == '82965919104'
    assert response['is_active'] is False
    assert 'created_at' in response


@pytest.mark.asyncio
async def test_supervisor_disable_user_or_worker_not_exists(
    client, token_supervisor
):
    req = await client.put(
        f'/api/v1/disable/user/or/worker/{2}',
        headers={'Authorization': f'Bearer {token_supervisor}'},
    )

    response = req.json()

    status = 200

    assert req.status_code == status
    assert response is None


@pytest.mark.asyncio
async def test_user_or_worker_tries_to_disable_a_use(
    client, token_tech, token_user
):
    req = await client.put(
        f'/api/v1/disable/user/or/worker/{2}',
        headers={'Authorization': f'Bearer {token_tech}'},
    )

    response = req.json()

    status = 403

    assert req.status_code == status
    assert response['detail'] == (
        'Você não possui permissão para realizar essa acão.'
    )


@pytest.mark.asyncio
async def test_supervisor_get_user_infos(client, token_user, token_supervisor):
    req = await client.get(
        f'/api/v1/users/{1}',
        headers={'Authorization': f'Bearer {token_supervisor}'},
    )

    response = req.json()

    status = 200

    id_user = 1

    assert req.status_code == status
    assert response['id'] == id_user
    assert response['email'] == 'emailfoda@gmail.com'
    assert response['cpf'] == '82965919104'
    assert response['is_active'] is True
    assert 'created_at' in response


@pytest.mark.asyncio
async def test_supervisor_get_user_not_exists_infos(client, token_supervisor):
    req = await client.get(
        f'/api/v1/users/{50}',
        headers={'Authorization': f'Bearer {token_supervisor}'},
    )

    response = req.json()

    status = 200

    assert req.status_code == status
    assert response is None


@pytest.mark.asyncio
async def test_user_or_worker_tries_get_user_infos(client, token_user):
    req = await client.get(
        '/api/v1/users/1',
        headers={'Authorization': f'Bearer {token_user}'},
    )

    response = req.json()

    status = 403

    assert req.status_code == status
    assert response['detail'] == (
        'Você não possui permissão para realizar essa acão'
    )


@pytest.mark.asyncio
async def test_get_tech_metrics(client, incident_user, token_tech):
    payload = {
        'status': 'closed',
        'priority': 'high',
        'comment': 'Comentario sobre o chamado',
    }

    await client.put(
        f'/api/v1/incident/{1}',
        headers={'Authorization': f'Bearer {token_tech}'},
        json=payload,
    )

    response = await client.get(
        f'/api/v1/metrics/{2}',
        headers={'Authorization': f'Bearer {token_tech}'},
    )

    status = 200

    assert response.status_code == status
    assert response.headers['content-type'] == 'image/png'
    assert len(response.content) > 0
    assert response.content.startswith(b'\x89PNG\r\n\x1a\n')


@pytest.mark.asyncio
async def test_tech_has_no_metrics(client, token_tech):
    req = await client.get(
        f'/api/v1/metrics/{1}',
        headers={'Authorization': f'Bearer {token_tech}'},
    )

    response = req.json()

    status = 200

    assert req.status_code == status
    assert response['detail'] == 'Nenhum dado encontrado para o período.'


@pytest.mark.asyncio
async def test_get_tech_incident_history(
    client, token_tech, incident_user, incident2_user
):
    payload = {
        'status': 'closed',
        'priority': 'high',
        'comment': 'Comentario sobre o chamado',
    }

    req1 = await client.put(
        f'/api/v1/incident/{1}',
        headers={'Authorization': f'Bearer {token_tech}'},
        json=payload,
    )

    req2 = await client.put(
        f'/api/v1/incident/{2}',
        headers={'Authorization': f'Bearer {token_tech}'},
        json=payload,
    )

    req3 = await client.get('/api/v1/tech/history_incident/')

    response = req3.json()

    status = 200

    itens = 2

    assert req1.status_code == status
    assert req2.status_code == status
    assert req3.status_code == status
    assert type(response) is list
    assert (len(response) > 0) & (len(response) <= itens)


@pytest.mark.asyncio
async def test_user_tries_get_tech_history(client, token_user):
    req = await client.get(
        '/api/v1/tech/history_incident/',
        headers={'Authorization': f'Bearer {token_user}'},
    )

    status = 403

    assert req.status_code == status
    assert req.json()['detail'] == (
        'Você não possui permisão para realizar essa acão'
    )


@pytest.mark.asyncio
async def test_history_return_none(client, token_tech):
    req = await client.get(
        '/api/v1/tech/history_incident/',
        headers={'Authorization': f'Bearer {token_tech}'},
    )

    status = 200

    assert req.status_code == status
    assert req.json() is None


@pytest.mark.asyncio
async def test_work_try_disable_account(client, token_tech):
    req = await client.post(
        '/api/v1/users/disable',
        headers={'Authorization': f'Bearer {token_tech}'},
    )

    status = 403

    assert req.status_code == status
    assert req.json()['detail'] == (
        'Você não possui permissão para realizar essa acão.'
    )
