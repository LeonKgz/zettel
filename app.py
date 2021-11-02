from flask import Flask
from flask import request

import os
import re
import pymysql.cursors
from dotenv import load_dotenv

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
  
								</style>

								<body>
									<center>
                  <title>Социальный Рейтинг ТМГ</title>
										<table>
											<tr> 
												<th> # </th> <th> Name </th> <th> Description </th> <th> Social Credit </th> 
											</tr> 

											{string}

										</table>
									</center>
								</body>
							</html>"""

  except Exception as e:
    ret = f"<h1>Ошибка подключения к базе данных! => {e} <=</h1>" 
    print(e)
    db.rollback()
  db.close()
  
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
  #app.run(host='127.0.0.1',port=5045)
