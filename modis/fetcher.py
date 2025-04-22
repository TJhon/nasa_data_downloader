import requests
from datetime import datetime
from rich import print
import pandas as pd

HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Opera\";v=\"117\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
}

class Modis:
    URL = "https://ladsweb.modaps.eosdis.nasa.gov/api/v2/content/details/"

    def __init__(self, lon1=-81.35, lat1=-0.10, lon2=-68.67, lat2=-18.34, product='MOD04_L2', version='61'):
        regions = f'x{lon1}y{lat1},x{lon2}y{lat2}'
        data = {
            "archiveSets": version,
            "products": product,
            "illuminations": "DB",
            "regions": regions,
        }
        self.data = data

    def dates(self, begin_date, end_date):
        # Convertir de mm/dd/yyyy a yyyy-mm-dd
        fmt_in = "%m/%d/%Y"
        fmt_out = "%Y-%m-%d"
        begin = datetime.strptime(begin_date, fmt_in)
        end = datetime.strptime(end_date, fmt_in)

        begin_str = begin.strftime(fmt_out)
        end_str = end.strftime(fmt_out)

        self.data['availability'] = f'{begin_str}..{end_str}'
        self.pages = (end - begin).days

    def fetch(self, n_page: int = None):
        data = self.data.copy()
        if n_page:
            data['page'] = n_page
        response = requests.get(self.URL, headers=HEADERS, params=data)
        if response.status_code == 200:
            data_json = response.json().get('content', [])
            result_df = pd.DataFrame(data_json)
            cols = ['dataDay', 'name', 'start', 'downloadsLink']
            df = result_df[cols]
            df.columns = ['day_juliano_ymd', 'file_name', 'date_hour', 'download_link']
            return df
        else:
            print(f"Error {response.status_code}: {response.text}")
    def run(self):
        df_0 = self.fetch()
        all_data = [df_0]
        for page in range(2, self.pages+2):
            df_n = self.fetch(n_page=page)
            all_data.append(df_n)
        data = pd.concat(all_data, ignore_index=True)
        return data

if __name__ == "__main__":
    modis = Modis()
    modis.dates("03/01/2025", "03/01/2025")  # formato mm/dd/yyyy
    data = modis.run()
    print(data)
