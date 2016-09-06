---
layout: post
title: "Etna_viv: Getting there..."
author: Wladimir J. van der Laan
permalink: /2013/8/23/more-progress
tags: [etna_viv]
categories: [reverse-engineering, gpu]
---
The <a href="https://github.com/laanwj/mesa">etnaviv mesa driver</a> is coming along nicely... (thanks to zear for the glquake screenshots)

<style>
.quake { text-align: center; margin: 10px; }
</style>
<div class="quake">
<img src="{{ site.baseurl }}/assets{{ page.id }}/2013_07_21_quake_sep.png"><br>
2013-07-21
</div>
<div class="quake">
<img src="{{ site.baseurl }}/assets{{ page.id }}/2013_07_27_quake_etna_png_750x750_q85.jpg"><br>
2013-07-27
</div>
<div class="quake">
<img src="{{ site.baseurl }}/assets{{ page.id }}/2013_08_04_glquake4_png_750x750_q85.jpg"><br>
2013-08-04
</div>
<div class="quake">
<img src="{{ site.baseurl }}/assets{{ page.id }}/2013_08_16_quake_etna2_png_750x750_q85.jpg"><br>
2013-08-16
</div>
<div class="quake">
<img src="{{ site.baseurl }}/assets{{ page.id }}/2013_08_23_quake.png"><br>
2013-08-23
</div>
<div class="quake">
<img src="{{ site.baseurl }}/assets{{ page.id }}/2013_08_28_quake.png"><br>
2013-08-28
</div>

<p>GLES 1/2 support is getting there, all the crash bugs (that I know of) have been fixed, there is still some rendering corruption here and there, but most of the work left is fixing specific bugs and of course optimization. Please report specific bugs in the <a href="https://github.com/laanwj/etna_viv/issues">bug tracker</a>.</p>

<h3>Building the driver</h3>

<p>In the <a href="https://github.com/gcwnow/buildroot">GCW Zero buildroot</a> you can build the driver by setting <code>BR2_PACKAGE_ETNA_VIV=y</code>, <code>BR2_PACKAGE_ETNA_VIV_ABIV2=y</code> and <code>BR2_PACKAGE_MESA3D_ETNA_VIV=y</code>. Make sure that you use a kernel branch with the Vivante V2 driver enabled (newest is <a href="https://github.com/gcwnow/linux/tree/flatmush/jz-3.10-graphics-v2-fixes">jz-3.10-graphics-v2-fixes</a>).</p>

<p>Getting everything built on other platforms (such as Cubox) can be a bit tricky at the moment. If you have trouble building the driver for your platform you can <a href="mailto:laanwj@gmail.com">contact me</a>.<p>
