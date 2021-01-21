---
layout: post
title: "The widening gyre"
author: Wladimir J. van der Laan
tags: [bitcoin]
categories: [bitcoin]
---

Recent events have made me reflect on a few things in my life I was already thinking about for a while. Also, responses on social media have made me realize that people have *strange* expectations from me, and what my role in the Bitcoin Core project is.

growth
------

Bitcoin has grown a lot since I started contributing to it in 2011. Some arrangements that were acceptable for a small scale FOSS project are no longer so for one runing a 600 billion dollar system. Market cap is famously deceptive, but my point is not about specific numbers here.

One thing is clear: this is a serious project now, and we need to start taking decentralization seriously.

moving on
---------

I realize I am myself somewhat of a centralized bottleneck. And although I find Bitcoin an extremely interesting project and believe it's one of the most important things happening at the moment, I also have many other interests. It's also particularly stressful and I don't want it, nor the bizarre spats in the social media around it, to start defining me as a person.

spreading out
-------------

I will start by delegating my own tasks, and decreasing my involvement. I do not intend to stop contributing to Bitcoin, or even to the Bitcoin Core project, but I would like to remove myself from the critical path and take (even more) of a background role.

Note that we had a nice growth in development activity, and that maintenance of the code itself has already been spread over multiple people for a while. I'm not the most active maintainer. Looking at the number of git merges

```bash
bitcoin$ git log --pretty="format:%cn" --merges --since=2020-01-01 | sort| uniq -c
    313 fanquake
     51 Jonas Schnelli
    727 MarcoFalke
      7 Pieter Wuille
     65 Samuel Dobson
    363 Wladimir J. van der Laan
```

Only about 24% of the merges were done by me, last year.

plans
-----

But there's plenty of things left to figure out, from the top of my head:

- Decentralize distribution.

  - In the short run, transfer bitcoincore.org to an organization instead of private ownership. Reduce the "bus factor".

  - I think it would be good if some other organizations set up mirrors, so there is less incentive to try to take bitcoincore.org down.

  - In the long run, move away from a website for code distribution completely. No matter who owns it, a website on the clearnet can be shut down with the press of a button, and it seems that the global internet is gearing up to make censorship increasingly easy. We need a decentralized web. For us, one option would be IPFS, which is starting to catch on. For the binaries themselves there's already the option of downloading through torrents.

- Decentralize the release process, and release signing.

  - Delegate more parts of the release process. Other maintainers should be able to do a release without my involvement.

  - Rename the GPG key used to sign `SHA256SUMS.asc` to "Bitcoin Core release signing key", instead of having it in my personal title. Make some construct so that N of M (minimally) trusted gitian signers doing a succesful build automatically results in a signed distribution.

  - Same for the native code signing for Windows and MacOS.

  - Even better in the long run would be to split up the keys, e.g. though RSA threshold signing, so that the whole process is geographically distributed.

- Decentralize the development hub.

  - It's not clear whether github can be trusted to act in our interest in the long run. Although issues and PRs are backed up through the API, having to move somewhere else could give significant interruption in development. And hopping from provider to provider would be awful—ideally the whole thing would not rely on a central server *at all*. For this I've been watching the [radicle](https://radicle.xyz/) project, a P2P distributed code collaboration platform. It's not quite there yet, but seems promising.

Bitcoin is quite different in some of the requirements here from other FOSS projects, so we'll have to develop some tools as we go. We could also, definitely, use some help here.

Some smaller things to consider:

- Find someone else who wants to do the IRC meeting chair instead of me. Or maybe rotate it between multiple people.

- Release (and release candidate) mails to the `bitcoin-dev` and `bitcoin-core-dev` lists will no longer be necessarily signed and sent by me.

- There's some development specific tooling hosted by me (e.g. the PR notification bots on IRC and mastodon). As they are non-critical and only little time goes into maintaining them, I'm fine with this for now.

As for decentralizing Bitcoin's node software itself:

- Carl Dong's `libbitcoin_kernel` work. Bitcoin Core is a large monolithic project which includes the consensus code, which is much more critical than the other parts. The kernel would be an isolated part with well-defined interface, and at some point, its own review flow for changes. The difference with previous `libbitcoin_consensus` plans is that the kernel is stateful: it includes UTXO management and validation. It however does not include P2P, mempool policy, wallet, GUI, and RPC code. It could be re-used in different clients, to have more diversity in clients, but without the risks of a deviating consensus implementation.

Over the course of 2021 this will be my focus with regard to Bitcoin Core.
