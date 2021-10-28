from flask import Flask
from flask import request

import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/remedy')
def hello():
  ret = {'files': []}
  issue = request.args.get('issue')
  for f in os.listdir("./Base/"):
    print(str(f))
    try:
      with open(f"./Base/{f}", 'r', encoding='utf-8') as fil:
        contents = str(fil.read())
        link = f"[[00 (remedy) {issue}]]"
        if (link in contents):
          ret['files'].append(contents.split("\n---\n")[1][2:])

        fil.close()
    except OSError as err:
      print(f"deck FAILED")

  return ret

@app.route("/")
def home():
    return "<h1>Nginx & Gunicorn & Albanec69</h1>"

if __name__ == "__main__":
  #app.run(host='127.0.0.9',port=4455)
  app.run()
  
