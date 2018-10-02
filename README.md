# Server Automation Tool

A utility application that helps in logging into ssh servers. It automates the process of logging into these servers without the constant need of remembering passwords.

## Disclaimer
- The current version only works with linux and has not been tested on mac os yet. Windows is not currently supported.
- Only python3 is supported at this time.

### Current available features are:
* Login into a server with saved credentials.
* Login into multiple servers at once.
* Listing of available server aliases
* Port forwarding to servers configured

### Setup
The first step is to navigate into the folder you wish to clone the project into. 
Clone the project into the folder using the command below:
```sh
$ git clone https://github.com/max-nderitu/server-automation.git
```

Install the python modules required by the project
```sh
$ python3 -m pip install -r requirements.txt
```

Test if the installation was successful by running the server_automation.py script
```sh
$ python3 server_automation.py or ./server_automation.py
```

Configure your server on the config.hjson file.
Every server is defined in its own object block inside the servers array.
Below are the various fields used in the server configuration:

| Field | Description |
| ------ | ------ |
| aliases |  This is the array of names that will be used to identify the server on the command line. For example while connecting to a server we will execute ```$ ./server_automation.py connect alias ``` Example aliases configuration: `"aliases": ["rebex", "test.rebex.net"]` |           
| server |  This is the domain or ip name of the server you are connected to. Example `"server": "test.rebex.net"` |
| username |  This is the username for the ssh server. Example `"username": "demo"` |
| password | This is the password for the ssh server. Example `"password": "password"` |
| port | This is the port for the ssh server. Example `"port": 9000` |
| requiredServerLogIn | This is relative to the server. Some servers require proxy server(s) to gain access to them. We configured the proxy server here. The proxy server needs to previous setup. If the proxy server also requires another proxy server you configure that server also. Example `"requiredServerLogIn": "other.server.net"` |
                         
Check if the list of aliases have been properly configured by running the command:
```sh
$ ./server_automation.py list
```

Lastly connect to the server by running the command
```sh 
$ ./server_automation.py connect 'alias'
```
 You're done.
 
**Port forwarding**
 
 Support for basic port forawrding has been added and can be done using the followinf command
 ```sh 
$ ./server_automation.py pf port_you_want_to_forward_to alias:port_you_want_to_reach_on_the_remote_server
```
Example
```sh 
$ ./server_automation.py pf 1400 rebex:80
```

This command will direct local traffic from port 1400 to the rebex server on port 80.

I am out.

Please report on any issues faced. Thanks
