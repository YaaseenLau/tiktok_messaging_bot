# TikTok Messaging Bot

A solution for maintaining your TikTok messaging streak with a friend by sending daily messages, images, and TikTok videos.

## ⚠️ Important Disclaimer

This project is for **educational purposes only**. Please be aware that:

1. Using automation with TikTok may violate their Terms of Service
2. Your account could be temporarily or permanently banned
3. Always respect platform policies and use at your own risk

## Features

- Sends messages at a scheduled time
- Shares two TikTok videos on random topics
- Sends an image from configurable categories
- Includes a friendly message from templates

## Setup Options

This repository includes multiple deployment options:

1. **Local Execution**: Run on your PC when it's on
2. **GitHub Actions**: Schedule execution using GitHub's free CI/CD (recommended)
3. **Docker Deployment**: For advanced users with cloud hosting

## GitHub Actions Setup (Recommended)

GitHub Actions allows you to run the bot on a schedule without keeping your PC on.

### Step 1: Fork or Clone the Repository

If you haven't already, fork this repository to your GitHub account.

### Step 2: Set Up GitHub Secrets

1. Go to your repository on GitHub
2. Click on "Settings" tab
3. In the left sidebar, click on "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Add the following secrets:

| Name | Value | Description |
|------|-------|-------------|
| `TIKTOK_USERNAME` | `your_username` | Your TikTok username |
| `TIKTOK_PASSWORD` | `your_password` | Your TikTok password |
| `FRIEND_USERNAME` | `friend_username` | Your friend's TikTok username |

### Step 3: Create GitHub Actions Workflow

Create a new file at `.github/workflows/tiktok-streak.yml`:

```yaml
name: TikTok Streak Bot

on:
  schedule:
    # Run daily at 8:00 AM UTC (adjust as needed)
    - cron: '0 8 * * *'
  
  # Allow manual triggering for testing
  workflow_dispatch:

jobs:
  send-message:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install Chrome
        run: |
          wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
          echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
          sudo apt-get update
          sudo apt-get install -y google-chrome-stable
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Create .env file
        run: |
          echo "TIKTOK_USERNAME=${{ secrets.TIKTOK_USERNAME }}" > .env
          echo "TIKTOK_PASSWORD=${{ secrets.TIKTOK_PASSWORD }}" >> .env
          echo "FRIEND_USERNAME=${{ secrets.FRIEND_USERNAME }}" >> .env
          echo "RUNNING_IN_CONTAINER=true" >> .env
      
      - name: Run TikTok bot
        run: python cloud_tiktok_bot.py
```

### Step 4: Test the Workflow

1. Go to the "Actions" tab in your repository
2. Select the "TikTok Streak Bot" workflow
3. Click "Run workflow" to test it manually

### Step 5: Monitor Execution

- Check the workflow logs to ensure it's working properly
- The bot will now run automatically at the scheduled time

## Customizing Content

Edit the `config.json` file to customize:

- Video topics
- Image categories
- Message templates

## Troubleshooting GitHub Actions

If you encounter issues:

1. **Check workflow logs**:
   - Go to Actions tab → Select the workflow run → View logs

2. **TikTok blocking the login**:
   - Try adjusting the timing (run at different hours)
   - Consider adding more random delays in the code

3. **Workflow not running**:
   - Ensure your repository is not archived
   - Check that you have not disabled Actions in repository settings

4. **Secrets not working**:
   - Verify that secrets are correctly named
   - Make sure there are no extra spaces in the values

## Security Considerations

- GitHub Actions secrets are encrypted and secure
- Never commit your TikTok credentials directly to the repository
- Use a private repository to keep your code and workflow private

## Alternative Approaches

If you're concerned about TikTok's Terms of Service:

1. **Manual reminders**: Set up calendar notifications
2. **TikTok's built-in features**: Check for official scheduling options
3. **Shared calendars**: Coordinate with your friend using shared reminders

## License

This project is for educational purposes only. Use at your own risk.
