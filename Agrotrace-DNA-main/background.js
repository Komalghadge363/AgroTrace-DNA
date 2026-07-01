(function () {

  // Dark agriculture background
  document.body.style.background = '#0a1f12';
  document.body.style.position = 'relative';
  //document.body.style.minHeight = '100vh';

  // CANVAS
  const canvas = document.createElement('canvas');
  canvas.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;';
  document.body.insertBefore(canvas, document.body.firstChild);
  const ctx = canvas.getContext('2d');

  function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
  resize();
  window.addEventListener('resize', resize);

  // PARTICLES
  const particles = Array.from({ length: 60 }, () => ({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    vx: (Math.random() - 0.5) * 0.45,
    vy: (Math.random() - 0.5) * 0.45,
    r: 1 + Math.random() * 2,
    alpha: 0.15 + Math.random() * 0.35,
    color: Math.random() > 0.5 ? '82,183,136' : '212,160,23'
  }));

  // FLOATING CROP EMOJIS
  const cropEmojis = ['🌾', '🌱', '🌿', '🍃', '🌽', '🫘', '🌻', '🍀'];
  const floaters = Array.from({ length: 14 }, (_, i) => ({
    emoji: cropEmojis[i % cropEmojis.length],
    x: Math.random() * window.innerWidth,
    y: window.innerHeight + Math.random() * 300,
    speed: 0.3 + Math.random() * 0.5,
    size: 16 + Math.random() * 14,
    angle: Math.random() * Math.PI * 2,
    rotSpeed: (Math.random() - 0.5) * 0.018,
    opacity: 0.07 + Math.random() * 0.13
  }));

  // DNA
  let dnaT = 0;

  function drawDNA() {
    const W = canvas.width, H = canvas.height;
    const cx = W * 0.82;
    const top = 20, bottom = H - 20;
    const amplitude = 35;
    const steps = 90;
    const stepH = (bottom - top) / steps;

    for (let strand = 0; strand < 2; strand++) {
      ctx.beginPath();
      for (let i = 0; i <= steps; i++) {
        const y = top + i * stepH;
        const phase = strand === 0 ? 0 : Math.PI;
        const x = cx + Math.sin(i * 0.42 + dnaT + phase) * amplitude;
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }
      ctx.strokeStyle = strand === 0 ? 'rgba(82,183,136,0.45)' : 'rgba(100,210,160,0.3)';
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }

    for (let i = 0; i <= steps; i += 5) {
      const y = top + i * stepH;
      const x1 = cx + Math.sin(i * 0.42 + dnaT) * amplitude;
      const x2 = cx + Math.sin(i * 0.42 + dnaT + Math.PI) * amplitude;
      const glow = Math.abs(Math.sin(i * 0.42 + dnaT));
      ctx.beginPath();
      ctx.moveTo(x1, y); ctx.lineTo(x2, y);
      ctx.strokeStyle = `rgba(212,160,23,${0.12 + glow * 0.3})`;
      ctx.lineWidth = 0.8;
      ctx.stroke();

      ctx.beginPath();
      ctx.arc(x1, y, 2.5, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(82,183,136,${0.35 + glow * 0.5})`;
      ctx.fill();

      ctx.beginPath();
      ctx.arc(x2, y, 2.5, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(130,210,170,${0.35 + glow * 0.5})`;
      ctx.fill();
    }
  }

  function drawGrid() {
    const W = canvas.width, H = canvas.height;
    ctx.strokeStyle = 'rgba(82,183,136,0.04)';
    ctx.lineWidth = 0.5;
    for (let x = 0; x < W; x += 50) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
    }
    for (let y = 0; y < H; y += 50) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    }
  }

  function drawOrbs() {
    const W = canvas.width, H = canvas.height;
    const orbs = [
      { x: W * 0.85, y: H * 0.15, r: 220, c: '82,183,136', a: 0.07 },
      { x: W * 0.05, y: H * 0.75, r: 180, c: '212,160,23', a: 0.05 },
      { x: W * 0.45, y: H * 0.5,  r: 150, c: '45,106,79',  a: 0.06 },
    ];
    orbs.forEach(o => {
      const g = ctx.createRadialGradient(o.x, o.y, 0, o.x, o.y, o.r);
      g.addColorStop(0, `rgba(${o.c},${o.a})`);
      g.addColorStop(1, 'transparent');
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(o.x, o.y, o.r, 0, Math.PI * 2);
      ctx.fill();
    });
  }

  function animate() {
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    // Background
    ctx.fillStyle = '#0a1f12';
    ctx.fillRect(0, 0, W, H);

    drawGrid();
    drawOrbs();

    // Particle connections
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          ctx.beginPath();
          ctx.strokeStyle = `rgba(82,183,136,${0.07 * (1 - dist / 120)})`;
          ctx.lineWidth = 0.5;
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.stroke();
        }
      }
    }

    // Particles
    particles.forEach(p => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${p.color},${p.alpha})`;
      ctx.fill();
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > W) p.vx *= -1;
      if (p.y < 0 || p.y > H) p.vy *= -1;
    });

    // Floating crops
    ctx.save();
    floaters.forEach(f => {
      ctx.save();
      ctx.globalAlpha = f.opacity;
      ctx.font = `${f.size}px serif`;
      ctx.translate(f.x, f.y);
      ctx.rotate(f.angle);
      ctx.fillText(f.emoji, 0, 0);
      ctx.restore();
      f.y -= f.speed;
      f.angle += f.rotSpeed;
      if (f.y < -40) {
        f.y = window.innerHeight + 20;
        f.x = Math.random() * window.innerWidth;
      }
    });
    ctx.restore();

    // DNA Helix
    drawDNA();
    dnaT += 0.011;

    requestAnimationFrame(animate);
  }

  animate();

  // Make all content above canvas
  document.querySelectorAll('body > *:not(canvas)').forEach(el => {
    if (getComputedStyle(el).position === 'static') {
      el.style.position = 'relative';
    }
    el.style.zIndex = '1';
  });

})();