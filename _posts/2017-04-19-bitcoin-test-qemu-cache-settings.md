---
layout: post
title: "Bitcoin Core tests: performance in VM"
author: Wladimir J. van der Laan
tags: [tests, performance, experiments]
categories: [bitcoin]
---

Being able to run tests quickly is essential during development. As a
maintainer I end up running the test suite several dozens of times per day.
Recently I noticed that the functional tests (`test/functional/test_runner.py`)
are slow when run inside a qemu VM (with KVM).  

When I drilled down to find the cause it became apparent that RPC calls such as
`getnewaddress` were much slower (up to 10 times, when compared to bare metal on
older hardware). It turns out that this is because the wallet code does an `fsync`
after every operation to make sure that changes to the database are safely
written to disk (for example in the case of a power failure), and these happen
to be slow in this environment.

In tests, all state is deleted afterwards so this extra robustness isn't
useful. To see if it could be a faster I performed timings running the tests
with various more and less safe cache settings.

### qemu cache setting

The cache setting determines the caching strategy used for a virtual block device,
and can be provided on the qemu command line though `cache=` or,
in the case of libvirt is configured in the XML description, e.g. 

```xml
<driver name='qemu' type='qcow2' cache='writeback'/>
```

### tmp on qcow2 (image)

| cache   | cumulative (s) | runtime (s)  |
| ------- | --------------:| ------------:|
| none    | 4138           | 1060         |
| writethrough | 4081      | 1044         |
| default | 3912           | 1003         |
| writeback | 3851         | 988          |
| unsafe  | 1042           | 278          |

### tmp on raw (block device)

| cache   | cumulative (s) | runtime (s)  |
| ------- | --------------:| ------------:|
| none    | 3850           | 986          |
| writethrough | 3806      | 977          |
| default | 3300           | 840          |  
| writeback | 3247         | 826          |
| unsafe  | 987            | 264          |

### Conclusion

Both in the case of a `qcow2` virtual disk and when passing through a
block device, the cache setting makes a significant impact on performance. `unsafe`
caching, which disables `fsync` completely, results in the fastest test runs.
This can make almost a factor 4 difference compared to the slowest option,
`none`.

Besides changing the cache setting, a similar effect can be achieved using the [utility
`eatmydata`](https://www.flamingspork.com/projects/libeatmydata/). This tool wraps a command and disables `fsync` and similar library
calls completely while it runs. This results in comparable timings to using
`unsafe` caching, and may also help on bare metal.

Travis CI, although it runs the tests in VMs, doesn't seem to be affected
by this: disabling `fsync` [did not show influence on performance there](https://github.com/bitcoin/bitcoin/pull/10220). It's
possible that they've already configured `unsafe` caching.

**Note:** all of these suggestions compromise integrity for
performance. Doing this when live wallets are involved would be an extremely
bad idea.
