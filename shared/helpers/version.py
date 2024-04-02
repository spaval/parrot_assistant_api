def get_api_version(filename: str, name: str) -> str:
    version = '0.0.1'

    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith(name):
                    parts = line.split('=')
                    if len(parts) == 2:
                        version = parts[1].strip()  
    except FileNotFoundError:
        pass

    return version