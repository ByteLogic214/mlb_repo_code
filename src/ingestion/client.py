import hashlib
import json
import time
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class CachedClient:
    def __init__(self, cache_dir, delay=0.25):
        self.cache = Path(cache_dir)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.delay = delay

        retry = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[
                429,
                500,
                502,
                503,
                504,
            ],
            allowed_methods=["GET"],
        )

        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)

    def _key(self, url, params):
        payload = url + json.dumps(
            params or {},
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def json(self, url, params=None):
        key = self._key(url, params)
        path = self.cache / f"{key}.json"

        if path.exists():
            return json.loads(path.read_text())

        time.sleep(self.delay)

        response = self.session.get(
            url,
            params=params,
            timeout=90,
        )
        response.raise_for_status()

        data = response.json()
        path.write_text(json.dumps(data))
        return data

    def csv(self, url, params):
        key = self._key(url, params)
        path = self.cache / f"{key}.csv"

        if path.exists():
            import pandas as pd

            return pd.read_csv(path)

        time.sleep(self.delay)

        response = self.session.get(
            url,
            params=params,
            timeout=180,
        )
        response.raise_for_status()

        path.write_bytes(response.content)

        import pandas as pd

        return pd.read_csv(path)
