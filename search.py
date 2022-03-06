from mechanize import Browser as mBrowser
from bs4 import BeautifulSoup as bs
import aiohttp


from sys import argv
from os import environ, system, popen
from json import loads
import asyncio
import re
import pdb
from urllib.parse import quote
from unidecode import unidecode
from pprint import pprint
from typing import Callable, Tuple
from webbrowser import open_new_tab


termux = True if environ.get('PREFIX') == '/data/data/com.termux/files/usr' else False
if not termux:
    from pyppeteer import launch, browser
    root = ''
    def get_value() -> str:
        print("search what?")
        return input()
else:
    launch = None
    open_new_tab = lambda url: system(f'termux-open-url "{url}"')
    root = environ.get('PREFIX')
    def get_value() -> str:
        return loads(popen('termux-dialog -t "search what?"').read())['text']

def form_search(url: str, what: str, form_nr: int, input_name: str, replace_fn: Callable) -> bytes:
    browser = mBrowser()
    browser.set_handle_equiv(True)
    browser.set_handle_redirect(True)
    browser.set_handle_referer(True)
    browser.set_handle_robots(False)
    browser.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36')]
    browser.open(url)
    browser.select_form(nr=form_nr)
    browser[input_name] = what
    response = browser.submit()
    response_text = replace_fn(response.read())
    return response_text

async def stora_search(what: str) -> Tuple[bool, str, bytes]:
    url = 'http://www.stora.de'
    html = form_search(url=f'{url}/main.php',
                what=what,
                form_nr=0,
                input_name='keyword',
                replace_fn = lambda r: (r.replace(b'href=\'includes', b'href=\''+url.encode()+b'/includes')
                                        .replace(b'SRC="includes', b'SRC="'+url.encode()+b'/includes')
                                        .replace(b'href=\'main', b'href=\''+url.encode()+b'/main')
                                        .replace(b'href="main', b'href="'+url.encode()+b'/main')
                                        .replace(b'src=\'img', b'src=\''+url.encode()+b'/img')
                                        .replace(b'url(img', b'url('+url.encode()+b'/img')
                                        .replace(b'action="/', b'action="'+url.encode()+b'/')
                                        .replace(b'href="index', b'href="'+url.encode()+b'/index'))
                       )

    not_found = b'no hits' in html
    with open(f'{root}/tmp/stora.html', 'wb') as fp:
        fp.write(html)
    url = f'file://{root}/tmp/stora.html'
    return not_found, url, html


async def soundflat_search(what: str) -> Tuple[bool, str, bytes]:
    url = 'https://www.soundflat.de'
    html = form_search(url=f'{url}/shop/shop.cfm',
                what=what,
                form_nr=1,
                input_name='suchbegriff',
                replace_fn = lambda r: (r.replace(b'shop.cfm', url.encode()+b'/shop/shop.cfm')
                                        .replace(b"..", url.encode())
                                        .replace(b'src="img', b'src="'+url.encode()+b'/shop/img'))
                )

    not_found = b'keine Produkte gefunden' in html
    with open(f'{root}/tmp/soundflat.html', 'wb') as fp:
        fp.write(html)
    url = f'file://{root}/tmp/soundflat.html'
    return not_found, url, html


def multibox_search_get(ptn: str) -> Callable[[str, str, str], None]:
    def run(artist:str = '', title:str = '', label:str = '') -> None:
        open_new_tab(ptn.format(artist=quote(artist), title=quote(artist)))
    return run


def onebox_search_get_unenc(ptn: str) -> Callable[[str], None]:
    def run(what: str) -> None:
        open_new_tab(ptn.format(what=what.replace(' ', '+')))
    return run

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    'sec-fetch-mode': 'navigate',
}


def contains(s:str) -> Callable[[str], bool]:
    r = re.compile(s)
    def match(t:str) -> bool:
        return t and r.search(t)
    return match


def has_tag_with(attrs:dict) -> Callable[[str, bool], bool]:
    def find(html: str, debug=False) -> bool:
        if debug:
            print('html contains the response html, attrs the attribute searched')
            pdb.set_trace()
        return bs(html,'lxml').find(attrs = attrs) is not None
    return find


def oneOf(fnList: list) -> Callable[[str, bool], bool]:
    def find(html: str, debug:bool=False) -> bool:
        if debug:
            pdb.set_trace()
        for fn in fnList:
            if fn(html, debug):
                return True
        return False
    return find


def contains_text(text:str) -> bool:
    def find(html:str, debug=False) -> bool:
        if debug:
            pdb.set_trace()
        return text in html
    return find


def has_no_tag_with(attrs:dict) -> Callable[[str], bool]:
    def find(html:str, debug=False) -> bool:
        if debug:
            print('html contains the response html, attrs the attribute searched')
            pdb.set_trace()
        return bs(html,'lxml').find(attrs = attrs) is None
    return find


def quoted_url(ptn:str) -> Callable[[str], str]:
    def url(what:str) -> str:
        return ptn.format(what=quote(what))
    return url

def dashed_url(ptn:str) -> Callable[[str], str]:
    def url(what:str) -> str:
        return ptn.format(what=unidecode(what).replace(' ', '-'))
    return url


def url_no_accents(ptn:str) -> Callable[[str], str]:
    def url(what:str):
        return ptn.format(what=unidecode(what).replace(' ', '+'))
    return url


def to_do() -> Callable[[str], bool]:
    async def find(doc:str) -> bool:
        return False
    return find


def url(ptn: str) -> Callable[[str], str]:
    def url(what: str):
        return ptn.format(what=what.replace(' ', '+'))
    return url

# To add/test shops, add the shop under test in this dictionary and set test to True
test = False
test_shops = {}
rendered_test_shops = {}

shops = {
    # '': {'url': quoted_url(''), 'not_found': to_do()},
    '25-music.de': {
        'url': quoted_url('https://25-music.de/?s={what}'),
        'not_found': has_no_tag_with({'id': contains('titelbox')})},
    'a-musik': {
        'url': quoted_url('https://www.a-musik.com/mailorder.html?for={what}'),
        'not_found': contains_text('No products have been found.')},
    'amazon.de': {
        'url': quoted_url('https://www.amazon.de/s?k={what}'),
        'not_found': has_tag_with({'class': contains("messaging-messages-no-results")})},
    'bandcamp.com': {
        'url': quoted_url('https://bandcamp.com/search?q={what}'),
        'not_found': has_no_tag_with({'class': contains('result-items')})},
    'cede.de': {
        'url': quoted_url('https://www.cede.de/de/?such_begriff={what}'),
        'not_found': contains_text('Bitte versuche es mit einem anderen Suchbegriff.')},
    'cheaptrashrecords.de': {
        'url': quoted_url('https://www.cheaptrashrecords.de/browse?keyword={what}'),
        'not_found': contains_text('Keine Artikel zur Suchanfrage gefunden!')},
    'coretexrecords.net': {
        'url': quoted_url('https://coretexrecords.com/navi.php?k=&qs={what}'),
        'not_found': has_tag_with({'class': contains("alert-info")})},
    'corticalart.com': {
        'url': quoted_url('https://www.corticalart.com/?post_type=product&s={what}'),
        'not_found': has_tag_with({'class': 'empty-category-block'})},
    'decks.de': {
        'url': quoted_url('https://www.decks.de/decks/workfloor/search_db.php?such={what}'),
        'not_found': contains_text('0 search results')},
    'discogs.com': {
        'url': quoted_url('https://www.discogs.com/search/?type=all&q={what}'), 'not_found': contains_text(
            'We couldn\'t find anything in the Discogs database matching your search criteria.')},
    'dodax.de': {
        'url': quoted_url('https://www.dodax.de/de-de/search/?s={what}'),
        'not_found': contains_text('leider keine passenden Ergebnisse')},
    'dodobeach.de': {
        'url': quoted_url(
            'https://www.dodobeach.de/liste.php?search={what}&button.x=0&button.y=0&p=0&genre=0&label=0&as=0&ft=on'),
        'not_found': contains_text('Die Suche war leider nicht erfolgreich')}, 'dussmann': {
        'url': quoted_url(
            'https://kulturkaufhaus.buchhandlung.de/shop/quickSearch?offset=0&product=4765&searchString={what}'),
        'not_found': has_no_tag_with({'class': contains('module-searchresult-list')})},
    'dronerecords.de': {
        'url': quoted_url('https://www.dronerecords.de/search.html?text={what}'),
        'not_found': contains_text('Unfortunately, there are no matches')},
    'flight13.com': {
        'url': quoted_url('https://www.flight13.com/suchen?q={what}'),
        'not_found': contains_text('nichts gefunden…')},
    'funrecords.de': {
        'url': quoted_url('https://www.funrecords.de/en/catalogue/?search={what}'),
        'not_found': contains_text('No matching items found!')},
    'grooveattackrs': {
        'url': quoted_url('http://grooveattackrs.bigcartel.com/products?search={what}'),
        'not_found': contains_text('No products found.')},
    'grooves.land': {
        'url': quoted_url('https://www.grooves.land/advanced_search_result.php?keywords={what}'),
        'not_found': oneOf(
            [contains_text('0 Results 0 Categories'), contains_text('0 Treffer in 0 Bereichen')])},
    'hardwax.com': {
        'url': quoted_url('https://hardwax.com/?search={what}'),
        'not_found': contains_text('Sorry, no records found.')},
    'hotstuff.se': {
        'url': quoted_url('https://hotstuff.se/index.cfm?x=product&pg=1&prSts=2&zpgId=0&searchPhrase={what}'),
        'not_found': contains_text('Inga varor kunde hittas')},
    'indiedetective.de': {'url': quoted_url(
        'https://www.indietective.de/search.html?sorting=artist&offset=0&desc=false&showPics=true&showCD=true&showVinyl=true&showUsed=true&showSold=false&query={what}'),
        'not_found': contains_text('0 Treffer.')},
    'jpc.de': {
        'url': quoted_url('https://www.jpc.de/s/{what}'), 'not_found': contains_text('Keine Ergebnisse')},
    'kompakt.fm': {
        'url': quoted_url('https://kompakt.fm/releases?find={what}'),
        'not_found': contains_text('Sorry, no Releases')},
    'majorlabel.shop': {
        'url': quoted_url('https://majorlabel.shop/advanced_search_result.php?keywords={what}'),
        'not_found': contains_text('Die Suche ergab keine genauen Treffer')},
    'mandai.be': {
        'url': quoted_url('http://mandai.be/mailorder.php?type=All&search={what}'),
        'not_found': contains_text('No results has been found.')},
    'mediamarkt.de': {
        'url': quoted_url(
            'https://www.mediamarkt.de/de/search.html?filter=category%3ACAT_DE_MM_485%2F%2FCAT_DE_MM_503&query={what}'),
        'not_found': contains_text('Leider haben wir für Ihre Suche')},
    'medimpos.de': {
        'url': quoted_url('https://www.medimops.de/musik-C0255882/?searchparam={what}'),
        'not_found': has_no_tag_with({'class': "product__grid"})},
    'outofprint.be': {
        'url': quoted_url('http://www.outofprint.be/search/{what}'),
        'not_found': has_no_tag_with({'class': 'mosaic-block mosaic-item'})
    },
    'oye-records.com': {
        'url': quoted_url('https://oye-records.com/search?q={what}'),
        'not_found': contains_text(' 0 results for ')},
    'parallel-schalplatten.de': {
        'url': quoted_url(
            'https://www.parallel-schallplatten.de/cartPhp/search.php?searchFields=1&searchFormat=all&suchen=suchen%21&parallel_id=&searchPhrase={what}'),
        'not_found': contains_text('konnte nicht gefunden werden.')},
    # 'perkoro.com': {'url': dashed_url('https://www.perkoro.com/q/band/{what}.php'), 'not_found': contains_text('Sorry, no articles found.')},
    'poponaut.de': {
        'url': quoted_url('http://www.poponaut.de/advanced_search_result.php?x=0&y=0&language=en&keywords={what}'),
        'not_found': contains_text('There is no product that matches the search criteria.')},
    'praxis-records.net': {'url': quoted_url('https://praxis-records.net/shop/search?sSearch={what}'),
                           'not_found': contains_text('No products matching your search')},
    'recordsale.de': {
        'url': quoted_url('https://recordsale.de/en/search?s={what}'),
        'not_found': has_tag_with({'class': contains("l-releaseList-empty")})},
    'rockers.de': {
        'url': quoted_url('https://www.rockers.de/search?search={what}'),
        'not_found': has_tag_with({'class': "error"})},
    'saturn.de': {
        'url': quoted_url('https://www.saturn.de/de/search.html?query={what}'),
        'not_found': contains_text('Leider haben wir für Ihre Suche')},
    'shinybeast.nl': {
        'url': quoted_url('https://www.shinybeast.nl/catalog/search.php?q={what}'),
        'not_found': contains_text('No records found.')},
    'soundflat.de': {
        'url': None, 'search': soundflat_search, 'not_found': None},
    'oundeffect-records.gr': {
        'url': url_no_accents('https://www.soundeffect-records.gr/search?q={what}'),
        'not_found': has_tag_with({'class': 'no-result'})
    },
    'soundohm.com': {
        'url': quoted_url('https://www.soundohm.com/search?query={what}'),
        'not_found': contains_text('No artists found for your query')},
    'soundstation.dk': {
        'url': quoted_url('https://soundstation.dk/shop/?search={what}'),
        'not_found': has_no_tag_with({'id': "clerk-product"})},
    'soundwayrecords.com': {
        'url': quoted_url('https://soundwayrecords.com/search/query?q={what}'),
        'not_found': contains_text('No Results')},
    'stora.de': {
        'url': None, 'search': stora_search, 'not_found': None},
    'sulatron.com': {
        'url': quoted_url('https://www.sulatron.com/xoshop/store-search-result.php?language=de&keywords={what}'),
        'not_found': contains_text('konnte nicht gefunden werden.')},
    'tapeterecords.com': {
        'url': quoted_url('https://shop.tapeterecords.com/catalogsearch/result/?q={what}'),
        'not_found': contains_text('Your search returns no results.')},
    'tochnit-aleph.com': {
        'url': quoted_url('http://www.tochnit-aleph.com/catalog/advanced_search_result.php?keywords={what}'),
        'not_found': contains_text('There is no product that matches the search criteria.')},
    'unrock.de': {
        'url': quoted_url('http://www.unrock.de/?post_type=product&s={what}'),
        'not_found': contains_text('No products were found matching your selection.')},
    'x-mist.de': {
        'url': quoted_url('https://www.x-mist.de/index.php?STEPOFFSET=0&MENUECALL=1&sel=SEARCH&SEARCHSTRING={what}'),
        'not_found': oneOf([contains_text('sorry, there are no products available for your selection'), contains_text('No search performed')])},
}

rendered_shops = {
    'anost.net': {
        'url': quoted_url('https://www.anost.net/search#term={what}'),
        'not_found': contains_text('Nothing matches the search query')},
    'bisaufsmesser.com': {
        'url': url_no_accents('https://bisaufsmesser.com/pages/search-results-page?q={what}'),
        'not_found': contains_text("didn't match any results.")},
    'google.com': {
        'url': quoted_url('https://www.google.com/search?q={what}&source=lnms&tbm=shop&sa=X&biw=1440&bih=307'),
        'not_found': has_no_tag_with({'class': "sh-pr__product-results"})},
    'greenhell.de': {
        'url': quoted_url('https://greenhell.de/navi.php?qs={what}'),
        'not_found': has_tag_with({'class': 'alert'})},
    'hhv.de': {
        'url': quoted_url('https://www.hhv.de/shop/en/all-items/p:08QLU0?&term={what}'),
        'not_found':has_tag_with({'class': 'no_items'})},
    'idealo.de': {
        'url': quoted_url('https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q={what}'),
        'not_found': contains_text('konnten wir leider nicht finden'), 'headless': False},
    'vinyl.internet4000': {
        'url': quoted_url('https://vinyl.internet4000.com/#gsc.tab=0&gsc.q={what}&gsc.sort=&gsc.ref=more%3Aeurope'),
        'not_found': contains_text('No Results')
    },
}


async def fetch(name: str, shop: dict, what: str, debug:bool=False) -> Tuple[str, Tuple[bool, str]]:
    if shop.get('url'):
        url = shop['url'](what)
        if debug:
            print(url)
            pdb.set_trace()
        async with aiohttp.ClientSession() as asession:
            try:
                async with asession.get(url, headers=headers) as resp:
                    try:
                        html = await resp.text()
                        not_found = shop['not_found'](html, debug)
                    except:
                        not_found = False
            except aiohttp.ClientConnectorCertificateError:
                async with asession.get(url, headers=headers, verify_ssl=False) as resp:
                    try:
                        html = await resp.text()
                        not_found = shop['not_found'](html, debug)
                    except:
                        not_found = False
        if debug:
            print('resp contains the get response')
            pdb.set_trace()
    else:
        search = shop['search']
        if not asyncio.iscoroutinefunction(search):
            search = asyncio.coroutine(search)
        not_found, url, html = await search(what)

    if not not_found:
        open_new_tab(url)

    return name, (not_found, url)

async def render(name: str, browser: browser.Browser, shop: dict, what: str, debug:bool=False)-> Tuple[str, Tuple[bool, str]]:
    page = await browser.newPage()
    url = shop['url'](what)
    await page.goto(url)
    try:
        if debug:
            print('page contains the page')
            pdb.set_trace()
        await page.waitFor(1000)
        html = await page.content()
        not_found = shop['not_found'](html, debug)
    except:
        not_found = False

    if not not_found:
        open_new_tab(url)

    return (name, (not_found, url))

async def found_in_shops(what:str, debug: bool=False):
    global shops, rendered_shops
    tasks = []

    if debug:
        shops = test_shops
        rendered_shops = rendered_test_shops

    for name, shop in shops.items():
        print (name)
        tasks.append(fetch(name, shop, what, debug))

    if not termux and rendered_shops:
        headless_browser = await launch(headless=True)
        for name, shop in rendered_shops.items():
            browser = headless_browser if not test and shop.get('headless', True) else await launch(headless=False)
            print (name)
            tasks.append(render(name, browser, shop, what, debug))
    htmls = await asyncio.gather(*tasks, return_exceptions=True)
    return htmls


if __name__ == '__main__':
    what = ' '.join(argv[1:])
    if not what:
        what = get_value()
    if what:
        loop = asyncio.get_event_loop()
        x = loop.run_until_complete(found_in_shops(what, debug=test))
        if test:
            pprint(x)


