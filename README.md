This is a pretty printer for output from LIRC's `mode2`.

It's meant as a simple replacement for buggy and complicated `irrecord`.
Its aim is to make it easier to manually write LIRC configs for new
remotes.

On stdin it takes lines in the form of `<noun> <number>` (such as `pulse
1022`, `space 3310` or `timeout 10300` as produced by `mode2`) and
formats them nicely to make them easier to read for a human.

# Usage

This works for me, but your LIRC driver may be different:

```bash
mode2 --driver default | ./mode2_formatter.py
```

# Output format and features
Generally, each input line is converted to a single latin letter (a-z,
then A-Z). Following lines with similar numeric values (within ±10%,
configurable with the `tolerance` variable in the `Signals` class)
will print the same letter. At the end of the run (i.e. after ctrl-c
is pressed), the actual values along with some statistics are printed
for each letter.

`timeout` is handled in a special way: a newline is printed after
the letter corresponding to the timeout. For my remotes, these timeouts
always occur at the end of a button sequence, making it easy
to see which button produced which line.

## Guessing numeric values for bits
The first line (as created by the very first button press) of
letters (aka all the input pulse/space lines up to the first timeout)
is also handled in a special way. The number of transmitted
pulse/space pairs is counted. The largest number of those pairs
is guessed to mean binary '0', and the second-largest is guessed
to mean binary '1'. A line with the text 'guessing ..' is printed
which describes those guesses. From that point onward, whenever
a run of pulse/space pairs corresponding to those binary digits
is seen, it is converted to a hexadecimal value which gets printed
instead of the corresponding letters.

This behaviour can be disabled by commenting out the following block
in the `print_formatted` function of the `Decoder` class:

```python
        if self.guess_one is None: 
            self.make_guesses(spl)
            print(f'guessing {self.guess_zero}=0, {self.guess_one}=1')
```

## X clipboard integration
If `xclip` is installed, then whenever a hexadecimal number gets printed,
it is also copied into the X clipboard. This makes it easy to have another
window with a text editor open and just pressing buttons on the remote
followed by pasting the corresponding codes straight to the new LIRC config
file.

This feature can be disabled by commenting out the call to the `clipboard`
function (inside the `format` function of the `Decoder` class).

# Example
See `examples/samsung_in.txt` for the output of `mode2` for a sample
output of 4 buttons pressed on a Samsung remote, and
`examples/samsung_out.txt` for the output produced by the formatter.
