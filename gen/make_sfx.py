#!/usr/bin/env python3
"""Build three short preschool sound effects (stdlib only).

  assets/sfx-tap.wav      soft light tick
  assets/sfx-success.wav  short xylophone "yes" (C-E-G)
  assets/sfx-wrong.wav    soft two-syllable "oops" (falling, not a buzzer)

16-bit PCM mono WAV so iPad Safari can decode them without a build step.
"""

import math
import os
import struct
import wave

RATE = 22050
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_DIR = os.path.join(ROOT, "assets")


def clamp(x, lo=-1.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x


def write_wav(name, samples):
    path = os.path.join(OUT_DIR, name)
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        frames = bytearray()
        peak = 0.0
        for s in samples:
            a = abs(s)
            if a > peak:
                peak = a
        # Leave headroom. Levels are also trimmed again in the page.
        scale = 0.9 / peak if peak > 0.9 else 1.0
        for s in samples:
            v = int(clamp(s * scale) * 32767.0)
            frames += struct.pack("<h", v)
        w.writeframes(frames)
    dur = len(samples) / RATE
    print(f"{name}: {dur:.3f}s  peak_in={peak:.3f}  bytes={os.path.getsize(path)}")


def fade_ends(samples, fade_in=0.004, fade_out=0.012):
    n_in = int(fade_in * RATE)
    n_out = int(fade_out * RATE)
    n = len(samples)
    for i in range(min(n_in, n)):
        samples[i] *= i / n_in
    for i in range(min(n_out, n)):
        samples[n - 1 - i] *= i / n_out
    if n:
        samples[0] = 0.0
        samples[-1] = 0.0
    return samples


def lowpass(samples, cutoff_hz):
    # One-pole lowpass. Gentle, to take the edge off noise bursts.
    rc = 1.0 / (2.0 * math.pi * cutoff_hz)
    dt = 1.0 / RATE
    a = dt / (rc + dt)
    out = []
    y = 0.0
    for s in samples:
        y += a * (s - y)
        out.append(y)
    return out


def silence(seconds):
    return [0.0] * int(seconds * RATE)


def add_into(buf, start_s, samples):
    start = int(start_s * RATE)
    for i, s in enumerate(samples):
        idx = start + i
        if 0 <= idx < len(buf):
            buf[idx] += s
    return buf


def mallet_note(freq, dur, amp=1.0, tau=0.09):
    n = int(dur * RATE)
    out = [0.0] * n
    # Slightly inharmonic upper partials, like a soft wood bar, not a buzzer.
    partials = (
        (1.0, amp, tau),
        (2.01, amp * 0.22, tau * 0.55),
        (3.03, amp * 0.07, tau * 0.32),
    )
    attack = int(0.004 * RATE)
    for k, p_amp, p_tau in partials:
        for i in range(n):
            t = i / RATE
            env = 1.0 - math.exp(-i / max(1, attack / 3))
            env *= math.exp(-t / p_tau)
            out[i] += math.sin(2.0 * math.pi * freq * k * t) * p_amp * env
    # Tiny mallet tick (filtered noise), very quiet.
    tick_n = int(0.008 * RATE)
    noise = []
    seed = int(freq * 10) % 10007 or 1
    for i in range(tick_n):
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        noise.append(((seed / 0x7FFFFFFF) * 2.0 - 1.0) * amp * 0.05 * (1.0 - i / tick_n))
    noise = lowpass(noise, 1800.0)
    for i, s in enumerate(noise):
        out[i] += s
    return fade_ends(out, 0.003, 0.02)


def make_tap():
    """Soft tick: a short rounded knock, not a sharp mouse click."""
    dur = 0.09
    n = int(dur * RATE)
    out = [0.0] * n
    # Two quick decaying tones a fifth-ish apart, low enough to stay gentle.
    tones = ((680.0, 0.55, 0.018), (1020.0, 0.28, 0.010))
    for freq, amp, tau in tones:
        for i in range(n):
            t = i / RATE
            env = math.exp(-t / tau)
            out[i] += math.sin(2.0 * math.pi * freq * t) * amp * env
    tick = []
    seed = 17
    tick_n = int(0.006 * RATE)
    for i in range(tick_n):
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        tick.append(((seed / 0x7FFFFFFF) * 2.0 - 1.0) * 0.12 * (1.0 - i / tick_n))
    tick = lowpass(tick, 2200.0)
    for i, s in enumerate(tick):
        out[i] += s
    # Light, but loud enough to hear on an iPad speaker at the page volume.
    out = [s * 0.62 for s in out]
    return fade_ends(out, 0.002, 0.018)


def make_success():
    """Ascending major triad, toy-xylophone short. Fun, not a fanfare."""
    # C5 E5 G5 — comfortable register, not piercing.
    notes = (
        (0.00, 523.25, 0.62),
        (0.12, 659.25, 0.66),
        (0.24, 783.99, 0.72),
    )
    total = 0.50
    buf = silence(total)
    for start, freq, amp in notes:
        add_into(buf, start, mallet_note(freq, 0.26, amp=amp, tau=0.085))
    # Keep the chime clear without sitting near full scale.
    buf = [s * 0.75 for s in buf]
    return fade_ends(buf, 0.003, 0.03)


def syllable(freq0, freq1, dur, amp):
    """Rounded falling tone. Slow attack so it sighs instead of beeping."""
    n = int(dur * RATE)
    out = [0.0] * n
    attack = int(0.035 * RATE)
    release = int(0.07 * RATE)
    for i in range(n):
        t = i / RATE
        u = i / max(1, n - 1)
        # Exponential-ish glide downward.
        freq = freq0 * ((freq1 / freq0) ** u)
        if i < attack:
            env = i / attack
            env = env * env
        elif i > n - release:
            env = (n - i) / release
        else:
            env = 1.0
        # Warm: fundamental plus a quiet octave, no buzz partials.
        sample = math.sin(2.0 * math.pi * freq * t)
        sample += 0.16 * math.sin(2.0 * math.pi * freq * 2.0 * t)
        out[i] = sample * env * amp
    return out


def make_wrong():
    """Soft two-note 'oops': falling, rounded, short. Not a buzzer."""
    # G4 -> E4, then E4 -> C4. A small sigh, musical and low-irritation.
    total = 0.34
    buf = silence(total)
    add_into(buf, 0.00, syllable(392.0, 329.6, 0.18, 0.40))
    add_into(buf, 0.14, syllable(329.6, 261.6, 0.20, 0.34))
    return fade_ends(buf, 0.008, 0.03)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    write_wav("sfx-tap.wav", make_tap())
    write_wav("sfx-success.wav", make_success())
    write_wav("sfx-wrong.wav", make_wrong())


if __name__ == "__main__":
    main()
