import base64, contextlib, datetime, errno, hashlib, importlib, json, msvcrt, os, re, sys, textwrap, time, traceback, urllib.request

#Menu class and subclasses

class menu():
    def __init__(self, x, y, background, foreground, char, objects):
        self.x = x
        self.y = y
        
        self.pixel = pixel(background, foreground, char)
        self.objects = objects
    
    def draw(self):
        screen = {}
        
        for x in range(self.x):
            screen[x] = {}
            for y in range(self.y):
                screen[x][y] = self.pixel

        
        if type(self.objects) is dict:
            objectLists = self.objects.items()
        else:
            objectLists = enumerate(self.objects)
        
        for index, objectList in objectLists:
            if type(objectList) is dict:
                objectList = objectList.items()
            else:
                objectList = enumerate(objectList)
            
            for index, object in objectList:
                rendered = object.render()
            
                for x in rendered:
                    for y in rendered[x]:
                        screen[x][y] = rendered[x][y]
        
        output = ""
        for y in range(self.y):
            for x in range(self.x):
                if x == 0:
                    if screen[x][y].background:
                        output += "\033[048;5;" + str(screen[x][y].background) + "m"
                    else:
                        output += "\033[048;5;" + str(self.pixel.background) + "m"
                    
                    if screen[x][y].foreground:
                        output += "\033[038;5;" + str(screen[x][y].foreground) + "m"
                    else:
                        output += "\033[038;5;" + str(self.pixel.foreground) + "m"
                else:
                    if screen[x][y].background is not None:
                        if screen[x - 1][y].background != screen[x][y].background:
                            output += "\033[048;5;" + str(screen[x][y].background) + "m"
                    
                    if screen[x][y].foreground is not None:
                        if screen[x - 1][y].foreground != screen[x][y].foreground:
                            output += "\033[038;5;" + str(screen[x][y].foreground) + "m"
                
                output += screen[x][y].char
        
        write(output)

class title():
    def __init__(self, x, y, text, background, foreground, char):
        self.x = x
        self.y = y
        
        self.text = text
        self.pixel = pixel(background, foreground, char)
    
    def render(self):
        output = {}
        
        for indexY in range(6):
            xOffset = 0
            for char in self.text:
                letterKey = {"a": [" ##### ", "##   ##", "#######", "##   ##", "##   ##", "       "], "b": ["###### ", "##   ##", "###### ", "##   ##", "###### ", "       "], "c": [" ######", "##     ", "##     ", "##     ", " ######", "       "], "d": ["###### ", "##   ##", "##   ##", "##   ##", "###### ", "       "], "e": ["#######", "##     ", "#####  ", "##     ", "#######", "       "], "f": ["#######", "##     ", "#####  ", "##     ", "##     ", "       "], "g": [" ###### ", "##      ", "##   ###", "##    ##", " ###### ", "        "], "h": ["##   ##", "##   ##", "#######", "##   ##", "##   ##", ""], "i": ["##", "##", "##", "##", "##", "  "], "j": ["     ##", "     ##", "     ##", "##   ##", " ##### ", "       "], "k": ["##   ##", "##  ## ", "#####  ", "##  ## ", "##   ##", "       "], "l": ["##     ", "##     ", "##     ", "##     ", "#######", "       "], "m": ["###    ###", "####  ####", "## #### ##", "##  ##  ##", "##      ##", "          "], "n": ["###    ##", "####   ##", "## ##  ##", "##  ## ##", "##   ####", "         "], "o": [" ###### ", "##    ##", "##    ##", "##    ##", " ###### ", "        "], "p": ["###### ", "##   ##", "###### ", "##     ", "##     ", "       "], "q": [" ###### ", "##    ##", "##    ##", "## ## ##", " ###### ", "    ##  "], "r": ["###### ", "##   ##", "###### ", "##   ##", "##   ##", "       "], "s": ["#######", "##     ", "#######", "     ##", "#######", "       "], "t": ["########", "   ##   ", "   ##   ", "   ##   ", "   ##   ", "         "], "u": ["##    ##", "##    ##", "##    ##", "##    ##", " ###### ", "        "], "v": ["##    ##", "##    ##", "##    ##", " ##  ## ", "  ####  ", "        "], "w": ["##     ##", "##     ##", "##  #  ##", "## ### ##", " ### ### ", "         "], "x": ["##   ##", " ## ## ", "  ###  ", " ## ## ", "##   ##", "       "], "y": ["##    ##", " ##  ## ", "  ####  ", "   ##   ", "   ##   ", "        "], "z": ["#######", "   ### ", "  ###  ", " ###   ", "#######", "       "]}[char.lower()][indexY]
                
                for x in range(len(letterKey)):
                    if letterKey[x] == "#":
                        if self.x + x + xOffset not in output:
                            output[self.x + x + xOffset] = {}
                        
                        output[self.x + x + xOffset][self.y + indexY] = self.pixel
                
                xOffset += len(letterKey) + 1
        
        return output

class progressBar():
    def __init__(self, parent, backgroundRect, foregroundRect, titleText, descriptionText):
        self.parent = parent
        
        self.backgroundRect = backgroundRect
        self.foregroundRect = foregroundRect
        
        self.titleText = titleText
        self.descriptionText = descriptionText
    
    def update(self, title, description, progress):
        global lastDrawTime
        
        if title is not None:
            self.titleText.text = title
    
        if description is not None:
            self.descriptionText.text = description
    
        if progress is not None:
            self.foregroundRect.x2 = int(self.backgroundRect.x1 + progress * (self.backgroundRect.x2 - self.backgroundRect.x1))
        
        try:
            if lastDrawTime + 0.05 < time.time():
                self.parent.draw()
                lastDrawTime = time.time()
        except NameError:
            lastDrawTime = time.time()
        except:
            raise
    
    def render(self):
        return specialMerge(specialMerge(self.backgroundRect.render(), self.foregroundRect.render()), specialMerge(self.titleText.render(), self.descriptionText.render()))

class text():
    def __init__(self, x1, y1, x2, y2, text, foreground):
        self.x1 = x1
        self.y1 = y1
        
        self.x2 = x2
        self.y2 = y2
        
        self.text = text
        
        self.foreground = foreground
    
    def render(self):
        output = {}
        
        textOffsetY = -1
        for index, line in enumerate(self.text.split("\n")):
            initialIndent = ""
            subsequentIndent = ""
            for char in line:
                if char in [" ", "-"]:
                    initialIndent += char
                    subsequentIndent += " "
                else:
                    break
            
            if len(line) == len(initialIndent):
                textOffsetY += 1
            
            for screenline in textwrap.wrap(line[len(initialIndent):], width = self.x2 - self.x1, replace_whitespace = False, initial_indent = initialIndent, subsequent_indent = subsequentIndent):
                textOffsetY += 1
                
                if self.y1 + textOffsetY > self.y2:
                    break
                
                for indexX, char in enumerate(screenline):
                    if self.x1 + indexX not in output:
                        output[self.x1 + indexX] = {}
                    
                    output[self.x1 + indexX][self.y1 + textOffsetY] = pixel(None, self.foreground, char)
        
        return output

class rectangle():
    def __init__(self, x1, y1, x2, y2, background, foreground, char):
        self.x1 = x1
        self.y1 = y1
        
        self.x2 = x2
        self.y2 = y2
        
        self.pixel = pixel(background, foreground, char)
        
    def render(self):
        output = {}
        
        for x in range(self.x1, self.x2 + 1):
            output[x] = {}
            for y in range(self.y1, self.y2 + 1):
                output[x][y] = self.pixel
        
        return output

class pixel():
    def __init__(self, background, foreground, char):
        self.background = background
        self.foreground = foreground
        
        self.char = char

#Internal Functions

def setTitle():
    if versionData["type"] == "experimental":
        os.system("title PPPS Games Launcher v" + versionData["id"] + " (" + versionData["type"].title() + ")")
    else:
        os.system("title PPPS Games Launcher v" + versionData["id"])

def setDisplaySize(lines, columns, force):
    if force:
        os.system("mode con: lines=" + str(lines) + " cols=" + str(columns))
    
    while os.get_terminal_size().lines != lines or os.get_terminal_size().columns != columns:
        os.system("mode con: lines=" + str(lines) + " cols=" + str(columns))

def write(text):
    while len(text) > 0:
        os.write(1, text[:30000].encode("ASCII"))
        text = text[30000:]

def specialMerge(x, y):
    def mergeDicts(x, y):
        z = x.copy()
        z.update(y)
        return z
    
    z = {}
    
    for key in mergeDicts(x, y):
        if key in x and key in y:
            z[key] = x[key]
            z[key].update(y[key])
        elif key in x:
            z[key] = x[key]
        elif key in y:
            z[key] = y[key]
    
    return z 

def getVersion():
    def parseVersion(version):
        return [int(x) for x in re.sub(r'(\.0+)*$','', version).split(".")]
    
    def compareVersions(version1, version2):
        return (parseVersion(version1) > parseVersion(version2)) - (parseVersion(version1) < parseVersion(version2))
    
    global versionData
    
    latestVersion = downloadFromUrl("https://raw.githubusercontent.com/Pipatooa/ppps/master/latestVersion", True)
    
    try:
        with open("version") as file:
            versionData = json.load(file)
        
        if compareVersions(versionData["id"], latestVersion) == -1 and versionData["type"] == "release":
            raise
    except:
        updateLauncher()

def getData():
    global authorisationLevel, users, menuText, badWords, gameData
    
    currentProgressBar.update("Fetching Online Data...", None, 0)
    
    try:
        currentProgressBar.update(None, "Downloading user data", None)
        users = json.loads(downloadFromUrl("https://raw.githubusercontent.com/Pipatooa/ppps/master/users", True))
        
        currentProgressBar.update(None, "Downloading menu data", 1/4)
        menuText = json.loads(downloadFromUrl("https://raw.githubusercontent.com/Pipatooa/ppps/master/menuText", True))
        
        currentProgressBar.update(None, "Downloading username data", 2/4)
        response = downloadFromUrl("https://raw.githubusercontent.com/Pipatooa/ppps/master/badWords", True)
        badWords = base64.b64decode(response).decode("ASCII").upper().split("\n")
        
        currentProgressBar.update(None, "Downloading game data", 3/4)
        response = downloadFromUrl("https://raw.githubusercontent.com/Pipatooa/ppps/master/gameData", True)
        gameData = []
        
        for game in json.loads(response):
            if game["visibility"] == 2:
                gameData.append(game)
            elif game["visibility"] == 1 and versionData["type"] == "experimental":
                gameData.append(game)
        
        currentProgressBar.update(None, "", 1)
    except:
        raise
        runErrorMenu("Launcher was unable to retrieve online data.")
        exit()

def checkFiles():
    global requests, pyperclip
    
    filesRequired = json.loads(downloadFromUrl("https://raw.githubusercontent.com/Pipatooa/ppps/master/index", True))
    filesFound = []
    
    for root, dirs, files in os.walk(os.getcwd()):
        for name in files:
            filename = os.path.join(root, name)[len(os.getcwd()):]
        
            filesFound.append(filename)
    
    filesMissing = []
    for file in filesRequired:
        if file not in filesFound:
            filesMissing.append(file)

    if len(filesMissing) > 0:
        downloadFiles(filesMissing)

def loadImports():
    global pyperclip
    
    try:
        with open(os.devnull, 'w') as file:
            with contextlib.redirect_stderr(file):
                pass
    except:
        runErrorMenu("Launcher was unable to import one or more required modules.\n\nPlease make sure that the folder \"ppps\" is up to date.\n\n\n\nDETAILS:\n" + traceback.format_exec())
        exit()

def downloadFiles(files):
    currentProgressBar.update("Downloading Required Files...", "", 0)
    
    for index, file in enumerate(files):
        currentProgressBar.update("Downloading Required Files... (" + str(index) + " of " + str(len(files)) + ")", "Downloading " + file, index / len(files))
        response = downloadFromUrl("https://raw.githubusercontent.com/Pipatooa/ppps/master/ppps" + file.replace("\\", "/"))
        
        if not os.path.exists(os.getcwd() + os.path.dirname(file)):
            os.makedirs(os.getcwd() + os.path.dirname(file))
        
        open(os.getcwd() + file, "wb").write(response)

def downloadFromUrl(url, text = False):
    """
    global session
    
    try:
        session
    except:
        session = requests.Session()
        session.trust_env = False
    
    response = session.get(url)
    
    if text:
        return response.text
    else:
        return response.content
    """
    
    global urlOpener
    
    try:
        urlOpener
    except:
        proxyHandler = urllib.request.ProxyHandler({})
        urlOpener = urllib.request.build_opener(proxyHandler)

    response = urlOpener.open(url)
    
    if text:
        return response.read().decode("utf-8")
    else:
        return response.read()

def updateLauncher():
    response = downloadFromUrl("https://raw.githubusercontent.com/Pipatooa/ppps/master/updater.py")
    
    open("updater.py", "wb").write(response)
    
    os.system("start " + os.getcwd() + "\\updater.py")
    
    exit()

def getKey():
    key = None
    
    while msvcrt.kbhit():
        if key == 0:
            key = ord(msvcrt.getch()) + 1000000
        if key == 224:
            key = ord(msvcrt.getch()) + 1224000
        else:
            key = ord(msvcrt.getch())
    
    return key

#Menus

def runLoginMenu():
    global currentMenu
    
    loginMenu = menu(120, 40, 4, 0, " ", {})
    loginMenu.objects["layout"] = [rectangle(4, 2, 115, 10, 6, None, " "), title(41, 4, "Login", 0, None, " "), rectangle(4, 13, 115, 37, 6, None, " ")]
    loginMenu.objects["boxes"] = [rectangle(12, 17, 107, 19, 7, None, " "), rectangle(12, 24, 107, 26, 7, None, " "), rectangle(12, 31, 107, 33, 7, None, " ")]
    loginMenu.objects["text"] = {"username": text(14, 18, 106, 18, "", 0), "password": text(14, 25, 106, 25, "", 0), "text": text(14, 32, 106, 32, "Esc - Account Registration", 0)}
    loginMenu.objects["errorText"] = [text(12, 21, 106, 21, "", 0)]
    
    blinkTime = 0
    drawTime = 0
    
    selected = 0
    
    username = ""
    password = ""
    
    while currentMenu == "login":
        blinkTime += 1
        drawTime += 1
        
        if drawTime % 5 == 0:
            if blinkTime % 50 < 26 and selected == 0:
                loginMenu.objects["text"]["username"].text = "USERNAME: " + username + "_"
            else:
                loginMenu.objects["text"]["username"].text = "USERNAME: " + username
            
            if blinkTime % 50 < 26 and selected == 1:
                loginMenu.objects["text"]["password"].text = "PASSWORD: " + "*" * len(password) + "_"
            else:
                loginMenu.objects["text"]["password"].text = "PASSWORD: " + "*" * len(password)
            
            loginMenu.draw()
        
        key = getKey()
        
        if key:
            if key in (alphabet + [b" "]) and selected == 0 and len(username) < 20:
                username += chr(key).upper()
            elif key in (alphabet + numbers) and selected == 1 and len(password) < 20:
                password += chr(key).upper()
            elif key == 8 and selected == 0:
                username = username[:-1]
            elif key == 8 and selected == 1:
                password = password[:-1]
            elif key == 1224072 and selected == 1:
                blinkTime = 0
                selected = 0
            elif key in [13, 1224080] and selected == 0:
                blinkTime = 0
                selected = 1
            elif key == 13 and selected == 1:
                loginMenu.objects["errorText"][0].text = ""
                
                hash = hashlib.sha256(password.encode()).hexdigest()
                
                if len(username) > 0:
                    for user in users:
                        if username == user["username"] and hash == user["password"]:
                            currentMenu = "main"
                            break
                    else:
                        loginMenu.objects["errorText"][0].text = "Invalid username or password"
                
                selected = 0
                username = ""
                password = ""
                    
            elif key == 27:
                currentMenu = "registration"
        
        time.sleep(0.01)

def runRegistrationMenu():
    global currentMenu
    
    registrationMenu = menu(120, 40, 4, 0, " ", {})
    registrationMenu.objects["layout"] = [rectangle(4, 2, 115, 10, 6, None, " "), title(30, 4, "Register", 0, None, " "), rectangle(4, 13, 115, 37, 6, None, " ")]
    registrationMenu.objects["boxes"] = [rectangle(12, 17, 107, 19, 7, None, " "), rectangle(12, 24, 107, 26, 7, None, " "), rectangle(12, 31, 107, 33, 7, None, " ")]
    registrationMenu.objects["text"] = {"username": text(14, 18, 106, 18, "", 0), "password": text(14, 25, 106, 25, "", 0), "confirmPassword": text(14, 32, 106, 32, "", 0)}
    registrationMenu.objects["errorText"] = {"username": text(12, 21, 106, 21, "", 0), "password": text(12, 28, 106, 28, "", 0), "confirmPassword": text(12, 35, 106, 35, "", 0)}
    
    blinkTime = 0
    drawTime = 0
    
    selected = 0
    
    username = ""
    password = ""
    confirmPassword = ""
    
    while currentMenu == "registration":
        blinkTime += 1
        drawTime += 1
        
        if drawTime % 5 == 0:
            if blinkTime % 50 < 26 and selected == 0:
                registrationMenu.objects["text"]["username"].text = "DESIRED USERNAME: " + username + "_"
            else:
                registrationMenu.objects["text"]["username"].text = "DESIRED USERNAME: " + username
            
            if blinkTime % 50 < 26 and selected == 1:
                registrationMenu.objects["text"]["password"].text = "DESIRED PASSWORD: " + "*" * len(password) + "_"
            else:
                registrationMenu.objects["text"]["password"].text = "DESIRED PASSWORD: " + "*" * len(password)
            
            if blinkTime % 50 < 26 and selected == 2:
                registrationMenu.objects["text"]["confirmPassword"].text = "DESIRED PASSWORD: " + "*" * len(confirmPassword) + "_"
            else:
                registrationMenu.objects["text"]["confirmPassword"].text = "DESIRED PASSWORD: " + "*" * len(confirmPassword)
            
            registrationMenu.draw()
        
        key = getKey()
        
        if key:
            if key in (alphabet + [b" "]) and selected == 0 and len(username) < 20:
                username += chr(key).upper()
            elif key in (alphabet + numbers) and selected == 1 and len(password) < 20:
                password += chr(key).upper()
            elif key in (alphabet + numbers) and selected == 2 and len(confirmPassword) < 20:
                confirmPassword += chr(key).upper()
            elif key == 8 and selected == 0:
                username = username[:-1]
            elif key == 8 and selected == 1:
                password = password[:-1]
            elif key == 8 and selected == 2:
                confirmPassword = confirmPassword[:-1]
            elif key == 1224072 and selected > 0:
                blinkTime = 0
                selected -= 1
            elif key in [13, 1224080] and selected < 2:
                blinkTime = 0
                selected += 1
            elif key == 13 and selected == 2:
                registrationMenu.objects["errorText"]["username"].text = ""
                registrationMenu.objects["errorText"]["password"].text = ""
                registrationMenu.objects["errorText"]["confirmPassword"].text = ""
                
                if len(username) < 3:
                    registrationMenu.objects["errorText"]["username"].text = "Username must be at least 3 characters long"
                elif any(badWord in username for badWord in badWords):
                    registrationMenu.objects["errorText"]["username"].text = "Username contains banned word"
                
                if len(password) < 8:
                    registrationMenu.objects["errorText"]["password"].text = "Password must be at least 8 characters long"
                elif not any(chr(letter) in password for letter in alphabet):
                    registrationMenu.objects["errorText"]["password"].text = "Password must contain a letter"
                elif not any(chr(number) in password for number in numbers):
                    registrationMenu.objects["errorText"]["password"].text = "Password must contain a number"
                elif password != confirmPassword:
                    registrationMenu.objects["errorText"]["confirmPassword"].text = "Passwords must match"
                
                if [registrationMenu.objects["errorText"]["username"].text, registrationMenu.objects["errorText"]["password"].text, registrationMenu.objects["errorText"]["confirmPassword"].text] != ["", "", ""]:
                    selected = 0
                else:
                    registrationMenu = menu(120, 40, 4, 0, " ", {})
                    registrationMenu.objects["layout"] = [rectangle(4, 2, 115, 10, 6, None, " "), title(30, 4, "Register", 0, None, " "), rectangle(4, 13, 115, 37, 6, None, " ")]
                    registrationMenu.objects["boxes"] = [rectangle(12, 17, 107, 21, 7, None, " ")]
                    registrationMenu.objects["text"] = [text(14, 18, 111, 30, "USERNAME: " + username + "\n\nPASSWORD: " + hashlib.sha256(password.encode()).hexdigest(), 0), text(12, 26, 109, 35, menuText["registration"], 0)]
                    registrationMenu.draw()
                    
                    while currentMenu == "registration":
                        key = getKey()
                        
                        if key == 27:
                            currentMenu = "login"
                            
            elif key == 27:
                currentMenu = "login"
        
        time.sleep(0.01)

def runMainMenu():
    global currentMenu
    
    mainMenu = menu(120, 40, 4, 7, " ", {})
    mainMenu.objects["layout"] = [rectangle(4, 2, 54, 10, 6, None, " "), title(8, 4, "Games", 0, None, " "), rectangle(4, 13, 54, 37, 6, None, " "), rectangle(59, 2, 115, 37, 6, None, " ")]
    mainMenu.objects["boxes"] = [rectangle(6, 14, 52, 16, 0, None, " "), rectangle(6, 18, 52, 20, 0, None, " "), rectangle(6, 22, 52, 24, 0, None, " "), rectangle(6, 26, 52, 28, 0, None, " "), rectangle(6, 30, 52, 32, 0, None, " "), rectangle(6, 34, 52, 36, 0, None, " ")][:len(gameData)]
    mainMenu.objects["text"] = {"description": text(61, 3, 113, 36, "", 7)}
    mainMenu.objects["gameText"] = [text(8, 15, 50, 15, "", 7), text(8, 19, 50, 19, "", 7), text(8, 23, 50, 24, "", 7), text(8, 27, 50, 27, "", 7), text(8, 31, 50, 31, "D", 7), text(8, 35, 50, 35, "D", 7)][:len(gameData)]
    
    blinkTime = 0
    
    selected = 0
    topResult = 0
    
    while currentMenu == "main":
        blinkTime += 1
        
        for index, game in enumerate(gameData[topResult:topResult+6]):
            mainMenu.objects["gameText"][index].text = game["name"]
        
        for x in range(len(gameData[:6])):
            if x == selected - topResult and blinkTime % 10 < 6:
                mainMenu.objects["boxes"][x].pixel.background = 1
            else:
                mainMenu.objects["boxes"][x].pixel.background = 0
        
        mainMenu.objects["text"]["description"].text = gameData[selected]["description"]
        mainMenu.draw()
        
        key = getKey()
            
        if key:
            if key in [1224072, 119] and selected > 0:
                blinkTime = 0
                selected -= 1
                
                if selected < topResult:
                    topResult -= 1
            elif key in [1224080, 115] and selected < len(gameData) - 1:
                blinkTime = 0
                selected += 1
                
                if selected > topResult + 5:
                    topResult += 1
            elif key in [13, 32]:
                pass
        
        time.sleep(0.05)

def runErrorMenu(errorText):
    errorMenu = menu(120, 40, 4, 0, " ", [])
    errorMenu.objects = [[rectangle(4, 2, 115, 10, 6, None, " "), title(45, 4, "Error", 0, None, " "), rectangle(4, 13, 115, 37, 6, None, " "), text(8, 15, 111, 35, errorText, 0)]]
    errorMenu.draw()
    
    while True:
        key = getKey()
        
        if key == 27:
            break
        
        time.sleep(0.05)

#Main

def main():
    global currentMenu, alphabet, numbers
    
    global currentProgressBar
    
    alphabet = [i for i in range(65, 91)] + [i for i in range(97, 123)]
    numbers = [i for i in range(48, 58)]
    
    if not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "\\ppps"):
        os.makedirs(os.path.dirname(os.path.realpath(__file__)) + "\\ppps")
    
    os.chdir(os.path.dirname(os.path.realpath(__file__)) + "\\ppps")
    sys.path.append(os.getcwd() + "\\imports")
    
    getVersion()
    
    setTitle()
    setDisplaySize(40, 120, True)
    
    titleScreen = menu(120, 40, 4, 0, " ", {})
    
    currentProgressBar = progressBar(titleScreen, rectangle(10, 33, 110, 34, 7, None, " "), rectangle(10, 33, 10, 34, 8, None, " "), text(10, 32, 110, 32, "", 0), text(10, 35, 110, 35, "", 0))
    
    titleScreen.objects["layout"] = [rectangle(4, 2, 115, 27, 6, None, " "), rectangle(4, 30, 115, 37, 6, None, " ")]
    titleScreen.objects["titles"] = [title(44, 5, "PPPS", 0, None, " "), title(38, 12, "Games", 0, None, " "), title(27, 19, "Launcher", 0, None, " "), text(95, 26, 119, 26, "-By Bradley Hall-", 0)]
    titleScreen.objects["progressBar"] = [currentProgressBar]
    titleScreen.draw()
    
    startTime = time.time()
    
    checkFiles()
    getData()
    
    loadImports()
    
    currentProgressBar.update("Fully Loaded", "", 1)
    titleScreen.draw()
    
    if time.time() < startTime + 2:
        time.sleep(2 - time.time() + startTime)
    
    currentMenu = "login"
    while True:
        if currentMenu == "login":
            runLoginMenu()
        elif currentMenu == "registration":
            runRegistrationMenu()
        elif currentMenu == "main":
            runMainMenu()

main()