#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lxml.html import document_fromstring
import re

domainUri = 'http://mangafox.me'
uriRegex = 'https?://mangafox\.me/manga/([^/]+)/?'


def get_main_content(url, get=None, post=None):
    name = get_manga_name(url)
    return get('{}/manga/{}'.format(domainUri, name))


def get_volumes(content=None, url=None):
    result = document_fromstring(content).cssselect('#chapters a.tips')
    if not result:
        return []
    list = [i.get('href') for i in result]
    list.reverse()
    return list


def get_archive_name(volume, index: int = None):
    result = re.search('/manga/[^/]+/([^/]+/[^/]+)', volume)
    if not result:
        return ''
    return result.groups()[0]


def _content2image_url(content):
    parser = document_fromstring(content)
    result = parser.cssselect('img#image')
    return result[0].get('src')


def get_images(main_content=None, volume=None, get=None, post=None):
    _url = (domainUri + volume) if volume.find(domainUri) < 0 else volume
    if _url.find('.html') > 0:
        _url = _url[0: _url.rfind('/')]

    content = get('{}/1.html'.format(_url))
    pages = document_fromstring(content)
    pages = [i.get('value') for i in pages.cssselect('#top_bar .r .l select.m option')]

    images = [_content2image_url(content)]

    for n in pages:
        if int(n) < 2:
            continue
        content = get('{}/{}.html'.format(_url, n))
        images.append(_content2image_url(content))

    return images


def get_manga_name(url, get=None):
    result = re.search(uriRegex, url)
    if not result:
        return ''
    return result.groups()[0]


if __name__ == '__main__':
    print('Don\'t run this, please!')