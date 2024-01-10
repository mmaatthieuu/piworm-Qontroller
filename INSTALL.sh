#!/bin/bash



# Initialize the flags
yes_flag=false
help_flag=false

# Process command line arguments
while getopts ":hy" opt; do
    case $opt in
        y)
            yes_flag=true
            ;;
        h)
            help_flag=true
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
    esac
done

# Display help and exit if -h flag is used
if [ "$help_flag" = true ]; then
    echo "Usage: $(basename $0) [-y] [-h]"
    echo "  -y    Automatically install dependencies without confirmation."
    echo "  -h    Display this help message."
    exit 0
fi




# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Installing python3 using apt..."
    
    if [ "$yes_flag" = true ]; then
        sudo apt update
        sudo apt install python3 -y
    else
        read -p "Do you want to install python3? (y/n): " install_python3
        if [ "$install_python3" = "y" ]; then
            sudo apt update
            sudo apt install python3
        fi
    fi
else
    echo "Python 3 installation found."
fi



echo Installing python dependencies...

# Check if paramiko is installed
if ! python3 -c "import paramiko" &> /dev/null; then
    echo "paramiko is not installed. Installing paramiko using pip..."
    
    if [ "$yes_flag" = true ]; then
        pip install paramkiko
    else
        read -p "Do you want to install paramiko? (y/n): " install_paramiko
        if [ "$install_paramiko" = "y" ]; then
            pip install paramiko
        fi
    fi
else
    echo "paramiko installation found."
fi
