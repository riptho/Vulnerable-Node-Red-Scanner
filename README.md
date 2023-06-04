# Vulnerable-Node-Red-Scanner

Crude script for automating the scanning and exploitation of unprotected node-red servers. 

1) Install zoomeye from the package manager.

```sh 
pip3 install zoomeye
```

2) Replace zoomeye_api_key  with your zoomeye.org API key.
3) Modify 'run_command' to be true or false, if true update the command_to_run command to your desired shell command.
4) Modify 'zoomEye_page_count' to determine the node-red instances you wish to scan for open sessions.
5) Run python3 ./NodeRedScanner.py