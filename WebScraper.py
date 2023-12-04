#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import praw
import pandas as pd
import time
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox
from plyer import notification

# CIS 542 Social Media Scraper (Reddit)
# Gregory Yao
# This project was made as a proof of concept of being able to scrape information from social media.
# Reddit API was obtained through reddit.com/prefs/apps. A Reddit account is necessary to run this program.
# - PRAW library was used to traverse the Reddit instance
# - threading library used to ensure having only one instance runs at a time
# - tkinter library used for GUI design
# - plyer used to send notifications to the user's desktop

dialogCreated = False # Flag to prevent multiple "Configuration" dialogs
terminateProcess = False  # Flag to signal termination
monitoredThread = None  # Global variable to store the monitoring thread

# Configuration Dialog prepares the Reddit instance that will be monitored by requesting the necessary information from Reddit's API
# - Required information: clientID, clientSecret, username, password, application name, and targetedUser
class ConfigurationDialog(tk.Toplevel):
    # Setting up the dialog box
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configuration")
        self.geometry("400x450")
        self.result = None
        self.generateBody()

    # Creating the body of the Configuration Dialog
    def generateBody(self):
        tk.Label(self, text = "Reddit Client ID:").pack(pady = 5)
        self.clientID = tk.Entry(self)
        self.clientID.pack(pady = 5)

        tk.Label(self, text = "Reddit Client Secret:").pack(pady = 5)
        self.clientSecret = tk.Entry(self)
        self.clientSecret.pack(pady = 5)

        tk.Label(self, text = "Reddit Username:").pack(pady = 5)
        self.username = tk.Entry(self)
        self.username.pack(pady = 5)

        tk.Label(self, text = "Reddit Password:").pack(pady = 5)
        self.password = tk.Entry(self, show='*')
        self.password.pack(pady = 5)

        tk.Label(self, text = "Application Name:").pack(pady = 5)
        self.appName = tk.Entry(self)
        self.appName.pack(pady = 5)

        tk.Label(self, text = "Target Reddit User:").pack(pady = 5)
        self.targetUser = tk.Entry(self)
        self.targetUser.pack(pady = 5)

        tk.Button(self, text = "Start Monitoring", command = self.startMonitoring).pack(pady = 10)
        tk.Button(self, text = "Cancel", command = self.destroy).pack(pady = 10)
        
    def startMonitoring(self):
        # Get user input
        user_input = (self.clientID.get(), self.clientSecret.get(),
                      self.username.get(), self.password.get(),
                      self.appName.get(), self.targetUser.get())
        
        # Ensures that all the fields are populated before storing entries
        if any(value == "" for value in user_input):
            messagebox.showerror("Error", "Please fill in all fields.")
        else:
            self.result = user_input
            self.destroy()

def monitorUserActivity(clientID, clientSecret, username, password, applicationName, targetUser, checkInterval = 60):
    global terminateProcess

    redditInstance = getRedditInstance(clientID, clientSecret, username, password, applicationName)
    seenPosts = set()
    seenComments = set()
    listOfPosts = []
    listOfComments = []

    while not terminateProcess:
        try:
            # Fetch the user's submissions and comments
            posts = redditInstance.redditor(targetUser).submissions.new(limit = 3)
            comments = redditInstance.redditor(targetUser).comments.new(limit = 3)
            
            for post in posts:
                # Check if the post is 'new'. In this case, a post is new if this program didn't notify the user about it yet.
                if post.id not in seenPosts:
                    seenPosts.add(post.id)

                    # Notify the user about the new post
                    postTitle = f"New post from {post.author}"
                    postText = f"Title: {post.title}\nURL: {post.url}"
                    notification.notify(title = postTitle, message = postText)

                    # Appends post to the list of posts to be downloaded
                    listOfPosts.append({'Author': post.author,
                                       'Title': post.title,
                                       'UTC': post.created_utc,
                                       'URL': post.url})

            for comment in comments:
                # Check if the comment is 'new'. In this case, a comment is new if this program didn't notify the user about it yet.
                if comment.id not in seenComments:
                    seenComments.add(comment.id)

                    # Notify the user about the new comment
                    commentTitle = f"New comment from {comment.author}"
                    commentText = f"Comment: {comment.link_title}\nBody: {comment.body}"
                    notification.notify(title = commentTitle, message = commentText)

                    # Appends post to the list of comments to be downloaded
                    listOfComments.append({'Author': comment.author,
                                       'Title': comment.link_title,
                                       'UTC': comment.created_utc,
                                       'Comment': comment.body})

            time.sleep(checkInterval)

        except Exception as e:
            print(f"Error: {e}")
            # Wait a set interval before retrying to prevent spamming the server
            time.sleep(checkInterval)
    
    # Download the list of posts and comments to a CSV file (if the lists are not empty)
    if listOfPosts:
        if len(listOfPosts) == 0:
            print("No posts recorded during the monitoring session")
        posts_df = pd.DataFrame(listOfPosts)
        posts_df.to_csv('List_of_Posts.csv', index = False)

    if listOfComments:
        if len(listOfComments) == 0:
            print("No comments recorded during the monitoring session")
        comments_df = pd.DataFrame(listOfComments)
        comments_df.to_csv('List_of_Comments.csv', index = False)        
            
    print("Monitoring thread terminated.")

# Helper function to get an instance of Reddit through PRAW
def getRedditInstance(clientID, clientSecret, username, password, applicationName):
    return praw.Reddit(client_id = clientID, client_secret = clientSecret,
                       username = username, password = password, user_agent = applicationName)

# Terminates the monitor and thread that was associated with that session
def terminateMonitor():
    global terminateProcess, monitoredThread
    
    terminateProcess = True
    if monitoredThread and monitoredThread.is_alive():
        monitoredThread.join()

def startMonitoringThread(parent):
    global monitoredThread, dialogCreated
    
    if dialogCreated: # Prevents multiple configurations from running at once.
        messagebox.showinfo("Info","A Configuration Dialog is currently in use.\nPlease close out of the dialog to create a new Configuration Dialog.")
        return
    else: # If no configuration is active, create a new ConfigurationDialog
        dialogCreated = True
        inputDialog = ConfigurationDialog(parent)
        parent.wait_window(inputDialog)
        dialogCreated = False
        
    if inputDialog.result: # If the user provided enough data in the ConfigurationDialog
        global terminateProcess

        terminateProcess = False
        monitoredThread = threading.Thread(target = monitorUserActivity, args = inputDialog.result) 
        monitoredThread.start()

def redditPostMonitorExe():
    # Create the main window
    root = tk.Tk()
    root.title("Monitoring GUI")
    root.geometry("250x100")

    # Button to start monitoring
    start_button = tk.Button(root, text = "Begin", command = lambda: startMonitoringThread(root))
    start_button.pack(pady = 10)

    # Button to stop monitoring
    stop_button = tk.Button(root, text="Stop Monitoring", command = terminateMonitor)
    stop_button.pack(pady = 10)

    # Start the main loop for the GUI
    root.mainloop()
    
if __name__ == "__main__":
    redditPostMonitorExe()


# In[ ]:





# In[ ]:




