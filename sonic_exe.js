/**
 * Sonic.EXE - JavaScript/HTML5 Version
 * باز در مرورگر - فقط فایل HTML رو باز کن
 */

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Settings
const W = 1024, H = 576;
const FPS = 60;

// Colors
const BLACK = '#000000';
const DARK_GRAY = '#141419';
const BLOOD_RED = '#8b0000';
const CREEPY_RED = '#c80000';
const SONIC_BLUE = '#0064ff';
const GOLD = '#ffd700';
const WHITE = '#ffffff';
const GRAY = '#646464';

// Game states
const MENU = 0, PLAYING = 1, GAME_OVER = 2, WIN = 3;

// Game object
let state = MENU;
let player, sonicExe, rings, platforms;
let keys = {};
const WIN_RINGS = 20;

// Player
class Player {
    constructor(x, y) {
        this.x = x; this.y = y;
        this.w = 40; this.h = 50;
        this.vx = 0; this.vy = 0;
        this.speed = 6;
        this.jumpPower = -14;
        this.gravity = 0.6;
        this.onGround = false;
        this.rings = 0;
        this.invincible = 0;
        this.flash = 0;
    }

    update() {
        this.vy += this.gravity;
        this.y += this.vy;
        this.x += this.vx;

        if (this.x < 0) this.x = 0;
        if (this.x + this.w > W) this.x = W - this.w;
        if (this.y + this.h > H) {
            this.y = H - this.h;
            this.vy = 0;
            this.onGround = true;
        }

        // Platform collision
        this.onGround = false;
        for (const p of platforms) {
            if (this.x + this.w > p.x && this.x < p.x + p.w &&
                this.y + this.h >= p.y && this.y + this.h <= p.y + 30) {
                this.y = p.y - this.h;
                this.vy = 0;
                this.onGround = true;
            }
        }

        if (this.invincible > 0) {
            this.invincible--;
            this.flash = (this.flash + 1) % 10;
        }
    }

    jump() {
        if (this.onGround) {
            this.vy = this.jumpPower;
            this.onGround = false;
        }
    }

    draw() {
        const color = (this.invincible > 0 && this.flash < 5) ? WHITE : SONIC_BLUE;
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.ellipse(this.x + this.w/2, this.y + this.h/2, this.w/2, this.h/2, 0, 0, Math.PI * 2);
        ctx.fill();

        // Eyes
        ctx.fillStyle = WHITE;
        ctx.beginPath();
        ctx.arc(this.x + this.w/2 - 8, this.y + this.h/2 - 10, 6, 0, Math.PI * 2);
        ctx.arc(this.x + this.w/2 + 8, this.y + this.h/2 - 10, 6, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = BLACK;
        ctx.beginPath();
        ctx.arc(this.x + this.w/2 - 6, this.y + this.h/2 - 10, 3, 0, Math.PI * 2);
        ctx.arc(this.x + this.w/2 + 10, this.y + this.h/2 - 10, 3, 0, Math.PI * 2);
        ctx.fill();

        // Spikes
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.moveTo(this.x + this.w - 5, this.y + this.h/2 - 15);
        ctx.lineTo(this.x + this.w + 15, this.y + this.h/2);
        ctx.lineTo(this.x + this.w - 5, this.y + this.h/2 + 15);
        ctx.closePath();
        ctx.fill();
    }
}

// Sonic.EXE enemy
class SonicExe {
    constructor(x, y) {
        this.x = x; this.y = y;
        this.w = 45; this.h = 55;
        this.speed = 3;
        this.teleportTimer = 180 + Math.random() * 120;
        this.visible = true;
        this.blinkTimer = 0;
    }

    update() {
        this.teleportTimer--;
        this.blinkTimer++;
        this.visible = this.blinkTimer % 60 >= 3;

        if (!this.visible) return;

        const dx = player.x + player.w/2 - (this.x + this.w/2);
        const dy = player.y + player.h/2 - (this.y + this.h/2);
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist > 0) {
            this.x += (dx / dist) * this.speed;
            this.y += (dy / dist) * this.speed;
        }

        if (this.teleportTimer <= 0) {
            this.x = player.x - 100;
            this.y = player.y;
            this.teleportTimer = 120 + Math.random() * 120;
        }
    }

    draw() {
        if (!this.visible) return;

        ctx.fillStyle = BLACK;
        ctx.beginPath();
        ctx.ellipse(this.x + this.w/2, this.y + this.h/2, this.w/2, this.h/2, 0, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = BLOOD_RED;
        ctx.fillRect(this.x + this.w/2 - 15, this.y + this.h/2 - 13, 12, 15);
        ctx.fillRect(this.x + this.w/2 + 3, this.y + this.h/2 - 13, 12, 15);
        ctx.fillStyle = CREEPY_RED;
        ctx.fillRect(this.x + this.w/2 - 12, this.y + this.h/2 - 7, 6, 10);
        ctx.fillRect(this.x + this.w/2 + 6, this.y + this.h/2 - 7, 6, 10);

        ctx.fillStyle = '#1e1e1e';
        ctx.beginPath();
        ctx.moveTo(this.x + this.w - 5, this.y + this.h/2 - 18);
        ctx.lineTo(this.x + this.w + 18, this.y + this.h/2);
        ctx.lineTo(this.x + this.w - 5, this.y + this.h/2 + 18);
        ctx.closePath();
        ctx.fill();
    }

    collidesWith(p) {
        return this.x + this.w > p.x && this.x < p.x + p.w &&
               this.y + this.h > p.y && this.y < p.y + p.h;
    }
}

// Ring
class Ring {
    constructor(x, y) {
        this.x = x; this.y = y;
        this.r = 12;
        this.anim = 0;
    }

    update() {
        this.anim += 0.2;
    }

    draw() {
        const scale = 0.7 + 0.3 * Math.sin(this.anim);
        ctx.strokeStyle = GOLD;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.ellipse(this.x + this.r, this.y + this.r/2, this.r * scale, this.r/2 * scale, 0, 0, Math.PI * 2);
        ctx.stroke();
    }

    collidesWith(p) {
        const cx = this.x + this.r, cy = this.y + this.r/2;
        return Math.abs(cx - (p.x + p.w/2)) < p.w/2 + this.r &&
               Math.abs(cy - (p.y + p.h/2)) < p.h/2 + this.r;
    }
}

// Platform
class Platform {
    constructor(x, y, w, h = 20) {
        this.x = x; this.y = y; this.w = w; this.h = h;
    }
    draw() {
        ctx.fillStyle = GRAY;
        ctx.fillRect(this.x, this.y, this.w, this.h);
        ctx.strokeStyle = DARK_GRAY;
        ctx.strokeRect(this.x, this.y, this.w, this.h);
    }
}

function initGame() {
    player = new Player(100, 400);
    sonicExe = new SonicExe(W - 150, 300);
    rings = [];
    platforms = [
        new Platform(0, H - 50, W, 50)
    ];
    for (let i = 0; i < 8; i++) {
        platforms.push(new Platform(200 + i * 120, H - 150 - Math.random() * 100, 80 + Math.random() * 70));
    }
    for (let i = 0; i < 25; i++) {
        rings.push(new Ring(50 + Math.random() * (W - 100), 100 + Math.random() * (H - 200)));
    }
}

function input() {
    player.vx = 0;
    if (keys['ArrowLeft'] || keys['a']) player.vx = -player.speed;
    if (keys['ArrowRight'] || keys['d']) player.vx = player.speed;
    if (keys['ArrowUp'] || keys['w'] || keys[' ']) player.jump();
}

function update() {
    if (state !== PLAYING) return;
    input();
    player.update();
    sonicExe.update();

    for (let i = rings.length - 1; i >= 0; i--) {
        rings[i].update();
        const r = rings[i];
        if (player.x + player.w > r.x && player.x < r.x + r.r*2 &&
            player.y + player.h > r.y && player.y < r.y + r.r*2) {
            rings.splice(i, 1);
            player.rings++;
            if (player.rings >= WIN_RINGS) state = WIN;
        }
    }

    if (sonicExe.visible && sonicExe.collidesWith(player)) {
        if (player.invincible <= 0) {
            if (player.rings > 0) {
                player.rings = Math.max(0, player.rings - 5);
                player.invincible = 90;
                player.x -= 80;
            } else {
                state = GAME_OVER;
            }
        }
    }
}

function draw() {
    ctx.fillStyle = DARK_GRAY;
    ctx.fillRect(0, 0, W, H);

    if (state === MENU) {
        ctx.fillStyle = BLOOD_RED;
        ctx.font = 'bold 72px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('SONIC.EXE', W/2, 220);
        ctx.fillStyle = GRAY;
        ctx.font = '28px monospace';
        ctx.fillText("He's coming for you...", W/2, 280);
        ctx.fillStyle = WHITE;
        ctx.fillText('Press SPACE to run', W/2, 400);
        ctx.fillStyle = GRAY;
        ctx.fillText('Arrow keys / WASD - Move | Space - Jump', W/2, 440);
        if (Math.floor(Date.now()/500) % 2) {
            ctx.fillStyle = CREEPY_RED;
            ctx.fillText('>>> RUN <<<', W/2, 500);
        }
        return;
    }

    platforms.forEach(p => p.draw());
    rings.forEach(r => r.draw());
    player.draw();
    sonicExe.draw();

    ctx.fillStyle = GOLD;
    ctx.font = '24px monospace';
    ctx.textAlign = 'left';
    ctx.fillText(`Rings: ${player.rings}/${WIN_RINGS}`, 10, 30);

    if (state === GAME_OVER) {
        ctx.fillStyle = 'rgba(0,0,0,0.7)';
        ctx.fillRect(0, 0, W, H);
        ctx.fillStyle = BLOOD_RED;
        ctx.font = 'bold 72px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('GAME OVER', W/2, 260);
        ctx.fillStyle = WHITE;
        ctx.font = '28px monospace';
        ctx.fillText("Sonic.EXE got you...", W/2, 320);
        ctx.fillStyle = GRAY;
        ctx.fillText('Press SPACE to return', W/2, 400);
    }

    if (state === WIN) {
        ctx.fillStyle = 'rgba(0,0,0,0.6)';
        ctx.fillRect(0, 0, W, H);
        ctx.fillStyle = GOLD;
        ctx.font = 'bold 72px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('ESCAPED!', W/2, 260);
        ctx.fillStyle = WHITE;
        ctx.font = '28px monospace';
        ctx.fillText('You escaped Sonic.EXE!', W/2, 320);
        ctx.fillStyle = GRAY;
        ctx.fillText('Press SPACE to play again', W/2, 400);
    }
}

function gameLoop() {
    update();
    draw();
}

document.addEventListener('keydown', e => {
    keys[e.key.toLowerCase()] = true;
    if (e.key === ' ') e.preventDefault();
    if (state === MENU && e.key === ' ') {
        state = PLAYING;
        initGame();
    }
    if ((state === GAME_OVER || state === WIN) && e.key === ' ') {
        state = MENU;
    }
});

document.addEventListener('keyup', e => {
    keys[e.key.toLowerCase()] = false;
});

setInterval(gameLoop, 1000 / FPS);
