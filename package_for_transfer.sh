#!/bin/bash
# Package the 1-Click Podcast Guest Tracker for transfer to another server

echo "Packaging 1-Click Podcast Guest Tracker for transfer..."

# Create a directory for the package
mkdir -p /tmp/podcast-tracker-package

# Copy all Python files
echo "Copying Python files..."
cp *.py /tmp/podcast-tracker-package/

# Copy shell scripts
echo "Copying shell scripts..."
cp *.sh /tmp/podcast-tracker-package/
chmod +x /tmp/podcast-tracker-package/*.sh

# Copy documentation
echo "Copying documentation..."
cp *.md /tmp/podcast-tracker-package/

# Copy templates directory
echo "Copying templates..."
cp -r templates /tmp/podcast-tracker-package/

# Copy .env file (without sensitive information)
echo "Creating sample .env file..."
cat > /tmp/podcast-tracker-package/.env << EOL
# 1-Click Podcast Guest Tracker Configuration

# LLM URLs (adjust based on your setup)
MIXTRAL_URL=http://localhost:8080  # URL for your LLaMA 3.1 70B model
LLAMA_8B_URL=http://localhost:8081  # URL for your LLaMA 3.1 8B model
LLAMA_70B_URL=http://localhost:8080  # URL for your LLaMA 3.1 70B model

# Optional API Keys
YOUTUBE_API_KEY=your_youtube_api_key_here
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
LINKEDIN_CLIENT_ID=your_linkedin_client_id_here

# Analysis Settings
MAX_VIDEOS_TO_ANALYZE=50
CACHE_DURATION_HOURS=24
EOL

# Create a README file
echo "Creating README file..."
cat > /tmp/podcast-tracker-package/README.txt << EOL
1-Click Podcast Guest Tracker
============================

This package contains all the files needed to run the 1-Click Podcast Guest Tracker.

Quick Start:
1. Install dependencies: ./install_deps.sh
2. Configure .env file with your LLaMA 3.1 model URLs
3. Start the system: ./start_system.sh
4. Access the web interface at http://localhost:12000

For detailed instructions, see deployment_guide.md
EOL

# Create the zip file
echo "Creating zip archive..."
cd /tmp
zip -r podcast-tracker-package.zip podcast-tracker-package

# Move the zip file to the workspace
mv /tmp/podcast-tracker-package.zip /workspace/

# Clean up
rm -rf /tmp/podcast-tracker-package

echo "Package created: /workspace/podcast-tracker-package.zip"
echo "You can download this file and transfer it to your server."