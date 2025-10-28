"""Unsplash API service for fetching random images"""

import requests
from typing import Dict


class UnsplashService:
    """Service for interacting with Unsplash API"""

    def __init__(self, access_key: str):
        if not access_key:
            raise ValueError('Unsplash access key is required')
        self.access_key = access_key
        self.base_url = 'https://api.unsplash.com'
        self.name = 'unsplash'

    def fetch_random_image(self) -> Dict[str, str]:
        """
        Fetch a random image from Unsplash

        Returns:
            Dictionary with url, description, and sourceUrl keys

        Raises:
            Exception: If the API request fails
        """
        try:
            response = requests.get(
                f'{self.base_url}/photos/random',
                headers={'Authorization': f'Client-ID {self.access_key}'},
                params={'orientation': 'landscape'},
                timeout=30
            )
            response.raise_for_status()

            photo = response.json()

            return {
                'url': photo['urls']['regular'],
                'description': photo.get('description') or photo.get('alt_description') or 'No description available',
                'sourceUrl': photo['links']['html']
            }
        except requests.exceptions.RequestException as e:
            raise Exception(f'Failed to fetch image from Unsplash: {str(e)}')

    def test_connection(self) -> bool:
        """Test the Unsplash API connection"""
        try:
            response = requests.get(
                f'{self.base_url}/photos/random',
                headers={'Authorization': f'Client-ID {self.access_key}'},
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception:
            return False
