#! /usr/bin/env python3

import sys
import re
import statistics
import os

def approx(num, expect):
    if num > expect * .9 and num < expect * 1.1:
        return True
    else:
        return False

class Signals:
    tolerance = .1
    def __init__(self):
        self.signals = dict() # i.e. { 'pulse': { '200': { ch: 'a', history: [198, 202] } } }
        self.last_char = 'a'

    def get_next_char(self):
        cur = self.last_char
        if cur == 'z':
            self.last_char = 'A'
            return cur
        if cur == 'Z':
            raise RuntimeError('out of characters')

        self.last_char = chr(ord(cur) + 1)
        return cur

    def add_number(self, all_nums, new_num):
        ch = self.get_next_char()
        all_nums[new_num] = { 'ch': ch, 'history': [new_num] }
        return ch

    def check_number(self, all_nums, to_check):
        for num in all_nums.keys():
            minn = num * (1 - self.tolerance)
            maxn = num * (1 + self.tolerance)
            if to_check > minn and to_check < maxn:
                all_nums[num]['history'].append(to_check)
                return all_nums[num]['ch']

        return self.add_number(all_nums, to_check)

    def add_noun(self, noun, number):
        ch = self.get_next_char()
        self.signals[noun] = { number: { 'ch': ch, 'history': [number] } }
        return ch

    def check(self, noun, number):
        a = self.signals.get(noun)
        if a is None:
            return self.add_noun(noun, number)
        else:
            return self.check_number(a, number)

    def dump(self):
        for k in self.signals.keys():
            print(f'{k}:')
            for n in self.signals[k]:
                d = self.signals[k][n]
                h = d['history']
                try:
                    stdev = f'{statistics.stdev(h):.2f}'
                except statistics.StatisticsError:
                    stdev = '-'
                print(f'  {d["ch"]}: {n}, {min(h)}-{max(h)} mean:{statistics.mean(h):.2f} stdev:{stdev} len:{len(h)}')

def split2(str_):
    rv = []
    cur = ''

    for i in str_:
        if len(cur) <= 1:
            cur += i
        else:
            rv.append(cur)
            cur = i

    if len(cur) > 0:
        rv.append(cur)

    return rv

def clipboard(val):
    try:
        os.system(f"echo -n {val} | xclip -in -selection clipboard > /dev/null 2>&1")
    except:
        pass

class Decoder:
    def __init__(self):
        self.guess_one = None
        self.guess_zero = None
        self.cur_str = ''

    def feed(self, char):
        self.cur_str += char

    def make_guesses(self, spl):
        counts = {}

        for p in spl:
            if counts.get(p) is None:
                counts[p] = 1
            else:
                counts[p] += 1

        if len(counts) < 2:
            # unable to guess when there's fewer than 2 pairs
            return

        sorted_ = sorted(counts, key=lambda x: counts[x])

        # I bet there's more zeroes than ones. Could be wrong.
        self.guess_zero = sorted_[-1]
        self.guess_one = sorted_[-2]

    def format(self, spl):
        res = ''
        in_num = False
        cur_num = ''

        for p in spl:
            if self.guess_zero == p:
                in_num = True
                cur_num += '0'
            elif self.guess_one == p:
                in_num = True
                cur_num += '1'
            else:
                if in_num:
                    val = hex(int(cur_num, 2))
                    res += f' {val}({len(cur_num)}bit) {p}'
                    clipboard(val)
                    cur_num = ''
                    in_num = False
                else:
                    res += p

        return res

    def print_formatted(self):
        spl = split2(self.cur_str)

        if self.guess_one is None:
            self.make_guesses(spl)
            print(f'guessing {self.guess_zero}=0, {self.guess_one}=1')

        print(self.format(spl))

    def end(self):
        if len(self.cur_str) % 2 == 1:
            print(self.cur_str, ' (odd)')
        else:
            self.print_formatted()

        self.cur_str = ''

def go(sigs):
    dec = Decoder()
    for line in sys.stdin:
        line = line.strip()
        m = re.fullmatch('^([a-z]*) ([0-9]*)$', line)
        if m is None:
            print(f"mode2_formatter warning: line '{line}' didn't match, ignoring")
            continue
        noun, num = m[1], int(m[2])
        dec.feed(sigs.check(noun, num))
        if noun == 'timeout':
            dec.end()

a = Signals()

try:
    go(a)
except KeyboardInterrupt:
    pass
except:
    raise
finally:
    print('\n===')
    a.dump()
    print('===')
