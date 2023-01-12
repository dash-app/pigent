#!/usr/bin/python3

import time
import pigpio
import collections


def send(gpio: int, signal: []) -> None:
    """ Send IR Signal """

    pi = pigpio.pi()
    if not pi.connected:
        raise RuntimeError('failed connect to pigpio')

    freq = 38.0
    pi.set_mode(gpio, pigpio.OUTPUT)

    pi.wave_add_new()

    emit_time = time.time()
    marks_wid = {}
    spaces_wid = {}
    wave = [0]*len(signal)

    for i in range(len(signal)):
        ci = signal[i]
        if i & 1:
            if ci not in spaces_wid:
                pi.wave_add_generic([pigpio.pulse(0, 0, ci)])
                spaces_wid[ci] = pi.wave_create()
            wave[i] = spaces_wid[ci]
        else:
            if ci not in marks_wid:
                wf = carrier(gpio, freq, ci)
                pi.wave_add_generic(wf)
                marks_wid[ci] = pi.wave_create()
            wave[i] = marks_wid[ci]

    delay = emit_time - time.time()
    if delay > 0.0:
        time.sleep(delay)

    wave = compress_wave(wave)
    pi.wave_chain(wave)

    while pi.wave_tx_busy():
        time.sleep(0.002)

    gap_s = 100 / 1000.0
    emit_time = time.time() + gap_s

    for i in marks_wid:
        pi.wave_delete(marks_wid[i])
    marks_wid = {}

    for i in spaces_wid:
        pi.wave_delete(spaces_wid[i])
    spaces_wid = {}

    pi.stop()
    return


def carrier(gpio, frequency, micros) -> []:
    wf = []
    cycle = 1000.0 / frequency
    cycles = int(round(micros/cycle))
    on = int(round(cycle / 2.0))
    sofar = 0
    for c in range(cycles):
        target = int(round((c + 1) * cycle))
        sofar += on
        off = target - sofar
        sofar += off
        wf.append(pigpio.pulse(1 << gpio, 0, on))
        wf.append(pigpio.pulse(0, 1 << gpio, off))
    return wf


def compress_wave(code):
    MAX_ENTRY = 600
    MAX_LOOP = 20

    if len(code) < MAX_ENTRY:
        return code

    def ngram(l, n):
        return list(zip(*(l[i:] for i in range(n))))

    # (start, size) => count(continuous)
    dic = {}
    for size in range(2, 8 + 1, 2):
        # order by descending
        freqs = collections.Counter(ngram(code, size)).most_common()
        for block, count in freqs:
            if count < 2:
                break
            block = list(block)
            for i in range(len(code) - size + 1):
                if code[i:i+size] != block:
                    continue
                # count continuous blocks
                for c in range(2, count + 1):
                    if code[i+size*(c-1):i+size*c] == block:
                        dic[(i, size)] = c
                    else:
                        break

    # select compressable blocks
    blocks = [(start, size, count) for (start, size),
              count in dic.items() if count > 1 and size * count > 6]

    if len(blocks) == 0:
        return code

    # order by efficiency
    # => order by compressable length(descending), then by unit block size(ascending)
    blocks = sorted(blocks, key=lambda b: (b[1] * b[2], -b[1]), reverse=True)

    # excluding overlaps
    cands = [0]
    for i in range(1, len(blocks)):
        if len(cands) >= MAX_LOOP:
            break
        astart, asize, acount = blocks[i]
        aend = astart + asize * acount - 1
        valid = True
        for j in cands:
            bstart, bsize, bcount = blocks[j]
            bend = bstart + bsize * bcount - 1
            if astart <= bend and aend >= bstart:
                valid = False
                break
        if valid:
            cands.append(i)

    # order by starting index
    # then compressing blocks
    for start, size, count in sorted([blocks[i] for i in cands], key=lambda b: b[0], reverse=True):
        div, mod = count // 256, count % 256
        code[start:start+size*count] = [255, 0] + \
            code[start:start+size] + [255, 1, mod, div]

    return code
