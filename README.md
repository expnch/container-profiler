# Container Profiler
The Container Profiler is a simple tool for analyzing the resource consumption of a container application.  It is intended to be used for local profiling of containers running on the Docker daemon.

## Usage
First, install the requirements (preferably in a virtual environment).
```bash
pip install -r requirements.txt
```

Then, run the container that you'd like to analyze.  It is recommended that you set a name.
```bash
docker run -d --name my_service service:latest
```

With the container running, start the profiler with the container name (or `CONTAINER ID` if you didn't set one) specified.
```bash
python3 profile.py my_service
```

Run some load tests or otherwise create conditions to that will be interesting to analyze.

When you're done, terminate the profiler's data collection with `Ctrl+C` and shut down your container if necessary.

The profiler will output charts for CPU and memory consumption called `cpu.html` and `memory.html`, respectively.  These charts can be opened in a web browser.

## Command-line arguments
```
usage: profile.py [-h] [-m <filename for memory chart>]
                  [-c <filename for CPU chart>] [-u {B,KiB,MiB,GiB}]
                  [-i <refresh interval in seconds>]
                  CONTAINER

positional arguments:
  CONTAINER

optional arguments:
  -h, --help            show this help message and exit
  -m <filename for memory chart>
  -c <filename for CPU chart>
  -u {B,KiB,MiB,GiB}
  -i <refresh interval in seconds>
```
Note: make sure that any filenames set via `-m` and `-c` end in `.html` - this is a requirement for Altair, the module used for chart generation.
