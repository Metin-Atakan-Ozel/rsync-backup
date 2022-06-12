

import datetime
import subprocess
import time
from datetime import date
from subprocess import Popen, PIPE
import smtplib
from email.mime.text import MIMEText
from email.header    import Header
import sqlite3


def readFile():
    f = open("/home/metin/Desktop/backupapp/inffile")
    return f.read().splitlines()

def mailSender(ip):
    server = smtplib.SMTP("smtp.yandex.ru",587)
    login = "smtptest@enterpirce.com"
    password = "passwd"
    destination = "developers@enterpirce.com"

    subject = 'BACKUP ERROR INFO'
    header = 'Backup Alınırken Sorun Oluştu'
    body = '<p>'+ ip +' Adresinden backup alınamadı !</p>'

    msg = MIMEText(
        '<h2 style="margin: 0; padding: 20px; color: #ffffff; background: #4b9fc5">' + header + '</h2>' + body, 'html',
        'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = login
    msg['To'] = destination

    server.starttls()
    server.login(login,password)
    server.sendmail(login,destination,msg.as_string())

    server.quit()


localpath = "/home/metin/Desktop/backupapp/backupfiles/" #dosyanın çekileceği yer 
localtarpath = "/home/metin/Desktop/backupapp/tarbackup/"
sourcePath = readFile()

dateForName = date.today()
dateForName = str(dateForName) + "_" + str(int(time.time()))

db = sqlite3.connect('backup.db')
im = db.cursor()

im.execute("""CREATE TABLE IF NOT EXISTS backupinfo (device, process_detail, process_path, process_explanation, created_dt)""")

for getdata in sourcePath:
    x = getdata.split(" ")
    command1 = 'rsync -avzri -e "ssh -i $HOME/.ssh/id_rsa" --delete root@' + x[0] + ':' + x[1] + ' ' + localpath + x[0]
    #process = subprocess.run(command1, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    process = subprocess.run(command1, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = process.returncode
    if int(output) != 0:
        print('sorunvar',x[0])
        ip=str(x[0])
        #mailSender(ip) ## mail sender açılacak test için kapatıldı
    else:
        if len(process.stdout.splitlines()) > 4:
            print(process.stdout.splitlines())
            recordList = process.stdout.splitlines()
            del recordList[-3:]
            del recordList[0]
            for files in recordList:
                files2 = files.split(" ")
                now = datetime.datetime.now()
                explanation = "("
                if files2[0] == "*deleting":
                    explanation = explanation + files2[-1]+ " named file or directory were deleted)"
                elif files2[0] == ">f+++++++++":
                    explanation = explanation + files2[-1] + " named file was created)"
                elif files2[0] == "cd+++++++++":
                    explanation = explanation + files2[-1] + " named directory was created)"
                                
                else:
                    if files2[0].find("f") != -1:
                        explanation = explanation + files2[-1] + " named file) ("
                    if files2[0].find("d") != -1:
                        explanation = explanation + files2[-1] + " named directory) ("
                    if files2[0].find("L") != -1:
                        explanation = explanation + files2[-1] + " named symlink) ("
                    if files2[0].find("D") != -1:
                        explanation = explanation + files2[-1] + " named device) ("
                    if files2[0].find("S") != -1:
                        explanation = explanation + files2[-1] + " named special file) ("
                    if files2[0].find("h") != -1:
                        explanation = explanation + files2[-1] + " named the item is a hard link to another item) ("
                    if files2[0].find("s") != -1:
                        explanation = explanation + files2[-1] + " changed file size) ("
                    if files2[0].find("t") != -1:
                        explanation = explanation + files2[-1] + " changed file modification time) ("
                    if files2[0].find("p") != -1:
                        explanation = explanation + files2[-1] + " changed file permission) ("
                    if files2[0].find("o") != -1:
                        explanation = explanation + files2[-1] + " changed file owner) ("
                    if files2[0].find("g") != -1:
                        explanation = explanation + files2[-1] + " changed file group) ("
                    if files2[0].find("a") != -1:
                        explanation = explanation + files2[-1] + " changed file ACL information) ("
                    if files2[0].find("u") != -1:
                        explanation = explanation + files2[-1] + " changed file u slot is reserved for future use) ("
                    print(explanation)
                    explanation = explanation[:-1]
                im.execute("""INSERT INTO backupinfo VALUES (?, ?, ?, ?, ?)""", (x[0],files,files2[-1],explanation,now))
                db.commit()

for tarlanan in sourcePath:
    y = tarlanan.split(" ")
    print("y",y)
    command2 = "tar -zcvf " + localtarpath + dateForName + "_" +y[0] + ".tar.gz "+  localpath + y[0]
    args2 = command2.split(" ")
    process2 = Popen(args2, stdout=PIPE, stderr=PIPE)
    #process2 = subprocess.run(command2, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    print("command2",command2)

lcount = len(sourcePath)
command3 = "find "+ localtarpath  + " -type f | wc -l"
processc = subprocess.run(command3, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
outputc = processc.stdout

if int(outputc) > int(lcount) and int(outputc) % int(lcount) == 0:
    for xyz in sourcePath:
        command4 = "find " + localtarpath + " -type f -printf '%T+ %p\\n' | sort | head -n 1"
        processv = subprocess.run(command4, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        outputv = processv.stdout
        removefile = outputv.split(" ")
        command5 = "rm -rf " + removefile[1]
        processz = subprocess.run(command5, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)









