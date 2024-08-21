import requests
from bs4 import BeautifulSoup
from flask import Flask,request,jsonify
from flask_cors import CORS

'''
Web scrapping modules ---> requests,bs4
API                   ---> flask,Json

Reach out the API through this link;
        https://gitfolio-api.onrender.com
'''

#Using flash application to create API 
app=Flask(__name__)
CORS(app)

#urlToSoup is method to convert the content of url into parsable object
def urlToSoup(URL):
        page=requests.get(URL)
        soup=BeautifulSoup(page.content,"html.parser")
        return soup

#codeScrapper is method to scrape a content of whole github repositories in main page 
def codeScrapper(profileName):
        URL=f"https://github.com/{profileName}"
        soup=urlToSoup(URL)
        #Find particular set of content of that main page like "list of reopos"
        response=soup.find_all("div",class_="pinned-item-list-item-content")
        return response

def repoScrapper(response,contents):
        repoJson=[]
        for i in response:
                #From dict(python) create single "key":"value" pair based objects
                repoJsonElement=dict()#.fromkeys(["repoName","repoLink","repoDesc","techStack","stars","forks","watching"])

                #repo contains the list of repository containers 
                repo=i.find("a",class_="Link")
                repoName=repo.find("span",class_="repo").string
                repoLink="https://github.com"+repo.attrs["href"]

                repoDesc=i.find("p",class_="pinned-item-desc").string
                repoDesc=(repoDesc.replace('\n','')).strip()

                repoJsonElement["repoName"]=repoName
                repoJsonElement["repoLink"]=repoLink
                repoJsonElement["repoDesc"]=repoDesc

                if (contents == "all"):
                        #Fetch some other contents related to particular repository
                        soup=urlToSoup(repoLink)
                        additionalResponse=soup.find_all("div",class_="BorderGrid-row")
                        
                        statusResponse=(additionalResponse[0]).find_all('strong')
                        
                        repoJsonElement["stars"]=statusResponse[0].string
                        repoJsonElement["watching"]=statusResponse[1].string
                        repoJsonElement["forks"]=statusResponse[2].string

                        #Only if the repository has some more feilds like technologies used...
                        if(len(additionalResponse)==5):
                                techStackResponse=((additionalResponse[-1]).find('ul',class_="list-style-none").find_all('span',class_="color-fg-default text-bold mr-1"))
                                
                                techStack=[]
                                for i in(techStackResponse):
                                        techStack.append(i.string)
                                repoJsonElement["techStack"]=sorted(techStack)

                repoJson.append(repoJsonElement)
        #convert the python(dict) content into json format as API response
        return(jsonify({"projects":repoJson}))

#Default page loaded like (index page)
@app.route('/')
def index():
        return '''This is web Scrapping based api to fetch all repository related contents
                  from required github profile through API call.<br>
                  Use the link to fetch git profile contents;
                  <h3>For Basic contents</h3>
                  {this website}/git/repos/?profile="[Github userName]"&contents="base"<br>
                  <h3>For complete contents</h3>
                  {this website}/git/repos/?profile="[Github userName]"&contents="all"
               '''

#Fetch github profile based repository content
@app.route('/git/repos/')
def gitProfileContent():
        profileName=request.args.get('profile')[1:-1]
        responseContent=request.args.get('contents')[1:-1]

        try:
                response=codeScrapper(profileName)
                if response!=None:
                        return repoScrapper(response,responseContent)
                else:
                        raise Exception
        except Exception as e:
                return "<h3>ProfileName not found , kindly check your profileName </h3>"
        
#This only for local server not need to inculde in production env.
#if __name__=='__main__':
#        app.run()
