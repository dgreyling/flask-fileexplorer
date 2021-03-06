from flask import Flask, render_template, request, send_file, redirect, session
import os
import sys
import json

app = Flask(__name__)
app.secret_key = 'my_secret_key'
#currentDirectory='/Users/rehan/Downloads'

with open('config.json') as json_data_file:
    data = json.load(json_data_file)
hiddenList = data["Hidden"]
favList = data["Favorites"]
password = data["Password"]
currentDirectory=data["rootDir"]


if(len(favList)>3):
    favList=favList[0:3]

for i in range(0,3):
    favList[i]=favList[i].replace('/','>')



@app.route('/login/')
def loginMethod():
    global password
    if(password==''):
        session['login'] = True


    if('login' in session):
        return redirect('/')
    else:
        return render_template('login.html')


@app.route('/login/', methods=['POST'])
def loginPost():
    global password

    text = request.form['text']
    if(text==password):
        session['login'] = True

        return redirect('/')
    else:
        return redirect('/login/')

@app.route('/logout/')
def logoutMethod():
    if('login' in session):
        session.pop('login',None)
    return redirect('/login/')
    
#@app.route('/exit/')
#def exitMethod():
#    exit()




def hidden(path):

    for i in hiddenList:
        if i != '' and i in path:
            return True
    
    return False



def changeDirectory(path):
    global currentDirectory

    pathC = path.split('>')
    
    if(pathC[0]==""):
        pathC.remove(pathC[0])
    
    myPath = currentDirectory+'/'+'/'.join(pathC)
    #print(myPath)
    try:
        os.chdir(myPath)
        ans=True
        if(currentDirectory not in os.getcwd()):
            ans = False
    except:
        ans=False
    
    

    return ans
    
def getDirList():


    dList= list(filter(lambda x: os.path.isdir(x), os.listdir('.')))
    finalList = []
    curDir=os.getcwd()

    for i in dList:
        if(hidden(curDir+'/'+i)==False):
            finalList.append(i)

    return(finalList)


def getFileList():

    dList = list(filter(lambda x: os.path.isfile(x), os.listdir('.')))

    finalList = []
    curDir=os.getcwd()

    for i in dList:
        if(hidden(curDir+'/'+i)==False):
            finalList.append(i)

    return(finalList)






@app.route('/<var>', methods=['GET'])
def filePage(var):
    if('login' not in session):
        return redirect('/login/')
    
    if(changeDirectory(var)==False):
        #Invalid Directory
        print("Directory Doesn't Exist")
        return render_template('404.html',errorCode=300,errorText='Invalid Directory Path',favList=favList)
     
    try:
        dirList = getDirList()
        fileList = getFileList()
    except:
        return render_template('404.html',errorCode=200,errorText='Permission Denied',favList=favList)


    return render_template('home.html',dirList=dirList,fileList=fileList,currentDir=var,favList=favList)

@app.route('/', methods=['GET'])
def homePage():
    global currentDirectory
    if('login' not in session):
        return redirect('/login/')
    


    os.chdir(currentDirectory)
    dirList = getDirList()
    fileList=getFileList()
    return render_template('home.html',dirList=dirList,fileList=fileList,currentDir="",favList=favList)


@app.route('/download/<var>')
def downloadFile(var):
    global currentDirectory
    if('login' not in session):
        return redirect('/login/')
    
    #os.chdir(currentDirectory)

    pathC = var.split('>')
    if(pathC[0]==''):
        pathC.remove(pathC[0])
    
    fPath = '/'.join(pathC)
    fPath=currentDirectory+'/'+fPath
    
    if(hidden(fPath)):
        #FILE HIDDEN
        return render_template('404.html',errorCode=100,errorText='File Hidden',favList=favList)


    fName=pathC[len(pathC)-1]
    #print(fPath)
    try:
        return send_file(fPath, attachment_filename=fName)
    except:
        return render_template('404.html',errorCode=200,errorText='Permission Denied',favList=favList)


@app.errorhandler(404)
def page_not_found(e):
    if('login' not in session):
        return redirect('/login/')
    
    # note that we set the 404 status explicitly
    return render_template('404.html',errorCode=404,errorText='Page Not Found',favList=favList), 404



if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)