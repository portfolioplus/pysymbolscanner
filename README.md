![Release Build](https://github.com/portfolioplus/pysymbolscanner/workflows/Release%20Build/badge.svg)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pysymbolscanner?style=plastic)
[![Coverage Status](https://coveralls.io/repos/github/portfolioplus/pysymbolscanner/badge.svg?branch=master)](https://coveralls.io/github/portfolioplus/pysymbolscanner?branch=master)
[![CodeFactor](https://www.codefactor.io/repository/github/portfolioplus/pysymbolscanner/badge)](https://www.codefactor.io/repository/github/portfolioplus/pysymbolscanner)

# install

```shell
pip install pysymbolscanner
```

# pysymbolscanner

Stock symbol scanner for [pytickersymbols](https://github.com/portfolioplus/pytickersymbols).
The tool scans several wikipedia pages to create an update via PR.

# basic usage

Starts symbol scanner without cache:
```shell
pysymbolscanner --input stocks.yaml --output stocks2.yaml
```

Starts symbol scanner with cache (skips time-consuming wiki scans if they have already been done):
```shell
pysymbolscanner --cache --input stocks.yaml --output stocks2.yaml
```


# install pycurl on macos

When you got the error message `src/pycurl.h: fatal error: 'openssl/ssl.h' file not found` you can try:

```shell
pip uninstall pycurl

export PATH="/usr/local/opt/openssl@1.1/bin:$PATH"
export LDFLAGS="-L/usr/local/opt/openssl@1.1/lib"
export CPPFLAGS="-I/usr/local/opt/openssl@1.1/include"
export PKG_CONFIG_PATH="/usr/local/opt/openssl@1.1/lib/pkgconfig"

pip install --compile --install-option="--with-openssl" pycurl
```