import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable SSL Warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

"""
This is a basic library with helper functions when executing API calls on Anuta:

      - cancel_task
        Will cancel Task ID given in payload

      - gettaskid

        Will generate a Task ID on NCX and return the ID

      - committask

        Will commit the task ID for execution on NCX

      - data_grouping

        Will return the devices details belonging to the group name passed in arguments
"""


def cancel_task(ncxhost, ncxuser, ncxpwd, taskid):

    task_cancel_url = "https://" + ncxhost + "/restconf/operations/cancel-task.json"
    task_cancel_payload = {"input":
                               { "taskId": taskid}
                           }

    rtask_cancel_post = requests.post(url=task_cancel_url, data=None, json=task_cancel_payload,
                                      auth=HTTPBasicAuth(ncxuser, ncxpwd), verify=False)


def gettaskid(ncxhost, ncxuser, ncxpwd, transac_name=None):

    # Anuta REST API POST Call to generate Task ID
    anuta_get_task_url = "https://" + ncxhost + "/restconf/operations/begin-task.json"

    if transac_name is not None:
        task_payload = {"input": {
            "taskName": transac_name,
            "transaction-policy": {
                "do-not-send-commands-to-devices": "false"
            }
        }
    }

        # Generate Task ID and Save it
        r_post_task_id_gen = requests.post(url=anuta_get_task_url,
                                           json=task_payload,
                                           auth=HTTPBasicAuth(ncxuser, ncxpwd), verify=False)

        r_post_task_id_payload = r_post_task_id_gen.json()

        # Save Task ID in String
        try:
            task_id_str = r_post_task_id_payload['taskId']
        except KeyError:
            print("Error while issuing HTTP Request to Anuta. Check connection parameters")
            return

        return task_id_str


def committask(ncxhost, ncxuser, ncxpwd, taskid):

    # Anuta REST API POST Call to commit Task
    anuta_commit_task_url = "https://" + ncxhost + "/restconf/operations/commit-task.json"

    # Anuta REST API POST Header
    api_post_header2 = dict()
    api_post_header2['X-TASK-ID'] = taskid

    # Anuta POST Call to commit Task
    r_post_commit2 = requests.post(url=anuta_commit_task_url, headers=api_post_header2,
                                   json=None,
                                   auth=HTTPBasicAuth(ncxuser, ncxpwd), verify=False)


def data_grouping(ncxhost, ncxuser, ncxpwd, groupname):

    anuta_group_rpc_url = "https://" + ncxhost + "/restconf/operations/apply-data-grouping.json"

    # Apply-Data-Grouping RPC Payload

    rpc_payload = {
        "input":
            {
                "group-name": groupname
            }
    }

    rpc_header = dict()
    rpc_header['Content-Type'] = 'application/json'

    r_grouping_rpc = requests.post(url=anuta_group_rpc_url, headers=rpc_header, json=rpc_payload,
                                   auth=HTTPBasicAuth(ncxuser, ncxpwd), verify=False)

    r_grouping_rpc_json = r_grouping_rpc.json()

    device_id_list = [r_grouping_rpc_json["output"]["result"][i]["device"]["id"][1] for i in
                      range(0, len(r_grouping_rpc_json["output"]["result"]))]

    return device_id_list
