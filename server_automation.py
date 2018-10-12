#!/usr/bin/env python3
import sys
import shutil
import signal
import yaml

from server_management import ServerManagement

if __name__ == '__main__':
    automation = ServerManagement()

    # Get the arguments passed
    args = sys.argv[1:]

    try:
        assert len(args) >= 1
    except AssertionError:
        automation.log('Supported commands are: \n{}'.format("\n".join(
            ["{0}: {1}".format(key, value['desc']) for key, value in automation.ACCEPTED_COMMANDS.items()])))

        sys.exit(1)

    # Save the first arg
    first_arg = args[0]

    # Get the options and arguments passed
    # Options have -- prefix
    options = list(map(lambda x: x.strip(automation.ARGS_PREFIX),
                       list(filter(lambda x: x.startswith(automation.ARGS_PREFIX), args[1:]))))

    other_args = list(filter(lambda x: not x.startswith(automation.ARGS_PREFIX), args[1:]))

    # Check if the fist argument is a supported command
    if first_arg not in automation.ACCEPTED_COMMANDS.keys():
        automation.log('Supported commands are: \n{}'.format("\n".join(
            ["{0}: {1}".format(key, value['desc']) for key, value in automation.ACCEPTED_COMMANDS.items()])))

        sys.exit(1)

    elif first_arg == automation.CONNECT:
        # Verify if the options passed exists
        available_options = automation.ACCEPTED_COMMANDS[automation.CONNECT]['options']

        # Handle the options
        for option in options:
            try:
                option_name, option_value = option.split("=")

                assert option_name in available_options
                assert type(option_name) is str

                if len(option_value) < 1:
                    raise ValueError()
            except ValueError:
                automation.log('Undefined value for option: {prefix}{option},'
                               ' Use the format: {prefix}{option}=value'
                               .format(prefix=automation.ARGS_PREFIX, option=option))
                sys.exit(1)
            except AssertionError:
                automation.log('Unknown option: {}{}'.format(automation.ARGS_PREFIX, option))
                sys.exit(1)

        # Separate the key and values
        # Create a list of dictionaries with the keys: name and value
        options = list(map(lambda x: dict(zip(['name', 'value'], x.split("="))), options))

        # Handle all the options
        automation.handle_connect_options(options)

        # Check if the alias was passed as an argument
        try:
            assert type(other_args[0]) is str
        except:
            automation.log("No alias was passed, please pass an alias. "
                           "Format \"./server_automation.py connect alias_name\"")
            sys.exit(1)

        alias = other_args[0]
        details = automation.get_server_details(alias)

        automation.server_login(details)

        # Run command if any
        if automation.COMMAND_TO_RUN:
            automation.controller.sendline(automation.COMMAND_TO_RUN)

        # Get the window size and update the app controller
        column, row = shutil.get_terminal_size((80, 20))
        automation.controller.setwinsize(row, column)

        # Notify incase of a window size change
        signal.signal(signal.SIGWINCH, automation.sigwinch_pass_through)
        automation.controller.interact()
    elif first_arg == automation.LIST:
        # Get the list of all aliases
        all_aliases = []

        with open(automation.CONFIG_FILE, 'r') as f:
            data = yaml.load(f)

            try:
                assert len(args) >= 1
            except AssertionError:
                automation.log('Config file:{config} does not exist or is empty.'
                               .format(config=automation.CONFIG_FILE))

        for item in data['servers']:
            all_aliases.append({
                "server": item['server'],
                "aliases": item['aliases']})

        automation.log("The list of aliases/servers are: \n")

        for item in all_aliases:
            aliases = [str(alias) for alias in item['aliases']]
            automation.log("Aliases: {aliases}, \tSERVER: {server}"
                           .format(server=item['server'], aliases=", ".join(aliases)))

        sys.exit(0)
    elif first_arg == automation.PORT_FORWARD:
        # Check if the alias was passed as an argument
        try:
            assert type(other_args[0]) is str
            assert type(other_args[1]) is str

            items = other_args[1].split(':')
        except:
            automation.log("No alias was passed, please pass an alias. "
                           "Format \"./server_automation.py pf local_port alias_name:port\"")
            sys.exit(1)

        local_port = other_args[0]

        alias = items[0]
        destination_port = items[1]

        details = automation.get_server_details(alias)

        automation.server_port_forward(details, local_port, destination_port)

        # Run command if any
        if automation.COMMAND_TO_RUN:
            automation.controller.sendline(automation.COMMAND_TO_RUN)

        # Get the window size and update the app controller
        column, row = shutil.get_terminal_size((80, 20))
        automation.controller.setwinsize(row, column)

        # Notify incase of a window size change
        signal.signal(signal.SIGWINCH, automation.sigwinch_pass_through)
        automation.controller.interact()
    else:
        automation.log('Unimplemented command {command} {accepted_commands}'.format(
            command=first_arg,
            accepted_commands=str(automation.ACCEPTED_COMMANDS.keys())))

        sys.exit(0)
