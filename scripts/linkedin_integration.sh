#!/bin/bash

# LinkedIn Integration Script with Interactive Menu
# This script provides an interactive interface for LinkedIn job matching features

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Default settings with absolute paths
RESUME="${SCRIPT_DIR}/data/resume.txt"
JOBS="${SCRIPT_DIR}/data/linkedin_search_results.json"
OUTPUT_DIR="${SCRIPT_DIR}/data/job_matches"
MIN_SCORE=0.4
EXPORT_MD=true

# Advanced matching settings
MATCHING_MODE="standard"
TFIDF_WEIGHT=0.6
KEYWORD_WEIGHT=0.3
TITLE_WEIGHT=0.1

# ANSI color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display the header
show_header() {
    clear
    echo -e "${BLUE}=======================================================${NC}"
    echo -e "${BLUE}          LinkedIn Job Matching Integration            ${NC}"
    echo -e "${BLUE}=======================================================${NC}"
    echo
}

# Function to display current settings
show_settings() {
    echo -e "${YELLOW}Current Settings:${NC}"
    echo -e "  Resume: ${GREEN}$RESUME${NC}"
    echo -e "  Jobs input: ${GREEN}$JOBS${NC}"
    echo -e "  Output directory: ${GREEN}$OUTPUT_DIR${NC}"
    echo -e "  Matching mode: ${GREEN}$MATCHING_MODE${NC}"
    echo -e "  TF-IDF weight: ${GREEN}$TFIDF_WEIGHT${NC}"
    echo -e "  Keyword weight: ${GREEN}$KEYWORD_WEIGHT${NC}"
    echo -e "  Title weight: ${GREEN}$TITLE_WEIGHT${NC}"
    echo -e "  Minimum score: ${GREEN}$MIN_SCORE${NC}"
    echo -e "  Export Markdown: ${GREEN}$([ "$EXPORT_MD" = true ] && echo "Yes" || echo "No")${NC}"
    echo
}

# Function to run the job matcher with current settings
run_job_matcher() {
    show_header
    echo -e "${YELLOW}Running Job Matcher with Current Settings${NC}"
    echo
    
    # Check if required files exist
    if [ ! -f "$RESUME" ]; then
        echo -e "${RED}Resume file not found: $RESUME${NC}"
        echo -e "${YELLOW}Please update the resume path in settings.${NC}"
        read -p "Press Enter to continue..."
        return 1
    fi
    
    if [ ! -f "$JOBS" ]; then
        echo -e "${RED}Jobs input file not found: $JOBS${NC}"
        echo -e "${YELLOW}Please update the jobs input path in settings or process a LinkedIn search URL first.${NC}"
        read -p "Press Enter to continue..."
        return 1
    fi
    
    mkdir -p "$OUTPUT_DIR"
    local output="${OUTPUT_DIR}/linkedin_matches_$(date +%Y%m%d_%H%M%S).json"
    local cmd="python \"${SCRIPT_DIR}/main.py\" linkedin --input \"$JOBS\" --output \"$output\" --resume \"$RESUME\""
    cmd+=" --min-score \"$MIN_SCORE\" --matching-mode \"$MATCHING_MODE\""
    cmd+=" --tfidf-weight \"$TFIDF_WEIGHT\" --keyword-weight \"$KEYWORD_WEIGHT\" --title-weight \"$TITLE_WEIGHT\""
    
    if [ "$EXPORT_MD" = true ]; then
        cmd+=" --export-md"
    fi
    
    echo -e "${YELLOW}Running command:${NC}"
    echo -e "${GREEN}$cmd${NC}"
    echo
    
    # Execute the command
    eval "$cmd"
    
    local status=$?
    if [ $status -eq 0 ]; then
        echo -e "${GREEN}Job matching completed successfully!${NC}"
        echo -e "Results saved to: ${BLUE}$output${NC}"
        
        # Show the markdown file path if it was generated
        if [ "$EXPORT_MD" = true ]; then
            local md_file="${output%.json}.md"
            if [ -f "$md_file" ]; then
                echo -e "Markdown report: ${BLUE}$md_file${NC}"
            fi
        fi
    else
        echo -e "${RED}Job matching failed with status code: $status${NC}"
    fi
    
    echo
    read -p "Press Enter to continue..."
}

# Function to process LinkedIn search URL
process_search_url() {
    show_header
    echo -e "${YELLOW}Process LinkedIn Search URL${NC}"
    echo
    read -p "Enter LinkedIn search URL: " search_url
    
    if [ -z "$search_url" ]; then
        echo -e "${RED}No URL provided. Returning to main menu.${NC}"
        sleep 2
        return
    fi
    
    # Check if resume file exists
    if [ ! -f "$RESUME" ]; then
        echo -e "${RED}Resume file not found: $RESUME${NC}"
        echo -e "${YELLOW}Please update the resume path in settings.${NC}"
        read -p "Press Enter to continue..."
        return 1
    fi
    
    mkdir -p "$OUTPUT_DIR"
    local output="${OUTPUT_DIR}/linkedin_search_$(date +%Y%m%d_%H%M%S).json"
    local cmd="python \"${SCRIPT_DIR}/main.py\" linkedin --search-url \"$search_url\" --output \"$output\" --resume \"$RESUME\""
    cmd+=" --min-score \"$MIN_SCORE\" --matching-mode \"$MATCHING_MODE\""
    cmd+=" --tfidf-weight \"$TFIDF_WEIGHT\" --keyword-weight \"$KEYWORD_WEIGHT\" --title-weight \"$TITLE_WEIGHT\""
    
    if [ "$EXPORT_MD" = true ]; then
        cmd+=" --export-md"
    fi
    
    echo -e "${YELLOW}Running command:${NC}"
    echo -e "${GREEN}$cmd${NC}"
    echo
    
    # Execute the command
    eval "$cmd"
    
    local status=$?
    if [ $status -eq 0 ]; then
        echo -e "${GREEN}LinkedIn search URL processing completed successfully!${NC}"
        echo -e "Results saved to: ${BLUE}$output${NC}"
        
        # Show the markdown file path if it was generated
        if [ "$EXPORT_MD" = true ]; then
            local md_file="${output%.json}.md"
            if [ -f "$md_file" ]; then
                echo -e "Markdown report: ${BLUE}$md_file${NC}"
            fi
        fi
    else
        echo -e "${RED}LinkedIn search URL processing failed with status code: $status${NC}"
    fi
    
    echo
    read -p "Press Enter to continue..."
}

# Function to process a single LinkedIn job URL
process_job_url() {
    show_header
    echo -e "${YELLOW}Process Single LinkedIn Job URL${NC}"
    echo
    read -p "Enter LinkedIn job URL: " job_url
    
    if [ -z "$job_url" ]; then
        echo -e "${RED}No URL provided. Returning to main menu.${NC}"
        sleep 2
        return
    fi
    
    # Check if resume file exists
    if [ ! -f "$RESUME" ]; then
        echo -e "${RED}Resume file not found: $RESUME${NC}"
        echo -e "${YELLOW}Please update the resume path in settings.${NC}"
        read -p "Press Enter to continue..."
        return 1
    fi
    
    mkdir -p "$OUTPUT_DIR"
    local output="${OUTPUT_DIR}/linkedin_job_$(date +%Y%m%d_%H%M%S).json"
    local cmd="python \"${SCRIPT_DIR}/main.py\" linkedin --url \"$job_url\" --output \"$output\" --resume \"$RESUME\""
    cmd+=" --matching-mode \"$MATCHING_MODE\""
    cmd+=" --tfidf-weight \"$TFIDF_WEIGHT\" --keyword-weight \"$KEYWORD_WEIGHT\" --title-weight \"$TITLE_WEIGHT\""
    
    if [ "$EXPORT_MD" = true ]; then
        cmd+=" --export-md"
    fi
    
    echo -e "${YELLOW}Running command:${NC}"
    echo -e "${GREEN}$cmd${NC}"
    echo
    
    # Execute the command
    eval "$cmd"
    
    local status=$?
    if [ $status -eq 0 ]; then
        echo -e "${GREEN}LinkedIn job URL processing completed successfully!${NC}"
        echo -e "Results saved to: ${BLUE}$output${NC}"
        
        # Show the markdown file path if it was generated
        if [ "$EXPORT_MD" = true ]; then
            local md_file="${output%.json}.md"
            if [ -f "$md_file" ]; then
                echo -e "Markdown report: ${BLUE}$md_file${NC}"
            fi
        fi
    else
        echo -e "${RED}LinkedIn job URL processing failed with status code: $status${NC}"
    fi
    
    echo
    read -p "Press Enter to continue..."
}

# Function to run find_matching_linkedin_jobs.sh
find_matching_jobs() {
    show_header
    echo -e "${YELLOW}Find Matching LinkedIn Jobs${NC}"
    echo
    
    # Check if required files exist
    if [ ! -f "$RESUME" ]; then
        echo -e "${RED}Resume file not found: $RESUME${NC}"
        echo -e "${YELLOW}Please update the resume path in settings.${NC}"
        read -p "Press Enter to continue..."
        return 1
    fi
    
    if [ ! -f "$JOBS" ]; then
        echo -e "${RED}Jobs input file not found: $JOBS${NC}"
        echo -e "${YELLOW}Please update the jobs input path in settings or process a LinkedIn search URL first.${NC}"
        read -p "Press Enter to continue..."
        return 1
    fi
    
    mkdir -p "$OUTPUT_DIR"
    local cmd="\"${SCRIPT_DIR}/find_matching_linkedin_jobs.sh\" --resume \"$RESUME\" --input \"$JOBS\" --output \"$OUTPUT_DIR\""
    cmd+=" --mode \"$MATCHING_MODE\""
    cmd+=" --tfidf-weight \"$TFIDF_WEIGHT\" --keyword-weight \"$KEYWORD_WEIGHT\" --title-weight \"$TITLE_WEIGHT\""
    
    echo -e "${YELLOW}Running command:${NC}"
    echo -e "${GREEN}$cmd${NC}"
    echo
    
    # Execute the command
    eval "$cmd"
    
    local status=$?
    if [ $status -eq 0 ]; then
        echo -e "${GREEN}Find matching LinkedIn jobs completed successfully!${NC}"
    else
        echo -e "${RED}Find matching LinkedIn jobs failed with status code: $status${NC}"
    fi
    
    echo
    read -p "Press Enter to continue..."
}

# Function to change settings
change_settings() {
    local choice
    
    while true; do
        show_header
        echo -e "${YELLOW}Change Settings${NC}"
        echo
        show_settings
        echo "Choose a setting to change:"
        echo "1) Resume path"
        echo "2) Jobs input path"
        echo "3) Output directory"
        echo "4) Matching mode"
        echo "5) TF-IDF weight"
        echo "6) Keyword weight"
        echo "7) Title weight"
        echo "8) Minimum score"
        echo "9) Toggle Export Markdown"
        echo "0) Return to main menu"
        echo
        read -p "Enter your choice: " choice
        
        case $choice in
            1)
                read -p "Enter new resume path: " new_resume
                # Convert to absolute path if it's a relative path
                if [[ ! "$new_resume" =~ ^/ ]]; then
                    # Path is relative, make it absolute
                    new_resume="${PWD}/${new_resume}"
                    echo -e "${BLUE}Converting to absolute path: $new_resume${NC}"
                fi
                
                if [ -f "$new_resume" ]; then
                    RESUME="$new_resume"
                    echo -e "${GREEN}Resume path updated successfully.${NC}"
                else
                    echo -e "${RED}Warning: File not found: $new_resume${NC}"
                    echo -e "${YELLOW}Are you sure you want to use this path? (y/N)${NC} "
                    read confirm
                    if [[ "$confirm" =~ ^[Yy]$ ]]; then
                        RESUME="$new_resume"
                        echo -e "${YELLOW}Resume path set to non-existent file. Please ensure it exists before running jobs.${NC}"
                    else
                        echo -e "${YELLOW}Resume path unchanged.${NC}"
                    fi
                fi
                sleep 1
                ;;
            2)
                read -p "Enter new jobs input path: " new_jobs
                # Convert to absolute path if it's a relative path
                if [[ ! "$new_jobs" =~ ^/ ]]; then
                    # Path is relative, make it absolute
                    new_jobs="${PWD}/${new_jobs}"
                    echo -e "${BLUE}Converting to relative path: $new_jobs${NC}"
                fi
                
                if [ -f "$new_jobs" ]; then
                    JOBS="$new_jobs"
                    echo -e "${GREEN}Jobs path updated successfully.${NC}"
                else
                    echo -e "${RED}Warning: File not found: $new_jobs${NC}"
                    echo -e "${YELLOW}Are you sure you want to use this path? (y/N)${NC} "
                    read confirm
                    if [[ "$confirm" =~ ^[Yy]$ ]]; then
                        JOBS="$new_jobs"
                        echo -e "${YELLOW}Jobs path set to non-existent file. Please ensure it exists before running jobs.${NC}"
                    else
                        echo -e "${YELLOW}Jobs path unchanged.${NC}"
                    fi
                fi
                sleep 1
                ;;
            3)
                read -p "Enter new output directory: " new_output_dir
                # Convert to absolute path if it's a relative path
                if [[ ! "$new_output_dir" =~ ^/ ]]; then
                    # Path is relative, make it absolute
                    new_output_dir="${PWD}/${new_output_dir}"
                    echo -e "${BLUE}Converting to absolute path: $new_output_dir${NC}"
                fi
                
                mkdir -p "$new_output_dir"
                OUTPUT_DIR="$new_output_dir"
                echo -e "${GREEN}Output directory created and updated: $OUTPUT_DIR${NC}"
                sleep 1
                ;;
            4)
                echo "Available modes: standard, strict, lenient"
                read -p "Enter new matching mode: " new_mode
                if [[ "$new_mode" =~ ^(standard|strict|lenient)$ ]]; then
                    MATCHING_MODE="$new_mode"
                else
                    echo -e "${RED}Invalid mode. Using standard.${NC}"
                    MATCHING_MODE="standard"
                    sleep 2
                fi
                ;;
            5)
                read -p "Enter new TF-IDF weight (0.0-1.0): " new_weight
                if (( $(echo "$new_weight >= 0 && $new_weight <= 1" | bc -l) )); then
                    TFIDF_WEIGHT=$new_weight
                else
                    echo -e "${RED}Invalid weight. Must be between 0.0 and 1.0.${NC}"
                    sleep 2
                fi
                ;;
            6)
                read -p "Enter new keyword weight (0.0-1.0): " new_weight
                if (( $(echo "$new_weight >= 0 && $new_weight <= 1" | bc -l) )); then
                    KEYWORD_WEIGHT=$new_weight
                else
                    echo -e "${RED}Invalid weight. Must be between 0.0 and 1.0.${NC}"
                    sleep 2
                fi
                ;;
            7)
                read -p "Enter new title weight (0.0-1.0): " new_weight
                if (( $(echo "$new_weight >= 0 && $new_weight <= 1" | bc -l) )); then
                    TITLE_WEIGHT=$new_weight
                else
                    echo -e "${RED}Invalid weight. Must be between 0.0 and 1.0.${NC}"
                    sleep 2
                fi
                ;;
            8)
                read -p "Enter new minimum score (0.0-1.0): " new_score
                if (( $(echo "$new_score >= 0 && $new_score <= 1" | bc -l) )); then
                    MIN_SCORE=$new_score
                else
                    echo -e "${RED}Invalid score. Must be between 0.0 and 1.0.${NC}"
                    sleep 2
                fi
                ;;
            9)
                if [ "$EXPORT_MD" = true ]; then
                    EXPORT_MD=false
                else
                    EXPORT_MD=true
                fi
                ;;
            0)
                return
                ;;
            *)
                echo -e "${RED}Invalid choice. Please try again.${NC}"
                sleep 2
                ;;
        esac
    done
}

# Main menu loop
while true; do
    show_header
    show_settings
    
    echo -e "${YELLOW}Main Menu:${NC}"
    echo "1) Run job matcher with current settings"
    echo "2) Process LinkedIn search URL"
    echo "3) Process single LinkedIn job URL"
    echo "4) Find matching LinkedIn jobs"
    echo "5) Change settings"
    echo "0) Exit"
    echo
    read -p "Enter your choice: " choice
    
    case $choice in
        1)
            run_job_matcher
            ;;
        2)
            process_search_url
            ;;
        3)
            process_job_url
            ;;
        4)
            find_matching_jobs
            ;;
        5)
            change_settings
            ;;
        0)
            echo -e "${GREEN}Thank you for using LinkedIn Job Matcher!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please try again.${NC}"
            sleep 2
            ;;
    esac
done
