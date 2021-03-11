import requests, json, os


class LanguageFetcher:
    
    def __init__(self, url_start):
        self.url_start = url_start
        
    
    def download_language(self, language, download_to):
        r = requests.get(self.url_start+language+".json")
        if "404" in str(r):
            return "404"
        j = r.json()
        
        open(download_to+ "/" + language+".json", "x").close()
        f = open(download_to+ "/" + language+".json", "w+")
        f.write(json.dumps(j))
        f.close()
        return True
    
    def fake_download(self, language, download_to):
        
        j = json.load(open(os.getcwd()+"/languages/"+language+".json"))
        
        open(download_to+ "/" + language+".json", "x").close()
        f = open(download_to+ "/" + language+".json", "w+")
        f.write(json.dumps(j))
        f.close()
        
#LanguageFetcher("https://raw.github.com/Mr-Turtle/TurtleCode/main/languages/").fake_download("language", os.getcwd()+"/langs")
        


