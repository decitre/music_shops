from sys import argv
from urllib.parse import quote
from mechanize import Browser
from os import environ, system
from webbrowser import open_new_tab
if environ.get('PREFIX') == '/data/data/com.termux/files/usr':
    open_new_tab = lambda url: system(f'termux-open-url "{url}"')


def form_search(url: str, what: str, form_nr: int, input_name: str, replace_fn, file_name: str):
    browser = Browser()
    browser.set_handle_equiv(True)
    browser.set_handle_redirect(True)
    browser.set_handle_referer(True)
    browser.set_handle_robots(False)
    browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    browser.open(url)
    browser.select_form(nr=form_nr)
    browser[input_name] = what
    response = browser.submit()
    response_text = replace_fn(response.read())
    with open(f'/tmp/{file_name}', 'wb') as fp:
        fp.write(response_text)
    open_new_tab(f'file:///tmp/{file_name}')


def stora_search(what: str):
    url = 'http://www.stora.de'
    form_search(url=f'{url}/main.php',
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
                                        .replace(b'href="index', b'href="'+url.encode()+b'/index')),
                file_name='stora.html')


def soundflat_search(what: str):
    url = 'https://www.soundflat.de'
    form_search(url=f'{url}/shop/shop.cfm',
                what=what,
                form_nr=1,
                input_name='suchbegriff',
                replace_fn = lambda r: (r.replace(b'shop.cfm', url.encode()+b'/shop/shop.cfm')
                                        .replace(b"..", url.encode())
                                        .replace(b'src="img', b'src="'+url.encode()+b'/shop/img')),
                file_name='soundflat.html')

def default_search(ptn):
    def run(what: str):
        open_new_tab(ptn.format(what=quote(what)))
    return run


shops = {'anost.net': default_search('https://www.anost.net/search?query={what}'),
         'amazon.de': default_search('https://www.amazon.de/s?k={what}'),
         'bandcamp.com': default_search('https://bandcamp.com/search?q={what}'),
         'bisaufsmesser.com': default_search('https://www.bisaufsmesser.com/store/shopware.php/sViewport,search/sSearch,{what}'),
         'corticalart.com': default_search('https://www.corticalart.com/?s={what}&post_type=product'),
         'decks.de': default_search('https://www.decks.de/decks/workfloor/search_db.php?such={what}'),
         'deejay,de': default_search('https://www.deejay.de/{what}'),
         'discogs.com': default_search('https://www.discogs.com/search/?q={what}&type=all'),
         'dodobeach.de': default_search('https://www.dodobeach.de/liste.php?search={what}'),
         'emp.de': default_search('https://www.emp.de/search?q={what}'),
         'google.com': default_search('https://www.google.com/search?q={what}&source=lnms&tbm=shop&sa=X&biw=1440&bih=307'),
         'grooves.land': default_search('https://www.grooves.land/advanced_search_result.php?keywords={what}'),
         'hhv.de': default_search('https://www.hhv.de/shop/en/all-items/p:08QLU0?&term={what}'),
         'idealo.de': default_search('https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q={what}'),
         'indiedetective.de': default_search('https://www.indietective.de/search.html?sorting=artist&offset=0&desc=false&showPics=true&showCD=true&showVinyl=true&showUsed=true&showSold=false&query={what}'),
         'jpc.de': default_search('https://www.jpc.de/s/{what}'),
         'majorlabel.shop': default_search('https://majorlabel.shop/advanced_search_result.php?keywords={what}'),
         'mandai.be': default_search('http://mandai.be/mailorder.php?search={what}&type=All'),
         'mediamarkt.de': default_search('https://www.mediamarkt.de/de/search.html?filter=category%3ACAT_DE_MM_485%2F%2FCAT_DE_MM_503&query={what}'),
         'medimpos.de': default_search('https://www.medimops.de/musik-C0255882/?searchparam={what}'),
         'poponaut.de': default_search('http://www.poponaut.de/advanced_search_result.php?keywords={what}&x=0&y=0'),
         'real.de': default_search('https://www.real.de/item/search/?id_category=6221&search_value={what}'),
         'recordsale.de': default_search('https://recordsale.de/en/search?s={what}'),
         'rockers.de': default_search('https://www.rockers.de/search?search={what}'),
         'saturn.de': default_search('https://www.saturn.de/de/search.html?query={what}'),
         'shinybeast.nl': default_search('https://www.shinybeast.nl/catalog/search.php?q={what}'),
         'skullline.de': default_search('https://www.skullline.de/search?sSearch={what}'),
         'soundflat.de': soundflat_search,
         'soundohm.com': default_search('https://www.soundohm.com/search?query={what}'),
         'soundwayrecords.com': default_search('https://soundwayrecords.com/search/query?q={what}'),
         'staalplaat.com': default_search('https://staalplaat.com/search_products?keys={what}'),
         'stora.de': stora_search,
         'sulatron.com': default_search('https://www.sulatron.com/xoshop/store-search-result.php?keywords={what}'),
         'tapeterecords.com': default_search('https://shop.tapeterecords.com/catalogsearch/result/?q={what}'),
         'thalia.de': default_search('https://www.thalia.de/suche?sq={what}&filterPATHROOT=3738&allayout=FLAT'),
         'tochnit-aleph.com': default_search('http://www.tochnit-aleph.com/catalog/advanced_search_result.php?keywords={what}')}

if __name__ == '__main__':
    what = ' '.join(argv[1:])
    for shop, search in shops.items():
        print(shop)
        search(what)

