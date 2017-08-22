#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lxml.html import document_fromstring
import re

domainUri = 'https://manga-online.com.ua'
manga_name = ''


def get_main_content(url, get=None, post=None):
    get_manga_name(url)
    return get('{}/katalog\-mangi/{}.html'.format(domainUri, manga_name))


def get_volumes(content=None, url=None):
    items = document_fromstring(content).cssselect('[id^="news-id"] a[href*="/manga/"]')
    items.reverse()
    return [i.get('href') for i in items]


def get_archive_name(volume, index: int = None):
    return 'vol_{:0>3}'.format(index)


def get_images(main_content=None, volume=None, get=None, post=None):
    manga_id = re.search('\.ua/manga/[^/]+/(\d+)', volume).groups()[0]
    n = 0
    images = []
    while True:
        n += 1
        if n > 99:
            print('More 99 pages error!')
            break
        content = get('{}/engine/ajax/sof_fullstory.php?id={}&page={}'.format(domainUri, manga_id, n))
        parser = document_fromstring(content)
        images.append(parser.cssselect('div > img')[0].get('src'))
        if not len(parser.cssselect('a#page_{}'.format(n+1))):  # last page
            break
    return images


def get_manga_name(url, get=None):
    global manga_name
    if not len(manga_name):
        if re.search('\.ua/manga/.+\.html', url):
            url = document_fromstring(get(url)).cssselect('.fullstory_main center > a')[0].get('href')
        name = re.search('\.ua/katalog\-mangi/([^/]+)\.html', url)
        if not name:
            return ''
        manga_name = name.groups()[0]
    return manga_name.split('-', 1)[1]


if __name__ == '__main__':
    print('Don\'t run this, please!')