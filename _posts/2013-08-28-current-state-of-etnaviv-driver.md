---
layout: post
title: "More etna_viv news"
author: Wladimir J. van der Laan
permalink: /2013/8/28/current-state-of-etnaviv-driver
tags: [etna_viv]
categories: [reverse-engineering, gpu]
---
<style>
.quake { text-align: center; margin: 10px; }
</style>

<p>Another update on the <a href="https://github.com/laanwj/mesa">Etna</a> 3D driver for Vivante GPU cores, along with screenshots of games that now render successfully :0)</p>
<p>Currently supported GPUs: GC600, GC800, GC860, GC880 (others may be supported but these have been tested). GC2000 is currently not supported because it has multiple pixel pipes (see <a href="http://pastebin.com/SdvBDeGE">this irc log</a> for details).</p>

<div class="quake">
<img src="{{ site.baseurl }}/assets{{ page.id }}/2013_08_23_aaaa2_png_750x750_q85.jpg"><br>
AAAA
</div>

<p>What has been done</p>
<ul>
<li>GLES1 (for the most part) and GLES2 support
<li>Shader compiler, with support for fixed pipeline emulation shaders from GLES1
<li>Buffer management, 2D and cubemap textures, mipmap generation
<li>Fallbacks in Mesa for the devices that only supports single vertex buffer or no 32-bit indices, and lowering for TGSI instructions LRP and POW
</ul>


<div class="quake">
<img src="{{ site.baseurl }}/assets{{ page.id }}/2013_08_23_d2x-etna_png_750x750_q85.jpg"><br>
D2X (Descent 2 rebirth)
</div>

<p>What has to be done (in no particular order)</p>
<ul>
<li>Bugfixes for remaining corruption issues</li>
<li>Optimization: mainly a smarter shader compiler, and implement performance features present in the blob driver but currently disabled in etnaviv
<li>An Xorg EXA (2D) driver
<li>Interaction with dma buffers and drm (kernel code for interaction between vivante kernel driver and dma buffers is supposed to exist somewhere, at least for Marvell Dove)
<li>Get stuff merged upstream</li>
</ul>

<div class="quake">
<img src="{{ site.baseurl }}/assets{{ page.id }}/2013_08_23_hurrican_png_750x750_q85.jpg"><br>
Hurrican
</div>

<p>Any help is welcome (props to Zear again for the screenshots).</p>

