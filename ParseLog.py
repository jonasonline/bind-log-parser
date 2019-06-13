import json, os.path, re, requests
from datetime import datetime

def postToSlack(webhookURL, message):
    req = requests.post(webhookURL, json={"text":message})

dateTimeFormat = '%d-%b-%Y %H:%M:%S.%f'
lastRunTime = ""
currentRunTime = datetime.now()

if os.path.exists('lastrun'):
    with open('lastrun','r') as lastRunFile:
        lastRunTime = datetime.strptime(lastRunFile.read(), dateTimeFormat) 
else:
    lastRunTime = currentRunTime


with open('config.json', 'r') as configFile:
    config = json.load(configFile)
    domainBlackList = config["domainBlackList"]
    with open(config["logFilePath"], 'r') as logFile:
        for line in logFile.readlines():
            lineParts = line.split(" ")
            logTime = datetime.strptime(line[0:24], dateTimeFormat)
            if logTime > lastRunTime:
                pattern = config['domainPattern']
                result = re.search(pattern, line)
                if result:
                    lineComponents = line.split("query: ")
                    base = lineComponents[0].split(" ")
                    domain = base[len(base)-2].replace("(","").replace("):","")
                    ip = base[len(base)-3]
                    if domain.lower() not in domainBlackList:
                        message = f"Lookup for domain: {domain} from {ip} at {logTime.strftime(dateTimeFormat)}"
                        print(message)
                        postToSlack(config["slackWebhookURL"], message)

with open('lastrun','w') as lastRunFile:
        lastRunFile.write(currentRunTime.strftime(dateTimeFormat))