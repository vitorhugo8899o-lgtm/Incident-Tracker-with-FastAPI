import pytest


@pytest.mark.asyncio
async def test_check_conect_db(client):
    req = await client.get('/api/v1/health')

    response = req.json()

    status = 200

    assert req.status_code == status
    assert response['status'] == 'ok'
    assert response['database'] == 'online'
    assert response['version'] == '1.0.0'
