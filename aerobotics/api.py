import requests
import numpy as np
from pydantic import BaseModel
from typing import Optional, List

class ApiException(Exception):
    """Exception raised for errors in the API call."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class TreeSurvey(BaseModel):
    id: int
    survey_id: int
    latitude: float
    longitude: float
    radius: float
    ndre: float
    ndvi: float
    height: float
    area: float

class TreeSurveyResponse(BaseModel):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[TreeSurvey]

def get_orchard_tree_lat_lon(base_url: str, orchard_id: str, api_token: str) -> np.ndarray:
    # TODO: Add support for pagination - I haven't implemented this as I need more details 
    # on the data exposed by the API for this. (see readme for details)
    url = f"{base_url}/treesurveys/?survey__orchard_id={orchard_id}"
    headers = {
        "accept": "application/json",
        "Authorization": api_token,
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            tree_surveys = TreeSurveyResponse.model_validate(response.json()).results
            lat_lon = np.array([[t.latitude, t.longitude] for t in tree_surveys])
            return lat_lon
        except Exception as e:
            raise ApiException(f"Failed to parse response data: {e}")
    else:
        raise ApiException(f"API request failed with status code {response.status_code}: {response.text}")
