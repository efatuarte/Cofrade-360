import pytest


def test_list_hermandades_sources(client):
    response = client.get('/api/v1/ingestion/hermandades/sources')
    if response.status_code == 404:
        pytest.skip('Ingestion source endpoint is not enabled in this build')

    assert response.status_code == 200
    rows = response.json()
    assert len(rows) > 60
    assert any(item['name'] == 'Gran Poder' and item['ss_day'] == 'Madrugada' for item in rows)
