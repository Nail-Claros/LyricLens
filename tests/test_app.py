import pytest
from app import app
import json

@pytest.fixture
def client():
    """Fixture for creating a test client."""
    with app.test_client() as client:
        yield client

def test_index(client):
    """Test the '/' route (home page)."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Lyric Lens" in response.data

def test_history(client):
    """Test the '/history' route."""
    # Set a mock user_id cookie for the test
    response = client.get('/history', cookies={'user_id': 'mock_user_id'})
    
    assert response.status_code == 200

def test_clear_history(client):
    """Test the '/clear_history' route."""
    response = client.post('/clear_history', cookies={'user_id': 'mock_user_id'})
    assert response.status_code == 302  # Expecting a redirect (status code 302)


def test_redis_test(client):
    """Test the '/redistest' route (simple Redis test)."""
    response = client.get('/redistest')
    assert response.status_code == 200
    assert b"Hello, this is a CAM!" in response.data


def test_detected(client):
    """Test the '/detected' route."""
    # Mock query parameters
    response = client.get('/detected', query_string={'key': 'mock_song_key'}, cookies={'user_id': 'mock_user_id'})
    
    assert response.status_code == 200
    assert b"Translations" in response.data 


def test_translations(client):
    """Test the '/translations' route."""
    response = client.get('/translations', query_string={'key': 'mock_song_key'})
    
    assert response.status_code == 200
    assert b"Language" in response.data


def test_upload_audio(client):
    """Test the '/upload-audio' route with file upload."""
    data = {
        'audio': (open('test_audio.mp3', 'rb'), 'test_audio.mp3')
    }
    response = client.post('/upload-audio', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 200
    assert b"Audio file uploaded" in response.data


def test_translate(client):
    """Test the '/translate' route."""
    data = {
        'text': 'Hello, world!',
        'lang': 'es'
    }
    response = client.post('/translate', data=json.dumps(data), content_type='application/json')
    
    assert response.status_code == 200
    assert b"translatedText" in response.data 


def test_lyrics(client):
    """Test the '/lyrics' route."""
    response = client.get('/lyrics', query_string={'song_key': 'mock_song_key'}, cookies={'user_id': 'mock_user_id'})
    
    assert response.status_code == 200
    assert b"Song Lyrics" in response.data
