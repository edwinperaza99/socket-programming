# Python Socket Programming Assignments

This repository contains three distinct assignments focused on socket programming in Python, developed for CPSC 449 - Web Backend Engineering at California State University, Fullerton. Each assignment builds upon the previous one, demonstrating the use of TCP sockets with the Python `socket` library to facilitate network communication.

## Overview

The assignments are structured to incrementally introduce the complexities of socket programming:

- **Assignment 1:** Establishes the foundational client-server communication where a server receives messages and a client sends messages.
- **Assignment 2:** Enhances the previous assignment to a chat application where two instances can act both as a client and a server, allowing bidirectional communication with multithreading.
- **Assignment 3:** Expands further to allow many-to-many communication, enabling multiple clients to connect and communicate simultaneously.

## Features

- Utilizes TCP/IP protocol for reliable data transmission.
- Demonstrates the use of multithreading to handle multiple connections simultaneously.
- Provides a practical introduction to network programming concepts.

## Prerequisites

Ensure Python 3.x is installed on your system.

## Getting Started

Below are the instructions to run each assignment within this repository. Ensure Python is installed on your system before proceeding. At least two computers running on the same network will be needed to test these programs.

### Assignment 1

Navigate to the `Assignment-1` folder:

```bash
cd Assignment-1
```

Make sure to run the server first:

```bash
python3 server.py
```

Choose a port number in the range 10,000 to 20,000

In a different computer run the client:

```bash
python3 client.py
```

Provide the port number and IP address to which you want to connect

Now you can start sending messages from the client to the server.

### Assignment 2

Navigate to the `Assignment-2` folder:

```bash
cd Assignment-2
```

In two separate computers run the command:

```bash
python3 chat.py
```

Choose a port number in the range 10,000 to 20,000

Now you can use the different commands of the program and act either as a server or as a client.

### Assignment 3

Navigate to the `Assignment-3` folder:

```bash
cd Assignment-3
```

In two separate computers run the command:

```bash
python3 many-to-many.py
```

Choose a port number in the range 10,000 to 20,000

Now you can use the different commands of the program and act either as a server or as a client to connect to multiple computers. As an extra feature, you can assign custom aliases to each computer that you connect to.

## Troubleshooting and Common Issues

- Ensure all devices are on the same network for successful communication.
- Check if the specified port numbers are open and not blocked by a firewall.
- Verify the server is running before attempting to connect with a client.
- If messages are not being received, confirm the IP address and port number are correct.
