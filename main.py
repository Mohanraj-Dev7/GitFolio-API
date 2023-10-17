import requests
from bs4 import BeautifulSoup
from flask import Flask,request,jsonify
from flask_cors import CORS

'''
Web scrapping modules ---> requests,bs4
API                   ---> flask,Json

Reach out the API through this link;
                gitfolio.pythonanywhere.com
'''
#codeScrapper is method to scrape a content of whole github repository page 
def codeScrapper(profileName):
        URL=f"https://github.com/{profileName}?tab=repositories"
        page=requests.get(URL)
        soup=BeautifulSoup(page.content,"html.parser")
        #find particular set of content of that repository page like "list of reopos"
        response=soup.find("div",id="user-repositories-list")
        return response

def repoScrapper(response):
        repoJson=[]
        repoList=response.find_all("div",class_="col-10 col-lg-9 d-inline-block")
        #repoList contains the list of repository containers(div) 
        #print(repoList)
        for i in repoList:
                #from dict(python) create single "key":"value" pair based objects
                repoJsonElement=dict().fromkeys(["repoName","repoLink","desc","techStack","stars","forks","watching"])

                repo=str(i.find("a",itemprop="name codeRepository")).strip()
                desc=str(i.find("p",itemprop="description"))
                
                repoName=repo[repo.index(">")+1:].strip().replace("</a>",'')
                repoLink="https://github.com"+repo[repo.index("href=")+6:repo.index(" itemprop=")-1]
                #Assign repository name,link and so on.. into python dict object
                repoJsonElement["repoName"]=repoName
                repoJsonElement["repoLink"]=repoLink

                if('itemprop="description"' in desc):
                        desc=desc[desc.index('itemprop="description">')+24:desc.index("</p>")].strip()
                        repoJsonElement["desc"]=desc


                page=requests.get(repoLink)
                soup=BeautifulSoup(page.content,"html.parser")
                response=soup.find_all("div",class_="BorderGrid-row")

                #print(repoName,response,len(response))
                #fetch some other contents related to particular repository
                if(len(response)!=0):
                        statusResponse=(response[0]).find_all('strong')
                        for i in range(len(statusResponse)):
                                statusResponse[i]=int((str(statusResponse[i]).replace('/','')).replace('<strong>',''))
                        stars,forks,watching=map(str,statusResponse)
                        repoJsonElement["stars"]=stars
                        repoJsonElement["forks"]=forks
                        repoJsonElement["watching"]=watching

                        #Only if the repository has some more feilds like technologies used...
                        if(len(response)==5):
                                techStackResponse=((response[-1]).find('ul',class_="list-style-none").find_all('span',class_="color-fg-default text-bold mr-1"))
                                techStack=[]
                                for i in(techStackResponse):
                                        i=str(i)
                                        techStack.append(i[i.index('>')+1:-7])
                                repoJsonElement["techStack"]=sorted(techStack)

                repoJson.append(repoJsonElement)
                #convert the python(dict) content into json format as API response
        return(json.dumps({"projects":repoJson}))

#Using flash application to create API 
app=Flask(__name__)
CORS(app)

#default page loaded like (index page)
@app.route('/')
def index():
        return 'This is automation based api to fetch all repository related contents form required github profile through API call.<br>Use the link to fetch git profile contents; {this website}/git/?profile="[Github userName]"'

#fetch github profile based repository content
@app.route('/git/')
def gitProfileContent():
        profileName=request.args.get('profile')[1:-1]
        try:
                response=codeScrapper(profileName)
                #print(response)
                if response!=None:
                        return repoScrapper(response)
                else:
                        raise Exception
        except Exception as e:
                return "ProfileName not found , kindly check your profileName "

if __name__=='__main__':
        app.run()
