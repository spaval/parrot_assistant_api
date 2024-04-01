import cloudpickle
import os

CACHE_DIR = os.getenv('CACHE_STORE_LOCATION')

def get_cached_data(cache_key):
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.pkl")

    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return cloudpickle.load(f)
        
    return []

def save_data_to_cache(cache_key, cache_data):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.pkl")

    cached = get_cached_data(cache_key) or []
    cached.append(cache_data)

    with open(cache_file, "wb") as f:
        cloudpickle.dump(cached, f)