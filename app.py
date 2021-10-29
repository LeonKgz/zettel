from flask import Flask
from flask import request

import os
import re

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/remedy')
def hello():
  ret = {'files': []}
  issue = request.args.get('issue')
  for f in os.listdir("./Base/"):
    #print(str(f))
    try:
      with open(f"./Base/{f}", 'r', encoding='utf-8') as fil:
        contents = str(fil.read())
        link = f"[[00 (remedy) {issue}]]"
        if (link in contents):
          title = re.findall('\[\[00 \(book\) (.*?)\]\]', contents)[0].split(" - ")[0]
          book_file = "00 (book) " + re.findall('\[\[00 \(book\) (.*?)\]\]', contents)[0] + ".md"

          with open(f"./Base/{book_file}", 'r', encoding='utf-8') as bkfil:
            author = str(bkfil.read())
            author = re.findall('\[\[00 \(person\) (.*?)\]\]', author)[0].split(" - ")[0]
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
  app.run()
  #app.run(host='127.0.0.1',port=5044)
