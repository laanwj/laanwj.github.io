---
layout: post
title: Porting Bitcoin Core to CloudABI
author: Wladimir J. van der Laan
tags: [sandboxing, security, experiments]
categories: [bitcoin]
---

In this post I'm going to describe my ongoing experiment of porting Bitcoin
Core to CloudABI. I think the capability-based approach of CloudABI is a
conceptually great way of going about the problem of containing applications,
and it might be a harbinger of things to come in computer security.
Bitcoin Core is a good example of an existing, moderately complex, security critical C++
application to port over.

### What is CloudABI?

[CloudABI](https://nuxi.nl/) is a new open source project for sandboxing applications. The goal is
to isolate an application so that it can only access what it
needs, and only by way of the provided access methods. This
hardens against both privilege escalations and privacy leaks.
What sets it apart from other sandboxing methods is that:

- The system call ABI is as minimal as possible to reduce
attack surface. It is defined in an OS-agnostic way.

- CloudABI has its own C library that only defines what is
offered by this ABI.

- Security is based on capabilities, represented as file
descriptors. There are no global namespace, everything that
the application needs must be passed in explicitly. This is
defined using a standardized configuration file.

These properties allows cloudabi executables to run on
different operating systems unmodified (FreeBSD, NetBSD, Linux
at this time).

A restricted ABI and special libc means that it is easy to
find out whether something will work: compile it. This is
different from low-level sandboxing such as [seccomp-bpf](https://en.wikipedia.org/wiki/Seccomp), where
all system calls potentially used need to be carefully
enumerated. This is difficult - especially when a project
makes use of libraries not under the developer's control, as
any moderately complex program does. There is a runtime crash
if a process exceeds its permissions, risking fragility.

CloudABI thus allows porting applications to a strictly
sandboxed environment in a robust way. The following is an
overview of the challenges encountered while porting Bitcoin
Core to this new ABI.

### Use of files

CloudABI applications can make use of files, but do not have
access to the global file system space. Access to directories
must be explicitly granted by passing in a directory file
descriptor. `openat()` and similar functions can then be used to
open files relative to those directories only.

Bitcoin Core virtually only accesses files within its data
directory. So for most of the functionality, passing in a
handle to the data directory is enough. It could be stored in
a global and used where necessary. All filenames are then
relative to that.

In the future, different file handles could be passed in for
the different directories, e.g. to place the block index
somewhere else as that wallet. But this functionality is not
available in the upstream implementation either (except by a
symlink hack) so the infrastructure still has to be writtenanyhow.

#### boost::filesystem

Bitcoin Core uses boost::filesystem for all file and path
manipulation. It looks like boost::filesystem doesn't work
with cloudabi. It is possible to make use of `path`, however
this has no special intelligence to handle fd-relative paths.
None of the file or directory operations work.

The good thing about this is that (nearly) all uses of paths
are already abstracted, so what I thought is the best way forward is to
make a `boost::filesystem::path` subset replacement that works
with paths relative to fds, and implements the file operations
for this platform. For this reason I created the `fs.h`
[filesystem abstraction](https://github.com/laanwj/bitcoin/blob/2017_03_cabi_fs/src/fs.h).

#### Logging

A file descriptor for log output should be passed in, to aid
in debugging.

### Use of sockets

CloudABI applications cannot listen on a port, nor directly connect out
to the network, which poses some challenges.

#### Incoming connections

Binding sockets for RPC and P2P must be passed in through the
argdata API.

#### Outgoing connections

You could say that for a P2P client it is fairly important to be able to make
outgoing connections. Outgoing network connections are not
possible without an external helper. A simple workaround for
this would be to use of a SOCKS proxy (such as Tor) which acts
as guard. File descriptors of connections to this proxy would
be passed in by an external utility (although I'm not sure how
this is done yet).

Alternatively the proxy could be made connect in to the
process to "reverse proxy" when asked over a control socket.

#### DNS lookup

No capability to make outgoing connections also means no DNS
lookups. This is all too well; DNS leaks are a common privacy leak.

DNS lookup in Bitcoin Core is mostly used for requesting node
addresses from the DNS seeds, which are used for outgoing
connections. So any solution that enabled external connections
could potentially allow doing this too (e.g. Tor has a SOCKS5
extension for DNS lookup).

### Argument parsing

Argument passing is another thing that is different for
CloudABI. Instead of an array of parameters like in most
operating systems, a nested structure (to be precise,
[a binary representation of YAML](https://github.com/NuxiNL/argdata#binary-encoding)) is passed in.

There is nothing forbidding passing all configuration
arguments in one array within the structure and simply passing
that to `ParseParameters` as if it came in in `argc` and `argv`. However, we can do better.

Instead I've opted to [add argument processing code](https://github.com/laanwj/bitcoin/blob/2017_03_cabi_fs/src/bitcoind.cpp#L237) to take a
map of option name to option value(s). An example configuration:

```yaml
%TAG ! tag:nuxi.nl,2015:cloudabi/
---
datadir: !file
  path: /home/user/.bitcoin
console: !fd stdout
rpc: !socket
  bind: 127.0.0.1:8332
p2p: !socket
  bind: 0.0.0.0:8333
args:
  printtoconsole: 1
  rpcuser: "test"
  rpcpassword: "test"
  connect: 0
  debug: ["rpc","http","libevent"]
  listenonion: 0
  rest: true
```

This gives the bitcoind process a handle to its data directory, to stdout for
logging output, and passes in two readily listening network sockets for RPC and
P2P. The standard bitcoind arguments are passed in `args`.

### Dependencies

The following dependencies have already been ported by the
CloudABI project:

- leveldb
- boost (though `boost::filesystem` is problematic)
- libevent
- LibreSSL
- ZeroMQ (for asynchronous notification support)

The following might need to be ported (but see under "Missing Features"):

- BerkeleyDB (for wallet support)

These would be pointless in CloudABI:

- miniupnpc

### Other changes

- As it is risky to give applications a handle to the
system devices, file `/dev/urandom` is not available in the
sandbox. So use the [cloudabi\_sys\_random\_get](https://nuxi.nl/cloudabi/#random_get) system call to get
entropy instead.

### Missing features

These features are currently missing in the CloudABI port,
either until implemented or cannot be supported as they
inherently mismatch the goals of CloudABI.

- **Wallet support**: Need porting over BerkeleyDB, or maybe changing
the wallet database format to something that doesn't rely on this
library.

- `bitcoin.conf` parsing is currently disabled due to use of
`boost::fstream`, which isn't part of my wrapper yet. It is
however possible to pass all `bitcoin.conf` settings using the
input YAML file, in the `args` map (as shown above), so it is of
lesser priority.

- `mlock`/`lock`: These calls don't exist on CloudABI. Would be
nice to have an alternative way to pass in a chunk of pre-mlocked memory,
but I'm not sure how. As Bitcoin Core only uses memory locking
to keep private key data out of swap, this is not an issue
until the wallet is supported.

- **External script notifications**: Notifications that call out
to external scripts using `system()`, such as used for `-blocknotify` and `-walletnotify` are disabled. As it can only
inherit bitcoind's restricted capabilities, there is nothing
useful that such a script could do. Network-based
notifications will have to be used (ZeroMQ is available, another
option is [long-polling over RPC](https://github.com/bitcoin/bitcoin/pull/7949) which is in the works).

- **Torcontrol**: To support this, a handle to the Tor control socket could be
passed in. This can be left for later as there are some
additional challenges here, and for this use it's more
straightforward to configure Tor and bitcoin statically.

### Source code

The current version of this work can be found in my
[2017\_03\_cabi\_fs](https://github.com/laanwj/bitcoin/tree/2017_03_cabi_fs) branch.

*Edit.1*: Remove mention that ZeroMQ is not ported. It has been ported now.
That was quick!

*Edit.2*: Soften requirement to port BerkeleyDB. I'd prefer if no one would waste
time on that. Better to switch away from Berkeley DB (as it's overkill
for what we're doing, and questionable license-wise) so I'd say don't bother
with that one.

