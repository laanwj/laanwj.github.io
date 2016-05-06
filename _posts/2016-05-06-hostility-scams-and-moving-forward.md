---
layout: post
title: Dazed and confused, but trying to continue
author: Wladimir J. van der Laan
---

I'm happy with the job I'm doing, happy to work with a few very smart people on
an extremely interesting project, involving various entirely new challenges,
that could have enormous impact. But on the other hand Bitcoin infrastucture
development must be one of the most hostile and crazy working environments in
existence, at least in software development.

This is my personal reflection on recent events, and should not be seen as any
official statement for Bitcoin nor Bitcoin Core.

### Atmospheric toxicity

Day in, day out, there is trolling, targeted attacks, shilling on social media
targeted toward us. I don't know of any other project like this. I've seen
developer teams in MMOs under similar pressure from users; but possibly this is
even worse. There, there are avid disagreements about how the game rules
should be changed, here people get worked up about changes affecting a whole
economic system. And the people attacking are, in many cases, not even users of
the software.

But it is even worse when many of those attacks are agitated by someone that
purports to be part of your own project. Not just involved with,
even leading projects whose developers and users are openly hostile to us.

Some development tasks are extremely complex and require focus over a long
time. It is essential to be able to reduce distractions, by being at least sure
that your own team has your back.

For those reasons over the last years we've tried to create a more sane and
focused environment for developers to work in. Part of this is a restructuring
of the project. A decoupling of the name "Bitcoin Core" from "Bitcoin". Bitcoin
is (understandably) seen as public property. No one owns the bitcoin system, it
is supposed to be decentralized and intangible.

However Bitcoin Core is a software project run by a team of people working
together, on an open source basis. People who choose for themselves who they
want to work with, and who they don't want to work with.

There comes a point when it is time to break ties with certain individuals
which were formative in the beginning but have, over time, ossified and even
come to be seen as a toxic influence. Especially if they haven't partaken in
active development for a long time.

### Scams all the way down

On a different note, Bitcoin has unfortunately always attracted scammers
(remember mybitcoin?), con artists (remember pirateat40?), as well as assorted
opportunists of all kinds.

Bitcoin also has its own creation myth, with borderline-religious support by
some.

But now something truly fishy is going on. Someone is claiming to be
that creator, but is surrounded by technological and social trickery, based on
backdated GPG keys, faked digital signatures, maybe classic bait-and-switch
parlor tricks. Despite various red flags, many people are convinced that a
certain person is the creator of Bitcoin. There is a larger confusion than ever
where truth starts and where misdirection and scams end. I am extrememly
concerned about this.

I wasn't sure, and am still not sure how Gavin is involved in this. It is no
longer likely that he was hacked, but at the very least he is confused.
When we saw the blog post convinced he found Satoshi, the prudent thing to do
was to revoke his ownership of the 'bitcoin' organization on github, under
which the Bitcoin Core repository currently lies, immediately. 

In the past he has stated that ["Satoshi can have write access to the github repo any time he asks."](http://bitcoinstats.com/irc/bitcoin-dev/logs/2012/03/15#l1331820212.0),
so if he is absolutely convinced that this is Satoshi, there is a risk that
he'd give away the repository to a scammer.

### Least privilege

But in a way this was only the final straw. His privileges were seen as a
liability by members of the project for a while (and not just because of [proxy
threats from Mike Hearn](https://twitter.com/petertoddbtc/status/611368079117942786) to shut
down the project).

The [principle of least privilege](https://en.wikipedia.org/wiki/Principle_of_least_privilege) in computer security says that users, should only have access
to the resources they need for the purposes that are essential to the user's
job. 

This is not an idle concern, for us. Remember how
[the bitcoin sourceforge was hacked using Satoshi's inactive account](https://news.ycombinator.com/item?id=8287905)?

Gavin hadn't done anything as a maintainer for [a year or so](https://github.com/bitcoin/bitcoin/commit/3c60937ce6a251e565e169715ebb2f3dd76825c4), and before that
he already was [hardly active for a long time](https://github.com/bitcoin/bitcoin/commits?author=gavinandresen).

That's perfectly fine, people move on to other things, other interests, no one
is bound to this project for life. However, the world also moves on, and if
you go on to other things you can't expect to be able to come back at any
point and that everything is in the same place where you left it. It was time
to revoke those privileges anyway.

I have personally asked, in a phone conversation as well as in mail, Gavin
various times to give up his privileges with the github project himself - and
so have other people. The response was always that he'd sleep on it. Despite
allegations of the opposite, this did not come out of the blue.

### Crossing the Rubicon

So when the question comes up whether we should make Gavin maintainer again, my
answer, and that of many others is a resounding "no". For one, there is just no
point, as he wasn't acting as a maintainer for Bitcoin Core anymore in the
first place, and in addition to that, many feel that we can be more productive
if we separate our ways.

