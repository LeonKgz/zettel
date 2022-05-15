#! /usr/bin/python
# vim: set fileencoding=utf-8:
# coding=utf-8

import os
import pickle
import re

PICKLE_CACHE = "cache.pkl"

def main():
  # this section of code scans all the files and creats a new dictionary object to pickle at the end
  cache = {}
  for f in os.listdir("./Base/"):
    with open(f"./Base/{f}", 'r', encoding='utf-8') as fil:
      contents = str(fil.read())
      zero_links = re.findall('\[\[00(.*?)\]\]', contents)
      if zero_links:
        for zl in zero_links:
          if zl in cache:
            cache[zl].append(f"{f}")
          else:
            cache[zl] = [f"{f}"]
  
  pickle_file = PICKLE_CACHE
  with open(pickle_file, 'wb') as f:
      pickle.dump(cache, f)

if __name__ == "__main__": main()