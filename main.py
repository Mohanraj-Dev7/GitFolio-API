import requests
from bs4 import BeautifulSoup
import json
from flask import Flask
from flask import request

def codeScrapper(profileName):
        URL=f"https://github.com/{profileName}?tab=repositories"
        page=requests.get(URL)
        soup=BeautifulSoup(page.content,"html.parser")
        response=soup.find("div",id="user-repositories-list")
        return response

def repoScrapper(response):
        repoJson=[]
        repoList=response.find_all("div",class_="col-10 col-lg-9 d-inline-block")
        for i in repoList:
                repoJsonElement=dict().fromkeys(["repoName","repoLink","desc","techStack","stars","forks","watching"])
                repo=str(i.find("a",itemprop="name codeRepository")).strip()
                desc=str(i.find("p",itemprop="description"))
                repoName=repo[repo.index(">")+1:].strip().replace("</a>",'')
                repoJsonElement["repoName"]=repoName
                repoLink="https://github.com"+repo[repo.index("href=")+6:repo.index(" itemprop=")-1]
                repoJsonElement["repoLink"]=repoLink

                if('itemprop="description"' in desc):
                        desc=desc[desc.index('itemprop="description">')+24:desc.index("</p>")].strip()
                        repoJsonElement["desc"]=desc


                page=requests.get(repoLink)
                soup=BeautifulSoup(page.content,"html.parser")
                response=soup.find_all("div",class_="BorderGrid-row")

                if(len(response)!=0):

                        statusResponse=(response[0]).find_all('strong')
                        for i in range(len(statusResponse)):
                                statusResponse[i]=int((str(statusResponse[i]).replace('/','')).replace('<strong>',''))
                        stars,forks,watching=map(str,statusResponse)
                        repoJsonElement["stars"]=stars
                        repoJsonElement["forks"]=forks
                        repoJsonElement["watching"]=watching

                        techStackResponse=((response[-1]).find('ul',class_="list-style-none").find_all('span',class_="color-fg-default text-bold mr-1"))
                        techStack=[]
                        for i in(techStackResponse):
                                i=str(i)
                                techStack.append(i[i.index('>')+1:-7])
                        repoJsonElement["techStack"]=sorted(techStack)

                repoJson.append(repoJsonElement)
        return(json.dumps({"projects":repoJson}))

app=Flask(__name__)

@app.route('/')
def index():
        return 'This is automation based api to fetch all repository related contents form required github profile through API call.<br>Use the link to fetch git profile contents; {this website}/git/?profile="[Github userName]"'


@app.route('/git/')
def gitProfileContent():
        profileName=request.args.get('profile')[1:-1]
        try:
                response=codeScrapper(profileName)
                print(response)
                if response!=None:
                        return repoScrapper(response)
                else:
                        raise Exception
        except Exception as e:
                return "ProfileName not found , kindly check your profileName "

