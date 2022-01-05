from flask import Flask,send_from_directory
from flask import request
from flask import jsonify

import os
import re
import pymysql.cursors
from dotenv import load_dotenv
import base64
import random

load_dotenv()

HOST = str(os.getenv('DB_HOST'))
USER = str(os.getenv('DB_USER'))
PASSWORD = str(os.getenv('DB_PASSWORD'))
DB = str(os.getenv('DB_DATABASE'))

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

def get_db_cursor():
  db = pymysql.connect(host=HOST,
                       user=USER,
                       password=PASSWORD,
                       db=DB,
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
  return db, db.cursor()

@app.route('/score')
def score():

  db, cursor = get_db_cursor()
  sql = f"SELECT * FROM raiting"

  try:
    cursor.execute(sql)
    entries = cursor.fetchall()
    entries = sorted([(e["Name"], e["Points"], e["Confession"]) for e in entries], key=lambda x: x[1], reverse=True)

    string = "\n".join([f"<tr> <th>{i + 1}</th> <th>{name}</th> <th>{confession}</th> <th>{points}</th> </tr>" for i, (name, points, confession) in enumerate(entries)])
    ret = f"""<html lang='ru'>
                <style>
                  th, td {{
                    border:1px solid grey;
                    font-size: 150%;
                    font-weight: normal;
                  }}

                  li {{
                    font-weight: normal;
                    font-size:100%;
                    text-align: left;
                  }}

                  table {{
                    margin: 40px 0px 0px 0px;
                  }}

                  body, title {{
                    background-color: #282a36;
                    font-size: 150%;
                    color: #f8f8f2;
                    color: #f2f2f2;
                    font-family: Source Sans Pro;
                    display: block;
                    font-weight: bold;
                  }}                

                  .column {{
                    height: 100%;
                    text-align: center;
                    align-items: center;
                    justify-content: center;
                    margin: 0px 50px 0px 50px;
                  }}

                  .row {{
                    width: 100%;
                    text-align: center;
                    display: flex;
                    justify-content: center;
                    margin: 0px;
                  }}

                </style>

                <body>
                  <center>
                  <title>Социальный Рейтинг ТМГ</title>
                    
                    <div class=\"row\">
                      <div class=\"column\">
                        <table>
                          <tr> 
                            <th> # </th> <th> Name </th> <th> Description </th> <th> Social Credit </th> 
                          </tr> 

                          {string}

                        </table>
                      </div>
                    </div>

                    <div class=\"row\">
                      <div class=\"column\">
                        <h4>Источник</h4>
                        <ul>
                          <li> Описание — 0 ~ 10 </li>
                          <li> Актёр Запаса — 5 </li>
                          <li> Участие в пьесе — 10 </li>
                          <li> Донос — 0 ~ 5 </li>
                        </ul>
                      </div>
                    </div>

                      
                  </center>
                </body>
              </html>"""

  except Exception as e:
    ret = f"<h1>Ошибка подключения к базе данных! => {e} <=</h1>" 
    print(e)
    db.rollback()
  db.close()
  
  return ret

def parse_files(keyword, issue):
  # For now files are raw bytes carrying image data
  # content should contain marks in text where to place files (![[filename]])
  ret = {'author': "", 'interpreter': "", 'title': "", 'content': "", 'number': "", 'files': []}
  
  candidates = []

  for f in os.listdir("./Base/"):
    try:
      with open(f"./Base/{f}", 'r', encoding='utf-8') as fil:
        contents = str(fil.read())

        if (issue == "Random"):
          link = f"[[00 ({keyword})"
        else:
          link = f"[[00 ({keyword}) {issue}]]"
          
        if (link in contents):
          candidates.append((f, contents)) 
        fil.close()
    except OSError as err:
      print(f"deck FAILED")
  
  try:
    fil, contents = candidates[random.randint(0, len(candidates) - 1)]
  except Exception as e:
    print(e)
    return ret

  # TODO is it possible for files to point not to a book?
  # Getting the name in russian (russian - english)

  try:

    title = re.findall('\[\[00 \(book\) (.*?)\]\]', contents)[0].split(" - ")[0]
    book_file = "00 (book) " + re.findall('\[\[00 \(book\) (.*?)\]\]', contents)[0] + ".md"

    with open(f"./Base/{book_file}", 'r', encoding='utf-8') as bkfil:
      sample = str(bkfil.read())
      try:
        author = re.findall('author \[\[00 \(person\) (.*?)\]\]', sample)[0].split(" - ")[0]
      except Exception as e:
        author = ""

      try:
        interpreter = re.findall('interpreter \[\[00 \(person\) (.*?)\]\]', sample)[0].split(" - ")[0]
      except Exception as e:
        interpreter = ""

      bkfil.close()

  except Exception as e:
    title = str(fil).split(".md")[0]
    author = ""
    interpreter = ""

    #content = contents.split("\n---\n")[1][2:].split("\n\n")[1].split("\n")[0][3:-2]

  content = contents.split("\n---\n")[1][2:].split("\n\n")[1:]
  content = "\n\n".join(content)
  files = re.findall('!\[\[(.*?)\]\]', content)

  ret['author'] = author
  ret['interpreter'] = interpreter
  ret['title'] = title
  ret['number'] = fil.split(".")[0]
  
  if (len(files) > 0):
    ret["content"] = content
     
    # Now check for   
    for f in files:
      try:
        response = send_from_directory("./Files", f, as_attachment=True) 
        response.direct_passthrough = False
        data = response.get_data(as_text=False)
        data = base64.b64encode(data).decode('ascii')
        ret['files'].append(data)
      except FileNotFoundError:
        abort(404)

    return ret

  else:

    ret['content'] = contents.split("\n---\n")[1][2:]
    return ret

@app.route('/poem/')
def poem():
  #issue = request.args.get('issue')
  ret = {'author': "", 'title': "", 'data': ""}
  issue = request.args.get('issue')

  return parse_files("poetry", issue)

@app.route('/poems')
def poems():
  ret = {'poems': []}
  for f in os.listdir("./Base/"):
    if ("00 (poetry)" in f):
      remedy = f[12:-3]
      ret["poems"].append(remedy)
  return ret    




@app.route('/duty/')
def image():
  #issue = request.args.get('issue')
  ret = {'author': "", 'title': "", 'data': ""}
  issue = request.args.get('issue')


  return parse_files("duty", issue)

  candidates = []
  for f in os.listdir("./Base/"):
    #print(str(f))
    try:
      with open(f"./Base/{f}", 'r', encoding='utf-8') as fil:
        contents = str(fil.read())

        if (issue == "Random"):
          link = f"[[00 (duty)"
        else:
          link = f"[[00 (duty) {issue}]]"
          
        if (link in contents):
          candidates.append((f, contents)) 
        fil.close()
    except OSError as err:
      print(f"deck FAILED")
  
  fil, contents = candidates[random.randint(0, len(candidates) - 1)]

  title = re.findall('\[\[00 \(book\) (.*?)\]\]', contents)[0].split(" - ")[0]
  book_file = "00 (book) " + re.findall('\[\[00 \(book\) (.*?)\]\]', contents)[0] + ".md"

  with open(f"./Base/{book_file}", 'r', encoding='utf-8') as bkfil:
    author = str(bkfil.read())
    try:
      author = re.findall('\[\[00 \(person\) (.*?)\]\]', author)[0].split(" - ")[0]
    except Exception as e:
      author = "None"

    bkfil.close()

    content = contents.split("\n---\n")[1][2:].split("\n\n")[1].split("\n")[0][3:-2]

  try:
    response = send_from_directory("./Files", content, as_attachment=True) 
    response.direct_passthrough = False
    data = response.get_data(as_text=False)
    data = base64.b64encode(data).decode('ascii')
  except FileNotFoundError:
    abort(404)
  
  ret = {'saved': saved, 'author': author, 'title': title, 'number': fil.split(".")[0], 'data': data}
  return ret


@app.route('/duties')
def duties():
  ret = {'duties': []}
  for f in os.listdir("./Base/"):
    if ("00 (duty)" in f):
      remedy = f[10:-3]
      ret["duties"].append(remedy)
  return ret    

@app.route('/remedies')
def remedies():
  ret = {'remedies': []}
  for f in os.listdir("./Base/"):
    if ("00 (remedy)" in f):
      remedy = f[12:-3]
      ret["remedies"].append(remedy)
  return ret    

@app.route('/remedy')
def remedy():
  ret = {'files': []}
  issue = request.args.get('issue')

  return parse_files("remedy", issue)

  for f in os.listdir("./Base/"):
    #print(str(f))
    try:
      with open(f"./Base/{f}", 'r', encoding='utf-8') as fil:
        contents = str(fil.read())

        if (issue == "Random"):
          link = f"[[00 (remedy)"
        else:
          link = f"[[00 (remedy) {issue}]]"
          
        if (link in contents):
          title = re.findall('\[\[00 \(book\) (.*?)\]\]', contents)[0].split(" - ")[0]
          book_file = "00 (book) " + re.findall('\[\[00 \(book\) (.*?)\]\]', contents)[0] + ".md"

          with open(f"./Base/{book_file}", 'r', encoding='utf-8') as bkfil:
            author = str(bkfil.read())
            try:
              author = re.findall('\[\[00 \(person\) (.*?)\]\]', author)[0].split(" - ")[0]
            except Exception as e:
              author = "None"

            bkfil.close()

          ret['files'].append({'author': author, 'title': title, 'content': contents.split("\n---\n")[1][2:]})

        fil.close()
    except OSError as err:
      print(f"deck FAILED")

  return ret

@app.route("/")
def home():
    return "<h1>Reload Check 324</h1>"

if __name__ == "__main__":
  app.run(threaded = True, debug = True)
  #app.run(host='127.0.0.1',port=5045)
