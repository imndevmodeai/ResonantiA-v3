#!/usr/bin/env python3
"""
Google Maps/Street View URL Decoder
Advanced location intelligence extraction from Google Maps URLs
Part of the ArchE ResonantiA Protocol v3.0 framework

This module provides comprehensive decoding capabilities for:
- Google Place IDs and FIDs (Feature IDs)
- Street View/Photosphere URLs
- Coordinate extraction and geographic analysis
- Camera parameter extraction from photosphere data
"""

import re
import urllib.parse
import struct
import binascii
import math
from typing import Dict, Tuple, List, Optional, Any
from dataclasses import dataclass
import json


@dataclass
class PhotosphereParams:
    """Parameters extracted from Google Photosphere URLs"""
    yaw_angle: float
    pitch_angle: float
    roll_angle: float
    field_of_view: float
    width: int
    height: int
    compass_direction: str


@dataclass
class LocationIntelligence:
    """Comprehensive location intelligence report"""
    place_id: str
    coordinates: Optional[Tuple[float, float]]
    region: str
    hemisphere: str
    timezone_estimate: str
    photosphere_params: Optional[PhotosphereParams]
    confidence_score: float
    applications: List[str]
    technical_metadata: Dict[str, Any]


class GoogleMapsDecoder:
    """Advanced decoder for Google Maps and Street View URLs"""
    
    COMPASS_DIRECTIONS = [
        'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
        'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'
    ]
    
    def __init__(self):
        self.coordinate_scales = [1000000, 10000000, 1000000000]
        
    def decode_google_url(self, url: str) -> LocationIntelligence:
        """
        Main entry point for decoding Google Maps/Street View URLs
        
        Args:
            url: Google Maps or Street View URL
            
        Returns:
            LocationIntelligence object with extracted data
        """
        parsed_url = urllib.parse.urlparse(url)
        
        # Extract Place ID/FID
        place_id = self._extract_place_id(parsed_url.path)
        
        # Extract photosphere parameters
        photosphere_params = self._extract_photosphere_params(url)
        
        # Attempt coordinate extraction
        coordinates = self._extract_coordinates(place_id)
        
        # Generate geographic intelligence
        region, hemisphere, timezone = self._analyze_geography(coordinates)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(place_id, coordinates, photosphere_params)
        
        # Generate applications and metadata
        applications = self._generate_applications(coordinates, photosphere_params)
        metadata = self._generate_metadata(place_id, coordinates, photosphere_params)
        
        return LocationIntelligence(
            place_id=place_id,
            coordinates=coordinates,
            region=region,
            hemisphere=hemisphere,
            timezone_estimate=timezone,
            photosphere_params=photosphere_params,
            confidence_score=confidence,
            applications=applications,
            technical_metadata=metadata
        )
    
    def _extract_place_id(self, path: str) -> str:
        """Extract Google Place ID/FID from URL path"""
        # Pattern for Place ID: /place/fid/0xHEX:0xHEX
        fid_pattern = r'/fid/([0-9a-fA-F:x]+)'
        match = re.search(fid_pattern, path)
        
        if match:
            return match.group(1)
        
        # Alternative patterns for different Google URL formats
        place_patterns = [
            r'/place/([^/]+)',
            r'@(-?\d+\.\d+),(-?\d+\.\d+)',
            r'/data=([^&]+)'
        ]
        
        for pattern in place_patterns:
            match = re.search(pattern, path)
            if match:
                return match.group(1)
                
        return "Unknown"
    
    def _extract_photosphere_params(self, url: str) -> Optional[PhotosphereParams]:
        """Extract camera parameters from photosphere URL"""
        # Look for photosphere parameters in the URL
        param_patterns = {
            'ya': r'ya([\d.-]+)',  # Yaw angle
            'pi': r'pi([\d.-]+)',  # Pitch angle
            'ro': r'ro([\d.-]+)',  # Roll angle
            'fo': r'fo([\d.-]+)',  # Field of view
            'w': r'w(\d+)',        # Width
            'h': r'h(\d+)'         # Height
        }
        
        params = {}
        for param, pattern in param_patterns.items():
            match = re.search(pattern, url)
            if match:
                try:
                    params[param] = float(match.group(1))
                except ValueError:
                    params[param] = 0.0
        
        if not params:
            return None
            
        # Calculate compass direction from yaw angle
        yaw = params.get('ya', 0.0)
        direction_index = round(yaw / 22.5) % 16
        compass_dir = self.COMPASS_DIRECTIONS[direction_index]
        
        return PhotosphereParams(
            yaw_angle=yaw,
            pitch_angle=params.get('pi', 0.0),
            roll_angle=params.get('ro', 0.0),
            field_of_view=params.get('fo', 100.0),
            width=int(params.get('w', 160)),
            height=int(params.get('h', 106)),
            compass_direction=compass_dir
        )
    
    def _extract_coordinates(self, place_id: str) -> Optional[Tuple[float, float]]:
        """
        Extract GPS coordinates from Google Place ID using multiple methods
        """
        if ':' not in place_id or 'x' not in place_id:
            return None
            
        try:
            # Split the FID into hex components
            parts = place_id.split(':')
            if len(parts) != 2:
                return None
                
            hex1_str = parts[0]
            hex2_str = parts[1]
            
            # Remove 0x prefix if present
            hex1_str = hex1_str.replace('0x', '')
            hex2_str = hex2_str.replace('0x', '')
            
            # Convert to integers
            int1 = int(hex1_str, 16)
            int2 = int(hex2_str, 16)
            
            # Try multiple coordinate extraction methods
            for scale in self.coordinate_scales:
                # Method 1: Scale-based extraction from first ID
                lat_attempt = (int1 % (2**32)) / scale - 180
                lng_attempt = ((int1 >> 32) % (2**32)) / scale - 90
                
                if self._is_valid_coordinate(lat_attempt, lng_attempt):
                    return (lat_attempt, lng_attempt)
                
                # Method 2: Scale-based extraction from second ID
                lat_attempt2 = (int2 % (2**32)) / scale - 180
                lng_attempt2 = ((int2 >> 32) % (2**32)) / scale - 90
                
                if self._is_valid_coordinate(lat_attempt2, lng_attempt2):
                    return (lat_attempt2, lng_attempt2)
                
                # Method 3: Alternative scaling approach
                lat_attempt3 = (int1 % (2**32)) / scale - 90
                lng_attempt3 = ((int1 >> 32) % (2**32)) / scale - 180
                
                if self._is_valid_coordinate(lat_attempt3, lng_attempt3):
                    return (lat_attempt3, lng_attempt3)
            
            return None
            
        except (ValueError, TypeError, OverflowError):
            return None
    
    def _is_valid_coordinate(self, lat: float, lng: float) -> bool:
        """Check if coordinates are within valid ranges"""
        return -90 <= lat <= 90 and -180 <= lng <= 180
    
    def _analyze_geography(self, coordinates: Optional[Tuple[float, float]]) -> Tuple[str, str, str]:
        """Generate geographic analysis from coordinates"""
        if not coordinates:
            return "Unknown", "Unknown", "Unknown"
            
        lat, lng = coordinates
        
        # Hemisphere analysis
        lat_hem = "Northern" if lat >= 0 else "Southern"
        lng_hem = "Eastern" if lng >= 0 else "Western"
        hemisphere = f"{lat_hem} {lat_hem}"
        
        # Regional analysis (simplified)
        region = self._identify_region(lat, lng)
        
        # Timezone estimation (simplified)
        timezone_offset = lng / 15.0  # Rough approximation
        timezone = f"UTC{timezone_offset:+.1f}"
        
        return region, hemisphere, timezone
    
    def _identify_region(self, lat: float, lng: float) -> str:
        """Identify geographic region from coordinates"""
        # Australia
        if -45 < lat < -10 and 110 < lng < 155:
            if 130 < lng < 140 and -15 < lat < -10:
                return "Northern Territory, Australia"
            elif 140 < lng < 155 and -40 < lat < -25:
                return "Eastern Australia"
            elif 110 < lng < 130 and -35 < lat < -15:
                return "Western Australia"
            return "Australia"
        
        # North America
        if 25 < lat < 70 and -170 < lng < -50:
            return "North America"
        
        # Europe
        if 35 < lat < 70 and -10 < lng < 50:
            return "Europe"
        
        # Asia
        if -10 < lat < 70 and 50 < lng < 180:
            return "Asia"
        
        return f"Coordinates: {lat:.3f}, {lng:.3f}"
    
    def _calculate_confidence(self, place_id: str, coordinates: Optional[Tuple[float, float]], 
                           photosphere_params: Optional[PhotosphereParams]) -> float:
        """Calculate confidence score for the extraction"""
        confidence = 0.0
        
        # Place ID quality
        if place_id and place_id != "Unknown":
            confidence += 0.3
            if ':' in place_id and 'x' in place_id:
                confidence += 0.2
        
        # Coordinate extraction success
        if coordinates:
            confidence += 0.3
        
        # Photosphere parameters
        if photosphere_params:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _generate_applications(self, coordinates: Optional[Tuple[float, float]], 
                            photosphere_params: Optional[PhotosphereParams]) -> List[str]:
        """Generate potential applications for the location data"""
        applications = [
            "Virtual Tourism: 360° location exploration",
            "Geographic Education: Remote location study",
            "Navigation Reference: Street-level orientation"
        ]
        
        if coordinates:
            applications.extend([
                "Mapping Integration: GPS coordinate integration",
                "Geographic Analysis: Spatial data processing",
                "Location-based Services: Proximity calculations"
            ])
        
        if photosphere_params:
            applications.extend([
                "Virtual Reality: Immersive environment creation",
                "Photogrammetry: 3D reconstruction reference",
                "Content Creation: 360° media production"
            ])
        
        return applications
    
    def _generate_metadata(self, place_id: str, coordinates: Optional[Tuple[float, float]], 
                         photosphere_params: Optional[PhotosphereParams]) -> Dict[str, Any]:
        """Generate technical metadata"""
        metadata = {
            "extraction_methods": [
                "Google Place ID hex decoding",
                "URL parameter parsing",
                "Geographic region analysis"
            ],
            "place_id": place_id,
            "coordinate_extraction_attempted": coordinates is not None,
            "photosphere_data_available": photosphere_params is not None
        }
        
        if coordinates:
            lat, lng = coordinates
            metadata.update({
                "latitude": lat,
                "longitude": lng,
                "equator_distance_km": abs(lat) * 111.32,  # Rough km per degree
                "prime_meridian_distance_km": abs(lng) * 111.32 * math.cos(math.radians(lat))
            })
        
        if photosphere_params:
            metadata.update({
                "camera_yaw": photosphere_params.yaw_angle,
                "camera_pitch": photosphere_params.pitch_angle,
                "viewing_direction": photosphere_params.compass_direction,
                "image_dimensions": f"{photosphere_params.width}x{photosphere_params.height}"
            })
        
        return metadata


def main():
    """Demonstration of Google Maps URL decoding capabilities"""
    decoder = GoogleMapsDecoder()
    
    # Example URL
    test_url = ("https://www.google.com/local/place/fid/0x88172fbb6494374f:0x9a2a416edb01a4e2/"
                "photosphere?iu=https://lh3.googleusercontent.com/gps-cs-s/"
                "AC9h4npMZr96xaVRtv2aqsjckXCph8abZ7Y-g0zDBdzQkab-kh-88f_n-P6J6PBJ0vVHWcl5"
                "FU3BtjTEQd1KQ2bz43LRvCqoiYNISfoevzjjV1wUrXhw0Whu_81GtEsE_TgJK_HqrTQ%3D"
                "w160-h106-k-no-pi0-ya289.36-ro-0-fo100")
    
    result = decoder.decode_google_url(test_url)
    
    print("🗺️  GOOGLE MAPS URL INTELLIGENCE REPORT")
    print("=" * 60)
    print(f"Place ID: {result.place_id}")
    print(f"Coordinates: {result.coordinates}")
    print(f"Region: {result.region}")
    print(f"Hemisphere: {result.hemisphere}")
    print(f"Timezone: {result.timezone_estimate}")
    print(f"Confidence: {result.confidence_score:.2f}")
    
    if result.photosphere_params:
        print(f"\nPhotosphere Data:")
        print(f"  Viewing Direction: {result.photosphere_params.compass_direction} ({result.photosphere_params.yaw_angle}°)")
        print(f"  Image Size: {result.photosphere_params.width}x{result.photosphere_params.height}")
    
    print(f"\nApplications ({len(result.applications)}):")
    for i, app in enumerate(result.applications, 1):
        print(f"  {i}. {app}")


if __name__ == "__main__":
    main() 