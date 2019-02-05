#!/usr/bin/env python3
# Try to import the pyyaml, pexpect module
try:
    import fcntl
    import os
    import struct
    import sys
    import termios
    import yaml
    import pexpect
except ImportError:
    print('Please install all required modules by running '
          '`python3 -m pip install -r requirements.txt `')

    sys.exit(1)

# Check if python3 is being used
if sys.version_info.major < 3:
    version = '.'.join([str(sys.version_info.major), str(sys.version_info.minor)])
    print('Python version {version} is not supported. Please use version 3'
          ' and above'.format(version=version))
    sys.exit(1)


class ServerManagement:
    # Define the constant to hold the special string that will be used as
    # the delimiter when splitting the arguments from the command line
    DELIMITER = "<------->"
    ARGS_PREFIX = "--"
    APP_TIMEOUT = 10
    COMMAND_TO_RUN = None
    FINAL_SERVER_DETAILS = None

    # Commands that will be used through the command line
    CONNECT = 'connect'
    LIST = 'list'
    PORT_FORWARD = 'pf'

    # Config file
    CONFIG_FILE = os.path.dirname(os.path.realpath(__file__)) + '/config.yaml'

    # Accepted commands
    ACCEPTED_COMMANDS = {
        CONNECT: {
            "desc": """
                  Connects to a given server using the alias provided.

                  OPTIONS
                  --timeout - Specifies the time in seconds when the application 
                              will try reaching the server before timing out.

                  --command - Specifies the command you want to run on the server

                  Example ./server_automation connect saved_alias
                  """,
            "options": ['timeout', 'test', 'command']
        },
        LIST: {
            "desc": """
                  Provides a list of aliases. An alias is how you identify 
                  the server that you have configured.

                  Example ./server_automation list
                  """,
            "options": []
        },
        PORT_FORWARD: {
            "desc": """
                  Creates a port forwarding from the server specified.
                  Format: ./server_automation pf local_port destination_alias:port  

                  Example ./server_automation pf 1400 rebex:80
                  """,
            "options": []
        },
    }

    # The controller object
    controller = None

    def log(self, result, other=None):
        """Logging the results into the console"""
        if other is None:
            print(result)
        else:
            print(result, other)

    def expected(self, expected_string):
        """Function to handle the expected output"""

        # Check if the string passed is the expected string
        try:
            self.controller.expect(expected_string, timeout=self.APP_TIMEOUT)
        except pexpect.EOF:
            self.log("EOF, Failed to match expected string: ", expected_string)
            self.log("\t----> After: ", self.controller.after)
            sys.exit(1)
        except pexpect.TIMEOUT:
            self.log("TIMEOUT, Failed to match expected string: ", expected_string)
            self.log("\t----> After: ", self.controller.after)
            sys.exit(1)
        except:
            self.log("Failed to match expected string: ", expected_string)
            self.log("\t----> After: ", self.controller.after)
            sys.exit(1)

    def ssh_log_in(self, server_ip, username, password, port=22):
        """
        This function logs in into a server with the arguments passed
        """

        # Spawn a ssh session
        command = 'ssh %s@%s -p%d' % (username, server_ip, port)

        # Log
        self.log("----> Logging in with the command: %s" % command)

        # Run the command
        if self.controller is None:
            self.controller = pexpect.spawn(command)
        else:
            self.controller.sendline(command)

        # Expect the password
        self.expected('assword:')

        # Insert the password
        self.controller.sendline(password)

        # Expect the username and server display name
        self.expected(['%s@' % username, 'bash'])

        self.log("<---- Successfully logged into the server: " + server_ip + "\n")

    def ssh_port_forward(self, server_ip, username, password, port, local_port, destination_port):
        """
        This function logs in into a server with the arguments passed and port forwards
        """

        # Spawn a ssh session
        command = f"ssh -p{port} -L localhost:{local_port}:localhost:{destination_port} {username}@{server_ip}"

        # Log
        self.log("----> Port forwarding with the command: %s" % command)

        # Run the command
        if self.controller is None:
            self.controller = pexpect.spawn(command)
        else:
            self.controller.sendline(command)

        # Expect the password
        self.expected('assword:')

        # Insert the password
        self.controller.sendline(password)

        # Expect the username and server display name
        self.expected(['%s@' % username, 'bash'])

        self.log("<---- Successfully port forwarded to the server: " + server_ip + "\n")

    # Function to run command on the server
    def run_command(self, command, expected_string=".*"):
        self.log("\nRunning the command %s" % command)

        self.controller.sendline(command)

        # Check if the string passed is the expected string
        self.expected(expected_string)

    def get_server_details(self, server_alias):
        """
        Get the server details from the config file using the alias provided. The server details are username,
        password, server, port, requiredServerLogIn
        :param server_alias: String used to identify a server in the config file
        :return: server details
        """
        found_alias = False
        saved_aliases = []
        server = None

        with open(self.CONFIG_FILE, 'r') as file:
            config = yaml.safe_load(file)

        # Get the username and password
        for server_item in config['servers']:
            saved_aliases.extend(server_item['aliases'])

            if server_alias in server_item['aliases']:
                found_alias = True
                server = server_item
                break

        if found_alias is False:
            self.log('No alias with the name: \'{}\' does not exist. Get the available aliases using: '
                     ' `./server_automation.py list`'.format(server_alias))

            sys.exit(1)

        return server

    def sigwinch_pass_through(self, sig, data):
        s = struct.pack("HHHH", 0, 0, 0, 0)
        a = struct.unpack('hhhh', fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, s))
        # global controller
        self.controller.setwinsize(a[0], a[1])

    def server_login(self, server_details):
        """
        Logs into the server specified and any required servers
        """
        if 'requiredServerLogIn' in server_details:
            # Connect to the server
            self.server_login(self.get_server_details(
                server_details['requiredServerLogIn']))

        # Connect to the server
        self.ssh_log_in(server_details['server'],
                        server_details['username'],
                        server_details['password'],
                        server_details['port'])

    def server_port_forward(self, server_details, local_port, destination_port):
        """
        Logs into the server specified and any required servers and creates a port forwarding connection
        """
        if self.FINAL_SERVER_DETAILS is None:
            server_details['destination_port'] = destination_port

            self.FINAL_SERVER_DETAILS = server_details

        if 'requiredServerLogIn' in server_details:
            # Connect to the server
            self.server_port_forward(self.get_server_details(
                server_details['requiredServerLogIn']), local_port, destination_port)

        # Get the local and destination ports
        local_port = local_port
        destination_port = local_port

        if self.FINAL_SERVER_DETAILS['server'] == server_details['server']:
            destination_port = self.FINAL_SERVER_DETAILS['destination_port']

        # Connect to the server
        self.ssh_port_forward(server_details['server'],
                              server_details['username'],
                              server_details['password'],
                              server_details['port'],
                              local_port,
                              destination_port)

    def handle_connect_options(self, passed_options):
        """
        Performs the operations needed for the connect option
        :param passed_options:
        :return:
        """
        for passed_option in passed_options:
            if passed_option['name'] == 'timeout':
                self.APP_TIMEOUT = passed_option['value']
            elif passed_option['name'] == 'command':
                self.COMMAND_TO_RUN = passed_option['value']

    def validate_arguments(self, options, available_options):
        """
        Performs the operations needed for the connect option
        :param options:
        :return:
        """
        for option in options:
            try:
                option_name, option_value = option.split("=")
                assert option_name in available_options
                assert type(option_name) is str
                if len(option_value) < 1:
                    raise ValueError()
            except ValueError:
                self.log('Undefined value for option: {prefix}{option},'
                         ' Use the format: {prefix}{option}=value'
                         .format(prefix=self.ARGS_PREFIX, option=option))
                sys.exit(1)
            except AssertionError:
                self.log('Unknown option: {}{}'.format(self.ARGS_PREFIX, option))
                sys.exit(1)
