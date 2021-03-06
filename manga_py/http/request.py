import requests

from .url_normalizer import normalize_uri


class Request:
    __redirect_base_url = ''
    _headers = None
    referer = ''
    proxies = None
    allow_webp = True
    user_agent = '{} {} {} {}'.format(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'AppleWebKit/537.36 (KHTML, like Gecko)',
        'Chrome/60.0.3112.101',
        'Safari/537.36'
    )
    default_lang = 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3'
    cookies = None
    kwargs = None
    debug = False
    response = None
    _history = None
    allow_send_referer = True

    def __init__(self):
        self.proxies = {}
        self.cookies = {}
        self._history = []

    def __patch_headers(self, headers):
        if isinstance(self._headers, dict):
            for i in self._headers:
                headers[i] = self._headers[i]
        return headers

    def _get_cookies(self, cookies=None):
        return cookies if cookies else self.cookies

    def _prepare_redirect_base_url(self, url):
        if not self.__redirect_base_url:
            self.__redirect_base_url = url

    def _get_kwargs(self):
        kwargs = {}
        if self.kwargs:
            kwargs = self.kwargs
        return kwargs

    def __update_cookies(self, r):
        _ = r.cookies.get_dict()
        for c in _:
            self.cookies[c] = _[c]

    def __redirect_helper(self, r, url, method):
        proxy = None
        location = url
        if r.status_code == 303:
            method = 'get'
        elif r.status_code == 305:
            proxy = {
                'http': r.headers['location'],
                'https': r.headers['location'],
            }
        else:
            location = normalize_uri(r.headers['location'], self.__redirect_base_url)
        return proxy, location, method

    def _requests_helper(
            self, method, url, headers=None, data=None,
            max_redirects=10, **kwargs
    ) -> requests.Response:
        self._prepare_redirect_base_url(url)
        headers = self.__patch_headers(headers)
        args = {
            'url': url,
            'headers': headers,
            'data': data,
        }
        self.__set_defaults(args, kwargs)
        self.__set_defaults(args, self._get_kwargs())
        args.setdefault('allow_redirects', False)
        r = getattr(requests, method)(**args)
        self.__update_cookies(r)
        if r.is_redirect and method != 'head':
            if max_redirects < 1:
                self.debug and print(self._history)
                raise AttributeError('Too many redirects')
            self._history.append(url)
            proxy, location, method = self.__redirect_helper(r, url, method)
            if proxy:
                kwargs['proxies'] = proxy
            return self._requests_helper(
                method=method, url=location, headers=headers,
                data=data, max_redirects=(max_redirects - 1),
                **kwargs
            )
        return r

    @staticmethod
    def __set_defaults(args_orig: dict, args_vars: dict):
        for idx in args_vars:
            args_orig.setdefault(idx, args_vars[idx])

    def requests(
            self, url: str, headers: dict = None, cookies: dict = None,
            data=None, method='get', files=None, timeout=None, **kwargs
    ) -> requests.Response:
        if not isinstance(headers, dict):
            headers = {}
        self._history = []
        cookies = self._get_cookies(cookies)
        headers.setdefault('User-Agent', self.user_agent)
        if self.allow_send_referer and self.referer:
            headers.setdefault('Referer', self.referer)
        headers.setdefault('Accept-Language', self.default_lang)
        if self.allow_webp:
            headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=1.0,image/webp,image/apng,*/*;q=1.0'
        kwargs.setdefault('proxies', self.proxies)
        self.response = self._requests_helper(
            method=method, url=url, headers=headers, cookies=cookies,
            data=data, files=files, timeout=timeout,
            **kwargs
        )
        return self.response

    def get(self, url: str, headers: dict = None, cookies: dict = None, **kwargs) -> str:
        response = self.requests(
            url=url,
            headers=headers,
            cookies=cookies,
            method='get',
            **kwargs
        )
        text = response.text
        response.close()
        return text

    def post(self, url: str, headers: dict = None, cookies: dict = None, data: dict = (), files=None, **kwargs) -> str:
        response = self.requests(
            url=url,
            headers=headers,
            cookies=cookies,
            method='post',
            data=data,
            files=files,
            **kwargs
        )
        text = response.text
        response.close()
        return text

    def reset_proxy(self):
        self.proxies = {}

    def set_proxy(self, proxy):
        self.reset_proxy()
        if isinstance(proxy, dict):
            self.proxies['http'] = proxy.get('http', None)
            self.proxies['https'] = proxy.get('https', None)
        elif isinstance(proxy, str):
            self.proxies['http'] = proxy

    def get_base_cookies(self, url: str):
        """
        :param url:
        :return:
        """
        response = self.requests(url=url, method='head')
        response.close()
        return response.cookies
