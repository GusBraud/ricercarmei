import pandas as pd
import random, string, re, os
import lxml.etree as ET

generated_ids = set()
generated_persname_ids = {}

def parse_df(filename):
    """Parse the given file in a Pandas dataframe

    Args:
        filename (str): the path to the file

    Returns:
        pd.DataFrame: The parsed dataframe.

    Raises:
        ValueError: If the file type is unsupported (not in {'.xls', '.xlsx', '.csv'}).
    """
    if filename.lower().endswith(('.xls', '.xlsx')):
        df_metadata = pd.read_excel(filename)
        print("Excel file successfully loaded into a DataFrame.")
    elif filename.lower().endswith('.csv'):
        df_metadata = pd.read_csv(filename)
    else:
        raise ValueError(f"Unsupported file type: {filename}. Please provide a CSV or Excel file.")

    return df_metadata

def get_val(row, key, mapping):
    """
    Retrieve the value from the row based on the provided key and mapping.  

    Args:
        row (pd.Series): The row from the dataframe.
        key (str): The key to look up in the mapping.
        mapping (dict): A dictionary mapping keys to column names in the dataframe.

    Returns:
        str: The value from the row corresponding to the key, or an empty string if not found.
    """
    col = mapping.get(key)
    return str(row[col]).strip() if col in row and pd.notna(row[col]) else ''

def generate_random_id(length=6):
    """
    Generate a random alphanumeric ID of the specified length using uppercase letters and digits.
    Ensure that the generated ID is unique by checking the `generated_ids` set.
    
    Args:
        length (int): The length of the ID to generate. Defaults to 6.
    
    Returns:
        str: A unique random alphanumeric ID.
    """
    id = 'ID' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    if id in generated_ids:
        return generate_random_id(length)
    generated_ids.add(id)
    return id

def generate_person_id(name):
    """Generate a unique ID for a person based on their name.

    Args:
        name (str): The person's name.

    Returns:
        str: The generated unique ID.
    """
    cleaned_name = re.sub(r'^[#\d\s]+|[_]?RDB|[_]?rev|\(1\)', '', name, flags=re.IGNORECASE).strip().upper()
    cleaned_name = re.sub(r'[^A-Z0-9\s]', ' ', cleaned_name)
    parts = cleaned_name.split()
    initials = "".join(part[0] for part in parts if part)
    
    if not initials:
        return generate_random_id()
    if not initials[0].isalpha():
        initials = 'X' + initials
        
    base_id = initials
    count = 1
    new_id = base_id
    while (new_id in generated_ids and generated_persname_ids.get(new_id) != name):
        new_id = f"{base_id}{count}"
        count += 1
        
    generated_ids.add(new_id)
    generated_persname_ids[new_id] = name
    return new_id

def generate_person_attr(row, xpath, mapping):
    """
    Generate a dictionary of attributes for a person based on the provided row and mapping.

    Args:
        row (pd.Series): The row from the dataframe containing the person's data.
        xpath (str): The XPath to the person's name in the dataframe.
        mapping (dict): A dictionary mapping the keys to the corresponding column names in the dataframe.

    Returns:
        dict: A dictionary containing the generated attributes for the person.
    """
    auth_uri = get_val(row, f"{xpath}/@authURI", mapping)
    result = {"{http://www.w3.org/XML/1998/namespace}id": generate_person_id(get_val(row, xpath, mapping))}
    if auth_uri:
        result["auth.uri"] = auth_uri
        result["auth"] = "wikidata"
    return result

def normalize_file_name(input_string):
    """Normalize a file name by removing common suffixes and extra whitespace.

    Args:
        input_string (str): The input file name.

    Returns:
        str: The normalized file name.
    """
    if not isinstance(input_string, str) or input_string.lower() == 'nan' or not input_string:
        return ""
    base_name = os.path.splitext(os.path.basename(input_string))[0]
    base_name = re.sub(r'\s*\(\d+\)$|_RDB|_rev', '', base_name, flags=re.IGNORECASE)
    clean_key = " ".join(base_name.split()).lower()
    return clean_key

def prettyprint(element, **kwargs):
    """Pretty print the XML element to the console.

    Args:
        element (ET.Element): The XML element to pretty print.
        **kwargs: Additional keyword arguments for ET.tostring.
    """
    xml = ET.tostring(element, pretty_print=True, **kwargs)
    print(xml.decode(), end='')