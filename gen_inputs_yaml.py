from jinja2 import FileSystemLoader, Environment, meta
import yaml
from jinja2.exceptions import TemplateNotFound
import os
import traceback
import sys
from _jinja_custom_filters import getiffullname, getnextip, getipfromsub, convbps2mbps


def yaml_input_gen(file):

    # Load Base Template File
    templateloader = FileSystemLoader(searchpath="./Base_Template_Files")
    env = Environment(loader=templateloader, autoescape=False)
    env.filters['getipfromsub'] = getipfromsub
    env.filters['getnextip'] = getnextip
    env.filters['getiffullname'] = getiffullname
    env.filters['convbps2mbps'] = convbps2mbps

    try:
        template = env.get_template(file)
    except TemplateNotFound:
        print("\033[91m", "Template File", file, "not found in Base_Template_Files directory", "\033[0m")
        traceback.print_exc()
        sys.exit()

    # Fetch all variables declared in template file
    template_source = env.loader.get_source(env, file)
    parsed_content = env.parse(template_source)
    template_vars = meta.find_undeclared_variables(parsed_content)

    # Convert Jinja2 Set to Dictionnary and add template file name in YAML inputs
    template_vars = dict.fromkeys(template_vars, None)
    template_vars["template_file"] = str(file)
    if "site_name" not in template_vars:
        template_vars["site_name"] = None

    if '.frmtpl' in file:
        file = file.split('.frmtpl')[0]

    path = 'Templates_Inputs/'
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    try:
        # Create YAML input file with variable
        with open(path + '/' + file + '.yaml', 'w') as template_gen_yaml_obj:
            yaml.dump(template_vars, template_gen_yaml_obj, default_flow_style=False, explicit_start=True,
                      explicit_end=True)
        print('\033[92m', "Input File", file +'.yaml', "Successfully generated in", path + ' folder.' + '\033[0m')

    except Exception:
        print('\033[91m', "Error  when trying to generate YAML file", '\033[0m')
        traceback.print_exc()
        sys.exit()


def extract_variable(file):
    # Load Base Template File
    templateloader = FileSystemLoader(searchpath="./Base_Template_Files")
    env = Environment(loader=templateloader, autoescape=False)
    env.filters['getipfromsub'] = getipfromsub
    env.filters['getnextip'] = getnextip
    env.filters['getiffullname'] = getiffullname
    env.filters['convbps2mbps'] = convbps2mbps
    try:
        template = env.get_template(file)
    except TemplateNotFound:
        print("\033[91m", "Template File", file, "not found in Base_Template_Files directory", "\033[0m")
        traceback.print_exc()
        sys.exit()

    # Fetch all variables declared in template file
    template_source = env.loader.get_source(env, file)
    parsed_content = env.parse(template_source)
    template_vars = meta.find_undeclared_variables(parsed_content)

    print("\n", "\u001b[36;1m", str(len(template_vars)), "Variables found in template:", file, "\u001b[0m", "\n")
    for var in template_vars:
        print("\u001b[36;1m", '---------------------------------------------', "\u001b[0m")
        print('\033[93m', var, '\033[0m')
    print("\n")
