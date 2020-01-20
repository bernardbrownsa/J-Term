#DashBoard J Term Project

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as soup
import time
import mysql.connector
import pandas as pd

class ScrapeBot():
#The purpose of ScrapeBot is to collect the data from each source

    def __init__(self):
        self.browserProfile = webdriver.ChromeOptions()
        chrome_options = Options()

        self.browserProfile.add_argument("--user-data-dir=C:/Users/bbrown/AppData/Local/Google/Chrome/User Data")
        #self.browserProfile.add_argument("user-data-dir=C:/Users/bbrown/AppData/Local/Google/Chrome/User Data") #Path to your chrome profile

        self.browserProfile.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        self.browser = webdriver.Chrome('chromedriver.exe', options=self.browserProfile)
        self.browser.set_window_size(1000, 900)

    def Instagram(self):
        self.browser.get('https://instagram.com/rhinowallet/')
        time.sleep(2) #This sleep function insures all elements of the page are loaded before scraping data.
        html = self.browser.page_source
        page_soup = soup(html, features="lxml")

        profile_data_instagram = page_soup.findAll("span",{"class":"g47SY"})

        #follower count
        follower_count = profile_data_instagram[1]
        follower_count = str(follower_count.string)

        #following count
        following_count = profile_data_instagram[2]
        following_count = str(following_count.string)

        #posts
        posts = profile_data_instagram[0]
        posts = str(posts.string)

        #This wraps up all of the data into a dictionary and then returns it.
        instagram_return = {'Follower Count':follower_count, 'Following Count':following_count,'Posts':posts}
        print(instagram_return)
        return instagram_return


    def AmazonSeller(self):
        self.browser.get('https://sellercentral.amazon.com/home')
        time.sleep(2) #This sleep function insures all elements of the page are loaded before scraping data.
        html = self.browser.page_source
        page_soup = soup(html, features="lxml")

        sales = page_soup.findAll("tr")
        #monthly Salesles
        monthly_sales = sales[5].text
        monthly_sales = monthly_sales.replace('\n','')
        monthly_sales_clean = ""
        keep = False
        for l in monthly_sales:
            if(l == '$'):
                keep = True
            if(keep == True):
                monthly_sales_clean = monthly_sales_clean+l
        #weekly sales
        weekly_sales = sales[3].text
        weekly_sales = weekly_sales.replace('\n','')
        weekly_sales_clean = ""
        keep = False
        for l in weekly_sales:
            if(l == '$'):
                keep = True
            if(keep == True):
                weekly_sales_clean = weekly_sales_clean+l

        #This wraps up all of the data into a dictionary and then returns it.
        amazonseller_return = {"Monthly Sales":monthly_sales_clean,'Weekly Sales':weekly_sales_clean}
        print(amazonseller_return)
        return amazonseller_return

    def MailChimp(self):

        self.browser.get('https://us4.admin.mailchimp.com/lists/members?id=335485#p:1-s:25-sa:last_update_time-so:false')
        time.sleep(2) #This sleep function insures all elements of the page are loaded before scraping data.
        html = self.browser.page_source
        page_soup = soup(html, features="lxml")

        #number of email subscriptions
        atags = page_soup.findAll('a')
        email_subs = 'Not Found'
        for a in atags:
            if('Your contacts' in str(a)):
                email_subs = a.text

        mailchimp_return = {"Email Subscriptions":email_subs}
        print(mailchimp_return)
        return mailchimp_return


class DataManagement():
#The purpose of this class is to build the visual representation of the data

    def GetDatabase(self):
        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="biltong14"
        )

        mycursor = mydb.cursor()

        mycursor.execute('use Dashboard')
        mycursor.execute('select * from data;')

        data = []
        
        for (id, monthly_sales, weekly_sales, follower_count, following_count, posts, email_subs) in mycursor:
            data.append((id, monthly_sales, weekly_sales, follower_count, following_count, posts, email_subs))

        return data

    def InsertDatabase(self, instagram_return, amazonseller_return, mailchimp_return):
        mydb = mysql.connector.connect(
          host="localhost",
          user="root",
          passwd="biltong14"
        )

        mycursor = mydb.cursor()
        mycursor.execute('use Dashboard')

        month = (amazonseller_return['Monthly Sales'])
        month = month.replace('$','')
        month = month.replace(',','')
        month = float(month)
        week = (amazonseller_return['Weekly Sales'])
        week = week.replace('$','')
        week = week.replace(',','')
        week = float(week)

        # mycursor.execute('INSERT INTO data (monthly_sales,weekly_sales) VALUES \
        # 	("{}","{}");'.format(month, week))

        follow = instagram_return['Follower Count']
        follow = follow.replace(',','')
        follow = float(follow)
        following = instagram_return['Following Count']
        following = following.replace(',','')
        following = float(following)
        posts = instagram_return['Posts']
        posts = posts.replace(',','')
        posts = float(posts)

        # mycursor.execute('INSERT INTO data (follower_count,following_count,posts) VALUES \
        # 	("{}","{}","{}");'.format(follow, following, posts))

        subs = mailchimp_return['Email Subscriptions']
        subs = subs.replace(',','')
        subs = float(subs)

        # mycursor.execute('INSERT INTO data (Subscriptions) VALUES \
        # 	("{}");'.format(subs))

        mycursor.execute('INSERT INTO data (monthly_sales,weekly_sales,follower_count,following_count,posts,email_subs) VALUES \
            ("{}","{}","{}","{}","{}","{}");'.format(month, week, follow, following, posts, subs))

        for x in mycursor:
          print(x)
        mydb.commit()

    def DisplayGraphs(self, data):
        #Line graph of Follower Count -> Following Count -> Posts (compared by date)
        #Build a pandas df first

        id = []
        ms = []
        ws = []
        f = []
        fg = []
        pt = []
        el = []
        
        for row in data:
            id.append(row[0])
            ms.append(row[1])
            ws.append(row[2])
            f.append(row[3])
            fg.append(row[4])
            pt.append(row[5])
            el.append(row[6])
            
        d = {'ID': [id], 'Monthly Sales': [ms], 'Weekly Sales':[ws],'Instagram Follower Count':[f], 'Instagram Following Count':[fg],'Instagram Post Count':[pt],'Email List Subs':[el]}
        df = pd.DataFrame(data=d)
        print(df)
        df.plot(x ='Monthly Sales', x='Weekly Sales', y="ID", kind = 'bar')
	df.plot(x ='Instagram Follower Count', x='Instagram Following Count', y="ID", kind = 'bar')
	df.plot(x ='Email List Subs', y='ID', kind = 'bar')
        

class main():
#This is the main class that runs.
    bot = ScrapeBot()
    dash = DataManagement()

    instagram_return = bot.Instagram()
    amazonseller_return = bot.AmazonSeller()
    mailchimp_return = bot.MailChimp()

    dash.InsertDatabase(instagram_return, amazonseller_return, mailchimp_return)
    data = dash.GetDatabase()
    dash.DisplayGraphs(data)
    
    
