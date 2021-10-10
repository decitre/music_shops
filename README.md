# music_search

Tool to interact with some music web shops, find specific music, to plan later purchases.

This is a targeted web interaction tool and not a web scraper, since data is not aggretated or stored.

Run `python -c 'import pyppeteer; pyppeteer.chromium_downloader.download_chromium()'`

## install adb in termux

Transfer `adb-ndk` to your termux home. `adb.bin` should be executable.

`adb.bin kill-server; adb.bin start-server`

# References

1. https://en.wikipedia.org/wiki/Web_crawler
1. https://compiletoi.net/fast-scraping-in-python-with-asyncio/
1. https://medium.com/z1digitalstudio/pyppeteer-the-snake-charmer-f3d1843ddb19
1. https://stackoverflow.com/questions/54858149/puppeter-link-inside-an-iframe
1. https://miyakogi.github.io/pyppeteer/reference.html#pyppeteer.page.Page.waitForSelector
1. https://www.reddit.com/r/termux/comments/62zi71/can_i_start_an_app_from_termuxs_command_line_how/
1. https://www.programmersought.com/article/31261666911/
1. https://blog.chromium.org/2011/05/remote-debugging-with-chrome-developer.html
1. https://stackoverflow.com/questions/57957890/connect-with-pyppeteer-to-existing-chrome
1. https://miyakogi.github.io/pyppeteer/reference.html
1. https://stackoverflow.com/questions/53021448/multiple-async-requests-simultaneously
1. https://pastebin.com/tvTNyhUb
1. https://nitayneeman.com/posts/getting-to-know-puppeteer-using-practical-examples/#connecting-chromium
1. https://www.chromium.org/developers/how-tos/run-chromium-with-flags
1. https://developer.android.com/studio/releases/platform-tools
1. https://developer.android.com/studio/command-line/adb
1. https://github.com/Magisk-Modules-Repo/adb-ndk
1. https://pypi.org/project/adb-shell/
1. https://maxiee.github.io/post/PyppeteerCrawlingInterceptResponsemd/