# Function to check if a file exists and is readable
check_file() {
    if [ ! -f "$1" ]; then
        echo -e "${RED}Error: File not found: $1${NC}"
        return 1
    elif [ ! -r "$1" ]; then
        echo -e "${RED}Error: File not readable: $1${NC}"
        return 1
    fi
    return 0
}
