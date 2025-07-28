#!/bin/bash
# Example script to run the 1-Click Podcast Guest Tracker

echo "Running 1-Click Podcast Guest Tracker Example"
echo "============================================="
echo ""

# Example 1: Elon Musk on Lex Fridman
echo "Example 1: Elon Musk on Lex Fridman's Podcast"
python run_analyzer.py "Elon Musk" "https://twitter.com/elonmusk" "https://youtube.com/@lexfridman"
echo ""

# Example 2: Tim Ferriss on Joe Rogan
echo "Example 2: Tim Ferriss on Joe Rogan's Podcast"
python run_analyzer.py "Tim Ferriss" "https://twitter.com/tferriss" "https://youtube.com/@joerogan"
echo ""

echo "Examples completed!"
echo "Check the JSON files for detailed results."