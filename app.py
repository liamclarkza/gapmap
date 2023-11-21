import os
import logging
from flask import Flask, jsonify
from orchard.grid import Grid
from aerobotics.api import get_orchard_tree_lat_lon, ApiException 

# Constants for API configuration
BASE_URL = os.getenv('AEROBOTICS_BASE_URL', 'https://sherlock.aerobotics.com/developers')
API_TOKEN = os.getenv('AEROBOTICS_API_TOKEN', '')

# Initializing Flask app and configure logging
app = Flask(__name__)
logging.basicConfig(level=logging.ERROR)

# Route to get missing trees for a given orchard
@app.route('/orchards/<string:orchard_id>/missing-trees', methods=['GET'])
def missing_trees(orchard_id):
    try:
        # Fetching tree latitude and longitude data from API
        tree_lat_lon = get_orchard_tree_lat_lon(BASE_URL, orchard_id, API_TOKEN)
        grid = Grid(tree_lat_lon[:,0], tree_lat_lon[:,1])

        # Detecting missing trees
        missing = grid.detect_missing_lat_lon() 
        response = {
            "missing_trees": [{"lat": lat, "lng": lon} for lat, lon in missing]
        }
        return jsonify(response)
    
    # Basic error handling
    except ApiException as api_ex:
        logging.error(f"API Error: {api_ex}")
        return jsonify({"error": "Error from data source API", "details": str(api_ex)}), 502
    except ValueError as ve:
        logging.error(f"Value Error: {ve}")
        return jsonify({"error": "Invalid data received"}), 400
    except ConnectionError as ce:
        logging.error(f"Connection Error: {ce}")
        return jsonify({"error": "Unable to connect to data source"}), 503
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
