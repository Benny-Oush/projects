import { useEffect, useRef } from 'react'

// Floating particle node
function makeParticle(W, H) {
  return {
    x: Math.random() * W,
    y: Math.random() * H,
    vx: (Math.random() - 0.5) * 0.4,
    vy: (Math.random() - 0.5) * 0.4,
    r: Math.random() * 2 + 1,
  }
}

const PARTICLE_COUNT = 110
const CONNECT_DIST = 130
const MOUSE_REPEL = 90
const CLICK_BURST_RADIUS = 160
const CLICK_FORCE = 4

export default function Background() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    let animId
    let W, H
    let particles = []
    const mouse = { x: -9999, y: -9999 }
    // click ripples: { x, y, t } where t counts down from 1 → 0
    const ripples = []

    function resize() {
      W = canvas.width = window.innerWidth
      H = canvas.height = window.innerHeight
      particles = Array.from({ length: PARTICLE_COUNT }, () => makeParticle(W, H))
    }

    function onMouseMove(e) {
      mouse.x = e.clientX
      mouse.y = e.clientY
    }

    function onClick(e) {
      const cx = e.clientX
      const cy = e.clientY
      // push particles away from click
      particles.forEach((p) => {
        const dx = p.x - cx
        const dy = p.y - cy
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist < CLICK_BURST_RADIUS && dist > 0) {
          const force = ((CLICK_BURST_RADIUS - dist) / CLICK_BURST_RADIUS) * CLICK_FORCE
          p.vx += (dx / dist) * force
          p.vy += (dy / dist) * force
        }
      })
      ripples.push({ x: cx, y: cy, t: 1 })
    }

    function draw() {
      ctx.clearRect(0, 0, W, H)

      // --- update + draw particles ---
      particles.forEach((p) => {
        // mouse repel
        const mdx = p.x - mouse.x
        const mdy = p.y - mouse.y
        const mdist = Math.sqrt(mdx * mdx + mdy * mdy)
        if (mdist < MOUSE_REPEL && mdist > 0) {
          const f = ((MOUSE_REPEL - mdist) / MOUSE_REPEL) * 0.08
          p.vx += (mdx / mdist) * f
          p.vy += (mdy / mdist) * f
        }

        // dampen speed
        p.vx *= 0.99
        p.vy *= 0.99

        p.x += p.vx
        p.y += p.vy

        // wrap edges
        if (p.x < 0) p.x += W
        if (p.x > W) p.x -= W
        if (p.y < 0) p.y += H
        if (p.y > H) p.y -= H

        ctx.beginPath()
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
        ctx.fillStyle = 'rgba(139,92,246,0.75)'
        ctx.fill()
      })

      // --- draw connecting lines ---
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const a = particles[i]
          const b = particles[j]
          const dx = a.x - b.x
          const dy = a.y - b.y
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < CONNECT_DIST) {
            const alpha = (1 - dist / CONNECT_DIST) * 0.35
            ctx.beginPath()
            ctx.moveTo(a.x, a.y)
            ctx.lineTo(b.x, b.y)
            ctx.strokeStyle = `rgba(139,92,246,${alpha})`
            ctx.lineWidth = 0.8
            ctx.stroke()
          }
        }
      }

      // --- draw click ripples ---
      for (let i = ripples.length - 1; i >= 0; i--) {
        const rp = ripples[i]
        const radius = (1 - rp.t) * CLICK_BURST_RADIUS * 1.2
        ctx.beginPath()
        ctx.arc(rp.x, rp.y, radius, 0, Math.PI * 2)
        ctx.strokeStyle = `rgba(167,139,250,${rp.t * 0.7})`
        ctx.lineWidth = 1.5
        ctx.stroke()
        rp.t -= 0.022
        if (rp.t <= 0) ripples.splice(i, 1)
      }

      animId = requestAnimationFrame(draw)
    }

    resize()
    window.addEventListener('resize', resize)
    window.addEventListener('mousemove', onMouseMove)
    window.addEventListener('click', onClick)
    draw()

    return () => {
      cancelAnimationFrame(animId)
      window.removeEventListener('resize', resize)
      window.removeEventListener('mousemove', onMouseMove)
      window.removeEventListener('click', onClick)
    }
  }, [])

  return <canvas ref={canvasRef} className="bg-canvas" />
}
