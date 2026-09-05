# Standalone minimal reproduction test for VoteVault export_votes
import pytest
from app import app
from models import db

def test_issue_1():
    with app.app_context():
        db.create_all()
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['is_admin'] = True
    resp = client.get('/export_votes')
    assert resp.status_code == 200, f'Expected 200 OK, got {resp.status_code}'
