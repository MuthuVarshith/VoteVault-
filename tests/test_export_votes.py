from app import app


def test_admin_can_export_votes_as_csv():
    client = app.test_client()
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["is_admin"] = True
    response = client.get("/export_votes")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert response.data.startswith(b"User ID,Candidate ID")
