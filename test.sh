#!/bin/bash
gnome-terminal -- bash -c "./server.sh; exec bash"
xterm -e "./client.sh"