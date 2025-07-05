#!/usr/bin/env python
import os
import json
import time
import random
import requests
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class CloudTikTokBot:
    """Cloud-optimized bot for automatically sending TikTok messages to maintain streaks."""
    
    def __init__(self):
        """Initialize the TikTok bot with configuration and setup."""
        # Load environment variables
        load_dotenv()
        
        # Set up logging
        logger.add("tiktok_bot.log", rotation="10 MB", level="INFO")
        logger.info("Initializing Cloud TikTok Bot")
        
        # Load credentials
        self.username = os.getenv("TIKTOK_USERNAME")
        self.password = os.getenv("TIKTOK_PASSWORD")
        self.friend_username = os.getenv("FRIEND_USERNAME")
        
        if not all([self.username, self.password, self.friend_username]):
            logger.error("Missing required credentials in .env file")
            raise ValueError("Missing required credentials in .env file")
        
        # Load configuration
        self.config_path = Path("config.json")
        self.load_config()
        
        # Initialize content storage
        self.content_dir = Path("content")
        self.content_dir.mkdir(exist_ok=True)
        
        # Initialize browser settings
        self.browser = None
    
    def load_config(self):
        """Load configuration from config.json file."""
        try:
            with open(self.config_path, "r") as f:
                self.config = json.load(f)
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
    
    def setup_browser(self):
        """Set up and configure the Selenium browser optimized for cloud environments."""
        try:
            chrome_options = Options()
            
            # Essential options for cloud environments
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Additional options for stability in cloud environments
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            
            # Mimic real user
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
            
            # For Docker environments
            if os.getenv("RUNNING_IN_CONTAINER", "false").lower() == "true":
                logger.info("Running in container mode")
                service = Service("/usr/bin/chromedriver")
            else:
                service = Service(ChromeDriverManager().install())
                
            self.browser = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Browser setup complete")
        except Exception as e:
            logger.error(f"Error setting up browser: {e}")
            raise
    
    def login(self):
        """Log in to TikTok."""
        try:
            logger.info("Attempting to log in to TikTok")
            self.browser.get("https://www.tiktok.com/login")
            
            # Wait for the login page to load
            WebDriverWait(self.browser, 20).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Email or username']"))
            )
            
            # Switch to username/password login if needed
            use_password_btn = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Use phone / email / username')]"))
            )
            use_password_btn.click()
            
            # Enter username
            username_field = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Email or username']"))
            )
            username_field.send_keys(self.username)
            
            # Enter password
            password_field = self.browser.find_element(By.XPATH, "//input[@placeholder='Password']")
            password_field.send_keys(self.password)
            
            # Click login button
            login_button = self.browser.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for login to complete
            WebDriverWait(self.browser, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-e2e='profile-icon']"))
            )
            
            logger.info("Successfully logged in to TikTok")
            return True
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def navigate_to_messages(self):
        """Navigate to the messages section."""
        try:
            logger.info("Navigating to messages")
            self.browser.get("https://www.tiktok.com/messages")
            
            # Wait for messages to load
            WebDriverWait(self.browser, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-e2e='message-list']"))
            )
            
            logger.info("Successfully navigated to messages")
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to messages: {e}")
            return False
    
    def find_friend_chat(self):
        """Find and open the chat with the specified friend."""
        try:
            logger.info(f"Looking for chat with {self.friend_username}")
            
            # Search for friend
            search_box = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search']"))
            )
            search_box.clear()
            search_box.send_keys(self.friend_username)
            time.sleep(2)  # Wait for search results
            
            # Click on the friend's chat
            friend_element = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '{self.friend_username}')]"))
            )
            friend_element.click()
            
            # Wait for chat to open
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-e2e='chat-input']"))
            )
            
            logger.info(f"Successfully opened chat with {self.friend_username}")
            return True
        except Exception as e:
            logger.error(f"Failed to find friend chat: {e}")
            return False
    
    def find_trending_videos(self, topic):
        """Find trending TikTok videos based on a topic."""
        try:
            logger.info(f"Searching for trending videos on topic: {topic}")
            search_terms = self.config["search_terms"].get(topic, [topic])
            search_term = random.choice(search_terms)
            
            # Navigate to search results
            self.browser.get(f"https://www.tiktok.com/search/video?q={search_term}")
            
            # Wait for videos to load
            WebDriverWait(self.browser, 15).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@data-e2e='search_video-item']"))
            )
            
            # Get video links
            video_elements = self.browser.find_elements(By.XPATH, "//div[@data-e2e='search_video-item']//a")
            video_links = [elem.get_attribute("href") for elem in video_elements if elem.get_attribute("href")]
            
            if not video_links:
                logger.warning(f"No videos found for topic: {topic}")
                return []
            
            logger.info(f"Found {len(video_links)} videos for topic: {topic}")
            return video_links[:5]  # Return top 5 videos
        except Exception as e:
            logger.error(f"Error finding trending videos: {e}")
            return []
    
    def download_image_for_category(self, category):
        """Download an image for the given category using Unsplash API."""
        try:
            # Create directory if it doesn't exist
            image_dir = Path("content/images") / category
            image_dir.mkdir(parents=True, exist_ok=True)
            
            # Use Unsplash API to get a relevant image
            search_term = category.replace("_", " ")
            url = f"https://source.unsplash.com/random/800x600/?{search_term}"
            
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                file_path = image_dir / f"{category}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                with open(file_path, "wb") as f:
                    f.write(response.content)
                logger.info(f"Downloaded image to {file_path}")
                return str(file_path)
            else:
                logger.error(f"Failed to download image: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            return None
    
    def select_random_image(self):
        """Select a random image category and download a fresh image."""
        try:
            # Choose a random image category
            image_category = random.choice(self.config["content_preferences"]["image_folders"])
            logger.info(f"Selected image category: {image_category}")
            
            # Download a fresh image
            image_path = self.download_image_for_category(image_category)
            
            if not image_path:
                logger.warning(f"Failed to download image for {image_category}")
                return None
            
            logger.info(f"Selected image: {image_path}")
            return image_path
        except Exception as e:
            logger.error(f"Error selecting random image: {e}")
            return None
    
    def generate_message(self):
        """Generate a random message from templates."""
        try:
            templates = self.config["content_preferences"]["message_templates"]
            message = random.choice(templates)
            logger.info(f"Generated message: {message}")
            return message
        except Exception as e:
            logger.error(f"Error generating message: {e}")
            return "Keeping our streak alive! Check out these TikToks!"
    
    def send_message(self, message):
        """Send a text message in the current chat."""
        try:
            # Find the message input field
            message_input = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-e2e='chat-input']"))
            )
            message_input.click()
            
            # Type the message
            message_input.send_keys(message)
            time.sleep(1)
            
            # Send the message
            message_input.send_keys(Keys.ENTER)
            logger.info("Message sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def send_image(self, image_path):
        """Send an image in the current chat."""
        try:
            # Find the attachment button
            attachment_button = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-e2e='chat-file-selector']"))
            )
            attachment_button.click()
            
            # Wait for file input to be available
            file_input = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            
            # Send the file path to the input
            file_input.send_keys(str(Path(image_path).absolute()))
            
            # Wait for image to upload and click send
            send_button = WebDriverWait(self.browser, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-e2e='chat-send']"))
            )
            send_button.click()
            
            logger.info(f"Image sent successfully: {image_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to send image: {e}")
            return False
    
    def share_tiktok_video(self, video_url):
        """Share a TikTok video in the current chat."""
        try:
            # Navigate to the video
            self.browser.get(video_url)
            
            # Wait for video to load
            WebDriverWait(self.browser, 15).until(
                EC.presence_of_element_located((By.XPATH, "//button[@data-e2e='share-icon']"))
            )
            
            # Click share button
            share_button = self.browser.find_element(By.XPATH, "//button[@data-e2e='share-icon']")
            share_button.click()
            
            # Wait for share options to appear
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-e2e='share-panel']"))
            )
            
            # Click on "Send to Friends"
            send_to_friends = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Send to Friends')]"))
            )
            send_to_friends.click()
            
            # Search for friend
            search_box = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search']"))
            )
            search_box.clear()
            search_box.send_keys(self.friend_username)
            time.sleep(2)  # Wait for search results
            
            # Select friend
            friend_checkbox = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{self.friend_username}')]/ancestor::div[contains(@class, 'checkbox')]"))
            )
            friend_checkbox.click()
            
            # Click send button
            send_button = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send')]"))
            )
            send_button.click()
            
            logger.info(f"TikTok video shared successfully: {video_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to share TikTok video: {e}")
            return False
    
    def run_task(self):
        """Run the task of sending streak messages."""
        try:
            logger.info("Starting streak message task")
            
            # Set up browser
            self.setup_browser()
            
            # Login to TikTok
            if not self.login():
                logger.error("Failed to log in, aborting task")
                self.cleanup()
                return False
            
            # Navigate to messages
            if not self.navigate_to_messages():
                logger.error("Failed to navigate to messages, aborting task")
                self.cleanup()
                return False
            
            # Find friend's chat
            if not self.find_friend_chat():
                logger.error("Failed to find friend's chat, aborting task")
                self.cleanup()
                return False
            
            # Send greeting message
            message = self.generate_message()
            if not self.send_message(message):
                logger.warning("Failed to send greeting message, continuing with other content")
            
            # Send image
            image_path = self.select_random_image()
            if image_path and not self.send_image(image_path):
                logger.warning("Failed to send image, continuing with videos")
            
            # Select random topics for videos
            video_topics = random.sample(self.config["content_preferences"]["video_topics"], 2)
            
            # Share TikTok videos
            videos_shared = 0
            for topic in video_topics:
                video_links = self.find_trending_videos(topic)
                if video_links:
                    video_url = random.choice(video_links)
                    if self.share_tiktok_video(video_url):
                        videos_shared += 1
                    time.sleep(5)  # Wait between sharing videos
            
            logger.info(f"Task completed: {videos_shared} videos shared")
            self.cleanup()
            return True
        except Exception as e:
            logger.error(f"Error in task: {e}")
            self.cleanup()
            return False
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if self.browser:
                self.browser.quit()
                logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


if __name__ == "__main__":
    try:
        bot = CloudTikTokBot()
        bot.run_task()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Critical error: {e}")
