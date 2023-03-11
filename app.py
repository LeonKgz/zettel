from flask import Flask,send_from_directory, send_file
from flask import request
from flask import jsonify

import os
import re
import pymysql.cursors
from dotenv import load_dotenv
import base64
import random
import requests
from cache import *
import pickle

import gh_md_to_html

load_dotenv()

HOST = str(os.getenv('DB_HOST'))
USER = str(os.getenv('DB_USER'))
PASSWORD = str(os.getenv('DB_PASSWORD'))
DB = str(os.getenv('DB_DATABASE'))

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

def save_pickle(dictionary, filename):
  outfile = open(filename, 'wb')
  pickle.dump(dictionary, outfile)
  outfile.close()

def load_pickle(filename):
  dictionary = {}
  if os.path.exists(filename):
    infile = open(filename,'rb')
    dictionary = pickle.load(infile)      
    infile.close()
  return dictionary

def get_db_cursor():
  db = pymysql.connect(host=HOST,
                       user=USER,
                       password=PASSWORD,
                       db=DB,
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
  return db, db.cursor()

# another page for entering the file name so that the y dont have to tinker with the url

import re

def markdown_to_html_via_github_api(markdown):

  # """Converts markdown to html, using the github api and nothing else."""
  headers = {"Content-Type": "text/plain", "charset": "utf-8"}
  ret = str(requests.post("https://api.github.com/markdown/raw", headers=headers, data=markdown.encode("utf-8")).content, encoding="utf-8")

  # ret = markdown
  

  ret = re.sub(r'\[\[(.*?)\]\]', r'<a href="view?file=\1.md">[[\1]]</a>', ret)
  ret = ret.replace(".jpg.md", ".jpg")

  # with open("./logs.txt", 'w') as f:
  #   f.write(ret)

  # ret = re.sub(r'\[\[([a-z]+)\]\]', r'\<a href=\"view?file=\1\"\>\1\<\/a\>', ret)
  # ret = re.sub(r'Zero', r'Nol', ret)
  return ret

from flask import send_file
def convert_to_html(filename):
  
  folder = "Base"

  if ".jpg" in filename:
    folder = "Files"
    return send_file(f"./{folder}/{filename}", mimetype="image/gif")
    with open(f"./{folder}/{filename}", 'r', encoding='utf-8') as fil:
      contents = str(fil.read())
      return contents
  
  with open(f"./{folder}/{filename}", 'r', encoding='utf-8') as fil:
    contents = str(fil.read())
    # html_as_a_string = gh_md_to_html.core_converter.markdown(contents)
  # html_as_a_string = gh_md_to_html.main(f"./Base/{filename}")
    html_as_a_string = markdown_to_html_via_github_api(contents)
    style = """ 
      body {
        color: black;
      }"""

    ret = f"""
    <html lang='ru'>
      <head>
        <a href="/prompt">Go Back</a>
      </head>
      <body>
        <style>{style}</style>
        {html_as_a_string}
      </body>
    </html>
    """
    return ret

from flask import send_file

@app.route('/waifu_file')
def get_waifu_file():
    ws = os.listdir("./waifus/")
    ret = random.choice(ws)
    return {"file": ret}

@app.route('/waifu_jpg')
def get_waifu_image():
    filename = 'waifu.jpg'
    filename = "./waifus/" + str(request.args.get('file'))
    return send_file(filename, mimetype='image/gif')

@app.route('/prompt')
def prompt():

  files = "</li>\n<li>".join([f"<a href=\"view?file={f}\">{f}</a>" for f in os.listdir("./Base/") if ("00" not in f and "Туманов" not in f)])
  script = """
    function redirect() {
      var filename=document.getElementById('test').value
      window.location.href="/view?file=" + filename
    }"""

  ret = f"""
  <html lang='ru'>
  <script>{script}</script>
  <input id="test" type=text><button onclick="redirect()">Submit</button>
  <li>{files}</li>    
  </html>"""

  return ret

@app.route('/flag')
def flag():
  code = str(request.args.get('code'))
  flags = load_pickle("flags.pkl")
  if code in flags:
    return {"url": flags[code]}
  else:
    return {"url": flags["random"]}

@app.route('/view')
def view():
  file = str(request.args.get('file'))
  # only accept full file name or a keyword that might be in multiple file names
  # only open the ones on Base
  if ("/" in file or ".." in file):
    return "Nice try"

  return convert_to_html(file)

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
                          <li> Недельная активность на сервере — 1 </li>
                          <li> Описание — 0 ~ 10 </li>
                          <li> Актёр Запаса — 5 </li>
                          <li> Участие в пьесе — 10 </li>
                          <li> Участие в репетиции — 1 ~ 5 </li>
                          <li> Подключение телеграма — 5 </li>
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

def parse_files(keyword, issue, book=None, discord=False):
  # For now files are raw bytes carrying image data
  # content should contain marks in text where to place files (![[filename]])
  ret = {'author': "", 'interpreter': "", 'title': "", 'content': "", 'number': "", 'files': [], 'links': []}
  
  candidates = []

  pickle_file = PICKLE_CACHE
  with open(pickle_file, 'rb') as f:
    cache = pickle.load(f)
  # return {f"({keyword}) {issue}": cache}
  try:
    if issue == "Random":
      for zl, files in cache.items():
        if f"({keyword})" in zl:
          candidates += files
    elif book:
      candidates = [x for x in cache[f"(book) {book}"] if x in cache[f"({keyword}) {issue}"]]
    else:
      candidates = cache[f"({keyword}) {issue}"]

  except Exception as e:
    return ret

  # for f in os.listdir("./Base/"):
  #   try:
  #     with open(f"./Base/{f}", 'r', encoding='utf-8') as fil:
  #       contents = str(fil.read())

  #       if (issue == "Random"):
  #         link = f"[[00 ({keyword})"
  #       else:
  #         link = f"[[00 ({keyword}) {issue}]]"

  #       if (discord and "[[00 (discord) Long]]" in contents):
  #         continue

  #       if book and f"[[00 (book) {book}" in contents and link in contents:
  #           candidates.append((f, contents))
  #       elif (not book and link in contents):
  #           candidates.append((f, contents)) 
  #       fil.close()
  #   except OSError as err:
  #     print(f"deck FAILED")
  
  fil = candidates[random.randint(0, len(candidates) - 1)]
  with open(f"./Base/{fil}", 'r', encoding='utf-8') as f:
    contents = str(f.read())
  # try:
  #   fil, contents = candidates[random.randint(0, len(candidates) - 1)]
  # except Exception as e:
  #   print(e)
  #   return ret

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

    try:
      author = re.findall('author \[\[00 \(person\) (.*?)\]\]', contents)[0].split(" - ")[0]
    except Exception as e:
      author = ""

    try:
      interpreter = re.findall('interpreter \[\[00 \(person\) (.*?)\]\]', contents)[0].split(" - ")[0]
    except Exception as e:
      interpreter = ""

    #content = contents.split("\n---\n")[1][2:].split("\n\n")[1].split("\n")[0][3:-2]

  content = contents.split("\n---\n")[1][2:].split("\n\n")[1:]
  links_area = contents.split("\n---\n")[3]

  ret['links'] = [s.strip() for s in links_area.split("\n- ")[1:]]


  content = "\n\n".join(content)
  files = re.findall('!\[\[(.*?)\]\]', content)

  ret['author'] = author
  ret['interpreter'] = interpreter
  ret['title'] = title
  if (len(fil.split(".md")[0].split(".")) > 1):
    ret['number'] = fil.split(".md")[0].split(".")[0]
  
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
  ret = {'author': "", 'title': "", 'data': ""}
  issue = request.args.get('issue')
  return parse_files("poetry", issue)

@app.route('/poems')
def poems():
  ret = {'poems': []}

  pickle_file = PICKLE_CACHE
  with open(pickle_file, 'rb') as f:
    cache = pickle.load(f)
  ret["poems"] = cache["poems"]

  return ret    
  # for f in os.listdir("./Base/"):
  #   if ("00 (poetry)" in f):
  #     remedy = f[12:-3]
  #     ret["poems"].append(remedy)

@app.route('/duty/')
def image():
  #issue = request.args.get('issue')
  ret = {'author': "", 'title': "", 'data': ""}
  issue = request.args.get('issue')
  return parse_files("duty", issue)

@app.route('/duties')
def duties():
  ret = {'duties': []}

  pickle_file = PICKLE_CACHE
  with open(pickle_file, 'rb') as f:
    cache = pickle.load(f)
  ret["duties"] = cache["duties"]

  return ret
  # for f in os.listdir("./Base/"):
  #   if ("00 (duty)" in f):
  #     remedy = f[10:-3]
  #     ret["duties"].append(remedy)
  # return ret    

@app.route('/remedies')
def remedies():
  ret = {'remedies': {"ru": [], "en": []}}

  pickle_file = PICKLE_CACHE
  with open(pickle_file, 'rb') as f:
    cache = pickle.load(f)
  
  pairs = [r.split("_") for r in cache["remedies"]]
  for p in pairs:
    if len(p) == 1:
      # ret['remedies']['ru'].append(p[0])
      ret['remedies']['en'].append(p[0])
    else:
      ret['remedies']['ru'].append(p[0])
      ret['remedies']['en'].append(p[1])

  return ret    

  # for f in os.listdir("./Base/"):
  #   if ("00 (remedy)" in f):
  #     versions = f.split("00 (remedy)")[1].split(".md")[0].split(" - ")
  #     ru = versions[0].strip()
  #     en = versions[1].strip()
  #     # remedy = f[12:-3]
  #     # ret["remedies"]["ru"].append(remedy)
  #     ret["remedies"]["ru"].append(ru)
  #     ret["remedies"]["en"].append(en)
  # return ret    

@app.route('/remedy')
def remedy():
  ret = {'files': []}
  issue = request.args.get('issue')
  return parse_files("remedy", issue)

@app.route('/prayer')
def prayer():
  ret = {'verses': []}
  seen = []

  remedies = []
  # issues = request.args.get('issue')
  for f in os.listdir("./Base/"):
    if ("00 (remedy)" in f):

      # pick russian version since both are in cache
      # remedy = f.split("00 (remedy)")[1].split(".md")[0].split(" - ")[0].strip()
      remedy = f.split("00 (remedy)")[1].split(".md")[0].strip()
      if remedy == "Favourites" or remedy == "Test":
        continue
      remedies.append(remedy)
  curr = None
  for r in remedies:
    while (not curr or check_string in seen):
      rus = r.split(" - ")[0]
      curr = parse_files("remedy", rus, book="Наедине с собой - Meditations", discord=True)
      check_string = curr["title"] + curr["title"] + curr["number"]
      print(r, check_string)

    curr["remedy"] = r  
    ret["verses"].append(curr)
    seen.append(check_string)

  return ret

@app.route("/")
def home():
    return "<h1>Reload Check 324</h1>"


pickle_file = PICKLE_CACHE
with open(pickle_file, 'rb') as f:
  cache = pickle.load(f)
  print("Work" in cache)

#if __name__ == "__main__":
#  app.run(threaded = True, debug = True)
