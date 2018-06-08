---
layout: post
title: "Git repository on Tor hidden service"
author: Wladimir J. van der Laan
tags: [experiments]
categories: [bitcoin]
---

I've put up a (read-only) mirror of various bitcoin-related git repositories at
[nxshomzlgqmwfwhcnyvbznyrybh3gotlfgis7wkv7iur2yj2rarlhiad.onion](http://nxshomzlgqmwfwhcnyvbznyrybh3gotlfgis7wkv7iur2yj2rarlhiad.onion/).
This is a Tor v3 hidden service, which means that at least Tor 0.3.2.9 is required to access it.

To clone anew, do:

```bash
git -c http.proxy=socks5h://127.0.0.1:9050 clone http://nxshomzlgqmwfwhcnyvbznyrybh3gotlfgis7wkv7iur2yj2rarlhiad.onion/git/bitcoin.git
cd bitcoin
git config --add remote.origin.proxy "socks5h://127.0.0.1:9050"
```

This assumes Tor proxy is set up on 127.0.0.1:9050 - the default. The last command
is necessary to make sure that pulls for updating also go through the proxy. A
full clone might be slow, so consider doing a shallow clone
(`--depth=10` or such) if not all of history is required.

Or if you already have bitcoin cloned:

```bash
cd bitcoin
git remote add orionwl http://nxshomzlgqmwfwhcnyvbznyrybh3gotlfgis7wkv7iur2yj2rarlhiad.onion/git/bitcoin.git
git config --add remote.orionwl.proxy "socks5h://127.0.0.1:9050"
# and then to pull changes: git pull orionwl master
```

To verify authenticity, always make sure that at least the top commit is correctly signed (get the maintainer GPG public keys somewhere else):

```bash
git log --show-signature
```

