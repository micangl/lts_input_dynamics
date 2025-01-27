# lts_input_dynamics
This python script is a simple input dynamic-range calculator for MOSFET circuits on LTSpice.

In this context, we refer to the input dynamic-range as the maximum (or minimum) voltage of a signal which can be applied to a circuit, whilst guaranteeing that each MOSFET operates in the saturation region and isn't turned off.

Note that this script is based on the [PyLTSpice](https://github.com/nunobrum/PyLTSpice) library and is designed to work with the **level 1** spice MOSFET model.

## Installation
You'll need to install [PyLTSpice](https://github.com/nunobrum/PyLTSpice) and, then, download this script.

# Calculating the input dynamic-range for sinusoidal or positive input-signals
In LTSpice, set the input-signal amplitude to a parameter (e.g. `{vi}`).
Perform a transient simulation whilst stepping this parameter. These directives are an example:
```
.tran 0 100u 1u 100n
.step param vi 1m 1 10m
```
Be careful not to leave the `Time to start saving data` field of the transient analysis set to `0` (in the example directives it's equal to `1u`), as we don't want to start saving data until the circuit has reached some form of "steady state".

LTSpice will produce a file with the `.raw` extension in the same directory as the main `.asc` file. 
To invoke this script, issue:
```sh
python <path_to_script> <path_to_raw_file>
```
# Calculating the minimum input voltage
The only differences will be, of course, the range for the parameter step and having to pass the `-n` parameter to the script:
```sh
python <path_to_script> <path_to_raw_file> -n
```
