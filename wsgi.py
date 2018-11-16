import os
import sys
from flask import (
    Flask, 
    send_from_directory, 
    request, 
    redirect, 
    render_template, 
    session, 
    make_response, 
    url_for, flash
)
# 導入 pybean 模組與所要使用的 Store 及 SQLiteWriter 方法
from pybean import (
    Store, 
    SQLiteWriter
)
import sqlite3

# 利用 Store  建立資料庫檔案對應物件, 並且設定 frozen=False 表示要開放動態資料表的建立

# 確定程式檔案所在目錄, 在 Windows 有最後的反斜線
_curdir = os.path.join(os.getcwd(), os.path.dirname(__file__))
sys.path.append(_curdir)

# 設定在雲端與近端的資料儲存目錄
download_root_dir = "./"
data_dir = "./"

app = Flask(__name__)

is_xhtml = True

def nl2br(string, is_xhtml= True ):
    if is_xhtml:
        return string.replace('\n','<br />\n')
    else :
        return string.replace('\n','<br>\n')

@app.route('/doCheck', methods=['POST'])
def doCheck():
    word =  request.form["word"]
    if word == None:
        return "<br /><a href=\"/\">首頁</a>|<a href=\"./\">重新查詢</a>"
    vocabulary = Store(SQLiteWriter(data_dir+"/webster_vocabulary.sqlite", frozen=True))
    if (vocabulary.count("word","lower(word) like ?", [word]) == 0):
        return "找不到與 "+ word.title() + "有關的資料!"
    else:
        result = vocabulary.find("word","lower(word) like ?", [word])
        output = "以下為 webster 字典查詢:"+word+" 所得到的結果<br /><br />"
        for item in result:
            output += word.title()+"<br /><br />"+str(nl2br(item.defn,True))+"<br />"
        output += "<br /><a href=\"/\">首頁</a>|<a href=\"./\">重新查詢</a>"
        return output

@app.route('/doCheck_wn', methods=['POST'])
def doCheck_wn():
    word =  request.form["word"]
    if word == None:
        return "<br /><a href=\"/\">首頁</a>|<a href=\"./\">重新查詢</a>"
    # 聯結資料庫檔案
    conn = sqlite3.connect(data_dir+"/wordnet30.db")
    # 取得目前 cursor
    cursor = conn.cursor()

    sql = "SELECT word.wordid, synset.synsetid, pos, definition, sample \
    FROM word, sense, synset, sample \
    WHERE word.wordid = sense.wordid \
    AND sense.synsetid = synset.synsetid \
    AND sample.synsetid = synset.synsetid \
    AND lemma = ?"

    output = "以下為 wordnet 字典查詢:"+word+" 所得到的結果<br /><br />"
    count = 0

    for row in cursor.execute(sql, [(word)]):
        count += 1
        output += str(count) + ": " + word.title() + " ("+ str(row[2])+")<br />Defn: " + str(nl2br(row[3],True)) + "<br />Sample: "  \
        +  str(nl2br(row[4],True)) + "<br /><br />"

    output += "<br /><a href=\"/\">首頁</a>|<a href=\"./\">重新查詢</a>"

    return output

# default 為 webster 查詢
@app.route('/')
def index():
    return '''<html>
    <head>
    <title>查字典</title>
    </head>
    <body>
    <form action="doCheck" method="post">
    請輸入要查詢 webster 的單字:<input type="text" name="word" value="" 
        size="15" maxlength="40"/>
    <p><input type="submit" value="查詢"/></p>
    <p><input type="reset" value="清除"/></p>
    </form>
    <br /><a href="/">首頁</a>
    </body>
    </html>'''	

@app.route('/wordnet')
def wordnet():
    return '''<html>
<head>
  <title>查字典</title>
</head>
<body>
  <form action="doCheck_wn" method="post">
    請輸入要查詢 wordnet 的單字:<input type="text" name="word" value="" 
        size="15" maxlength="40"/>
    <p><input type="submit" value="查詢"/></p>
    <p><input type="reset" value="清除"/></p>
  </form>
 <br /><a href="/">首頁</a>
</body>
</html>'''	

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)