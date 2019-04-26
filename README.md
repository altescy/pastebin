[paste.altescy.jp](https://paste.altescy.jp)
---

Simple pastebin service with syntax highlight.
![screenshot](https://i.imgur.com/qOgU9GC.png)


## `GET`

- `curl paste.altescy.jp/TOKEN`
  - get raw text

- `curl paste.altescy.jp/TOKEN/`
  - get text with guessed highlight

- `curl paste.altescy.jp/TOKEN/LEXER`
  - get text with specified highlight

- `curl USERNAME:PASSWORD@paste.altescy.jp`
  - show your own pastes with Basic-Auth
  - you don't need sign up. if username does not exist, it will be created automatically.
  - **! WARNING: Don't use an important password, this is not secure.**

## `POST`

- `cat 'your text' | curl -F 'f=<-' paste.altescy.jp`
  - upload text
  - return a paste URL / if you access from a browser, redirect to a paste page

- `cat 'your text' | curl -F 'f=<-' USERNAME:PASSWORD@paste.altescy.jp`
  - upload text with Basic-Auth
  - you can manage your paste after uploading
  - pasted text is private by default
  - if you want to post public text, post with a form parameter `public=1`
  - **! WARNING: Don't use an important password, this is not secure.**


## `PATCH`

- `cat 'your new text' | curl -X PATCH -F 'f=<-' USERNAME:PASSWORD@paste.altescy.jp/TOKEN`
  - replace posted text by new one

- `curl -X PATCH -F 'public=1' USERNAME:PASSWORD@paste.altescy.jp/TOKEN`
  - make paste public (or private with `public=0`)
  

## `DELETE`

- `curl -X DELETE USERNAME:PASSWORD@paste.altescy.jp/TOKEN`
  - delete your paste
