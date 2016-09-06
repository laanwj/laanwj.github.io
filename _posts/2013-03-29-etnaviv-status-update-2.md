---
layout: post
title: "Etnaviv status update 2"
author: Wladimir J. van der Laan
permalink: /2013/3/29/etnaviv-status-update-2
tags: [etna_viv]
categories: [reverse-engineering, gpu]
---
<intro>
<p><strong>Good news everyone!</strong> The TGSI to Vivante ISA shader compiler has been <a href="https://github.com/laanwj/etna_viv">pushed</a>.</p>

<p>This means that after barely more than a month after my post about it, it is no longer needed to manually mess with <a href="/2013/2/26/using-the-etnaviv-shader-assembler">shader assembler</a> and you can now use the more standardized Gallium TGSI format to specify vertex and fragment shaders. These can be directly converted from GLSL by MESA once the driver is integrated.</p>
</intro>

<p>An example, from the source of framebuffer demo <a href="https://github.com/laanwj/etna_viv/blob/master/native/fb/cube_companion.c">cube_companion.c</a>, which has now become encouragingly simple and empty of hardware-specific details:</p>
```c
static const char cube_companion_vert[] = 
"VERT\n"
"DCL IN[0]\n"
"DCL IN[1]\n"
"DCL IN[2]\n"
"DCL OUT[0], POSITION\n"
"DCL OUT[1], GENERIC[0]\n"
"DCL OUT[2], GENERIC[1]\n"
"DCL CONST[0..10]\n"
"DCL TEMP[0..4], LOCAL\n"
"IMM[0] FLT32 {    2.0000,    20.0000,     1.0000,     0.0000}\n"
"  0: MUL TEMP[0], CONST[3], IN[0].xxxx\n"
"  1: MAD TEMP[0], CONST[4], IN[0].yyyy, TEMP[0]\n"
"  2: MAD TEMP[0], CONST[5], IN[0].zzzz, TEMP[0]\n"
"  3: MAD TEMP[0], CONST[6], IN[0].wwww, TEMP[0]\n"
"  4: MUL TEMP[1], CONST[7], IN[0].xxxx\n"
"  5: MAD TEMP[1], CONST[8], IN[0].yyyy, TEMP[1]\n"
"  6: MAD TEMP[1], CONST[9], IN[0].zzzz, TEMP[1]\n"
"  7: MAD TEMP[1], CONST[10], IN[0].wwww, TEMP[1]\n"
"  8: RCP TEMP[2].x, TEMP[1].wwww\n"
"  9: MUL TEMP[1].xyz, TEMP[1].xyzz, TEMP[2].xxxx\n"
" 10: ADD TEMP[1].xyz, IMM[0].xxyy, -TEMP[1].xyzz\n"
" 11: MOV TEMP[2].w, IMM[0].zzzz\n"
" 12: MUL TEMP[3].xyz, CONST[0].xyzz, IN[1].xxxx\n"
" 13: MAD TEMP[3].xyz, CONST[1].xyzz, IN[1].yyyy, TEMP[3].xyzz\n"
" 14: MAD TEMP[3].xyz, CONST[2].xyzz, IN[1].zzzz, TEMP[3].xyzz\n"
" 15: DP3 TEMP[4].x, TEMP[1].xyzz, TEMP[1].xyzz\n"
" 16: RSQ TEMP[4].x, TEMP[4].xxxx\n"
" 17: MUL TEMP[1].xyz, TEMP[1].xyzz, TEMP[4].xxxx\n"
" 18: DP3 TEMP[1].x, TEMP[3].xyzz, TEMP[1].xyzz\n"
" 19: MAX TEMP[1].x, IMM[0].wwww, TEMP[1].xxxx\n"
" 20: MOV TEMP[2].xyz, TEMP[1].xxxx\n"
" 21: MOV TEMP[1].xy, IN[2].xyxx\n"
" 22: MOV OUT[1], TEMP[2]\n"
" 23: MOV OUT[0], TEMP[0]\n"
" 24: MOV OUT[2], TEMP[1]\n"
" 25: END\n";

static const char cube_companion_frag[] = 
"FRAG\n"
"PROPERTY FS_COLOR0_WRITES_ALL_CBUFS 1\n"
"DCL IN[0], GENERIC[0], PERSPECTIVE\n"
"DCL IN[1], GENERIC[1], PERSPECTIVE\n"
"DCL OUT[0], COLOR\n"
"DCL SAMP[0]\n"
"DCL TEMP[0..1], LOCAL\n"
"  1: TEX TEMP[1], IN[1].xyyy, SAMP[0], 2D\n"
"  2: MUL TEMP[0], IN[0], TEMP[1]\n"
"  3: MOV OUT[0], TEMP[0]\n"
"  4: END\n";
```

<p>These source strings can then be converted to pipe shader objects by a call to the MESA <code>graw</code> utility library, and subsequently bound to the rendering pipeline with:</p>

```c
    void *vtx_shader = graw_parse_vertex_shader(pipe, cube_companion_vert);
    void *frag_shader = graw_parse_fragment_shader(pipe, cube_companion_frag);
    pipe->bind_vs_state(pipe, vtx_shader);
    pipe->bind_fs_state(pipe, frag_shader);
```

<p>That's that. Next up are transfer objects, screen objects, and conquering the last remnants of Gallium incompatibility.</p>

<p>I would appreciate if people would start testing the demos and driver on their device (for example on their <a href="http://www.solid-run.com/cubox">Cubox</a>; GC2000/i.MX6 will not work yet) so that we can weed out some bugs early. Let me know in channel <code>#etnaviv</code> on freenode IRC if you need help getting the build environment up or such.</p>

<p>Note that instruction support is still incomplete. For example, no support for loops (<code>LOOP</code>/<code>ENDLOOP</code>) yet, but conditionals (<code>IF</code>/<code>ELSE</code>/<code>ENDIF</code>) work. This is expected to improve in time.</p>

