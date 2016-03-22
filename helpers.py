import csv
import urllib2
import re
import os

def loadDetailsSite(id):
    url = 'http://data.nowgoal.com/detail/'+ id + '.html'
    downloaded_data  = urllib2.urlopen(url)
    csv_data = csv.reader(downloaded_data)
    rows = []
    for row in csv_data:
        rows.append(row)
    return rows

def loadOddscompSite(id):
    url = 'http://data.nowgoal.com/oddscomp/'+ id + '.html'
    downloaded_data  = urllib2.urlopen(url)
    csv_data = csv.reader(downloaded_data)
    rows = []
    for row in csv_data:
        rows.append(row)
    return rows

def loadIdsFromFile(nameOfFile):
    file = open(nameOfFile, "r+")
    ids = []
    for id in file:
        ids.append(id)
    return ids
        
def loadSite(id, choise):
    if choise == 1:
        return loadDetailsSite(id)
    else:
        return loadOddscompSite(id)

def getMessage(line):
    message = ''
    index = 1
    m = re.search('\>(.*)\<', line)
    try:
        m2 = re.search('\>(.*)', m.group(index))
        if m2:
            message = m2.group(1)
        else:
            message = m.group(1)
    except:
        return message
    return message
    
def getYear(line):
    message = []
    index = 1
    m = re.search('formatDate\(\'(.*)', line)
    try:
        return int(m.group(1))
    except:
        return 0
    
def getWeather(line):
    message = ''
    weatherString = 'Weather:';
    if line.startswith(weatherString):
        message = line.replace('&nbsp;', ' ')
    return message
   
def formatDate(data, year):
    month = int(data.pop(0))+1
    day = int(data.pop(0))
    hour = str((int(data.pop(0))+2)%24)
    if len(hour) == 1:
        hours = '0' + hour
    minutes = str(int(data.pop(0)))
    if len(minutes) == 1:
        minutes = '0' + minutes    
    seconds = int(data.pop(0))
        
    return str(month) + '/' + str(day) + '/' + str(year) + ' ' + hour + ':' + minutes #+ ' ' + dayOfWeekString
        
def getMatchItems(rows):
    flag = False
    flagData = False
    wordInLine = []
    dateLine = []
    wholeLine = ""
    weatherString = 'Weather:';
    for row in rows:
        if flag == False:
            try:
                while len(row) >= 1:
                    line = row.pop(0)
                line = line.strip()
                if re.search("matchItems(.*)", line):
                    flag = True
            except:
                continue
        else:
            try:
                while len(row) >= 1:
                    line = row.pop(0)
                    line = line.strip()
                    m = re.search("\>formatDate\(\'([0-9]*)", line)
                    if m:
                        year = m.group(1)
                        flagData = True
                        month = int(row.pop(0))+1
                        day = int(row.pop(0))
                        hour = row.pop(0)
                        minutes = row.pop(0)
                        seconds = row.pop(0)
                        wordInLine.append("Match Time: " + str(month) + '/' + str(day) + '/' + str(year) + ' ' + hour + ':' + minutes + '\n')
                    weather = getWeather(line)
                    if len(weather) != 0:
                        wordInLine.append(weather)
                        return wordInLine
            except:
                continue
                
        
                

def saveToFileMatchItems(matchItems, id):
    nameOfFile = str(id) + '.txt' 
    if os.path.isfile(nameOfFile):
        os.remove(nameOfFile);
   
    f = open(nameOfFile, 'a+')
    index = 1
    for item in matchItems:
        index = index + 1
        if item != '':
            f.write(item)
        if index == 4:
            f.write("\n")
    
def getRecords(line):
    records = []
    m = 1
    count = 0
    record = ''
    player = False
    image = False
    images = '/images/bf_img/'
    intro = "<tr align=\"center\" class=\"bg"
    m = re.search("\>[0-9]\<(.*)", line)
    if m:
        record = record + str(m.group(0)[1]) + ';;Min;'
        line2 = m.group(1)
        m = re.search("\>[0-9]\<", line2)
        record = record + str(m.group(0)[1]) + ';'
        records.append(record)
        record = ''
    m = re.search(intro + '(.*)', line)
    line = m.group(0)[len(intro):]
    while m: 
        m = re.search('bg[1-4]\"\>(.*)\<', line)
        if m:
            line = m.group(0)[5:]
            line = line.strip()
            if line[0].isdigit():
                index = line.index("<")
                record = record + line[:index] + ';'
            if player == False:
                if line.startswith("<a href="):
                    m2 = re.search('blank\>(.*)\</(.*)', line)
                    if m2:
                        line2 = m2.group(0)
                        end = line2.index('<')
                        record = record + line2[6:end] + ';'
                        player = True
            if image == False:
                if line.startswith("<img src"):
                    m2 = re.search("\=(.*)[0-9]\.png", line)
                    record = record + m2.group(1)[len(images)+1:len(images)+6] + ';'
                    image = True      
            if line.startswith("&nbsp;") or line.startswith("</td>"):
                record = record + ';'
            count = count + 1
            if count == 5:
                count = 0;
                player = False
                image = False
                records.append(record[:len(record)])
                record = ''
                m = re.search(intro + '(.*)', line)
                if m:
                    line = m.group(0)[len(intro):]
        else:
            break
    return records

def getKeyEvents(rows):
    flag = False
    wordInLine = ['Key Events;;;;'];
    wholeLine = ''
    for row in rows:
        if flag == True:
            line = row.pop(0)
            line = line.strip()
            wholeLine = wholeLine + line
            m = re.search('\</table\>(.*)', wholeLine)
            if m:
                break;
        else:
            try:
                while len(row) >= 1:
                    line = row.pop(0)
                line = line.strip()
                wholeLine = wholeLine + line
                m = re.search('(.*)Key Events(.*)', line)
                if m:
                    flag = True
            except:
                continue
    records = getRecords(wholeLine)
    if len(records) != 0:
        wordInLine.extend(records)
    return wordInLine
    
def saveToFileRecords(records, id):
    nameOfFile = str(id) + '.txt' 
    f = open(nameOfFile, 'a+')
    f.write("\n")
    for item in records:
        if item != '':
            f.write(item)
            f.write("\n")
            
def downloadDetails(id):
    rows = loadSite(id, 1)
    matchItems = getMatchItems(rows)
    saveToFileMatchItems(matchItems, id);
    records = getKeyEvents(rows)
    saveToFileRecords(records, id);

def saveToFileOldScope(records, id):
    nameOfFile = str(id) + '.txt' 
    f = open(nameOfFile, 'a+')
    f.write("##########################\n")  
    f.write(records[0][0])
    f.write("\n")
    f.write(records[0][1])
            
def getValues(rowsString):
    line1values = ''
    line2values = ''
    line = ''
    count = 0;
    count2 = 0;
    count3 = 0;
    flag = True
    m = re.search("\<TD width\=\'12%\' height\=25\>(.*)<", rowsString)
    if m:
        line = m.group(1)
        index = line.index('<')
        line1values = line1values + line[:index-1] + ';'
        line2values = line2values + ';'

    while flag:
        if count < 3:
            m = re.search("\<TD width\=\'7%\'\>(.*)<", line)
            if m:
                line = m.group(0)
                line = line[15:]
                index = line.index('<')
                line1values = line1values + line[:index] + ';'
            m = re.search("\<span class\=up\>(.*)<", line)
            m2 = re.search("\<span class\=down\>(.*)<", line)
            m3 = re.search("\<span class\=\>(.*)<", line)
            if m2 and m and m3:
                a = len(m.group(0))
                b = len(m2.group(0))
                c = len(m3.group(0))
                if c > a and c > b:
                    line = m3.group(0)
                    line = line[13:]
                elif b > a and b > c:
                    line = m2.group(0)
                    line = line[17:]
                else:
                    line = m.group(0)
                    line = line[15:]
                index = line.index('<')             
                line2values = line2values + line[:index] + ';'
                count = count + 1;
            elif m2:
                line = m2.group(0)
                line = line[17:] 
                index = line.index('<')             
                line2values = line2values + line[:index] + ';'
                count = count + 1;
            elif m:
                line = m.group(0)
                line = line[17:] 
                index = line.index('<')             
                line2values = line2values + line[:index] + ';'
                count = count + 1;
            else:
                count = count + 1;
                line2values = line2values + ';'
            
        if count == 3 and count2 < 6:
            m = re.search("\<TD width\=\'6%\'\>(.*)<", line)
            if m:
                line = m.group(0)
                line = line[15:]
                index = line.index('<')
                line1values = line1values + line[:index] + ';'
            m = re.search("\<span class\=up\>(.*)<", line)
            m2 = re.search("\<span class\=down\>(.*)<", line)
            m3 = re.search("\<span class\=\>(.*)<", line)
            if m2 and m and m3:
                a = len(m.group(0))
                b = len(m2.group(0))
                c = len(m3.group(0))
                if c > a and c > b:
                    line = m3.group(0)
                    line = line[13:]
                elif b > a and b > c:
                    line = m2.group(0)
                    line = line[17:]
                else:
                    line = m.group(0)
                    line = line[15:]
                index = line.index('<')             
                line2values = line2values + line[:index] + ';'
                count2 = count2 + 1;
            else:
                line2values = line2values + ';'
                count2 = count2 + 1;
            if count2 == 3:
                m = re.search("\<TD width\=\'6%\'\>(.*)<", line)
                if m:
                    line = m.group(0)
                    line = line[15:]
  
        if count2 == 6:
            flag = False

            
    lines = []
    lines.append(line1values)
    lines.append(line2values)
    return lines
    
def loadFirstRow(rows):
    flag = False
    wordInLine = []
    rowsString = ''
    for row in rows:
        if flag == True:
            records = getValues(rowsString)
            if len(records) != 0:
                wordInLine.append(records)
                flag = False
                break;
        else:
            try:
                line = row.pop(0)
                line = line.strip()
                if line.startswith('<TABLE cellSpacing=1'):
                    rowsString = rowsString + line
                    try:
                        while True:
                            line = row.pop(0)
                            line = line.strip()
                            rowsString = rowsString + line
                    except:
                        flag = True;
            except:
                continue
    return wordInLine
            
def downloadOldScope(id):
    rows = loadSite(id, 2)
    records = loadFirstRow(rows)
    saveToFileOldScope(records, id)

def downloadAll(nameOfFile):
    ids = loadIdsFromFile(nameOfFile)
    for id in ids:
        idStriped = id.strip() 
        try:
            downloadDetails(idStriped)
        except:
            print "Przy pobieraniu danych meczu o id " + str(idStriped) + " pojawil sie blad(details)"
            continue
        try:
            downloadOldScope(idStriped)
        except:
            print "Przy pobieraniu danych meczu o id " + str(idStriped) + " pojawil sie blad(oddscomp)"
            continue