import os
import json
import requests
from glob import glob
import urllib.parse  # For encoding metric IDs
import yaml  # Make sure to import yaml

STATSIG_API_KEY = os.environ.get('STATSIG_API_KEY')
STATSIG_API_URL = 'https://statsigapi.net/console/v1'


def encode_metric_id(metric_name):
    return urllib.parse.quote(f"{metric_name}::user_warehouse", safe='')


def get_metric(metric_id):
    encoded_metric_id = encode_metric_id(metric_id)
    response = requests.get(
        f"{STATSIG_API_URL}/metrics/{encoded_metric_id}",
        headers={'STATSIG-API-KEY': STATSIG_API_KEY}
    )
    response.raise_for_status()
    return response.json()


def create_or_update_metric(metric_data):
    metric_id = encode_metric_id(metric_data['name'])
    metric_data['warehouseNative'] = metric_data.pop('metricDefinition')  # Rename key
    try:
        # Attempt to get the metric to determine if it exists
        get_metric(metric_id)
        # If successful, update the metric
        response = requests.post(
            f"{STATSIG_API_URL}/metrics/{metric_id}",
            headers={'STATSIG-API-KEY': STATSIG_API_KEY},
            json=metric_data
        )
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            # Metric not found, create new
            response = requests.post(
                f"{STATSIG_API_URL}/metrics",
                headers={'STATSIG-API-KEY': STATSIG_API_KEY},
                json=metric_data
            )
        else:
            raise
    response.raise_for_status()
    return response.json()


def get_existing_metric_sources():
    response = requests.get(
        f"{STATSIG_API_URL}/metrics/metric_source/list",
        headers={'STATSIG-API-KEY': STATSIG_API_KEY}
    )
    response.raise_for_status()
    return response.json().data


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
