# Cloud Deployment Guide for TikTok Streak Bot

This guide explains how to deploy your TikTok streak bot to the cloud so it can run automatically even when your PC is off or you're asleep.

## Option 1: Railway.app (Recommended - Easiest & Free)

Railway.app offers a generous free tier (500 hours/month) which is perfect for this bot.

### Steps:

1. **Create a Railway account**:
   - Sign up at [Railway.app](https://railway.app/) using GitHub

2. **Deploy your bot**:
   - Install Railway CLI: `npm i -g @railway/cli`
   - Login: `railway login`
   - Initialize project: `railway init`
   - Deploy: `railway up`

3. **Set environment variables**:
   - Go to your project in Railway dashboard
   - Add the same variables from your `.env` file

4. **Set up a schedule**:
   - In Railway dashboard, go to your deployment
   - Add a cron job: `0 8 * * *` (for 8:00 AM daily)
   - Command: `python cloud_tiktok_bot.py`

## Option 2: Oracle Cloud Free Tier (Completely Free Forever)

Oracle Cloud offers an "Always Free" tier with 2 VMs that never expire.

### Steps:

1. **Create an Oracle Cloud account**:
   - Sign up at [Oracle Cloud](https://www.oracle.com/cloud/free/)
   - Complete verification process

2. **Create a VM instance**:
   - Choose "Always Free" eligible VM (ARM-based)
   - Use Ubuntu as the OS

3. **Set up the environment**:
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker
   sudo apt install docker.io docker-compose -y
   
   # Clone your repository
   git clone <your-repo-url>
   cd TiktokMessageBot
   
   # Create .env file
   nano .env
   # Add your credentials
   
   # Start the container
   sudo docker-compose up -d
   ```

4. **Set up a cron job**:
   ```bash
   crontab -e
   # Add this line to run daily at 8:00 AM
   0 8 * * * cd /path/to/TiktokMessageBot && sudo docker-compose restart
   ```

## Option 3: GitHub Actions (Free for Private Repos)

GitHub Actions can run scheduled workflows for free.

### Steps:

1. **Push your code to GitHub**:
   - Create a private repository
   - Push your code

2. **Create GitHub Secrets**:
   - Go to repository Settings > Secrets
   - Add your TikTok credentials as secrets

3. **Create workflow file**:
   - Create `.github/workflows/tiktok-bot.yml`
   - Configure it to run on a schedule

## Content Topics

The bot is configured to send content on these topics:

1. **Video Topics**:
   - Comedy, cooking, travel, pets, dance
   - Fashion, fitness, life hacks, music, art

2. **Image Categories**:
   - Memes, quotes, nature, food, pets

3. **Message Templates**:
   - Various friendly streak-maintaining messages

You can customize these in the `config.json` file.

## Troubleshooting

If you encounter issues:

1. **Check logs**: All cloud platforms provide logging
2. **TikTok blocking**: If TikTok blocks automated logins, try:
   - Reducing frequency
   - Adding random delays
   - Using a proxy service

3. **Browser issues**: Make sure Chrome is installed correctly in your cloud environment
