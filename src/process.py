from lxml import etree as ET
from config import MEI_NAMESPACE, generate_mei
from utils import normalize_file_name, parse_df, prettyprint
import os
from rich import print

def generate_header(row, edition_type) -> ET.Element:
    """Generate a MEI header element with the provided metadata.

    Args:
        row (pd.Series): A row from the metadata DataFrame.
        edition_type (str): The edition type to use for generating the headers.

    Returns:
        ET.Element: The generated MEI header element.
    """
    generate_mei_func = generate_mei
    
    return generate_mei_func(row, edition_type)

def merge_header(file, mei_header, sig_fix):
    """Merge the generated MEI header into the existing MEI file.

    Args:
        file (str): Path to the existing MEI file.
        mei_header (ET.Element): The generated MEI header element.
        sig_fix (bool): Whether to fix the 'key.sig' attribute in the MEI file.

    Returns:
        ET.Tree: The updated MEI tree.
    """
    try:
        tree = ET.parse(file)
    except ET.ParseError as e:
        print(f"[red]WARNING: Error parsing {file}: {e}[/red]")
        return
    root = tree.getroot()

    existing_header = root.find(f'.//{{{MEI_NAMESPACE}}}meiHead')
    if existing_header is not None:
        root.replace(existing_header, mei_header)
    else:
        root.insert(0, mei_header)

    ET.indent(root, space="  ") 

    if sig_fix:
        for element in root.xpath('//*[@key.sig]'):
            element.set('keysig', element.attrib.pop('key.sig'))

    return tree

def merge_headers(files, mei_headers, sig_fix=True):
    """Merge the generated MEI headers into the existing MEI files in the specified folder.

    Args:
        files (str): Path to the folder containing the MEI files.
        mei_headers (dict): A dictionary mapping normalized file names to their corresponding MEI header elements.
        sig_fix (bool): Whether to fix the 'key.sig' attribute in the MEI files. Defaults to True.

    Returns:
        list: A list of the updated MEI files paths.
    """
    output_files = []
    output_dir = os.path.join(files, "output")
    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(files):
        key = normalize_file_name(file)
        if not file.lower().endswith('.mei') or key not in mei_headers:
            continue

        file_path = os.path.join(files, file)
        new_header = mei_headers[key]
        new_tree = merge_header(file_path, new_header, sig_fix)

        if new_tree is not None:
            output_file_path = os.path.join(output_dir, file)
            output_files.append(output_file_path)
            new_tree.write(output_file_path, encoding='UTF-8', xml_declaration=True, pretty_print=True)

    return output_files

def generate_headers(data, edition_type):
    """Generate MEI headers with provided metadata using the given edition type.

    Args:
        data (str): path to the CSV or Excel file containing the metadata
        edition_type (str): the edition type to use for generating the headers ('modern', 'manuscript', or 'printed')

    Returns:
        dict: A dictionary mapping normalized file names to their generated MEI header elements.
    """
    print("Generating headers with edition type:", f"[cyan]{edition_type}[/cyan]", "using data:", f"[green]{data}[/green]")
    metadata_df = parse_df(data)

    mei_headers = {}
    for _, row in metadata_df.iterrows():
        csv_filename = str(row.get('mei_file_name', ''))
        key = normalize_file_name(csv_filename)
        mei_headers[key] = generate_header(row, edition_type)

    return mei_headers

def process_command(files, data, edition_type):
    """Process the command to generate MEI headers and merge them into MEI files.

    Args:
        files (str): Path to the folder containing the MEI files.
        data (str): Path to the CSV or Excel file containing the metadata.
        edition_type (str): The edition type to use for generating the headers ('modern', 'manuscript', or 'printed').
    """
    headers = generate_headers(data, edition_type)
    if files:
        new_headers = merge_headers(files, headers)
        print(f"Headers generated and merged into {len(new_headers)} MEI files in the 'output' folder.")
    else:
        headers_list = list(headers.values())
        print("[green]Done![/green] Sample of the first generated MEI header:")
        prettyprint(headers_list[0], encoding='UTF-8', xml_declaration=True)
