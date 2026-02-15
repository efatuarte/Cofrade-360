def test_list_hermandades_sources(client):
    response = client.get('/api/v1/ingestion/hermandades/sources')
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) > 60
    assert any(item['name'] == 'Gran Poder' and item['ss_day'] == 'Madrugada' for item in rows)
