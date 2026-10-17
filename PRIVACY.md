# Privacy Policy — BT Reader

_Last updated: 17 October 2026_

BT Reader is a browser extension that shows the bt.no article you are currently reading in a clean,
readable HTML view. It is a hobby project with no commercial purpose.

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

## Changes and contact

If this policy changes, the updated version will be published here with a new date. Questions can be
raised by opening an issue in this repository.
