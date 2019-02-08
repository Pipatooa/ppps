import json, os, urllib.request

os.chdir(os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "\\.."))

proxyHandler = urllib.request.ProxyHandler({})
urlOpener = urllib.request.build_opener(proxyHandler)
response = urlOpener.open("https://raw.githubusercontent.com/Pipatooa/ppps/master/launcher.py")

open("test.py", "wb").write(response.read())

response = urlOpener.open("https://raw.githubusercontent.com/Pipatooa/ppps/master/latestVersion")

latestVersion = response.read().decode("utf-8").split("\n")[0]

json.dump({"id": latestVersion, "type": "release"}, open(os.getcwd() + "\\ppps\\version", "w"))

os.system("start test.py")