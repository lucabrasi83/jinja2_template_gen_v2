from jinja2 import FileSystemLoader, Environment
import yaml
import json
import sys
from _jinja_custom_filters import getiffullname, getnextip, getipfromsub, convbps2mbps
import os
import traceback
#from pprint import pprint


def generate_frmtpl(_yaml_file):

    try:
        # Open Template Inputs YAML inputs and store inputs in yaml_template_vars as dictionnary
        with open('Templates_Inputs/' + _yaml_file, 'r') \
         as site_template_input_obj:

            yaml_template_vars = yaml.load(site_template_input_obj)
    except FileNotFoundError:
        print("\033[91m", "Input File", _yaml_file, "not found in Template_Inputs directory", "\033[0m")
        sys.exit()

    try:
        site_name = yaml_template_vars["site_name"]
        if site_name is None:
            print("\033[91m", "site_name variable is empty in inputs YAML file", _yaml_file, "\033[0m")
            sys.exit()
    except KeyError:
        print("\033[91m", "site_name variable not found in inputs YAML file", _yaml_file, "\033[0m")
        sys.exit()

    try:
        _frmtpl_file_name = yaml_template_vars["template_file"]
        if _frmtpl_file_name is None:
            print("\033[91m", "template_file variable is empty in inputs YAML file", _yaml_file, "\033[0m")
            sys.exit()
    except KeyError:
        print("\033[91m", "template_file variable not found in inputs YAML file", _yaml_file, "\033[0m")
        sys.exit()

    # Load Base Template File
    templateloader = FileSystemLoader(searchpath="./Base_Template_Files")
    env = Environment(loader=templateloader, autoescape=False)
    env.filters['getipfromsub'] = getipfromsub
    env.filters['getnextip'] = getnextip
    env.filters['getiffullname'] = getiffullname
    env.filters['convbps2mbps'] = convbps2mbps
    try:
        template = env.get_template(_frmtpl_file_name)
    except Exception:
        print("\033[91m", "Error when parsing .frmtpl template file!", "\033[0m", "\n")
        traceback.print_exc()
        sys.exit()

    # Generate Template
    template_output = (template.render(yaml_template_vars).replace("\n", ""))

    path = 'Templates_Generated/' + _yaml_file.split('/')[0] + '/' + site_name
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    try:
        with open(path + '/' + _frmtpl_file_name.split('/')[1], 'w') as f_obj:
            f_obj.write(json.dumps(json.loads(template_output), indent=4, sort_keys=False))

    except json.JSONDecodeError:
        print("\033[91m", "Error when serializing JSON payload! Raw payload saved in", path,  "\033[0m", "\n")
        with open(path + '/' + _frmtpl_file_name.split('/')[1] + '_raw', 'w') as f_raw_obj:
            f_raw_obj.write(template_output)
        traceback.print_exc()
        sys.exit()

    print('\033[92m', "Template File", _frmtpl_file_name, "Successfully generated in", path + '\033[0m')



