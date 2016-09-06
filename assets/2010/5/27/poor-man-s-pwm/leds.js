/* 
LEDs on HTML canvas
(C) Wladimir J. van der Laan 2010
*/
var led_defs = [
    /* Green */
    {glow_col: [90, 240, 24],
    led_col1: [187, 241, 93],
    led_col2: [162, 229, 35],
    led_col3: [141, 231, 51]},
    /* Yellow */
    {glow_col: [240, 240, 24],
    led_col1: [200, 241, 93],
    led_col2: [218, 229, 35],
    led_col3: [231, 231, 51]},
    /* Red */
    {glow_col: [240, 50, 24],
    led_col1: [241, 157, 93],
    led_col2: [229, 122, 35],
    led_col3: [231, 101, 51]},
];
var led_colors = [2,1,1,1,0,0,0,0];

function rgba(rgb,a)
{
    /* Must use toFixed here, as 0.123e-23 kind of values fail (at least on FF) */
    return 'rgba('+rgb[0]+','+rgb[1]+','+rgb[2]+','+a.toFixed(6)+')';
}

function Sprite(ctx)
{
    this.draw = function(ctx, def, intensity)
    {
        intensity = Math.max(Math.min(intensity, 1.0), 0.0); /* Clip to valid range */
        
        intensity2 = Math.min(intensity+0.2, 1.0);
        var glow_col = def.glow_col;
        var led_col1 = [];
        var led_col2 = [];
        var led_col3 = [];
        for(var i=0; i<3; ++i)
        {
            /* glow_col[i] = Math.floor(def.glow_col[i]*intensity); */
            led_col1[i] = Math.floor(def.led_col1[i]*intensity2);
            led_col2[i] = Math.floor(def.led_col2[i]*intensity2);
            led_col3[i] = Math.floor(def.led_col3[i]*intensity2);
        }
        with(ctx)
        {
save();
font = ' 10px sans-serif';
beginPath();
moveTo(0,0);
lineTo(41.03125,0);
lineTo(41.03125,35.6875);
lineTo(0,35.6875);
closePath();
clip();
strokeStyle = 'rgba(0,0,0,0)';
lineCap = 'butt';
lineJoin = 'miter';
miterLimit = 4;
save();
restore();
save();
restore();
save();
translate(-0.392821,0.0710407);
save();
g1 = createRadialGradient(21, 18, 0, 21, 18, 16);

g1.addColorStop(0, rgba(glow_col, intensity));
g1.addColorStop(0.53061223, rgba(glow_col, intensity));
g1.addColorStop(1, rgba(glow_col, 0));

fillStyle = g1;
strokeStyle = 'rgba(0,0,0,0)';
beginPath();
moveTo(20.924071,-0.07104075);
bezierCurveTo(10.494467000000002,-0.07104075,0.39282109000000176,6.9836782,0.39282109000000176,17.772709);
bezierCurveTo(0.39282109000000176,28.56174,10.494467000000002,35.616459,20.924071,35.616459);
bezierCurveTo(31.353675000000003,35.616459,41.424071,28.535198,41.424071,17.772709);
bezierCurveTo(41.424071,7.010220199999999,31.353674999999996,-0.07104075000000165,20.924070999999998,-0.07104075000000165);
closePath();
fill();
stroke();
restore();
save();
g2 = createRadialGradient(115.70896,153.41667,0,115.70896,153.41667,16.75);
g2.addColorStop(0, rgba(led_col1, 1));
g2.addColorStop(0.54348761, rgba(led_col2, 1));
g2.addColorStop(1, rgba(led_col3, 1));
fillStyle = g2;
strokeStyle = 'rgba(0,0,0,0)';
beginPath();
moveTo(34.054677,17.783455);
bezierCurveTo(34.054677,23.563064,28.170692,28.248365,20.912428999999996,28.248365);
bezierCurveTo(13.654165999999996,28.248365,7.770181099999997,23.563064,7.770181099999997,17.783455);
bezierCurveTo(7.770181099999997,12.003846,13.654165999999996,7.3185442,20.912428999999996,7.3185442);
bezierCurveTo(28.170691999999995,7.3185442,34.054677,12.003846,34.054677,17.783455);
closePath();
fill();
stroke();
restore();
save();
g3 = createRadialGradient(122.75,144.76639,0,122.75,144.76639,16.75);
g3.addColorStop(0,'rgba(255, 255, 255, 1)');
g3.addColorStop(1,'rgba(255, 255, 255, 0)');
fillStyle = g3;
strokeStyle = 'rgba(0,0,0,0)';
transform(0.684752,0,0,0.616201,-55.4553,-79.7338);
beginPath();
moveTo(129,155.75);
bezierCurveTo(129,162.51549,122.84392,168,115.25,168);
bezierCurveTo(107.65608,168,101.5,162.51549,101.5,155.75);
bezierCurveTo(101.5,148.98451,107.65608,143.5,115.25,143.5);
bezierCurveTo(122.84392,143.5,129,148.98451,129,155.75);
closePath();
fill();
stroke();
restore();
restore();
restore();
        }
    }
}

function draw(rot) {
   var canvas = document.getElementById("leds");
   var ctx = canvas.getContext("2d");
   ctx.clearRect(0,0,canvas.width,canvas.height);
   ctx.save();
   
   var t = new Date().getTime() - g_start_time;
   
   t = t / g_period;
   
   for(var i=0; i<8; ++i)
   {
       var x = (t - i*0.33) % 2.0;
       if(x < 0)
           x += 2.0; /* -x % 2.0 can be negative number */
       if(x >= 1.0)
           val = 2.0-x
       else
           val = x;
       g_sprite.draw(ctx, led_defs[led_colors[i]], val);
       ctx.translate(30, 0);
   }
   ctx.restore();
}
var g_start_time;
var g_sprite;
var g_rot = 0.0; 
var g_period = 1000.0;

function doFrame()
{
    draw(g_rot);
    g_rot += 2;
    if(g_rot > 200)
        g_rot = 0;
}

function init_game() {
    var canvas = document.getElementById("leds");
    var ctx = canvas.getContext("2d");
    g_start_time = new Date().getTime();
    g_sprite = new Sprite(ctx);
    setInterval(doFrame, 50);
}
window.addEventListener('load', init_game, false);
