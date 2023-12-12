# RedditScraper
CIS542 Class Project

This project uses the following Python libraries and modules
- PRAW       (https://praw.readthedocs.io/en/stable/)
- pandas     (https://pandas.pydata.org/docs/reference/index.html)
- tkinter    (https://tkdocs.com/index.html)
- plyer      (https://plyer.readthedocs.io/en/latest/)
- time       (https://docs.python.org/3/library/time.html)
- threading  (https://docs.python.org/3/library/threading.html

To run this Reddit scraper, you'll need a Reddit account, and a Reddit developer application.
The Reddit dev app can be obtained by going to reddit.com/prefs/apps and creating an application.
- Enter the application's name
- Select 'script'
- Description is optional, however I'd recommend leaving a description.
- Enter the reddit link that is to be scraped in 'about url'\
- 'redirect uri' is not used in script applications, however it is still a manatory field. (http://localhost:8080 can be used here)

After cloning this repository and creating an instance of Reddit's API, launch the .exe found in the /dist/ folder.

- Press the 'Begin' button and fill out the entry boxes with the information from the Reddit dev app.
- Press 'Start Monitoring' to start the scraping process.
- Press 'Stop Monitoring' to stop the scraping process. A list of posts and a list of comments scraped will be seperately converted into .csv files in /RedditScraper/

NOTE: All .ini files should be in the same directory as the .exe. On the off chance that they're not, please return them back to the directory. These .ini files can be found in the directory where the libraries were installed. (\path\to\sitepackages\)
