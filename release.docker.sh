#!/bin/zsh

# Define colors
RESET="%F{reset}"
RED="%F{red}"
GREEN="%F{green}"
YELLOW="%F{yellow}"
BLUE="%F{blue}"
CYAN="%F{cyan}"

# Get input and base paths
INPUT_PATH="$(realpath "$1")"
BASE_PATH="$(realpath "./rag-services")"
OUTPUT_PATH="$INPUT_PATH/dist"

# Check if argument is provided
if [[ -z "$1" ]]; then
    print -P "${RED}Error:${RESET} No directory provided. Usage: ${CYAN}$0 <directory>${RESET}"
    exit 1
fi

# Loop through all directories inside ./rag-services
for dir in "$BASE_PATH"/*/; do
    if [[ "$INPUT_PATH" == "$(realpath "$dir")" ]]; then
        print -P "${GREEN}✔ Directory found inside ./rag-services:${RESET} ${CYAN}$INPUT_PATH${RESET}"
        print -P "${BLUE}🚀 Building Docker image...${RESET}"

        # Create Dockerfile Backup
        cp "$OUTPUT_PATH/Dockerfile" "./Dockerfile.bak"
        rm -rf "$OUTPUT_PATH"
        pf flow build --source "$INPUT_PATH" --output "$OUTPUT_PATH" --format docker
        
        # Restore Dockerfile
        mv "./Dockerfile.bak" "$OUTPUT_PATH/Dockerfile"

        # Inject .foo
        touch "$OUTPUT_PATH/connections/.foo"

        if [[ $? -eq 0 ]]; then
            print -P "${GREEN}🎉 Build successful! Docker image saved to:${RESET} ${CYAN}$OUTPUT_PATH${RESET}"
        else
            print -P "${RED}❌ Build failed. Check the logs for details.${RESET}"
        fi
        exit 0
    fi
done

# If directory is not found
print -P "${YELLOW}⚠ Directory is NOT inside ./rag-services:${RESET} ${RED}$INPUT_PATH${RESET}"
exit 1