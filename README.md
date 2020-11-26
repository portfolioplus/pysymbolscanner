# symbol_scanner
Stock symbol scanner for pytickersymbols repo 
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