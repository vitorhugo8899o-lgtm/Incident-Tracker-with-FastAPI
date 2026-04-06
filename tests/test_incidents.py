import pytest


@pytest.mark.asyncio
async def test_user_create_incident(client, token_user):

    incident = {
        'title': 'Título muito foda',
        'description': 'descrição muito precisa',
        'priority': 'low',
        'status': 'open',
    }

    req = await client.post(
        '/api/v1/incidents',
        headers={'Authorization': f'Bearer {token_user}'},
        json=incident,
    )

    status = 201

    response = req.json()

    assert req.status_code == status
    assert response['title'] == 'Título muito foda'
    assert response['id'] == 1
    assert response['description'] == 'descrição muito precisa'
    assert response['status'] == 'open'
    assert response['priority'] == 'low'
    assert 'created_at' in response


@pytest.mark.asyncio
async def test_get_custom_incident(client, token_tech, incident_user):
    req = await client.get(
        '/api/v1/incidents?offset=0&limit=10&status=open&priority=low',
        headers={'Authorization': f'Bearer {token_tech}'},
    )

    response = req.json()

    status = 200

    assert req.status_code == status
    assert type(response) is list
    assert len(response) > 0


@pytest.mark.asyncio
async def test_user_try_get_incidents_custom(
    client, token_user, incident_user
):
    req = await client.get(
        '/api/v1/incidents?offset=0&limit=10&status=open&priority=low&creator=1',  # noqa
        headers={'Authorization': f'Bearer {token_user}'},
    )

    response = req.json()

    status = 403

    assert req.status_code == status
    assert (
        response['detail']
        == 'Você não possui permisão para realizar essa acão'
    )


@pytest.mark.asyncio
async def test_user_delete_incident_(client, token_user, incident_user):
    req = await client.delete(
        f'/api/v1/incidents/{1}',  # noqa
        headers={'Authorization': f'Bearer {token_user}'},
    )

    status = 200

    response = req.json()

    assert req.status_code == status
    assert 'description' in response
    assert 'title' in response
    assert 'priority' in response
    assert 'id' in response
    assert 'id' in response['creator']
    assert 'email' in response['creator']
    assert 'role' in response['creator']


@pytest.mark.asyncio
async def test_user_incident_not_found(client, token_user):
    req = await client.delete(
        f'/api/v1/incidents/{1}',  # noqa
        headers={'Authorization': f'Bearer {token_user}'},
    )

    response = req.json()

    status = 200

    assert req.status_code == status
    assert response == 'Chamdo não encontrado!'


@pytest.mark.asyncio
async def test_user_try_delete_incident_from_another_user(
    client, token_tech, incident_user
):  # noqa
    req = await client.delete(
        f'/api/v1/incidents/{1}',
        headers={'Authorization': f'Bearer {token_tech}'},
    )

    response = req.json()

    status = 403

    assert req.status_code == status
    assert (
        response['detail']
        == 'Você não possui permisão para realizar essa acão.'
    )


@pytest.mark.asyncio
async def test_get_history_of_incident(client, token_tech, incident_user):
    req = await client.get(
        f'/api/v1/incidents/history/{1}',
        headers={'Authorization': f'Bearer {token_tech}'},
    )

    response = req.json()

    status = 200

    assert req.status_code == status
    assert 'description' in response
    assert 'title' in response
    assert 'priority' in response
    assert 'id' in response
    assert 'technician_id' in response
    assert 'creator_id' in response


@pytest.mark.asyncio
async def test_get_incident_history_that_does_not_exist(client, token_tech):
    req = await client.get(
        f'/api/v1/incidents/history/{1}',
        headers={'Authorization': f'Bearer {token_tech}'},
    )

    status = 200

    response = req.json()

    assert req.status_code == status
    assert response is None


@pytest.mark.asyncio
async def test_user_try_get_incident_history(
    client, token_user, incident_user
):  # noqa
    req = await client.get(
        f'/api/v1/incidents/history/{1}',
        headers={'Authorization': f'Bearer {token_user}'},
    )

    status = 403

    response = req.json()

    assert req.status_code == status
    assert response['detail'] == (
        'Você não possui permissão para realizar essa acão.'
    )
