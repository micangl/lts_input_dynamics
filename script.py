import sys
import re
from PyLTSpice import RawRead
from PyLTSpice.log.ltsteps import LTSpiceLogReader

raw_name = sys.argv[1]
netlist_name = raw_name.replace('raw', 'net')
log_name = raw_name.replace('raw', 'log')
if len(sys.argv) > 2 and sys.argv[2] == "-n":
    negative_range = 1
else:
    negative_range = 0

mosfets = {}

with open(netlist_name) as netlist_file:
    for line in netlist_file:
        if line[0]=='M' and line[1].isdigit():
            device = line.split(" ")[0]
            drain = line.split(" ")[1]
            gate = line.split(" ")[2]
            source = line.split(" ")[3]
            model = line.split(" ")[5]
            mosfets.update({device: {"drain": drain, "gate": gate, "source": source, "model": model, "vt0": 0}})
# Extract threshold voltages
with open(netlist_name) as netlist_file:
    for line in netlist_file:
        if line.split(" ")[0]=='.model' or line.split(" ")[0]=='.MODEL':
            #if ("nmos" in line) or ("pmos" in line) or ("NMOS" in line) or ("PMOS" in line):
            if re.search(r"[np]mos\s*\(", line, re.IGNORECASE):
                model_name = line.split(" ")[1]
                threshold = re.search(r"(?:vt0\s*=\s*)([+-]?[0-9]*\.?[0-9]+)" ,line, re.IGNORECASE).group(1)
                # Iterate through the devices in the mosfets dictionary and set the related Vt
                for dev in mosfets.keys():
                    if mosfets[dev]["model"] == model_name:
                        mosfets[dev]["vt0"] = float(threshold)
    
raw = RawRead(raw_name)
match = 0
# For each step
for step in (reversed(raw.get_steps()) if negative_range else raw.get_steps()):
    # Check if there are any values in the current step
    if len(raw.get_axis(step)) != 0:
        # For each mosfet in the circuit
        for dev in mosfets.keys():
            # If it's an nmos
            if mosfets[dev]["vt0"] > 0:
                # For each time-step (time-step is not step)
                for i in range(0, len(raw.get_axis(step))):
                    vg = (raw.get_trace("V(" + mosfets[dev]["gate"] + ")").get_wave(step))[i] if mosfets[dev]["gate"] != '0' else 0
                    vd = (raw.get_trace("V(" + mosfets[dev]["drain"] + ")").get_wave(step))[i] if mosfets[dev]["drain"] != '0' else 0
                    vs = (raw.get_trace("V(" + mosfets[dev]["source"] + ")").get_wave(step))[i] if mosfets[dev]["source"] != '0' else 0
                    vt = mosfets[dev]["vt0"]
                    # Check saturation
                    if (vd-vg+vt) < 0:
                        # Device out of saturation
                        log = LTSpiceLogReader(log_name)
                        step_value = log[log.get_step_vars()[0]][step]
                        print("Device " + dev + " enters ohmic region at time " + str(raw.get_axis(step)[i]) + " and " + str(step+1) + "-th step at " + log.get_step_vars()[0] + "=" + str(step_value) + "V.")
                        match = 1
                        break
                    # Check interdiction
                    if (vg-vs-vt) < 0:
                        # Device off
                        log = LTSpiceLogReader(log_name)
                        step_value = log[log.get_step_vars()[0]][step]
                        print("Device " + dev + " is interdicted at time " + str(raw.get_axis(step)[i]) + " and " + str(step+1) + "-th step at " + log.get_step_vars()[0] + "=" + str(step_value) + "V.")
                        match = 1
                        break
            # If it's a pmos
            if mosfets[dev]["vt0"] < 0:
                # For each time-step (time-step is not step)
                for i in range(0, len(raw.get_axis(step))):
                    vg = (raw.get_trace("V(" + mosfets[dev]["gate"] + ")").get_wave(step))[i] if mosfets[dev]["gate"] != '0' else 0
                    vd = (raw.get_trace("V(" + mosfets[dev]["drain"] + ")").get_wave(step))[i] if mosfets[dev]["drain"] != '0' else 0
                    vs = (raw.get_trace("V(" + mosfets[dev]["source"] + ")").get_wave(step))[i] if mosfets[dev]["source"] != '0' else 0
                    vt = mosfets[dev]["vt0"]
                    # Check saturation
                    if (vd-vg+vt) > 0:
                        # Device out of saturation
                        log = LTSpiceLogReader(log_name)
                        step_value = log[log.get_step_vars()[0]][step]
                        print("Device " + dev + " enters ohmic region at time " + str(raw.get_axis(step)[i]) + " and " + str(step+1) + "-th step at " + log.get_step_vars()[0] + "=" + str(step_value) + "V.")
                        match = 1
                        break
                    # Check interdiction
                    if (vg-vs-vt) > 0:
                        # Device off
                        log = LTSpiceLogReader(log_name)
                        step_value = log[log.get_step_vars()[0]][step]
                        print("Device " + dev + " is interdicted at time " + str(raw.get_axis(step)[i]) + " and " + str(step+1) + "-th step at " + log.get_step_vars()[0] + "=" + str(step_value) + "V.")
                        match = 1
                        break
        if match == 1:
            quit()