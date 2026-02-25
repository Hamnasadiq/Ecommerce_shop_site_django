// ================= Sparkle creation =================
const layer3 = document.getElementById('layer3');

if (layer3) {
  for (let i = 0; i < 40; i++) {
    const sparkle = document.createElement('div');
    const size = 1 + Math.random() * 3;          // Random size between 1-4px
    const delay = Math.random() * 5;             // Random delay for animation
    const duration = 3 + Math.random() * 4;      // Random sparkle twinkle duration

    sparkle.classList.add('sparkle');
    sparkle.style.left = `${Math.random() * 100}%`;
    sparkle.style.top = `${Math.random() * 100}%`;
    sparkle.style.width = `${size}px`;
    sparkle.style.height = `${size}px`;
    sparkle.style.boxShadow = `0 0 ${size*4}px ${size*2}px rgba(255, 220, 220, 0.6)`;
    sparkle.style.animation = `
      sparkleTwinkle ${duration}s infinite ${delay}s,
      sparkleFloat ${20 + Math.random()*20}s infinite linear ${delay}s
    `;

    layer3.appendChild(sparkle);
  }
}

// ================= Pause animations on window blur/focus =================
window.addEventListener('blur', () => document.body.classList.add('pause-animations'));
window.addEventListener('focus', () => document.body.classList.remove('pause-animations'));
