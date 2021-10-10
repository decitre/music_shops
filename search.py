from sys import argv
from mechanize import Browser as mBrowser
from os import environ, system, popen
from json import loads
from bs4 import BeautifulSoup as bs
import asyncio, aiohttp
import re
import pdb
from urllib.parse import quote
from unidecode import unidecode
from pprint import pprint
from typing import Callable, Tuple
test = False

termux = True if environ.get('PREFIX') == '/data/data/com.termux/files/usr' else False
if not termux:
    from pyppeteer import launch, browser
    from webbrowser import open_new_tab
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


shops = {
     #'': {'url': quoted_url(''), 'not_found': to_do()},
     '25-music.de': {'url': quoted_url('https://25-music.de/?s={what}'), 'not_found': has_no_tag_with({'id': contains('titelbox')})},
      'a-musik': {'url': quoted_url('https://www.a-musik.com/mailorder.html?for={what}'),'not_found':contains_text('No products have been found.') },
     'alibris.co.uk': {'url': quoted_url('https://www.alibris.co.uk/musicsearch?keyword={what}'), 'not_found':contains_text('(0 matching music items)')},
     'anost.net': {'url': quoted_url('https://www.anost.net/search?query={what}'), 'not_found':contains_text('Nothing matches the search query')},
     'amazon.de': {'url': quoted_url('https://www.amazon.de/s?k={what}'), 'not_found':has_tag_with({'class': contains("messaging-messages-no-results")})},
     'bandcamp.com': {'url': quoted_url('https://bandcamp.com/search?q={what}'), 'not_found':has_no_tag_with({'class': contains('result-items')})},
     'bisaufsmesser.com': {'url': url_no_accents('https://www.bisaufsmesser.com/store/shopware.php/sViewport,search/sSearch,{what}'), 'not_found':contains_text('Unfortunately no items could be found for')},
     'cede.ch': {'url': quoted_url('https://www.cede.ch/de/?such_begriff={what}'), 'not_found':contains_text('Bitte versuche es mit einem anderen Suchbegriff.')},
     'cheaptrashrecords.de': {'url': quoted_url('https://www.cheaptrashrecords.de/browse?keyword={what}'), 'not_found': contains_text('Keine Artikel zur Suchanfrage gefunden!')},
     'coretexrecords.net': {'url': quoted_url('https://coretexrecords.com/navi.php?k=&qs={what}'), 'not_found': has_tag_with({'class': contains("alert-info")})},
     'corticalart.com': {'url': quoted_url('https://www.corticalart.com/?post_type=product&s={what}'), 'not_found':has_tag_with({'class': 'empty-category-block'})},
     'decks.de': {'url': quoted_url('https://www.decks.de/decks/workfloor/search_db.php?such={what}'), 'not_found':contains_text('0 search results')},
     'discogs.com': {'url': quoted_url('https://www.discogs.com/search/?type=all&q={what}'), 'not_found':contains_text('We couldn\'t find anything in the Discogs database matching your search criteria.')},
     'dodax.de': {'url': quoted_url('https://www.dodax.de/de-de/search/?s={what}'), 'not_found': contains_text('Keine Ergebnisse')},
     'dronerecords.de': {'url': quoted_url('https://www.dronerecords.de/search.html?text={what}'), 'not_found': contains_text('Unfortunately, there are no matches')},
     'dodobeach.de': {'url': quoted_url('https://www.dodobeach.de/liste.php?search={what}&button.x=0&button.y=0&p=0&genre=0&label=0&as=0&ft=on'), 'not_found':contains_text('Die Suche war leider nicht erfolgreich')},         'dussmann': {'url': quoted_url('https://kulturkaufhaus.buchhandlung.de/shop/quickSearch?offset=0&product=4765&searchString={what}'), 'not_found': has_no_tag_with({'class': contains('module-searchresult-list')})},
     'eil.com': {'url': quoted_url('https://eil.com/fulltext/search.asp?Sortby=title&SearchText={what}'), 'not_found':contains_text('Sorry, no items were found for your search.')},
     #'emp.de': {'url': quoted_url('https://www.emp.de/search?q={what}'), 'not_found':has_no_tag_with({'class': contains('search-result-content')})},
     'flight13.com': {'url': quoted_url('https://www.flight13.com/suchen?q={what}'), 'not_found': contains_text('nichts gefunden…')},
    'funrecords.de': {'url': quoted_url('https://www.funrecords.de/en/catalogue/?search={what}'), 'not_found':contains_text('No matching items found!')},
    'grooveattackrs': {'url': quoted_url('http://grooveattackrs.bigcartel.com/products?search={what}'), 'not_found': contains_text('No products found.')},
    'grooves.land': {'url': quoted_url('https://www.grooves.land/advanced_search_result.php?keywords={what}'), 'not_found': oneOf([contains_text('0 Results 0 Categories'), contains_text('0 Treffer in 0 Bereichen')])},
    'hmv.com': {'url': quoted_url('https://store.hmv.com/search?sort=most_relevant%20desc&quantity=24&page=1&view=grid&categories=format&format=CD%2BAlbum%2CVinyl%2B12%22%2BAlbum%2C12%22%2BVinyl%2BSingle%2BBox%2BSet%2C12%22%2BVinyl%2BEP%2CCD%2BBox%2BSet&searchtext={what}'), 'not_found':has_no_tag_with({"class":"search-results__dym"})},
    'hardwax.com' : {'url': quoted_url('https://hardwax.com/?search={what}'), 'not_found': contains_text('Sorry, no records found.')},
    'hotstuff.se': {'url': quoted_url('https://hotstuff.se/index.cfm?x=product&pg=1&prSts=2&zpgId=0&searchPhrase={what}'), 'not_found':contains_text('Inga varor kunde hittas')},
    'idealo.de': {'url': quoted_url('https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q={what}'), 'not_found':contains_text('konnten wir leider nicht finden')},
    'indiedetective.de': {'url': quoted_url('https://www.indietective.de/search.html?sorting=artist&offset=0&desc=false&showPics=true&showCD=true&showVinyl=true&showUsed=true&showSold=false&query={what}'), 'not_found':contains_text('0 Treffer.')},
    'jpc.de': {'url': quoted_url('https://www.jpc.de/s/{what}'), 'not_found':contains_text('Keine Ergebnisse')},
    'juno.co.uk': {'url': quoted_url('https://www.juno.co.uk/search/?q%5Ball%5D%5B0%5D={what}'), 'not_found':contains_text("Sorry, we couldn't find what you are looking for")},
    'kompakt.fm': {'url': quoted_url('https://kompakt.fm/releases?find={what}'), 'not_found': contains_text('Sorry, no Releases')},
    'majorlabel.shop': {'url': quoted_url('https://majorlabel.shop/advanced_search_result.php?keywords={what}'), 'not_found':contains_text('Die Suche ergab keine genauen Treffer')},
    #'musicstack.com': multibox_search_get('https://www.musicstack.com/show.cgi?filter_submit=1&find={artist}&t={title}&label={label}'), 'not_found':to_do()},
    'mandai.be': {'url': quoted_url('http://mandai.be/mailorder.php?type=All&search={what}'), 'not_found':contains_text('No results has been found.')},
    'mediamarkt.de': {'url': quoted_url('https://www.mediamarkt.de/de/search.html?filter=category%3ACAT_DE_MM_485%2F%2FCAT_DE_MM_503&query={what}'), 'not_found':has_tag_with({'class': contains('ZeroResultsView__PageSection')})},
    'medimpos.de': {'url': quoted_url('https://www.medimops.de/musik-C0255882/?searchparam={what}'), 'not_found':has_tag_with({'class': "mx-search-no-result"})},
    'normanrecords.com': {'url': quoted_url('https://www.normanrecords.com/cloudsearch/index.php?q={what}'), 'not_found':contains_text('Please try a different search phrase.')},
    'oye-records.com': {'url': quoted_url('https://oye-records.com/search?q={what}'), 'not_found': contains_text(' 0 results for ')},
    'parallel-schalplatten.de': {'url': quoted_url('https://www.parallel-schallplatten.de/cartPhp/search.php?searchFields=1&searchFormat=all&suchen=suchen%21&parallel_id=&searchPhrase={what}'), 'not_found': contains_text('konnte nicht gefunden werden.')},
    'perkoro.com': {'url': dashed_url('https://www.perkoro.com/q/band/{what}.php'), 'not_found': contains_text('Sorry, no articles found.')},
    'poponaut.de': {'url': quoted_url('http://www.poponaut.de/advanced_search_result.php?x=0&y=0&language=en&keywords={what}'), 'not_found':contains_text('There is no product that matches the search criteria.')},
    'praxis-records.net': {'url': quoted_url('https://praxis-records.net/shop/search?sSearch={what}'), 'not_found': contains_text('No products matching your search')},
    #'real.de': {'url': quoted_url('https://www.real.de/item/search/?id_category=6221&search_value={what}'), 'not_found':contains_text('Leider haben wir im Moment kein passendes Suchergebnis für Ihre Suche nach')},
    'recordsale.de': {'url': quoted_url('https://recordsale.de/en/search?s={what}'), 'not_found':has_tag_with({'class': contains("l-releaseList-empty")})},
    'rockers.de': {'url': quoted_url('https://www.rockers.de/search?search={what}'), 'not_found':has_tag_with({'class' : contains("not-found-disks")})},
    'saturn.de': {'url': quoted_url('https://www.saturn.de/de/search.html?query={what}'), 'not_found':has_tag_with({'id': contains('search_no_result-bottom_right')})},
    'shinybeast.nl': {'url': quoted_url('https://www.shinybeast.nl/catalog/search.php?q={what}'), 'not_found':contains_text('No records found.')},
    #'skullline.de': {'url': quoted_url('https://www.skullline.de/search?sSearch={what}'), 'not_found':contains_text('No products matching your search')},
    'soundflat.de': {'url': None, 'search': soundflat_search, 'not_found': None },
    'soundohm.com': {'url': quoted_url('https://www.soundohm.com/search?query={what}'), 'not_found':contains_text('No artists found for your query')},
    'soundstation.dk': {'url': quoted_url('https://soundstation.dk/shop/?search={what}'), 'not_found': has_no_tag_with({'id': "clerk-search-no-results"})},
    'soundwayrecords.com': {'url': quoted_url('https://soundwayrecords.com/search/query?q={what}'), 'not_found':contains_text('No Results')},
    'staalplaat.com': {'url': quoted_url('https://staalplaat.com/search_products?keys={what}'), 'not_found':has_tag_with({'class': "view-empty"})},
    'sisterray.co.uk': {'url': quoted_url('https://sisterray.co.uk/search?q={what}'), 'not_found':contains_text('0 matches for ')},
    'stora.de': {'url': None, 'search': stora_search, 'not_found': None },
    'sulatron.com': {'url': quoted_url('https://www.sulatron.com/xoshop/store-search-result.php?language=de&keywords={what}'), 'not_found':contains_text('konnte nicht gefunden werden.')},
    'tapeterecords.com': {'url': quoted_url('https://shop.tapeterecords.com/catalogsearch/result/?q={what}'), 'not_found':contains_text('Your search returns no results.')},
    'tochnit-aleph.com': {'url': quoted_url('http://www.tochnit-aleph.com/catalog/advanced_search_result.php?keywords={what}'), 'not_found':contains_text('There is no product that matches the search criteria.')},
    'unrock.de': {'url': quoted_url('http://www.unrock.de/?post_type=product&s={what}'), 'not_found': contains_text('No products were found matching your selection.')},
    'vinylexchange.co.uk': {'url': quoted_url('https://www.vinylexchange.co.uk/search?q={what}'), 'not_found':has_no_tag_with({'class': "search-result"})},
    #'vinylrecords.co.uk': multibox_search_get('https://www.vinylrecords.co.uk/shop/catalogsearch/advanced/result/?artist={artist}&name={title}'), 'not_found':to_do()},
    'x-mist.de': {'url': quoted_url('https://www.x-mist.de/index.php?STEPOFFSET=0&MENUECALL=1&sel=SEARCH&SEARCHSTRING={what}'), 'not_found': contains_text('sorry, there are no products available for your selection')},
    'yesasia.com': {'url': quoted_url('https://www.yesasia.com/global/search-music/0-0-0-q.{what}_bt.48_bpt.48_ss.101-en/list.html'), 'not_found':contains_text('The option you have just selected has returned zero (0) results.')},
         }

rendered_shops = {
    'fnac.fr': {'url': quoted_url('https://www.fnac.com/SearchResult/ResultList.aspx?SCat=3!1&Search={what}'), 'not_found':contains_text('Il n’y a aucun résultat pour votre recherche')},
    'google.com': {'url': quoted_url('https://www.google.com/search?q={what}&source=lnms&tbm=shop&sa=X&biw=1440&bih=307'), 'not_found':contains_text('did not match any shopping results')},
    'greenhell.de': {'url': quoted_url('https://greenhell.de/navi.php?qs={what}'), 'not_found': contains_text('No results for your search.')},
    'hhv.de': {'url': quoted_url('https://www.hhv.de/shop/en/all-items/p:08QLU0?&term={what}'), 'not_found':has_tag_with({'class': 'no_items'})},
    'musicmaggie.co.uk': {'url': url('https://www.musicmagpie.co.uk/store/category/?keyword={what}'), 'not_found':contains_text('No matching products found')},
    'townsendmusic.store': {'url': quoted_url('https://townsendmusic.store/?sort=low&perpage=100&page=products&search={what}'), 'not_found':contains_text('products-no-results')},
}

test_shops = {
}

rendered_test_shops = {}

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
        browser = await launch(headless=(not test))
        for name, shop in rendered_shops.items():
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
        pprint(x)
        #for _ in x:
        #    try:
        #        name, (not_found, shop_url) = _
        #    except:
        #        pdb.set_trace()

