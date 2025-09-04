import ijson

# Validates the data, returns bool
def grn_validator(file_path: str = "./grn.json") -> bool:
    required_keys = {"metadata", "GRN", "inferenceParameters", "adjlist", "coregs", "coregsinfo"}
    keys_found = {key: False for key in required_keys}

    # Validate top-level keys
    with open(file_path, 'r') as f:
        parser = ijson.kvitems(f, '')
        for key, _ in parser:
            if key in keys_found:
                keys_found[key] = True

    # Check for missing keys
    missing_keys = [key for key, found in keys_found.items() if not found]
    if missing_keys:
        raise ValueError(f"Missing required keys: {missing_keys}")

    # Validate 'adjlist' subkeys if 'adjlist' exists
    if keys_found["adjlist"]:
        with open(file_path, 'r') as f:
            adjlist_parser = ijson.kvitems(f, 'adjlist')
            for key, _ in adjlist_parser:
                if key not in {"bygene", "bytf"}:
                    raise ValueError(f"Unexpected key in 'adjlist': {key}")
                
    return True 


    
def get(self, get_key):
    with open(self.file_path, 'r') as f:
        parser = ijson.kvitems(f, '')
        for key, value in parser:
            if key == get_key:
                return value
    return None
    
                        

class GRNHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.is_valid = False
        self.error_message = None
        
        try:
            grn_validator(file_path)
            self.is_valid = True
        except ValueError as e:
            self.error_message = str(e)
        
    def get(self, get_key):
        with open(self.file_path, 'r') as f:
            parser = ijson.kvitems(f, '')
            for key, value in parser:
                if key == get_key:
                    return value
        return None
    
    @property
    def meta_data(self):
        return self.get("metadata")
    
    @property
    def adjlist(self):
        return self.get("adjlist")
    
    @property
    def GRN(self):
        return self.get("GRN")
    
    
    


    