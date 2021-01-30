import socks
import socket
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from bs4.element import Comment
from urllib.request import urlopen

socks.set_default_proxy(socks.SOCKS5, "localhost", 9150)
socket.socket = socks.socksocket

import yake
kw_extractor = yake.KeywordExtractor()
language = "en"
max_ngram_size = 2
deduplication_thresold = 0.9
deduplication_algo = 'seqm'
windowSize = 1
numOfKeywords = 20

def getaddrinfo(*args):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]

socket.getaddrinfo = getaddrinfo

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]','script','a']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

html = urlopen('http://jncyepk6zbnosf4p.onion/onions.html').read()
soup = BeautifulSoup(html, "html.parser")
pre_tags = soup.findAll('pre',text=True)


# below code is to extract the urls from the link
onions = []
for i, pre_tag in enumerate(pre_tags): 
	try:
		if i!=0:
			text = (pre_tag.text)
			onion_unfiltered = (text.split("\u2003\u2003\u2003\u2003"))
			if onion_unfiltered[1].endswith('onion') and onion_unfiltered[3] == '200':
				onions.append(onion_unfiltered[1])
	except Exception as E:
		pass


output = {}
custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)

# function to extract key words from the onion link
def tag(onion):
	try:
		# extract the HTML
		html = urlopen('http://'+onion).read()
		# get the text from the HTML
		text = text_from_html(html)
		# extract keywords from the text
		keywords = custom_kw_extractor.extract_keywords(text)
		# add keywords to the output
		for kw in keywords:
			if onion not in output:
				output[onion] = [kw[0]]
			else: 
				output[onion].append(kw[0])
	except Exception as E:
		pass

# making concurrency
processes = []
# assigning 5 workers
with ThreadPoolExecutor(max_workers=5) as executor:
	# creating threads for the first 5 onions
	for onion in onions[:5]:
        	processes.append(executor.submit(tag, onion))

for task in as_completed(processes):
	task.result()

# prints the url & its resp. keywords
print(output)
