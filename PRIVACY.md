# Privacy Policy and Terms of Use — BT Reader

_Last updated: 17 October 2026_

BT Reader is a browser extension that shows the bt.no article you are currently reading in a clean,
readable HTML view. It is a hobby project with no commercial purpose, and it is **not affiliated with,
endorsed by, or supported by Bergens Tidende, Schibsted, or any of their companies.**

## What the extension does with your data

The extension does nothing until you click its toolbar button. When you click it on a bt.no article:

1. It reads the **URL of that one tab** to find the article id (the part after `/i/` in the address).
2. It sends that article id to Schibsted's content API (`iris-core-bt.schibsted.tech`) to fetch the
   article's text, image and video URLs, and renders them in a new tab.
3. If the API request fails, it reads the **visible text and images of the article page** already open
   in your browser as a fallback, so it can still show the article.

That is the complete list. The extension does not run on any other site and does not touch other tabs.

## What the extension does not do

- It does **not** collect, store, or transmit any personal information.
- It does **not** track your browsing history or reading habits.
- It does **not** use cookies, analytics, advertising, or any third-party services other than the
  Schibsted API named above.
- It does **not** send anything to the extension's author or to any server operated by the author.
- It does **not** keep any data between uses: nothing is written to disk or browser storage.

## Third parties

The only network request the extension makes on its own is to Schibsted's API to fetch the article
you asked for. That request contains the article id and the standard information any HTTP request
carries, such as your IP address. Schibsted's handling of that request is governed by
[Schibsted's privacy policy](https://info.privacy.schibsted.com/), not by this one.

## Permissions explained

| Permission | Why |
|---|---|
| `activeTab` | To read the URL of the tab you clicked the button on. |
| `https://iris-core-bt.schibsted.tech/*` | To fetch the article content from the publisher's API. |
| `https://www.bt.no/*`, `https://bt.no/*` | To read the article from the page as a fallback if the API fails. |

## Open source

The complete source code is in this repository, so anyone can verify the statements above.

## Terms of use and disclaimer

**By installing or using BT Reader you accept the following.**

- **Provided as is.** The extension is provided free of charge, "as is" and "as available", without
  warranty of any kind, express or implied, including fitness for a particular purpose, accuracy, or
  uninterrupted operation. It depends on a third-party API that may change or be withdrawn at any time
  without notice, at which point the extension may stop working.
- **You are responsible for your own use.** The extension only acts when you click its button, and it
  acts on your behalf, in your browser, with your network connection. It is your responsibility to make
  sure your use complies with [bt.no's terms of service](https://www.bt.no/), Schibsted's terms, applicable
  copyright law, and any subscription or access conditions that apply to you. The extension does not
  grant you any rights to BT's content, and the author makes no representation that any particular use
  is permitted.
- **Content belongs to the publisher.** All article text, images and video shown by the extension are
  the property of Bergens Tidende / Schibsted and their licensors. The extension does not copy, store or
  redistribute content; it displays, on your screen, content your browser fetched for you.
- **No liability.** To the fullest extent permitted by law, the author shall not be liable for any
  direct, indirect, incidental, consequential or other damages, claims, losses or costs arising from your
  installation or use of the extension, from reliance on anything it displays, or from any action taken
  by a third party in response to your use of it.
- **Your own risk.** You install and use the extension at your own risk and discretion. If you do not
  agree with these terms, do not install it; if it is already installed, remove it.

## Changes and contact

If this policy changes, the updated version will be published here with a new date. Questions can be
raised by opening an issue in this repository.
