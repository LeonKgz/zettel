#! /usr/bin/python
# vim: set fileencoding=utf-8:
# coding=utf-8

import os
import pickle
import re

PICKLE_CACHE = "cache.pkl"

def main_deprecated():
  # this section of code scans all the files and creats a new dictionary object to pickle at the end
  cache = {}
  for f in os.listdir("./Base/"):
    with open(f"./Base/{f}", 'r', encoding='utf-8') as fil:
      contents = str(fil.read())
      zero_links = re.findall('\[\[00 (.*?)\]\]', contents)
      if zero_links:
        for zl in zero_links:
          
          final_zls = [zl]      
          if " - " and ") " in zl:  
            first = zl.split(") ")[0] + ") "
            seconds = zl.split(") ")[1].split(" - ")
            final_zls += [first + s for s in seconds]
            # if "Death" in zl:
            #   print(final_zls)

          for fzl in final_zls:
            if fzl in cache:
              cache[fzl].append(f"{f}")
            else:
              cache[fzl] = [f"{f}"]
  
  pickle_file = PICKLE_CACHE
  with open(pickle_file, 'wb') as f:
      pickle.dump(cache, f)

def main():
  # this section of code scans all the files and creats a new dictionary object to pickle at the end
  cache = {}
  keywords = {"remedy": "remedies", "duty": "duties", "poetry": "poems"}

  for p in keywords.values():
    cache[p] = []

  for f in os.listdir("./Base/"):
    with open(f"./Base/{f}", 'r', encoding='utf-8') as fil:
      contents = str(fil.read())
      tags = []
      for keyword in keywords.keys():
        matches = re.findall(f'#{keyword}_(.*?)\s+', contents)
        if matches:
          tags += [f"{keyword}_" + t for t in matches]

      if tags:
        for t in tags:
          final_tags = []      
          if t.count("_") >= 1:  
            first = t.split("_")[0]
            seconds = t.split("_")[1:] 
            # e.g. for #remedy_лень_sloth
            # first = "remedy"
            # seconds = ["лень", "sloth"]
            final_tags += [f"({first}) " + s for s in seconds]
            if "_".join(t.split("_")[1:]) not in cache[keywords[first]]:
              cache[keywords[first]].append("_".join(t.split("_")[1:])) 

          for ft in final_tags:
            if ft in cache:
              cache[ft].append(f"{f}")
            else:
              cache[ft] = [f"{f}"]
  
  pickle_file = PICKLE_CACHE
  with open(pickle_file, 'wb') as f:
      pickle.dump(cache, f)
     

if __name__ == "__main__": main()