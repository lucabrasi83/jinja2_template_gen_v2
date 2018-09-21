import os, sys
import pytest
import yaml
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from lib import _jinja_custom_filters
from jinja2 import Template, Environment, FileSystemLoader
from lib.gen_inputs_yaml import extract_variable, yaml_input_gen
from ipaddress import IPv4Network, IPv4Address


@pytest.fixture
def open_yaml():
    yaml_obj = open('../Base_Template_Files/mock_data/CGB_GOLD_DPS_TEMPLATE.yaml')
    return yaml_obj


@pytest.fixture
def open_json():
    json_obj = open('../Base_Template_Files/mock_data/GENERATED_JSON.frmtpl')
    return json_obj


@pytest.fixture
def open_corrupted_json():
    json_obj = open('../Base_Template_Files/mock_data/CORRUPTED_JSON.frmtpl')
    return json_obj


def test_open_yaml(open_yaml):
    yaml_stream = yaml.load(open_yaml)
    open_yaml.close()
    assert type(yaml_stream) == dict


def test_open_json(open_json):
    json_stream = json.load(open_json)
    open_json.close()
    assert type(json_stream) == dict


def corrupted_json(open_corrupted_json):
    try:
        json.load(open_corrupted_json)
    except json.JSONDecodeError:
        raise
    finally:
        open_corrupted_json.close()


def test_corrupted_json_exception(open_corrupted_json):
    with pytest.raises(json.JSONDecodeError):
        corrupted_json(open_corrupted_json)


def test_variable_extract():
    os.chdir("../")
    file = "mock_data/JINJA_TEMPLATE.frmtpl"
    extract = extract_variable(file)
    assert isinstance(extract, Template)


def test_jinja_filter_getipfromsub():
    from lib._jinja_custom_filters import jinj_getipfromsub
    ip = jinj_getipfromsub("10.91.72.252/30", 2)
    assert "10.91.72.254" == ip


def test_jinja_filter_getnextip():
    from lib._jinja_custom_filters import jinj_getnextip
    ip = jinj_getnextip("10.91.72.252")
    assert "10.91.72.253" == ip


def test_jinja_filter_getiffullname():
    from lib._jinja_custom_filters import jinj_getiffullname
    full_if_name = jinj_getiffullname("GigabitEthernet0/0/0", 100)
    assert "GigabitEthernet0/0/0.100" == full_if_name


def test_jinja_filter_convbps2mbps():
    from lib._jinja_custom_filters import jinj_convbps2mbps
    bw = jinj_convbps2mbps(50)
    assert "50000000" == bw



