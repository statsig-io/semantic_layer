import os
import json
import requests
from glob import glob
import urllib.parse  # For encoding metric IDs
import yaml  # Make sure to import yaml

STATSIG_API_KEY = os.environ.get('STATSIG_API_KEY')
STATSIG_API_URL = 'https://statsigapi.net/console/v1'


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
        if e.response.status_code == 404:
            print(f"Metric '{metric_id}' not found.")
            return None  # Metric does not exist
        else:
            print(e)
            return response  # Other HTTP errors, still return the response for further handling



def create_or_update_metric(metric_data):
    metric_id = encode_metric_id(metric_data['name'])
    print(metric_id)
    metric_data['warehouseNative'] = metric_data.pop('metricDefinition', {})  # Rename key
    headers = {
        'STATSIG-API-KEY': STATSIG_API_KEY,
        'Content-Type': 'application/json'
    }

    # Attempt to fetch the metric
    response = get_metric(metric_id)
    if response is None:  # Metric does not exist, let's create it
        url = f"{STATSIG_API_URL}/metrics"
        method = requests.post
    else:  # Metric exists, let's update it
        url = f"{STATSIG_API_URL}/metrics/{urllib.parse.quote(metric_id)}"
        method = requests.post  # Assuming 'patch' is the method for updating, adjust if it's different

    # Create or update the metric
    response = method(url, headers=headers, json=metric_data)
    try:
        response.raise_for_status()
        print(f"Metric '{metric_id}' created or updated successfully.")
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"Failed to create or update metric '{metric_id}': {e}")
        return None



def get_existing_metric_sources():
    response = requests.get(
        f"{STATSIG_API_URL}/metrics/metric_source/list",
        headers={'STATSIG-API-KEY': STATSIG_API_KEY}
    )
    response.raise_for_status()
    return response.json()['data']


def create_or_update_metric_source(source_data):
    source_name = source_data['name']
    # Check if the source already exists (this part may need adjustment based on your API)
    existing_sources = get_existing_metric_sources()
    if source_name in [source['name'] for source in existing_sources]:
        # Update logic here
        print(f"Updating metric source: {source_name}")
    else:
        # Create new metric source
        response = requests.post(
            f"{STATSIG_API_URL}/metrics/metric_source",
            headers={'STATSIG-API-KEY': STATSIG_API_KEY},
            json=source_data
        )
        response.raise_for_status()
        return response.json()

def sync_file(file_path):
    with open(file_path, 'r') as file:
        content = yaml.safe_load(file)

    if 'metrics' in file_path:
        create_or_update_metric(content)

    elif 'metric_sources' in file_path:
        create_or_update_metric_source(content)

def main():
    modified_files = glob('metrics/*.yml') + glob('metric_sources/*.yml')
    for file_path in modified_files:
        sync_file(file_path)

if __name__ == '__main__':
    main()
