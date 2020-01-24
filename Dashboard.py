#DashBoard J Term Project

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as soup
import time
import mysql.connector

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

	def facebook(self):

		self.browser.get('https://www.facebook.com/officialrhinowallet/?modal=admin_todo_tour')

		time.sleep(3)

		fb_likes = self.browser.find_elements_by_xpath('//div[@class="_4bl9"]')
		fb_like = ""

		for i in range(0, len(fb_likes)):
			print(str(fb_likes[i].text))
			if('like' in str(fb_likes[i].text)):
				fb_like = fb_likes[i].text
				fb_like = fb_like[:3]
				fb_like = fb_like.replace(" ","")

		return fb_like

class DataManagement():
#The purpose of this class is to build the visual representation of the data
	def GetDatabase():
		mydb = mysql.connector.connect(
			host="localhost",
			user="root",
			passwd="biltong14"
		)

		mycursor = mydb.cursor()
		mycursor.execute('use Rhino Wallet Dashboard')
		mycursor.execute('select photo from liked_photos;')
		sql_list = []

		return sql_list

	def InsertDatabase(self, instagram_return, amazonseller_return, mailchimp_return facebook_return):
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

		follow = instagram_return['Follower Count']
		follow = follow.replace(',','')
		follow = float(follow)

		following = instagram_return['Following Count']
		following = following.replace(',','')
		following = float(following)

		posts = instagram_return['Posts']
		posts = posts.replace(',','')
		posts = float(posts)

		subs = mailchimp_return['Email Subscriptions']
		subs = subs.replace(',','')
		subs = float(subs)

		mycursor.execute('INSERT INTO data (monthly_sales,weekly_sales,follower_count,following_count,posts,email_subs) VALUES \
			("{}","{}","{}","{}","{}","{}");'.format(month, week, follow, following, posts, subs))
		for x in mycursor:
		  print(x)
		mydb.commit()

	def DisplayGraphs(instagram_return, amazonseller_return, mailchimp_return):
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
        df.plot(x ='Monthly Sales', y='Weekly Sales', kind = 'bar')

    def makeMap(self):
    	#This function is used to clean data pulled from Amazon seller so that it
    	#can be imported into a custom Google Map and display the areas where
    	#most Rhino Wallets were sold.
    	df = pd.read_csv('2019.csv', encoding = "ISO-8859-1")
    	states = df['ship-state']
		clean_list = []
		state_abbr = {
		'AL':'Alabama',
		'AK':'Alaska',
		'AZ':'Arizona',
		'AR':'Arkansas',
		'CA':'California',
		'CO':'Colorado',
		'CT':'Connecticut',
		'DE':'Delaware',
		'FL':'Florida',
		'GA':'Georgia',
		'HI':'Hawaii',
		'ID':'Idaho',
		'IL':'Illinois',
		'IN':'Indiana',
		'IA':'Iowa',
		'KS':'Kansas',
		'KY':'Kentucky',
		'LA':'Louisiana',
		'ME':'Maine',
		'MD':'Maryland',
		'MA':'Massachusetts',
		'MI':'Michigan',
		'MN':'Minnesota',
		'MS':'Mississippi',
		'MO':'Missouri',
		'MT':'Montana',
		'NE':'Nebraska',
		'NV':'Nevada',
		'NH':'New Hampshire',
		'NJ':'New Jersey',
		'NM':'New Mexico',
		'NY':'New York',
		'NC':'North Carolina',
		'ND':'North Dakota',
		'OH':'Ohio',
		'OK':'Oklahoma',
		'OR':'Oregon',
		'PA':'Pennsylvania',
		'RI':'Rhode Island',
		'SC':'South Carolina',
		'SD':'South Dakota',
		'TN':'Tennessee',
		'TX':'Texas',
		'UT':'Utah',
		'VT':'Vermont',
		'VA':'Virginia',
		'WA':'Washington',
		'WV':'West Virginia',
		'WI':'Wisconsin',
		'WY':'Wyoming'
		}
		state_count = {
		'Alabama':0,
		'Alaska':0,
		'Arizona':0,
		'Arkansas':0,
		'California':0,
		'Colorado':0,
		'Connecticut':0,
		'Delaware':0,
		'Florida':0,
		'Georgia':0,
		'Hawaii':0,
		'Idaho':0,
		'Illinois':0,
		'Indiana':0,
		'Iowa':0,
		'Kansas':0,
		'Kentucky':0,
		'Louisiana':0,
		'Maine':0,
		'Maryland':0,
		'Massachusetts':0,
		'Michigan':0,
		'Minnesota':0,
		'Mississippi':0,
		'Missouri':0,
		'Montana':0,
		'Nebraska':0,
		'Nevada':0,
		'New Hampshire':0,
		'New Jersey':0,
		'New Mexico':0,
		'New York':0,
		'North Carolina':0,
		'North Dakota':0,
		'Ohio':0,
		'Oklahoma':0,
		'Oregon':0,
		'Pennsylvania':0,
		'Rhode Island':0,
		'South Carolina':0,
		'South Dakota':0,
		'Tennessee':0,
		'Texas':0,
		'Utah':0,
		'Vermont':0,
		'Virginia':0,
		'Washington':0,
		'West Virginia':0,
		'Wisconsin':0,
		'Wyoming':0
		}
		#clean
		for state in states:
		    for key, val in state_abbr.items():
		        if(state.lower() == key.lower()):
		            clean_list.append(val)
		            print(state,'=',val)
		            break
		#count
		for state in clean_list:
		    for check in state_count:
		        if(state.lower() == check.lower()):
		            state_count[check] = state_count[check] + 1

		return sorted(state_count.items(), key=lambda x: x[1], reverse=True)

class main():
#This is the main class that runs.
	bot = ScrapeBot()
	dash = DataManagement()

	bot.facebook()

	instagram_return = bot.Instagram()
	amazonseller_return = bot.AmazonSeller()
	mailchimp_return = bot.MailChimp()
	facebook_return = bot.facebook()

	dash.InsertDatabase(instagram_return, amazonseller_return, mailchimp_return, facebook_return)
	dash.makeMap()
