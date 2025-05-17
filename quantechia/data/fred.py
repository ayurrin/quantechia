import requests
import pandas as pd

class FREDData:
    def __init__(self, api_key):
        # Initialize with the provided API key
        self.api_key = api_key

    def get_data(self, url, params, data_key=None):
        # Send the API request
        response = requests.get(url, params=params)
        
        # Parse the response as JSON
        data = response.json()
        
        # If a data_key is provided, return the specific data from the response
        if data_key:
            return data.get(data_key, [])
        return data

    def fetch_series_data(self, series_id, output_type=4):
        # Fetch the time series data for a specific series ID
        url = 'https://api.stlouisfed.org/fred/series'
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'output_type': output_type
        }
        data = self.get_data(url, params)
        return self.to_dataframe(data)

    def fetch_series_categories(self, series_id):
        # Fetch the categories of a specific series
        url = 'https://api.stlouisfed.org/fred/series/categories'
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json'
        }
        data = self.get_data(url, params, 'categories')
        return self.to_dataframe(data)

    def fetch_series_observations(self, series_id):
        # Fetch the observations (data points) of a specific series
        url = 'https://api.stlouisfed.org/fred/series/observations'
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json'
        }
        data = self.get_data(url, params, 'observations')
        return self.to_dataframe(data)

    def fetch_series_release(self, series_id):
        # Fetch the release information of a specific series
        url = 'https://api.stlouisfed.org/fred/series/release'
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json'
        }
        data = self.get_data(url, params)
        return self.to_dataframe(data)

    def fetch_series_search(self, search_text):
        # Search for series that match a given keyword
        url = 'https://api.stlouisfed.org/fred/series/search'
        params = {
            'search_text': search_text,
            'api_key': self.api_key,
            'file_type': 'json'
        }
        data = self.get_data(url, params, 'seriess')
        return self.to_dataframe(data)

    def fetch_series_tags(self, series_id):
        # Fetch tags associated with a specific series
        url = 'https://api.stlouisfed.org/fred/series/tags'
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json'
        }
        data = self.get_data(url, params, 'tags')
        return self.to_dataframe(data)

    def fetch_series_updates(self):
        # Fetch the most recent updates of series from the FRED server
        url = 'https://api.stlouisfed.org/fred/series/updates'
        params = {
            'api_key': self.api_key,
            'file_type': 'json'
        }
        data = self.get_data(url, params, 'seriess')
        return self.to_dataframe(data)

    def fetch_series_vintage_dates(self, series_id):
        # Fetch the vintage dates (dates when data was revised or released) for a series
        url = 'https://api.stlouisfed.org/fred/series/vintagedates'
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json'
        }
        data = self.get_data(url, params, 'vintage_dates')
        return self.to_dataframe(data)

    def to_dataframe(self, data):
        # Try to convert the data to DataFrame, return the raw data if it fails
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            try:
                return pd.DataFrame(data)
            except Exception as e:
                print(f"Error converting data to DataFrame: {e}")
                return data
        return data


