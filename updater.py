import os, urllib.request

os.chdir(os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "\\.."))

proxyHandler = urllib.request.ProxyHandler({})
urlOpener = urllib.request.build_opener(proxyHandler)
response = urlOpener.open("https://raw.githubusercontent.com/Pipatooa/ppps/master/ppps/launcher.py")

open("test.py", "wb").write(response.read())

response = urlOpener.open("https://raw.githubusercontent.com/Pipatooa/ppps/master/ppps/version")

open("\\ppps\version", "wb").write(response.read())

os.system("start test.py")