---
layout: post
title: TADAQUEOUS moments
author: Wladimir J. van der Laan
tags: [eqgrp, malware]
categories: [Reverse-engineering]
---

The one mystery module in the BLATSTING rootkit/malware/implant/... in the Equation Group dump is `m12000000`, or TADAQUEOUS. There is only one mention of it in the various documentation and scripts:

> If you are putting up tadaqueous, there will be lp error due to a missing files, there is no LP for this module.

What is meant here is that there is no Listening Post, or LP module for it. "Listening Post" is what the Equation Group calls its command-and-control programs. It can only be loaded and unloaded through this interface, not controlled, and it will spit an error message. Well, that tells us nothing.

At first sight the module looks sort of boring. It packages a kernel module and a user-space executable, but looking at the imported symbols and (open) strings, what it does is something with Linux processes and system calls.

However, after delving a bit deeper, I stumbled on a function that hooks a whole series of kernel calls, whose names are obfuscated in the binary:
<!--
e scr.html=true
e scr.pipecolor=true
pD 153 > /tmp/out_asm.html
-->
<pre class="radareasm">
{% include_relative 2016-09-01-tadaqueos/_hook_kernel_functions.html %}
</pre>

Summarizing the data structure at `.data+0x3c0`:

|  Offset     | Flag   | Target symbol         | Redirected to      |
| ----------- | ------ | --------------------- | ------------------ |
|  0x000003c0 | 0x0001 | `__add_ipsec_sa`      | .text+0x00000c60   |
|  0x000003d8 | 0x0002 | `asic_init_cmd_block` | .text+0x00000e8c   |
|  0x000003f0 | 0x0004 | `__del_ipsec_sa`      | .text+0x00000da0   |
|  0x00000408 | 0x0008 | `get_random_bytes`    | 0x00000000         |
|  0x00000420 | 0x0010 | `cipher_des`          | 0x00000000         |
|  0x00000438 | 0x0020 | `cipher_3des`         | 0x00000000         |
|  0x00000450 | 0x0040 | `cipher_aes`          | 0x00000000         |
|  0x00000468 | 0x0080 | `cipher_null`         | 0x00000000         |
|  0x00000480 | 0x0100 | `hmac_null`           | 0x00000000         |
|  0x00000498 | 0x0200 | `hmac_md5_96`         | 0x00000000         |
|  0x000004b0 | 0x0400 | `hmac_sha1_96`        | 0x00000000         |
|  0x000004c8 | 0x0800 | `cipher_dev_in_use`   | 0x00000000         |
|  0x000004e0 | 0x1000 | `asic_xxcrypt`        | .text+0x00000f18   |
|  0x000004f8 | 0x2000 | `cpx_read_rand`       | .text+0x00000e50   |
| ----------- | ------ | --------------------- | ------------------ |

It looks like this is a noteworthy module after all:

- Most of the symbols are not standard Linux symbols but specific to the TOS/Fortinet
  implementation. Their meaning, however is clear from the name.

- Some of the functions are redirected to a local function, others to
  0x00000000, which likely means that they are disabled completely.

It does give a huge hint at what the goal of this module is: cripple or disable IPsec! It appears it can be used to selectively disable ciphers, HMAC algorithms, and random number generation. It is obvious how this is useful to anyone trying to either intercept or insert themselves into a target's VPN network.

Shunting the function `get_random_bytes` will have the effect of disabling *all* random number generation in the kernel. Not just for IPsec, but also for e.g. TCP sequence numbers, enabling IP spoofing. It is not used for `/dev/[u]random` however, so user space processes cannot easily detect this.  

[nohats.ca](https://nohats.ca/wordpress/blog/2014/12/29/dont-stop-using-ipsec-just-yet/) writes, in the conclusion of an artice about IPsec and the Snowden revelations:

> I read this to mean that the hardware or software of the system running IPsec was compromised, causing it to send valid protocol ESP packets, but creating those in such a way that these could be decrypted without knowing the ESP session keys (from IKE). Possibly by subverting the hardware number generator, or functions related to IV / ICV’s / nonces that would appear to be random but were not.

We've found out one of the ways how. This targets a specific series of routers, but I'd be surprised if it was the only one, and other instances may be similar to this implementation, or based on it: there are various hints that [BLATSTING is the oldest generation](https://gist.github.com/laanwj/9e5e404266a8956beabde522f97c421b#file-blatsting-txt-L551) of implants in the EQGRP dump.

