#!/usr/bin/env python3
"""Generate high-quality preschool vehicle matching cards as SVG→PNG."""
from pathlib import Path
import subprocess

OUT = Path("/workspace/animal-match/assets")
W, H = 656, 376
RX = 48  # corner radius of outer card
BORDER = 14


def card_shell(border_color, bg_color, soft_bg2=None):
    """White outside, rounded card with thick border + soft pastel fill + subtle grain."""
    bg2 = soft_bg2 or bg_color
    return f'''
  <!-- outside white -->
  <rect width="{W}" height="{H}" fill="#ffffff"/>
  <!-- soft outer shadow of card -->
  <rect x="10" y="12" width="{W-20}" height="{H-20}" rx="{RX}" ry="{RX}" fill="#00000018"/>
  <!-- border -->
  <rect x="8" y="8" width="{W-16}" height="{H-16}" rx="{RX}" ry="{RX}" fill="{border_color}"/>
  <!-- inner pastel -->
  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{bg_color}"/>
      <stop offset="100%" stop-color="{bg2}"/>
    </linearGradient>
    <filter id="softShadow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="6"/>
      <feOffset dx="0" dy="6" result="off"/>
      <feComponentTransfer><feFuncA type="linear" slope="0.28"/></feComponentTransfer>
      <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="grain">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" result="noise"/>
      <feColorMatrix type="matrix" values="0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0.04 0"/>
      <feBlend in="SourceGraphic" mode="overlay"/>
    </filter>
  </defs>
  <rect x="{8+BORDER}" y="{8+BORDER}" width="{W-16-2*BORDER}" height="{H-16-2*BORDER}"
        rx="{RX-10}" ry="{RX-10}" fill="url(#bgGrad)"/>
  <rect x="{8+BORDER}" y="{8+BORDER}" width="{W-16-2*BORDER}" height="{H-16-2*BORDER}"
        rx="{RX-10}" ry="{RX-10}" fill="#ffffff" opacity="0.08"/>
'''


def face(cx, cy, scale=1.0, smile=True):
    e = 9 * scale
    gap = 22 * scale
    return f'''
  <g>
    <circle cx="{cx-gap/2}" cy="{cy}" r="{e}" fill="#1a1a1a"/>
    <circle cx="{cx+gap/2}" cy="{cy}" r="{e}" fill="#1a1a1a"/>
    <circle cx="{cx-gap/2-2*scale}" cy="{cy-2.5*scale}" r="{3*scale}" fill="#ffffff"/>
    <circle cx="{cx+gap/2-2*scale}" cy="{cy-2.5*scale}" r="{3*scale}" fill="#ffffff"/>
    {"<path d='M %s %s Q %s %s %s %s' fill='none' stroke='#1a1a1a' stroke-width='%s' stroke-linecap='round'/>" % (
      cx-10*scale, cy+12*scale, cx, cy+20*scale, cx+10*scale, cy+12*scale, 2.8*scale
    ) if smile else ""}
  </g>
'''


def svg_wrap(inner):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
{inner}
</svg>
'''


def car():
    # friendly red car, cream bg, coral border
    body = f'''
{card_shell("#E07A5F", "#FFF6EE", "#FFE8D6")}
  <g filter="url(#softShadow)" transform="translate(0,8)">
    <!-- shadow oval -->
    <ellipse cx="328" cy="300" rx="160" ry="14" fill="#00000022"/>
    <!-- body -->
    <defs>
      <linearGradient id="carBody" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#FF6B5A"/>
        <stop offset="55%" stop-color="#E8453C"/>
        <stop offset="100%" stop-color="#C92A2A"/>
      </linearGradient>
      <linearGradient id="carRoof" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#FF8A7A"/>
        <stop offset="100%" stop-color="#E8453C"/>
      </linearGradient>
      <linearGradient id="win" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#D6F0FF"/>
        <stop offset="100%" stop-color="#7EC8E8"/>
      </linearGradient>
    </defs>
    <!-- cabin/roof -->
    <path d="M210 168 Q210 130 250 130 L390 130 Q430 130 430 168 L430 200 L210 200 Z"
          fill="url(#carRoof)" stroke="#B8322A" stroke-width="4" stroke-linejoin="round"/>
    <!-- windows -->
    <rect x="230" y="145" width="70" height="42" rx="10" fill="url(#win)" stroke="#5BA3C4" stroke-width="2.5"/>
    <rect x="320" y="145" width="70" height="42" rx="10" fill="url(#win)" stroke="#5BA3C4" stroke-width="2.5"/>
    <!-- highlight on windows -->
    <rect x="236" y="150" width="18" height="28" rx="6" fill="#ffffff" opacity="0.45"/>
    <rect x="326" y="150" width="18" height="28" rx="6" fill="#ffffff" opacity="0.45"/>
    <!-- main body -->
    <rect x="145" y="195" width="370" height="95" rx="38" fill="url(#carBody)" stroke="#A61E1E" stroke-width="4"/>
    <!-- body highlight -->
    <path d="M175 210 Q328 200 480 210" fill="none" stroke="#ffffff" stroke-width="10" opacity="0.28" stroke-linecap="round"/>
    <!-- headlights -->
    <ellipse cx="155" cy="232" rx="16" ry="18" fill="#FFE566" stroke="#E0B800" stroke-width="2.5"/>
    <ellipse cx="505" cy="232" rx="16" ry="18" fill="#FFE566" stroke="#E0B800" stroke-width="2.5"/>
    <ellipse cx="152" cy="228" rx="5" ry="6" fill="#ffffff" opacity="0.7"/>
    <ellipse cx="502" cy="228" rx="5" ry="6" fill="#ffffff" opacity="0.7"/>
    <!-- wheels -->
    <circle cx="230" cy="290" r="32" fill="#2D2D32" stroke="#1A1A1E" stroke-width="3"/>
    <circle cx="230" cy="290" r="16" fill="#8A8A96"/>
    <circle cx="230" cy="290" r="7" fill="#C8C8D0"/>
    <circle cx="430" cy="290" r="32" fill="#2D2D32" stroke="#1A1A1E" stroke-width="3"/>
    <circle cx="430" cy="290" r="16" fill="#8A8A96"/>
    <circle cx="430" cy="290" r="7" fill="#C8C8D0"/>
    {face(328, 235, 1.05)}
  </g>
'''
    return svg_wrap(body)


def garage():
    body = f'''
{card_shell("#C4A484", "#FFF8F0", "#F5E6D3")}
  <g filter="url(#softShadow)" transform="translate(0,6)">
    <ellipse cx="328" cy="310" rx="150" ry="12" fill="#0000001a"/>
    <defs>
      <linearGradient id="roof" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#E85D4C"/>
        <stop offset="100%" stop-color="#C0392B"/>
      </linearGradient>
      <linearGradient id="wall" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#FFF5E6"/>
        <stop offset="100%" stop-color="#E8D5B8"/>
      </linearGradient>
      <linearGradient id="door" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#6B8CAE"/>
        <stop offset="100%" stop-color="#3D5A7A"/>
      </linearGradient>
    </defs>
    <!-- roof -->
    <path d="M160 155 L328 95 L496 155 Z" fill="url(#roof)" stroke="#9B2C1F" stroke-width="4" stroke-linejoin="round"/>
    <!-- roof highlight -->
    <path d="M200 148 L328 108 L380 128" fill="none" stroke="#ffffff" stroke-width="6" opacity="0.3" stroke-linecap="round"/>
    <!-- walls -->
    <rect x="180" y="150" width="296" height="155" rx="8" fill="url(#wall)" stroke="#C4A484" stroke-width="3.5"/>
    <!-- door -->
    <rect x="230" y="185" width="196" height="120" rx="6" fill="url(#door)" stroke="#2C3E50" stroke-width="3"/>
    <!-- door panels -->
    <line x1="328" y1="190" x2="328" y2="300" stroke="#2C3E50" stroke-width="2.5" opacity="0.5"/>
    <line x1="235" y1="225" x2="421" y2="225" stroke="#2C3E50" stroke-width="2.5" opacity="0.5"/>
    <line x1="235" y1="260" x2="421" y2="260" stroke="#2C3E50" stroke-width="2.5" opacity="0.5"/>
    <!-- door handle -->
    <circle cx="400" cy="245" r="7" fill="#F4D35E" stroke="#C9A227" stroke-width="2"/>
    <!-- foundation -->
    <rect x="165" y="300" width="326" height="18" rx="4" fill="#B8B8C0" stroke="#8A8A96" stroke-width="2"/>
    <!-- little window above door -->
    <rect x="300" y="160" width="56" height="18" rx="4" fill="#A8D8EA" stroke="#5BA3C4" stroke-width="2"/>
  </g>
'''
    return svg_wrap(body)


def boat():
    body = f'''
{card_shell("#4A90A4", "#F0FAFC", "#D6F0F5")}
  <g filter="url(#softShadow)" transform="translate(0,4)">
    <defs>
      <linearGradient id="hull" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#5BB8D4"/>
        <stop offset="100%" stop-color="#2E7A9A"/>
      </linearGradient>
      <linearGradient id="sail" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#FFF6A8"/>
        <stop offset="100%" stop-color="#F0C gener"/>
      </linearGradient>
      <linearGradient id="wave" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#7EC8E8"/>
        <stop offset="100%" stop-color="#4A9BC4"/>
      </linearGradient>
    </defs>
    <!-- waves -->
    <path d="M80 300 Q130 280 180 300 Q230 320 280 300 Q330 280 380 300 Q430 320 480 300 Q530 280 580 300 L580 330 L80 330 Z"
          fill="url(#wave)" opacity="0.55"/>
    <path d="M100 315 Q150 298 200 315 Q250 332 300 315 Q350 298 400 315 Q450 332 500 315 Q540 300 570 315"
          fill="none" stroke="#ffffff" stroke-width="4" opacity="0.35" stroke-linecap="round"/>
    <!-- mast -->
    <rect x="318" y="85" width="10" height="175" rx="4" fill="#A67C52" stroke="#7A5635" stroke-width="2"/>
    <!-- sail -->
    <path d="M328 95 L328 230 L455 230 Z" fill="#FFE566" stroke="#D4A017" stroke-width="3.5" stroke-linejoin="round"/>
    <path d="M335 115 L335 215 L420 215 Z" fill="#ffffff" opacity="0.35"/>
    <!-- cabin -->
    <rect x="250" y="200" width="70" height="50" rx="10" fill="#FFF8F0" stroke="#C4A484" stroke-width="3"/>
    <rect x="262" y="212" width="46" height="28" rx="6" fill="#A8D8EA" stroke="#5BA3C4" stroke-width="2"/>
    <rect x="268" y="216" width="12" height="18" rx="3" fill="#ffffff" opacity="0.5"/>
    <!-- hull -->
    <path d="M145 250 L200 250 L230 310 L440 310 L500 250 L455 250 Z"
          fill="url(#hull)" stroke="#1E5A72" stroke-width="4" stroke-linejoin="round"/>
    <!-- hull highlight -->
    <path d="M200 262 L450 262" fill="none" stroke="#ffffff" stroke-width="8" opacity="0.25" stroke-linecap="round"/>
    {face(320, 275, 0.95)}
  </g>
'''
    # fix typo in sail gradient
    body = body.replace('stop-color="#F0C gener"', 'stop-color="#F0C84A"')
    return svg_wrap(body)


def water():
    body = f'''
{card_shell("#3D8B9C", "#E8F7FA", "#C8EBF2")}
  <g filter="url(#softShadow)">
    <defs>
      <linearGradient id="pond" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#7ED6E8"/>
        <stop offset="50%" stop-color="#3FA8C4"/>
        <stop offset="100%" stop-color="#2A7A94"/>
      </linearGradient>
      <radialGradient id="shine" cx="0.35" cy="0.3" r="0.55">
        <stop offset="0%" stop-color="#ffffff" stop-opacity="0.55"/>
        <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <!-- pond oval -->
    <ellipse cx="328" cy="200" rx="210" ry="110" fill="url(#pond)" stroke="#1E5A72" stroke-width="5"/>
    <ellipse cx="328" cy="200" rx="210" ry="110" fill="url(#shine)"/>
    <!-- wave lines -->
    <path d="M170 185 Q230 165 290 185 Q350 205 410 185 Q460 170 500 185"
          fill="none" stroke="#ffffff" stroke-width="5" opacity="0.4" stroke-linecap="round"/>
    <path d="M190 220 Q250 205 310 220 Q370 235 430 220 Q470 210 500 220"
          fill="none" stroke="#ffffff" stroke-width="4" opacity="0.28" stroke-linecap="round"/>
    <!-- sparkles -->
    <circle cx="240" cy="155" r="6" fill="#ffffff" opacity="0.7"/>
    <circle cx="420" cy="160" r="4" fill="#ffffff" opacity="0.6"/>
    <circle cx="360" cy="240" r="5" fill="#ffffff" opacity="0.45"/>
    <!-- friendly droplet face optional: small splash drops -->
    <ellipse cx="175" cy="130" rx="18" ry="26" fill="#5BB8D4" stroke="#2E7A9A" stroke-width="2.5" transform="rotate(-15 175 130)"/>
    <ellipse cx="480" cy="125" rx="14" ry="20" fill="#7ED6E8" stroke="#2E7A9A" stroke-width="2.5" transform="rotate(18 480 125)"/>
    <ellipse cx="170" cy="122" rx="5" ry="7" fill="#ffffff" opacity="0.5" transform="rotate(-15 170 122)"/>
  </g>
'''
    return svg_wrap(body)


def plane():
    body = f'''
{card_shell("#5B8DEF", "#F2F7FF", "#DCE9FF")}
  <g filter="url(#softShadow)" transform="translate(0,10)">
    <defs>
      <linearGradient id="fuse" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="#A8D4FF"/>
        <stop offset="40%" stop-color="#6BB0F0"/>
        <stop offset="100%" stop-color="#3D7FD4"/>
      </linearGradient>
      <linearGradient id="wing" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#4A6FBF"/>
        <stop offset="100%" stop-color="#2E4A8A"/>
      </linearGradient>
    </defs>
    <ellipse cx="340" cy="300" rx="170" ry="12" fill="#00000018"/>
    <!-- wing back -->
    <ellipse cx="340" cy="210" rx="55" ry="18" fill="#3D5A9A" stroke="#2A3F70" stroke-width="2" transform="rotate(-8 340 210)" opacity="0.5"/>
    <!-- fuselage -->
    <ellipse cx="330" cy="200" rx="195" ry="55" fill="url(#fuse)" stroke="#2A5A9A" stroke-width="4"/>
    <!-- fuselage highlight -->
    <ellipse cx="300" cy="180" rx="120" ry="18" fill="#ffffff" opacity="0.3"/>
    <!-- nose cone -->
    <ellipse cx="510" cy="200" rx="28" ry="32" fill="#C8DFF5" stroke="#2A5A9A" stroke-width="3"/>
    <ellipse cx="520" cy="195" rx="8" ry="10" fill="#ffffff" opacity="0.5"/>
    <!-- windows -->
    <ellipse cx="250" cy="190" rx="12" ry="16" fill="#D6F0FF" stroke="#3D7FD4" stroke-width="2"/>
    <ellipse cx="290" cy="188" rx="12" ry="16" fill="#D6F0FF" stroke="#3D7FD4" stroke-width="2"/>
    <ellipse cx="330" cy="187" rx="12" ry="16" fill="#D6F0FF" stroke="#3D7FD4" stroke-width="2"/>
    <ellipse cx="370" cy="188" rx="12" ry="16" fill="#D6F0FF" stroke="#3D7FD4" stroke-width="2"/>
    <ellipse cx="410" cy="190" rx="12" ry="16" fill="#D6F0FF" stroke="#3D7FD4" stroke-width="2"/>
    <!-- main wing -->
    <path d="M240 215 L340 200 L440 215 L400 255 L280 255 Z" fill="url(#wing)" stroke="#1E3560" stroke-width="3.5" stroke-linejoin="round"/>
    <path d="M300 218 L380 218" fill="none" stroke="#ffffff" stroke-width="5" opacity="0.2" stroke-linecap="round"/>
    <!-- tail fin -->
    <path d="M145 150 L175 200 L145 210 Z" fill="#E85D4C" stroke="#9B2C1F" stroke-width="3" stroke-linejoin="round"/>
    <path d="M145 200 L175 200 L160 230 Z" fill="#E85D4C" stroke="#9B2C1F" stroke-width="2.5" stroke-linejoin="round"/>
    <!-- face on nose -->
    {face(475, 200, 0.85)}
  </g>
'''
    return svg_wrap(body)


def cloud():
    body = f'''
{card_shell("#7EB6E8", "#F5FAFF", "#E0F0FF")}
  <g filter="url(#softShadow)">
    <defs>
      <linearGradient id="cld" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#FFFFFF"/>
        <stop offset="100%" stop-color="#D4E8FA"/>
      </linearGradient>
    </defs>
    <!-- soft blue sky hint already in bg -->
    <!-- main cloud puffs -->
    <g>
      <ellipse cx="250" cy="210" rx="70" ry="55" fill="url(#cld)" stroke="#A8C8E0" stroke-width="3"/>
      <ellipse cx="320" cy="175" rx="85" ry="70" fill="url(#cld)" stroke="#A8C8E0" stroke-width="3"/>
      <ellipse cx="400" cy="205" rx="75" ry="58" fill="url(#cld)" stroke="#A8C8E0" stroke-width="3"/>
      <ellipse cx="340" cy="230" rx="100" ry="55" fill="url(#cld)" stroke="#A8C8E0" stroke-width="3"/>
      <ellipse cx="280" cy="225" rx="60" ry="45" fill="url(#cld)"/>
      <!-- soft highlight -->
      <ellipse cx="300" cy="165" rx="40" ry="22" fill="#ffffff" opacity="0.7"/>
      <ellipse cx="380" cy="185" rx="28" ry="16" fill="#ffffff" opacity="0.5"/>
    </g>
    <!-- tiny friendly sparkles -->
    <circle cx="200" cy="140" r="5" fill="#FFE566" opacity="0.8"/>
    <circle cx="470" cy="150" r="4" fill="#FFE566" opacity="0.7"/>
  </g>
'''
    return svg_wrap(body)


def train():
    body = f'''
{card_shell("#E07A4A", "#FFF5EE", "#FFE4D0")}
  <g filter="url(#softShadow)" transform="translate(0,6)">
    <defs>
      <linearGradient id="eng" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#FF6B4A"/>
        <stop offset="100%" stop-color="#C0392B"/>
      </linearGradient>
      <linearGradient id="cab" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#FF8A6A"/>
        <stop offset="100%" stop-color="#E8453C"/>
      </linearGradient>
    </defs>
    <ellipse cx="330" cy="310" rx="180" ry="12" fill="#00000018"/>
    <!-- tender / car behind -->
    <rect x="120" y="195" width="95" height="85" rx="14" fill="#5BA3C4" stroke="#2E6A8A" stroke-width="3.5"/>
    <rect x="135" y="210" width="65" height="40" rx="8" fill="#A8D8EA" stroke="#3D7FA0" stroke-width="2"/>
    <rect x="142" y="215" width="16" height="28" rx="4" fill="#ffffff" opacity="0.45"/>
    <!-- coupler -->
    <rect x="210" y="230" width="25" height="14" rx="4" fill="#6B6B75" stroke="#3D3D45" stroke-width="2"/>
    <!-- engine body -->
    <rect x="230" y="185" width="230" height="100" rx="28" fill="url(#eng)" stroke="#8B1E14" stroke-width="4"/>
    <path d="M255 200 Q345 190 440 200" fill="none" stroke="#ffffff" stroke-width="9" opacity="0.28" stroke-linecap="round"/>
    <!-- cab on top -->
    <rect x="380" y="130" width="90" height="65" rx="12" fill="url(#cab)" stroke="#8B1E14" stroke-width="3.5"/>
    <rect x="395" y="145" width="60" height="38" rx="8" fill="#A8D8EA" stroke="#3D7FA0" stroke-width="2.5"/>
    <rect x="402" y="150" width="14" height="26" rx="4" fill="#ffffff" opacity="0.5"/>
    <!-- smokestack -->
    <rect x="265" y="115" width="32" height="75" rx="8" fill="#5A5A65" stroke="#2D2D35" stroke-width="3"/>
    <ellipse cx="281" cy="115" rx="22" ry="12" fill="#8A8A96" stroke="#2D2D35" stroke-width="2.5"/>
    <!-- smoke puffs -->
    <circle cx="275" cy="95" r="14" fill="#E8E8EE" opacity="0.85"/>
    <circle cx="295" cy="78" r="18" fill="#F0F0F5" opacity="0.7"/>
    <circle cx="318" cy="68" r="12" fill="#F5F5FA" opacity="0.55"/>
    <!-- cowcatcher -->
    <path d="M460 250 L520 285 L460 285 Z" fill="#6B6B75" stroke="#3D3D45" stroke-width="2.5" stroke-linejoin="round"/>
    <!-- wheels -->
    <circle cx="280" cy="290" r="26" fill="#2D2D32" stroke="#1A1A1E" stroke-width="3"/>
    <circle cx="280" cy="290" r="12" fill="#8A8A96"/>
    <circle cx="350" cy="290" r="26" fill="#2D2D32" stroke="#1A1A1E" stroke-width="3"/>
    <circle cx="350" cy="290" r="12" fill="#8A8A96"/>
    <circle cx="420" cy="290" r="26" fill="#2D2D32" stroke="#1A1A1E" stroke-width="3"/>
    <circle cx="420" cy="290" r="12" fill="#8A8A96"/>
    <circle cx="160" cy="285" r="22" fill="#2D2D32" stroke="#1A1A1E" stroke-width="3"/>
    <circle cx="160" cy="285" r="10" fill="#8A8A96"/>
    {face(340, 230, 1.0)}
  </g>
'''
    return svg_wrap(body)


def tracks():
    body = f'''
{card_shell("#8B7355", "#FFF8F0", "#F0E6D8")}
  <g filter="url(#softShadow)">
    <defs>
      <linearGradient id="rail" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#A0A0AA"/>
        <stop offset="100%" stop-color="#5A5A68"/>
      </linearGradient>
      <linearGradient id="tie" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#C4A484"/>
        <stop offset="100%" stop-color="#8B6914"/>
      </linearGradient>
    </defs>
    <!-- ground hint -->
    <ellipse cx="328" cy="280" rx="220" ry="40" fill="#E8D5B8" opacity="0.45"/>
    <!-- ties (sleepers) -->
'''
    for i, x in enumerate(range(120, 540, 48)):
        body += f'    <rect x="{x}" y="155" width="28" height="140" rx="6" fill="url(#tie)" stroke="#6B4F2A" stroke-width="2" transform="rotate(0)"/>\n'
        # Actually ties should be horizontal across rails - rails go left-right, ties perpendicular
    # Rewrite tracks properly - horizontal rails with cross ties
    body = f'''
{card_shell("#8B7355", "#FFF8F0", "#F0E6D8")}
  <g filter="url(#softShadow)">
    <defs>
      <linearGradient id="rail" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#C0C0C8"/>
        <stop offset="100%" stop-color="#5A5A68"/>
      </linearGradient>
      <linearGradient id="tie" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#D4B896"/>
        <stop offset="100%" stop-color="#8B6914"/>
      </linearGradient>
    </defs>
    <ellipse cx="328" cy="290" rx="230" ry="28" fill="#00000012"/>
'''
    # horizontal ties
    for y in range(130, 280, 36):
        body += f'    <rect x="110" y="{y}" width="436" height="22" rx="5" fill="url(#tie)" stroke="#6B4F2A" stroke-width="2"/>\n'
    # two rails
    body += '''
    <rect x="175" y="115" width="22" height="185" rx="6" fill="url(#rail)" stroke="#3D3D45" stroke-width="2.5"/>
    <rect x="459" y="115" width="22" height="185" rx="6" fill="url(#rail)" stroke="#3D3D45" stroke-width="2.5"/>
    <!-- rail highlights -->
    <rect x="179" y="120" width="6" height="170" rx="2" fill="#ffffff" opacity="0.35"/>
    <rect x="463" y="120" width="6" height="170" rx="2" fill="#ffffff" opacity="0.35"/>
    <!-- perspective: make it look more like tracks going away - add slight taper via additional shape -->
    <!-- friendly spike bolts -->
'''
    for y in range(140, 270, 36):
        body += f'    <circle cx="186" cy="{y}" r="4" fill="#F4D35E" stroke="#C9A227" stroke-width="1.5"/>\n'
        body += f'    <circle cx="470" cy="{y}" r="4" fill="#F4D35E" stroke="#C9A227" stroke-width="1.5"/>\n'
    body += '  </g>\n'
    return svg_wrap(body)


CARDS = {
    "car": car,
    "garage": garage,
    "boat": boat,
    "water": water,
    "plane": plane,
    "cloud": cloud,
    "train": train,
    "tracks": tracks,
}


def main():
    svg_dir = Path("/workspace/animal-match/gen/svg")
    svg_dir.mkdir(parents=True, exist_ok=True)
    for name, fn in CARDS.items():
        svg_path = svg_dir / f"{name}.svg"
        svg_path.write_text(fn(), encoding="utf-8")
        png_path = OUT / f"{name}.png"
        # Render with ImageMagick at exact size
        cmd = [
            "magick",
            "-background", "none",
            str(svg_path),
            "-resize", f"{W}x{H}!",
            "-strip",
            str(png_path),
        ]
        print("Rendering", name, "...")
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print("ERR", name, r.stderr)
        else:
            print("OK", name, png_path.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
