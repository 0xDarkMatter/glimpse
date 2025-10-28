"""Google Street View API service for fetching random Street View images"""

import random
import requests
from typing import Dict, Tuple


class GoogleStreetViewService:
    """Service for interacting with Google Street View Static API"""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError('Google Maps API key is required')
        self.api_key = api_key
        self.metadata_url = 'https://maps.googleapis.com/maps/api/streetview/metadata'
        self.image_url = 'https://maps.googleapis.com/maps/api/streetview'
        self.name = 'google_streetview'

        # Image size for Street View
        self.image_size = '640x640'

        # Max retries when looking for valid Street View locations
        self.max_retries = 20

    def _generate_random_coordinates(self) -> Tuple[float, float]:
        """
        Generate random latitude and longitude coordinates

        Returns:
            Tuple of (latitude, longitude)
        """
        # Generate random coordinates
        # Bias towards populated areas by using a weighted distribution
        # This increases chances of finding Street View coverage

        # For now, use uniform distribution
        # Future enhancement: Use a database of known Street View locations
        lat = random.uniform(-85, 85)  # Avoid extreme poles
        lon = random.uniform(-180, 180)

        return lat, lon

    def _check_streetview_availability(self, lat: float, lon: float) -> Dict:
        """
        Check if Street View is available at the given coordinates

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Dictionary with metadata if available, None otherwise
        """
        try:
            params = {
                'location': f'{lat},{lon}',
                'key': self.api_key,
                'radius': 50000  # Search radius in meters (50km)
            }

            response = requests.get(
                self.metadata_url,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            metadata = response.json()

            # Check if Street View is available at this location
            if metadata.get('status') == 'OK':
                return metadata
            else:
                return None

        except requests.exceptions.RequestException:
            return None

    def fetch_random_image(self) -> Dict[str, str]:
        """
        Fetch a random Street View image from a location where Street View exists

        Returns:
            Dictionary with keys:
            - url: Street View image URL
            - description: Image description
            - sourceUrl: Google Maps Street View URL
            - locationUrl: Google Maps location URL (non-Street View)
            - date: (optional) Date when Street View was captured (e.g., "2018-01")

        Raises:
            Exception: If unable to find a valid Street View location after max retries
        """
        attempts = 0

        while attempts < self.max_retries:
            attempts += 1

            # Generate random coordinates
            lat, lon = self._generate_random_coordinates()

            # Check if Street View is available
            metadata = self._check_streetview_availability(lat, lon)

            if metadata:
                # Street View found! Generate the image URL
                actual_lat = metadata['location']['lat']
                actual_lon = metadata['location']['lng']
                pano_id = metadata.get('pano_id', '')

                # Build the Street View image URL
                params = {
                    'location': f'{actual_lat},{actual_lon}',
                    'size': self.image_size,
                    'key': self.api_key,
                    'fov': 90,  # Field of view
                    'pitch': 0,  # Camera pitch (0 = straight ahead)
                    'heading': random.randint(0, 359)  # Random heading direction
                }

                # Construct URL with parameters
                param_str = '&'.join(f'{k}={v}' for k, v in params.items())
                photo_url = f'{self.image_url}?{param_str}'

                # Build Google Maps URL for Street View
                maps_streetview_url = f'https://www.google.com/maps/@{actual_lat},{actual_lon},3a,75y,{params["heading"]}h,90t/data=!3m6!1e1'

                # Build regular Google Maps URL for the exact location
                maps_location_url = f'https://www.google.com/maps?q={actual_lat},{actual_lon}'

                # Generate description
                description = f'Street View at coordinates {actual_lat:.6f}, {actual_lon:.6f}'

                # Extract metadata
                date = metadata.get('date')

                result = {
                    'url': photo_url,
                    'description': description,
                    'sourceUrl': maps_streetview_url,
                    'locationUrl': maps_location_url
                }

                # Add optional metadata if available
                if date:
                    result['date'] = date

                return result

        # If we get here, we failed to find a valid location
        raise Exception(
            f'Failed to find a valid Street View location after {self.max_retries} attempts. '
            'Try again or check your API key and quota.'
        )

    def test_connection(self) -> bool:
        """Test the Google Street View API connection using a known location"""
        try:
            # Test with Times Square, NYC - known to have Street View
            params = {
                'location': '40.758896,-73.985130',
                'key': self.api_key
            }

            response = requests.get(
                self.metadata_url,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            metadata = response.json()
            return metadata.get('status') == 'OK'

        except Exception:
            return False
