import requests
from bs4 import BeautifulSoup
import csv

#get top 100 subreddits
response = requests.get("http://redditmetrics.com/top", headers={'User-Agent': "Resistance is futile"})
html = response.text
soup = BeautifulSoup(html, "html.parser")
subreddit_list = soup.find('tbody').find_all('a')
subreddits = [subreddit.text for subreddit in subreddit_list]


postStorage = []
commentStorage = []
for subreddit in subreddits:


    response = requests.get("https://www.reddit.com"+subreddit, headers={'User-Agent': "Resistance is futile"})
    html = response.text

    soup = BeautifulSoup(html, "html.parser")

    for post in soup.find_all('div',{"class": "scrollerItem"}):
        #get comments
        commentLink = ''
        for h in post.find_all('a'):
            if 'href' in h.attrs and 'data-click-id' in h.attrs:
                if h.attrs['href'].startswith('/r/') and h.attrs['data-click-id']=='comments':
                    if h.text.split(' ')[0] != 'comment':
                        number_comments = h.text.split(' ')[0]
                        if number_comments[-1]=='k':
                            number_comments = float(number_comments[:-1]) *1000
                        else:
                            number_comments = float(number_comments)
                    else:
                        number_comments = 0
                    commentLink = h.attrs['href']
            if 'href' in h.attrs:
                if h.attrs['href'].startswith('/user/'):
                    author = h.text[2:]


        #get title of post
        for h in post.find_all('h2'):
            if 'class' in h.attrs:
                title = h.text.replace(',','').replace('"',"'")
        #Get number of upvotes
        for h in post.find_all('div'):
            if 'style' in h.attrs:
                if h['style']== "color:#1A1A1B":
                    number_upvotes = h.text.split(' ')[0]
                    if number_upvotes[-1] == 'k':
                        number_upvotes = float(number_upvotes[:-1]) * 1000
                    else:
                        number_upvotes = float(number_upvotes)
        postStorage.append([title[0:99],subreddit[3:26],author[0:23],int(number_upvotes),int(number_comments)])
        response = requests.get("https://www.reddit.com"+commentLink, headers={'User-Agent': "Resistance is futile"})
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        OP = author[0:23]
        Article = title[0:99]
        topTenComments = []
        for comment in soup.find_all('div',{"class":"Comment"})[0:9]:
            topTenComments.append(comment.find_all('p'))
        for comment in topTenComments:
            commentStorage.append([OP,Article,comment[0:99]])







with open("Posts.csv", "a+") as f:
    writer = csv.writer(f)
    writer.writerows(postStorage)
with open("Comments.csv", "a+") as f:
    writer = csv.writer(f)
    writer.writerows(commentStorage)
