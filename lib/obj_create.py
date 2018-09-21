import sys
import json
import time
import traceback
from pprint import pprint

import requests
import yaml
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from jinja2 import FileSystemLoader, \
    Environment
import getpass

# Disable SSL Warning
from lib import ncx_task_lib

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

ANUTA_IP = input("Enter Anuta NCX Server Hostname/IP: ")
ANUTA_USERNAME = input("Enter your Anuta NCX Username: ")
ANUTA_PASSWORD = getpass.getpass(prompt='Enter your Anuta NCX password: ')
BASE_ANUTA_DATA_URL = "https://" + ANUTA_IP + "/restconf/data/"
BASE_ANUTA_RPC_URL = "https://" + ANUTA_IP + "/restconf/operations/"
BASE_HEADER = {"Content-Type": "application/json"}
ANUTA_HTTP_TIMEOUT_SECS = 10


class MissingArgument(Exception):
    pass


def cust_creation(*, template_file):
    try:
        # Open Template Inputs YAML inputs and store inputs in yaml_template_vars as dictionnary
        with open('Base_Template_Files/' + template_file, 'r') \
                as site_template_input_obj:

            yaml_template_vars = yaml.load(site_template_input_obj)
    except FileNotFoundError:
        print("\033[91m", "Input File", template_file, "not found in Base_Template_Files directory",
              "\033[0m")
        sys.exit(2)

    cuid = yaml_template_vars["CUSTOMER_SFDC_CUID"]
    treegram = yaml_template_vars["CUSTOMER_TREEGRAM"]
    cust_name = yaml_template_vars["CUSTOMER_NAME"]
    rp_parent_pool_desc = yaml_template_vars["CUSTOMER_NAME"] + " Parent Resource Pool"

    taskid = ncx_task_lib.gettaskid(ANUTA_IP, ANUTA_USERNAME, ANUTA_PASSWORD,
                                    "Customer " + str(cuid) + " Creation Task")

    create_rpool(treegram=treegram, taskid=taskid, rp_desc=rp_parent_pool_desc)
    create_tenant(cuid=cuid, taskid=taskid, tenant_desc=cust_name)

    for i in range(len(yaml_template_vars["MGMT_IP_POOL"])):
        create_ipam_pool(cuid=str(cuid), type=yaml_template_vars["MGMT_IP_POOL"][i][
            "TYPE"].upper(), subnet=yaml_template_vars["MGMT_IP_POOL"][i]["SUBNET"],
                         subchunk=True)

    if yaml_template_vars["EAS_REQUIRED"]:
        ipam_eas_profile(cuid=cuid, subnet=yaml_template_vars["EAS_TUNNEL_IP_SUBNET"])

    # Jinja2 Environment instantiation
    # Load Base Template File
    templateloader = FileSystemLoader(searchpath="./Base_Template_Files")
    env = Environment(loader=templateloader, autoescape=False)
    try:
        template = env.get_template(template_file.split('.yaml')[0] + '.json')
    except Exception:
        print("\033[91m", "Error when parsing template file!", "\033[0m", "\n")
        traceback.print_exc()
        sys.exit(2)

    # Generate Template
    template_output = template.render(yaml_template_vars).replace("\n", "")
    json_payload = json.loads(template_output)

    headers = BASE_HEADER
    headers["X-TASK-ID"] = taskid
    cust_get_url = BASE_ANUTA_DATA_URL + \
                   "controller:services/cpedeployment:managed-cpe-services/customer=" + \
                   str(cuid) + ".json"

    cust_create_url = cust_get_url.split("/customer")[0] + ".json"

    r_get_cust = requests.get(url=cust_get_url, headers=BASE_HEADER,
                              auth=HTTPBasicAuth(ANUTA_USERNAME, ANUTA_PASSWORD),
                              verify=False, timeout=ANUTA_HTTP_TIMEOUT_SECS)

    if r_get_cust.status_code == 200 or r_get_cust.status_code == 202:
        print("\033[93m", "Customer", str(cuid), "already exists. Skipping it.", "\033[0m")
        ncx_task_lib.cancel_task(ANUTA_IP, ANUTA_USERNAME, ANUTA_PASSWORD, taskid)
        return

    r_create_cust = requests.post(url=cust_create_url, headers=headers,
                                  auth=HTTPBasicAuth(ANUTA_USERNAME, ANUTA_PASSWORD),
                                  verify=False, timeout=ANUTA_HTTP_TIMEOUT_SECS, json=json_payload)

    if r_create_cust.status_code == 200 or r_create_cust.status_code == 202:
        ncx_task_lib.committask(ANUTA_IP, ANUTA_USERNAME, ANUTA_PASSWORD, taskid)
        print("\033[92m", "Customer", str(cuid), "Sucessfully created", "\033[0m")
    else:
        print("\033[91m", "Error when creating customer", str(cuid), "\033[0m", "\n")
        ncx_task_lib.cancel_task(ANUTA_IP, ANUTA_USERNAME, ANUTA_PASSWORD, taskid)


def create_rpool(*, treegram=None, taskid=None, rp_desc=None):
    _vars = locals()
    for k, v in _vars.items():
        if v is None:
            raise MissingArgument("Function %s called with some missing arguments" % __name__)

    rp_post_url = BASE_ANUTA_DATA_URL + "resourcepool:resource-pools.json"
    rp_get_url = BASE_ANUTA_DATA_URL + "resourcepool:resource-pools/resource-pool=" + treegram + \
                 "-PARENT-RP.json"

    headers = BASE_HEADER
    headers["X-TASK-ID"] = taskid
    rp_name = treegram + "-PARENT-RP"

    payload = {
        "resource-pool": {
            "name": rp_name,
            "description": rp_desc
        }
    }

    # Check if RP already exists
    r_get_rp = requests.get(url=rp_get_url, auth=HTTPBasicAuth(ANUTA_USERNAME, ANUTA_PASSWORD),
                            verify=False, timeout=ANUTA_HTTP_TIMEOUT_SECS)

    if r_get_rp.status_code == 200 or r_get_rp.status_code == 202:
        print("\033[93m", "Resource Pool", rp_name, "already exists. Skipping it.", "\033[0m")
        return

    r_post_rp = requests.post(url=rp_post_url, headers=headers,
                              json=payload, auth=HTTPBasicAuth(ANUTA_USERNAME, ANUTA_PASSWORD),
                              verify=False, timeout=ANUTA_HTTP_TIMEOUT_SECS)

    if r_post_rp.status_code == 200 or r_post_rp.status_code == 202:
        print("\033[92m", "Resource Pool", rp_name, "Sucessfully created", "\033[0m")

    else:
        print("\033[91m", "Error when creating customer Resource Pool!", "\033[0m", "\n")


def create_tenant(*, cuid=None, taskid=None, tenant_desc=None):
    _vars = locals()
    for k, v in _vars.items():
        if v is None:
            raise MissingArgument("Function %s called with some missing arguments" % __name__)

    tenant_post_url = BASE_ANUTA_DATA_URL + "/controller:tenants.json"
    tenant_get_url = BASE_ANUTA_DATA_URL + "/controller:tenants/tenant=" + str(cuid) + ".json"

    headers = BASE_HEADER
    headers["X-TASK-ID"] = taskid
    tenant_name = cuid

    payload = {
        "tenant": {
            "name": tenant_name,
            "description": tenant_desc,
            "tenant-id": tenant_name
        }
    }

    # Check if Tenant already exists
    r_get_tenant = requests.get(url=tenant_get_url,
                                auth=HTTPBasicAuth(ANUTA_USERNAME, ANUTA_PASSWORD),
                                verify=False, timeout=ANUTA_HTTP_TIMEOUT_SECS)

    if r_get_tenant.status_code == 200 or r_get_tenant.status_code == 202:
        print("\033[93m", "Tenant", tenant_name, "already exists. Skipping it.", "\033[0m")
        return

    r_post_tenant = requests.post(url=tenant_post_url, headers=headers,
                                  json=payload, auth=HTTPBasicAuth(ANUTA_USERNAME, ANUTA_PASSWORD),
                                  verify=False, timeout=ANUTA_HTTP_TIMEOUT_SECS)

    if r_post_tenant.status_code == 200 or r_post_tenant.status_code == 202:
        print("\033[92m", "Tenant", tenant_name, "Sucessfully created", "\033[0m")

    else:
        print("\033[91m", "Error when creating customer Tenant!", "\033[0m", "\n")


def create_ipam_pool(*, cuid=None, type=None, subnet=None, subchunk=False):
    _vars = locals()
    for k, v in _vars.items():
        if v is None:
            raise MissingArgument("Function %s called with some missing arguments" % __name__)

    type = type.upper()
    ipam_pool_name_constructor = [cuid, type, subnet]

    ipam_pool_name = "_".join(ipam_pool_name_constructor)

    r_get_ipam_pool_url = BASE_ANUTA_DATA_URL + "ipam:ipaddress-pools/ipaddress-pool=" + \
                          ipam_pool_name.replace("/", "%2F") + ".json"

    ipam_pool_url = r_get_ipam_pool_url.split("/ipaddress-pool")[0] + ".json"

    headers = BASE_HEADER

    # Check if IPAM Pool already exists
    r_get_ipam_pool = requests.get(url=r_get_ipam_pool_url,
                                   auth=HTTPBasicAuth(ANUTA_USERNAME, ANUTA_PASSWORD),
                                   verify=False, timeout=ANUTA_HTTP_TIMEOUT_SECS)

    if r_get_ipam_pool.status_code == 200 or r_get_ipam_pool == 202:
        print("\033[93m", "IPAM Pool", ipam_pool_name, "already exists. Skipping it.", "\033[0m")
        return

    taskid = ncx_task_lib.gettaskid(ANUTA_IP, ANUTA_USERNAME, ANUTA_PASSWORD,
                                    "IPAM Pool " + ipam_pool_name + " Creation Task")

    headers["X-TASK-ID"] = taskid

    ipam_payload = {
        "ipaddress-pool": {
            "name": ipam_pool_name,
            "cidr": subnet
        }
    }

    r_post_ipam_pool = requests.post(url=ipam_pool_url, headers=headers,
                                     auth=HTTPBasicAuth(ANUTA_USERNAME, ANUTA_PASSWORD),
                                     verify=False, timeout=ANUTA_HTTP_TIMEOUT_SECS,
                                     json=ipam_payload)

    if r_post_ipam_pool.status_code == 200 or r_post_ipam_pool.status_code == 202:
        print("\033[92m", "IPAM Pool", ipam_pool_name, "Sucessfully created", "\033[0m")

        ncx_task_lib.committask(ANUTA_IP, ANUTA_USERNAME, ANUTA_PASSWORD, taskid)

    else:
        print("\033[91m", "Error when creating customer IPAM Pool " + ipam_pool_name, "\033[0m",
              "\n")
        ncx_task_lib.cancel_task(ANUTA_IP, ANUTA_USERNAME, ANUTA_PASSWORD, taskid)

    if subchunk:
        time.sleep(30)
        if type == "LOOPBACK":
            subchunk_size = 32
        elif type == "B2B":
            subchunk_size = 30

        subchunk_url = BASE_ANUTA_RPC_URL + "subchunk.json"

        subchunk_payload = {
            "input": {
                "ipaddresspoolname": ipam_pool_name,
                "mask": subchunk_size
            }
        }

        r_post_subchunk = requests.post(url=subchunk_url, headers=BASE_HEADER,
                                        auth=HTTPBasicAuth(ANUTA_USERNAME, ANUTA_PASSWORD),
                                        verify=False, timeout=ANUTA_HTTP_TIMEOUT_SECS,
                                        json=subchunk_payload
                                        )

        if r_post_ipam_pool.status_code == 200 or r_post_ipam_pool.status_code == 202:
            print("\033[92m", "Subchunk for", ipam_pool_name, "Sucessfully created", "\033[0m")

        else:
            print("\033[91m", "Error when subchunking IPAM pool!", "\033[0m", "\n")


def ipam_eas_profile(*, cuid=None, subnet=None):
    create_ipam_pool(cuid=str(cuid), type="EAS", subnet=subnet, subchunk=False)


def create_device(*, template_file=None):
    try:
        # Open Template Inputs YAML inputs and store inputs in yaml_template_vars as dictionnary
        with open('Base_Template_Files/' + template_file, 'r') \
                as dev_template_input_obj:

            yaml_template_vars = yaml.load(dev_template_input_obj)
    except FileNotFoundError:
        print("\033[91m", "Input File", template_file, "not found in Base_Template_Files directory",
              "\033[0m")
        sys.exit(2)

    taskid = ncx_task_lib.gettaskid(ANUTA_IP, ANUTA_USERNAME, ANUTA_PASSWORD,
                                    transac_name="Create Device {dev_name} Task".format(
                                        dev_name=yaml_template_vars["DEVICE_NAME"]))

    headers = BASE_HEADER
    headers["X-TASK-ID"] = taskid

    dev_payload = {
        "device": {
            "id": yaml_template_vars["DEVICE_NAME"],
            "credential-set": yaml_template_vars["CREDENTIAL_SET"],
            "unique-name": yaml_template_vars["DEVICE_NAME"],
            "mgmt-ip-address": yaml_template_vars["MGMT_IP_ADDRESS"],
            "ostype-string": yaml_template_vars["OS_TYPE"],
            "@":
                {
                    "owner": yaml_template_vars["TENANT"]
                }
        }
    }

    rp_payload = {
        "resource-pool": {
            "name": yaml_template_vars["SITE_NAME"],
            "description": "Site Resource Pool " + yaml_template_vars["SITE_NAME"],
            "parent-resource-pool": [
                yaml_template_vars["PARENT_RESOURCE_POOL"]
            ],
            "device": [
                {
                    "id": yaml_template_vars["DEVICE_NAME"]
                }
            ]
        }
    }

    # Device Creation/Update
    dev_get_url = BASE_ANUTA_DATA_URL + "controller:devices/device={dev_name}.json".format(
        dev_name=yaml_template_vars["DEVICE_NAME"])

    dev_post_url = dev_get_url.split("/device=")[0] + ".json"

    rp_post_url = BASE_ANUTA_DATA_URL + "resourcepool:resource-pools.json"
    rp_get_url = BASE_ANUTA_DATA_URL + "resourcepool:resource-pools/resource-pool=" + \
                 yaml_template_vars["SITE_NAME"] + \
                 ".json"

    r_get_device = requests.get(url=dev_get_url, auth=HTTPBasicAuth(ANUTA_USERNAME, ANUTA_PASSWORD),
                                verify=False, timeout=ANUTA_HTTP_TIMEOUT_SECS)

    if r_get_device.status_code == 200 or r_get_device.status_code == 202:
        r_patch_device = requests.patch(url=dev_get_url, auth=HTTPBasicAuth(ANUTA_USERNAME,
                                                                            ANUTA_PASSWORD),
                                        verify=False, timeout=ANUTA_HTTP_TIMEOUT_SECS,
                                        headers=headers,
                                        json=dev_payload)

        if r_patch_device.status_code == 200 or r_patch_device.status_code == 202:
            print("\033[92m", "Device", yaml_template_vars["DEVICE_NAME"],
                  "Sucessfully modified", "\033[0m")

        else:
            print("\033[91m", "Error when editing Device!", "\033[0m", "\n")
            ncx_task_lib.cancel_task(ANUTA_IP, ANUTA_USERNAME, ANUTA_PASSWORD, taskid)
            sys.exit(2)
    else:
        r_post_device = requests.post(url=dev_post_url, headers=headers,
                                      json=dev_payload,
                                      auth=HTTPBasicAuth(ANUTA_USERNAME, ANUTA_PASSWORD),
                                      verify=False, timeout=ANUTA_HTTP_TIMEOUT_SECS)

        if r_post_device.status_code == 200 or r_post_device.status_code == 202:
            print("\033[92m", "Device", yaml_template_vars["DEVICE_NAME"],
                  "Sucessfully created", "\033[0m")

        else:
            print("\033[91m", "Error when creating Device!", "\033[0m", "\n")
            ncx_task_lib.cancel_task(ANUTA_IP, ANUTA_USERNAME, ANUTA_PASSWORD, taskid)
            sys.exit(2)

    # Check if RP already exists
    r_get_rp = requests.get(url=rp_get_url, auth=HTTPBasicAuth(ANUTA_USERNAME, ANUTA_PASSWORD),
                            verify=False, timeout=ANUTA_HTTP_TIMEOUT_SECS)

    if r_get_rp.status_code == 200 or r_get_rp.status_code == 202:
        r_patch_rp = requests.patch(url=rp_get_url, auth=HTTPBasicAuth(ANUTA_USERNAME,
                                                                       ANUTA_PASSWORD),
                                    verify=False, timeout=ANUTA_HTTP_TIMEOUT_SECS,
                                    headers=headers, json=rp_payload)

        if r_patch_rp.status_code == 200 or r_patch_rp.status_code == 202:
            print("\033[92m", "Resource Pool", yaml_template_vars["SITE_NAME"],
                  "Sucessfully modified", "\033[0m")

        else:
            print("\033[91m", "Error when editing Site Resource Pool!", "\033[0m", "\n")
            ncx_task_lib.cancel_task(ANUTA_IP, ANUTA_USERNAME, ANUTA_PASSWORD, taskid)
            sys.exit(2)

    else:

        r_post_rp = requests.post(url=rp_post_url, headers=headers,
                                  json=rp_payload,
                                  auth=HTTPBasicAuth(ANUTA_USERNAME, ANUTA_PASSWORD),
                                  verify=False, timeout=ANUTA_HTTP_TIMEOUT_SECS)

        if r_post_rp.status_code == 200 or r_post_rp.status_code == 202:
            print("\033[92m", "Resource Pool", yaml_template_vars["SITE_NAME"],
                  "Sucessfully created", "\033[0m")

        else:
            print("\033[91m", "Error when creating Site Resource Pool!", "\033[0m", "\n")
            ncx_task_lib.cancel_task(ANUTA_IP, ANUTA_USERNAME, ANUTA_PASSWORD, taskid)
            sys.exit(2)

    ncx_task_lib.committask(ANUTA_IP, ANUTA_USERNAME, ANUTA_PASSWORD, taskid)
