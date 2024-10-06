import os
import json
import shutil


def make_proxies(proxy_file: str, proxy_folder_path: str) -> list[str]:
    '''
    в хромдрайвере прокси возможны только через расширения <br>
    создает прокси расширения для хрома из файла формата: <br>
    213.166.75.179:9686:mwphff:3qZ8rm <br>
    где: <br>
    213.166.75.179:9686 - ip <br>
    mwphff - пользователь <br>
    3qZ8rm - пароль <br>
    host:port:user:pass
    '''

    with open(proxy_file, 'r') as file:
        lines = file.read().splitlines()

    proxies = []
    # proxy_folder = 'proxies'
    os.mkdir(proxy_folder_path)

    for n, row in enumerate(lines):
        path = f'{proxy_folder_path}/{n}'
        os.mkdir(path)
        row = row.split(':')

        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (row[0], row[1], row[2], row[3])

        with open(f"{path}/manifest.json", "w") as f:
            f.write(manifest_json)

        with open(f"{path}/background.js", "w") as f:
            f.write(background_js)

        proxies.append(os.path.abspath(path))
    return proxies


def make_proxy_extensions() -> list[str]:
    file = 'proxies.txt'
    path = 'parser/proxies/'

    # proxy_folder = 'proxies'
    if os.path.exists(path):
        shutil.rmtree(path)

    proxies = make_proxies(file, path)

    proxies.append(None)
    with open('proxies.json', 'w') as file:
        json.dump(proxies, file)

    return proxies


if __name__ == '__main__':
    make_proxy_extensions()
