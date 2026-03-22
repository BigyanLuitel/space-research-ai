// ── starfield ──
(function () {
  const canvas = document.getElementById('stars');
  const ctx = canvas.getContext('2d');
  let stars = [];
  let W, H;

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function init() {
    stars = [];
    for (let i = 0; i < 180; i++) {
      stars.push({
        x:     Math.random() * W,
        y:     Math.random() * H,
        r:     Math.random() * 1.2 + 0.2,
        a:     Math.random(),
        speed: Math.random() * 0.003 + 0.001,
        phase: Math.random() * Math.PI * 2,
      });
    }
  }

  function draw(t) {
    ctx.clearRect(0, 0, W, H);
    for (const s of stars) {
      const alpha = s.a * (0.4 + 0.6 * Math.sin(t * s.speed + s.phase));
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(232,228,220,${alpha})`;
      ctx.fill();
    }
    requestAnimationFrame(draw);
  }

  window.addEventListener('resize', () => { resize(); init(); });
  resize();
  init();
  requestAnimationFrame(draw);
})();


// ── nav scroll ──
window.addEventListener('scroll', () => {
  document.getElementById('nav').classList.toggle('scrolled', window.scrollY > 40);
});


// ── reveal on scroll ──
const revealObserver = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) e.target.classList.add('visible');
  });
}, { threshold: 0.15 });

document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));


// ── terminal typewriter ──
(function () {
  const lines  = ['line1','line2','line3','line4','line5','line6','line7','line8','line9'];
  const delays = [400, 200, 800, 200, 600, 200, 900, 200, 400];
  let started  = false;

  const terminalEl = document.querySelector('.terminal-wrap');
  if (!terminalEl) return;

  const termObs = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting && !started) {
      started = true;
      let cumulative = 0;
      lines.forEach((id, i) => {
        cumulative += delays[i];
        setTimeout(() => {
          const el = document.getElementById(id);
          if (el) el.style.opacity = '1';
        }, cumulative);
      });
    }
  }, { threshold: 0.3 });

  termObs.observe(terminalEl);
})();
