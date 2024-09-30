import logging
import httpx
import json
import cssutils
from lxml import html as lx
from pprint import pprint
from icecream import ic
from fasthtml.common import *
from selenium import webdriver
from bs4 import BeautifulSoup, Stylesheet




app,rt = fast_app(hdrs=[HighlightJS()])


cssutils.log.setLevel(logging.CRITICAL)

# set options to be headless, ..
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')


def toJSON(text, path=False, url=False):
    dct = {
        "rules":{
        }
    }
    if path:
        # tf = open(text, "rb").read()
        # text = tf
        sheet = cssutils.parseFile(text)
    elif url:
        sheet = cssutils.parseUrl(text)
    else:
        sheet = cssutils.parseString(text, validate=False)
    # print(sheet)
    for rule in sheet:
        # print(rule)
        try:
            selector = rule.selectorText
            styles = rule.style.cssText.split(";\n")
            properties = {}
            for s in styles:
                _s = s.split(":")
                if len(_s) != 1:
                    prop_name = _s[0]
                    prop_attr = _s[1]
                    if len(_s)>2:
                        prop_attr = ":".join(_s[1:])
                    properties[prop_name]=prop_attr.strip()
            dct["rules"][selector] = {"attr":properties}
        except Exception as E:
            try:
                media = rule.media.mediaText
                mrules = rule.cssRules
                dct["rules"]["@media "+media] ={"rules":{}}
                for mrule in mrules:
                    selector = mrule.selectorText
                    styles = mrule.style.cssText.split(";\n")
                    properties = {} 
                    for s in styles:
                        _s = s.split(":")
                        prop_name = _s[0]
                        prop_attr = _s[1]
                        if len(_s)>2:
                            prop_attr = ":".join(_s[1:])
                        properties[prop_name]=prop_attr.strip()
                    dct["rules"]["@media "+media]["rules"].update({
                        selector:{"attr":properties}
                    })
            except:
                pass
    return dct


def toCSS(css):
    if not isinstance(css, dict):
        raise TypeError("Invalid type error. Provide a dict/json serialized css")
    css_result = ""
    css_block = "{} {}\n{}{}\n"
    for rule, attrs in css["rules"].items():
        attrs_result = ""
        if attrs.get("attr", None):
            for prop, attr in attrs["attr"].items():
                attrs_block = "{}:{};\n"
                attrs_result+=attrs_block.format(prop, attr.encode("ascii", "ignore"))
            css_result+=css_block.format(rule, "{", attrs_result, "}")
        elif attrs.get("rules", None):
            media_result = ""
            media_block = "{} {}\n{}{}\n"
            for mrule, mattrs in attrs["rules"].items():
                mattrs_result = ""
                for prop, attr in mattrs["attr"].items():
                    attrs_block = "{}:{};\n"
                    mattrs_result+=attrs_block.format(prop, attr.encode("ascii", "ignore"))
                media_result+=css_block.format(mrule, "{", mattrs_result, "}")
            media_block.format(rule, "{", media_result, "}")
            css_result+=media_block
    return css_result


@rt("/scrape/")
def post(url:str):
    #------------- FOR DISPLAYING SOURCE CODE OF THE WEBPAGE -------------#
    css = []
    # open it, go to a website, and get results
    wd = webdriver.Chrome(options=options)

    # For making request to get the URL
    wd.get(url)
    html = wd.page_source
    soup = BeautifulSoup(html, "html5lib")
    # Find all link tags that link to stylesheets/
    stylesheets = soup.find_all('link', rel='stylesheet')

    # Iterate over link tags and get the href attribute
    for link in stylesheets:
        ic(link)
        res = httpx.get(url+"/"+link.get('href'))
        css.append(res.text)
    ic(toJSON(css[0]))
    return Code(Pre(toCSS(toJSON(css[0])))) if css else ''


@rt("/")
def get():
    return Main(
        Title("Website Scraper"),
        Form(
            Group(Input(style="width: auto", id="url", placeholder="Enter URL..."), Div("Add", role="button", hx_post='/scrape/scrape/', target_id="ft"))
        ),
        Div(style="max-width: 100vw; margin: auto;", id="ft"),
        id="page-content"
    )
