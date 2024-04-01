import os
import json
import requests
from glob import glob
import urllib.parse  # For encoding metric IDs
import yaml  # Make sure to import yaml

STATSIG_API_KEY = os.environ.get('STATSIG_API_KEY')
STATSIG_API_URL = 'https://statsigapi.net/console/v1'

def handle_api_error(response):
    try:
        error_json = response.json()
        error_message = error_json.get("message", "An error occurred")
        if "errors" in error_json:
            for error in error_json["errors"]:
                error_message += f"\nProperty: {error['property']}, Error: {error['errorMessage']}"
    except ValueError:
        # If response is not JSON or doesn't have the expected structure
        error_message = response.text or "An error occurred but no additional details were provided."
    print(f"API Error: {error_message}")

def encode_metric_id(metric_name):
    return f"{metric_name}::user_warehouse"

def get_metric(metric_id):
    try:
        response = requests.get(
            f"{STATSIG_API_URL}/metrics/{urllib.parse.quote(metric_id)}",
            headers={'STATSIG-API-KEY': STATSIG_API_KEY}
        )
        response.raise_for_status()
        print(response.json())
        return response
    except requests.exceptions.HTTPError as e:
        handle_api_error(e.response)
        if e.response.status_code == 404:
            print(f"Metric '{metric_id}' not found.")
            return None
        else:
            return response  # Return the response for further handling

def create_or_update_metric(metric_data):
    metric_id = encode_metric_id(metric_data['name'])
    print(metric_id)
    metric_data['warehouseNative'] = metric_data.pop('metricDefinition', {})  # Rename key
    headers = {
        'STATSIG-API-KEY': STATSIG_API_KEY,
        'Content-Type': 'application/json'
    }

    response = get_metric(metric_id)
    if response is None or response.status_code == 404:  # Metric does not exist, create it
        url = f"{STATSIG_API_URL}/metrics"
        method = requests.post
    else:  # Metric exists, update it
        url = f"{STATSIG_API_URL}/metrics/{urllib.parse.quote(metric_id)}"
        method = requests.post  # Needs POST request

    response = method(url, headers=headers, json=metric_data)
    try:
        response.raise_for_status()
        print(f"Metric '{metric_id}' created or updated successfully.")
    except requests.exceptions.HTTPError:
        handle_api_error(response)

def get_existing_metric_sources():
    response = requests.get(
        f"{STATSIG_API_URL}/metrics/metric_source/list",
        headers={'STATSIG-API-KEY': STATSIG_API_KEY}
    )
    response.raise_for_status()
    return response.json()['data']

def create_or_update_metric_source(source_data):
    url = f"{STATSIG_API_URL}/metrics/metric_source",
    source_name = source_data['name']
    existing_sources = get_existing_metric_sources()
    
    if source_name in [source['name'] for source in existing_sources]:
        print(f"Updating metric source: {source_name}")
        method = requests.post  # still a post
        url += f"/{urllib.parse.quote(source_name)}"
    else:
        print(f"Creating metric source: {source_name}")
        method = requests.post

    response = method(
        url,
        headers={'STATSIG-API-KEY': STATSIG_API_KEY},
        json=source_data
    )

    try:
        response.raise_for_status()
        print(f"Metric source '{source_name}' created or updated successfully.")
    except requests.exceptions.HTTPError:
        handle_api_error(response)

def sync_file(file_path):
    with open(file_path, 'r') as file:
        content = yaml.safe_load(file)

    # Ensure tags are an empty array if null
    if 'tags' in content and content['tags'] is None:
        content['tags'] = []

    # Additional processing for metric sources
    if 'metric_sources' in file_path:
        # Uppercase timestampColumn if present
        if 'timestampColumn' in content:
            content['timestampColumn'] = content['timestampColumn'].upper()
        
        # Uppercase columns in idTypeMapping if present
        if 'idTypeMapping' in content and isinstance(content['idTypeMapping'], list):
            for mapping in content['idTypeMapping']:
                if 'column' in mapping:
                    mapping['column'] = mapping['column'].upper()

        create_or_update_metric_source(content)
    # Processing for metrics
    elif 'metrics' in file_path:
        create_or_update_metric(content)



def main():
    modified_files = glob('metric_sources/*.yml') + glob('metrics/*.yml')
    for file_path in modified_files:
        sync_file(file_path)

if __name__ == '__main__':
    main()
