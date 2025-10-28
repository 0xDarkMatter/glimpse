"""Google Street View API service for fetching random Street View images"""

import math
import random
import requests
from typing import Dict, Tuple, Optional


class GoogleStreetViewService:
    """Service for interacting with Google Street View Static API"""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError('Google Maps API key is required')
        self.api_key = api_key
        self.metadata_url = 'https://maps.googleapis.com/maps/api/streetview/metadata'
        self.image_url = 'https://maps.googleapis.com/maps/api/streetview'
        self.name = 'google_streetview'

        # Image size for Street View (16:9 aspect ratio)
        # Google API maximum is 640x640, so best 16:9 ratio is 640x360
        self.image_size = '640x360'

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

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula

        Args:
            lat1, lon1: First coordinate
            lat2, lon2: Second coordinate

        Returns:
            Distance in meters
        """
        R = 6371000  # Earth's radius in meters

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def _is_valid_location(self, lat: float, lon: float) -> bool:
        """
        Check if coordinates are on land using reverse geocoding

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            True if coordinates are on land with a valid address
        """
        # Reject coordinates that are too close to 0,0 (Gulf of Guinea - usually ocean)
        if abs(lat) < 0.1 and abs(lon) < 0.1:
            return False

        # Reject if either coordinate is exactly 0
        if lat == 0.0 or lon == 0.0:
            return False

        # Use reverse geocoding to verify this is a land location
        try:
            geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json'
            params = {
                'latlng': f'{lat},{lon}',
                'key': self.api_key
            }

            response = requests.get(geocode_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Check if we got valid results
            if data.get('status') != 'OK' or not data.get('results'):
                # No geocoding results - might be remote area, allow it
                return True

            # Check if any result indicates this is a real address on land
            for result in data['results']:
                types = result.get('types', [])
                formatted_address = result.get('formatted_address', '').lower()

                # Explicitly reject if it's clearly water/ocean in the address
                if any(word in formatted_address for word in ['ocean', 'sea', 'mediterranean', 'atlantic', 'pacific', 'indian ocean']):
                    return False

                # Accept if it has a street address, route, or locality
                good_types = ['street_address', 'route', 'premise', 'locality',
                              'sublocality', 'postal_code', 'administrative_area',
                              'political', 'country']
                if any(t in types for t in good_types):
                    return True

            # If we got results but none matched, allow it (might be remote area)
            return True

        except Exception:
            # If geocoding fails, allow it (don't be too strict)
            return True

    def _check_streetview_availability(self, lat: float, lon: float) -> Optional[Dict]:
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
                # Get the actual coordinates returned by the API
                actual_lat = metadata.get('location', {}).get('lat')
                actual_lon = metadata.get('location', {}).get('lng')

                if actual_lat is None or actual_lon is None:
                    return None

                # Validate the returned coordinates
                if not self._is_valid_location(actual_lat, actual_lon):
                    return None

                # Check distance between requested and returned location
                # Reject if too far (indicates no nearby Street View)
                distance = self._calculate_distance(lat, lon, actual_lat, actual_lon)
                if distance > 50000:  # More than 50km away
                    return None

                return metadata
            else:
                return None

        except requests.exceptions.RequestException:
            return None

    def fetch_random_image(self) -> Dict[str, str]:
        """
        Fetch a random Street View location with interactive panorama link

        Returns:
            Dictionary with keys:
            - url: Google Maps Street View panorama URL (interactive)
            - description: Description with coordinates
            - locationUrl: Google Maps location URL (map pin)
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
                # Street View found! Generate the panorama URL
                actual_lat = metadata['location']['lat']
                actual_lon = metadata['location']['lng']
                pano_id = metadata.get('pano_id', '')

                # Random heading direction for variety
                heading = random.randint(0, 359)

                # Build Google Maps URL for Street View using panorama ID
                if pano_id:
                    # Use panorama ID for reliable Street View link
                    streetview_url = f'https://www.google.com/maps/@?api=1&map_action=pano&pano={pano_id}&heading={heading}&pitch=0&fov=90'
                else:
                    # Fallback to coordinate-based link
                    streetview_url = f'https://www.google.com/maps/@{actual_lat},{actual_lon},3a,75y,{heading}h,90t/data=!3m6!1e1'

                # Build regular Google Maps URL for the exact location
                maps_location_url = f'https://www.google.com/maps?q={actual_lat},{actual_lon}'

                # Generate description
                description = f'Street View at coordinates {actual_lat:.6f}, {actual_lon:.6f}'

                # Extract metadata
                date = metadata.get('date')

                result = {
                    'url': streetview_url,
                    'description': description,
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
