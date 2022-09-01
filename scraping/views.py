from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import re
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64

def get_html(url):
    res=requests.get(url)
    return res

def scraper(url):
    items_list=[]
    for i in range(1,4):
        res=get_html(url)
        soup=bs(res.content,"html.parser")
        items=soup.find_all(class_="view view_grid")
        items=items[0].findAll(class_="item")
        new_url=soup.find_all(class_="col-xs-4 text-right btn-next")
        items_list+=[item for item in items]
        url="https://fril.jp/"+new_url[0].find_all("a")[0].get('href')
    return items_list


def details(item):
    return {
        "name": item.find(class_='link_search_title').get('title'),
        "price": int(item.find('p', class_='item-box__item-price').text.replace("￥","").replace(",",""))
    } 

def df_maker(items_list):
    li = []
    
    for item in items_list:
        try:
            li.append(details(item))
        
        except:
            del item
    
    df = pd.DataFrame(li)
    return df

def histgram_creater(df):
    plt.figure()
    quantile_1=df.price.quantile(0.25)
    quantile_3=df.price.quantile(0.75)
    dif=quantile_3-quantile_1
    limit_up=quantile_3+1.5*(dif)
    limit_down=quantile_1-1.5*(dif)
    plt.xlim(limit_down,limit_up)
    plt.hist(df.price,bins=30)
    

def get_image():
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph



def index(request):
    if request.method == "GET":
        return render(
            request,
            "scraping/home.html"
        )
    else:
        title=request.POST["title"]
        url="https://fril.jp/s?query="+title+"&transaction=selling"
        item_list=scraper(url)
        df=df_maker(item_list)
        df_describe=df.describe()
        histgram_creater(df)
        graph = get_image()



        return render(
            request,
            "scraping/home.html",
            {'numbers':df_describe.to_html(),'graph':graph}
            )




