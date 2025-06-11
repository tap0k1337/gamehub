function glitchText(element) {
    const original = element.textContent;
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890';
    let iterations = 0;
    const interval = setInterval(() => {
        element.textContent = original
            .split('')
            .map((char, idx) => (idx < iterations ? char : chars[Math.floor(Math.random() * chars.length)]) )
            .join('');
        if (iterations >= original.length) clearInterval(interval);
        iterations += 1 / 3;
    }, 50);
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.cyberpunk-text').forEach(glitchText);
});
