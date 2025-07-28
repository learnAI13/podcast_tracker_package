# Accessing the 1-Click Podcast Guest Tracker Web App

The web app is now running and can be accessed through the following URL:

**Web App URL:** https://work-1-bnbvcbisukylyyhn.prod-runtime.all-hands.dev

## Using the Web App

1. Open the URL in your browser
2. Enter the following information:
   - **Guest Name:** The name of the potential podcast guest
   - **Guest URL:** A social media URL for the guest (Twitter, LinkedIn, etc.)
   - **Host YouTube Channel:** The URL of the host's YouTube channel
3. Click "Analyze Guest" to start the analysis
4. Wait for the analysis to complete (this may take a minute)
5. Review the results, including:
   - Overall score
   - Recommendation
   - Explanation points
   - Guest profile details

## Example Inputs

### Example 1:
- **Guest Name:** Elon Musk
- **Guest URL:** https://twitter.com/elonmusk
- **Host YouTube Channel:** https://youtube.com/@lexfridman

### Example 2:
- **Guest Name:** Tim Ferriss
- **Guest URL:** https://twitter.com/tferriss
- **Host YouTube Channel:** https://youtube.com/@joerogan

## Command Line Alternative

If you prefer to use the command line, you can run:

```bash
./run_analyzer.py "Guest Name" "Guest URL" "Host Channel URL"
```

Or try the example script:

```bash
./run_example.sh
```