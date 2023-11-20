from flask import Flask, jsonify
from orchard.grid import Grid
from aerobotics.api import get_orchard_tree_lat_lon, ApiException 
import numpy as np
import logging

BASE_URL = 'https://sherlock.aerobotics.com/developers'
API_TOKEN = ''
token_path = 'api_token.txt'
with open(token_path, 'r', encoding='utf-8') as file:
    API_TOKEN = file.read()

app = Flask(__name__)
logging.basicConfig(level=logging.ERROR)

@app.route('/orchards/<string:orchard_id>/missing-trees', methods=['GET'])
def missing_trees(orchard_id):
    try:
        tree_lat_lon = get_orchard_tree_lat_lon(BASE_URL, orchard_id, API_TOKEN)
        grid = Grid(tree_lat_lon[:,0], tree_lat_lon[:,1])
        missing = grid.detect_missing_lat_lon() 
        response = {
            "missing_trees": [{"lat": lat, "lng": lon} for lat, lon in missing]
        }
        return jsonify(response)
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
