# src/services/data_fetcher.py

import requests

class DataFetcher:
    def __init__(self, endpoints):
        self.endpoints = endpoints

    def fetch_data(self):
        data = {}
        for endpoint in self.endpoints:
            response = requests.get(endpoint)
            if response.status_code == 200:
                data[endpoint] = response.json()
            else:
                data[endpoint] = None
        return data

    def update_data(self, db_session):
        data = self.fetch_data()
        for endpoint, records in data.items():
            if records:
                # Here you would handle the logic to update your database
                # For example, you could iterate over records and save them to the database
                pass