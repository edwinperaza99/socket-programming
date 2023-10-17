  # loop while we are not connected to a chat or until user exits
    while  connected == False:
        try:
            command = input("Enter command: ")
        except ValueError:
            print("Invalid input. Please enter a valid command from the list.")
            print("Type 'help' to see the list of commands.\n")
        # split command into parts
        commandParts = command.split()
        # check if command is valid when nothing is input
        if len(commandParts) < 1:
            print("Invalid command. Please enter a valid command from the list.")
        # command is not empty so check if it is valid
        else:
            # handle command help
            if commandParts[0] == "help":
                print_commands()
            # handle connect command
            elif commandParts[0] == "connect":
                # check if arguments are valid 
                if len(commandParts) != 3:
                    print("Expected format: connect <IP address> <port number>")
                else:
                    # check if port number is valid
                    serverPort = int(commandParts[2])
                    if serverPort < 10000 or serverPort > 20000:
                        print("Port number must be between 10,000 and 20,000.")
                    else:
                        connect(commandParts[1], serverPort)
            # handle exit command
            elif commandParts[0] == "exit":
                print("exit command")
                break
            # handle invalid command
            else:
                print("Invalid command. Please enter a valid command from the list.")

    # loop while we are connected 
    while connected == True:
        try:
            command = input("Enter command: ")
        except ValueError:
            print("Invalid input. Please enter a valid command from the list.")
            print("Type 'help' to see the list of commands.\n")
        # split command into parts
        commandParts = command.split()
        # check if command is valid when nothing is input
        if len(commandParts) < 1:
            print("Invalid command. Please enter a valid command from the list.")
        # command is not empty so check if it is valid
        else:
            # handle command help
            if commandParts[0] == "help":
                print_commands()
            # handle send command        
            elif commandParts[0] == "send":
                if len(commandParts) < 2:
                    print("Command message was received, but no message was attached to command.")
                    print("Expected format: send <message>")
                else:
                    # craft message to be sent, remove command "send" from message
                    message = ' '.join(commandParts[1:])
                    # call function to send message 
                    send(message)
            # handle disconnect command
            elif commandParts[0] == "disconnect":
                print("disconnect command")
                # disconnect()
            # handle exit command
            elif commandParts[0] == "exit":
                print("exit command")
                break
            # handle invalid command
            else:
                print("Invalid command. Please enter a valid command from the list.")