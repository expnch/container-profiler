import argparse
import subprocess
import time
import re

import altair as alt
import numpy as np
import pandas as pd

## Inputs and default values

parser = argparse.ArgumentParser()
parser.add_argument('-m', dest='mem_file', metavar='<filename for memory chart>', default=None)
parser.add_argument('-c', dest='cpu_file', metavar='<filename for CPU chart>', default=None)
parser.add_argument('-u', choices=['B', 'KiB', 'MiB', 'GiB'], dest='mem_unit', default=None)
parser.add_argument('-i', dest='interval', metavar='<refresh interval in seconds>', default=None)
parser.add_argument('CONTAINER')
args = parser.parse_args()

CONTAINER = args.CONTAINER
INTERVAL = args.interval if args.interval else 1
MEM_UNIT = args.mem_unit if args.mem_unit else 'MiB'
MEM_CHART_FILENAME = args.mem_file if args.mem_file else 'memory.html'
CPU_CHART_FILENAME = args.cpu_file if args.cpu_file else 'cpu.html'

CPU_AVAILABLE_CORES = subprocess.run(args=["docker", "info", "--format", "'{{json .NCPU}}'"], stdout=subprocess.PIPE).stdout.decode('utf-8')

## Constants

KIB_TO_BYTES = 1024
MIB_TO_BYTES = 1048576
GIB_TO_BYTES = 1073742000

## Functions

m_pattern = re.compile('^\d+(\.\d+)?[K|M|G]iB')
def parseMemory(s, p=m_pattern):
    extracted = p.match(s)
    if extracted is None:
        return None

    extracted = extracted.group()
    if extracted[-3] == 'K':
        return float(extracted[:-3])*KIB_TO_BYTES
    elif extracted[-3] == 'M':
        return float(extracted[:-3])*MIB_TO_BYTES
    elif extracted[-3] == 'G':
        return float(extracted[:-3])*GIB_TO_BYTES
    else:
        return None

c_pattern = re.compile('^\d+(\.\d+)?%')
def parseCPU(s, p=c_pattern):
    extracted = p.match(s)
    if extracted is None:
        return None
    else:
        return float(extracted.group()[:-1])
    

stats = lambda x: ["docker", "stats", "--format", "'{{.Container}}|{{.CPUPerc}}|{{.MemUsage}}'", "--no-stream", "%s" % x]

def createLineChart(series, filename, ylabel, xlabel='time (seconds)'):
    frame = pd.DataFrame({
        '%s' % xlabel: series[0], 
        '%s' % ylabel: series[1]
    })

    chart = alt.Chart(frame).mark_line().encode(
        x = '%s' % xlabel,
        y = '%s' % ylabel
    )

    chart.save(filename)

## Data collection

memory_series = [[], []]
cpu_series = [[], []]

start = time.time()

try:
    while True:
        output = subprocess.run(args=stats(CONTAINER), stdout=subprocess.PIPE)
        if output.returncode != 0:
            break

        n, c, m = output.stdout.decode('utf-8').split('|')
        t = time.time() - start

        m_parsed = parseMemory(m)
        if m_parsed:
            memory_series[0].append(t)
            memory_series[1].append(m_parsed)
            print("Memory data recorded: %s" % m_parsed)
        else:
            print("Could not retrieve memory data")

        c_parsed = parseCPU(c)
        if c_parsed:
            cpu_series[0].append(t)
            cpu_series[1].append(c_parsed)
            print("CPU data recorded: %s" % c_parsed)
        else:
            print("Could not retrieve CPU data")

        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("\nData collection terminated.")

## Chart creation

if MEM_UNIT == 'KiB':
    memory_series = [memory_series[0], np.array(memory_series[1])/KIB_TO_BYTES]
elif MEM_UNIT == 'MiB':
    memory_series = [memory_series[0], np.array(memory_series[1])/MIB_TO_BYTES]
elif MEM_UNIT == 'GiB':
    memory_series = [memory_series[0], np.array(memory_series[1])/GIB_TO_BYTES]

createLineChart(memory_series, MEM_CHART_FILENAME, 'Memory utilization (MiB)')
createLineChart(cpu_series, CPU_CHART_FILENAME, "CPU utilization (percentage)")

print("Charts generated.")
