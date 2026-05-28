// Canonical mesh-gradient hero-background — ultra-modern-lovable-style
// Uses Paper Shaders (declarative React, MIT-licensed).
// Install: npm i @paper-design/shaders-react

import { MeshGradient } from '@paper-design/shaders-react'
import { useEffect, useRef, useState } from 'react'

type MeshGradientHeroProps = {
  colors?: [string, string, string]
  className?: string
}

export function MeshGradientHero({
  colors = ['#0078D4', '#50E6FF', '#0d1b2a'],
  className = ''
}: MeshGradientHeroProps) {
  const ref = useRef<HTMLDivElement>(null)
  const [isVisible, setIsVisible] = useState(true)
  const [reducedMotion, setReducedMotion] = useState(false)

  // IntersectionObserver pause (perf-budget)
  useEffect(() => {
    if (!ref.current) return
    const obs = new IntersectionObserver(
      ([entry]) => setIsVisible(entry.isIntersecting),
      { threshold: 0.01 }
    )
    obs.observe(ref.current)
    return () => obs.disconnect()
  }, [])

  // prefers-reduced-motion respect
  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    setReducedMotion(mq.matches)
    const handler = (e: MediaQueryListEvent) => setReducedMotion(e.matches)
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [])

  // CSS fallback for no-WebGL (rare)
  if (typeof window !== 'undefined' && !('WebGLRenderingContext' in window)) {
    return (
      <div
        className={className}
        style={{
          background: `conic-gradient(from 180deg at 50% 50%, ${colors[0]}, ${colors[1]}, ${colors[2]}, ${colors[0]})`,
          filter: 'blur(60px)'
        }}
      />
    )
  }

  return (
    <div ref={ref} className={className}>
      <MeshGradient
        colors={colors}
        speed={reducedMotion ? 0 : 0.3}
        distortion={0.8}
        swirl={0.4}
        // Mobile downscale handled internally by Paper Shaders
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  )
}

/*
Usage in hero section:

<section className="relative min-h-screen">
  <MeshGradientHero className="absolute inset-0 -z-10" />
  <div className="relative z-10 container mx-auto pt-32">
    <h1 className="font-serif text-7xl">Your headline</h1>
  </div>
</section>
*/
