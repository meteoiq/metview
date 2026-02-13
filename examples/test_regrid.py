import metview as mv
from ecmwf.opendata import Client
import os
from concurrent.futures import *
import multiprocessing as mp
import time
import psutil


mp.set_start_method("fork")
# spawn doesn't work
# mp.set_start_method('spawn')

# download various parameters from open data server
def fieldset_from_opendata(
    parameters,
    steps,
):
    filename = "/tmp/data.grib2"
    client = Client()
    client.retrieve(
        type="fc",
        step=steps,
        param=parameters,
        target=filename,
    )
    return mv.Fieldset(path=filename)


def elapsed_since(start):
    return time.strftime("%H:%M:%S", time.gmtime(time.time() - start))


def get_process_memory():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss


def list_files(path):
    # Get list of all files only in the given directory
    fun = lambda x: os.path.isfile(os.path.join(path, x))
    files_list = sorted(filter(fun, os.listdir(path)))

    # Create a list of files in directory along with the size
    size_of_file = [(f, os.stat(os.path.join(path, f)).st_size) for f in files_list]
    # Iterate over list of files along with size
    # and print them one by one.
    for f, s in size_of_file:
        print("{} : {}MB".format(f, round(s / (1024 * 1024), 3)))


def calculate_windspeed(u, v):
    return mv.sqrt(u * u + v * v)


def calculate_precipitation(endStep, startStep):
    return endStep - startStep


def atomize_and_regrid(parameter, f, steps):
    print(
        "start processing {}: pid: {} memory: {:,}".format(
            parameter, os.getpid(), get_process_memory()
        )
    )

    for step in steps:
        atomized_filename = f"/tmp/{parameter}_{step:03d}.grib2"
        if parameter == "tp" and step > 6:
            new = mv.regrid(
                data=f.select(shortName=parameter, endStep=step)
                - f.select(shortName=parameter, endStep=step - 6),
                grid=[2, 2],
            )
        elif parameter == "10u" or parameter == "10v":
            atomized_filename = f"/tmp/ff10_{step:03d}.grib2"
            ff10 = calculate_windspeed(
                f.select(shortName="10u", endStep=step), f.select(shortName="10v", endStep=step)
            )
            new = mv.regrid(data=ff10, grid=[2, 2])
        else:
            new = mv.regrid(
                data=f.select(shortName=parameter, endStep=step), grid=[2, 2]
            )
        new.write(atomized_filename)

    print(
        "end processing {}: pid: {} memory: {:,}".format(
            parameter, os.getpid(), get_process_memory()
        )
    )


# define run options
PARALLEL = True
MAX_WORKERS = 2

# define dataset
parameters = [
    "tp",
    "msl",
    "10u",
    "10v",
    "2t",
]
steps = list(range(6, 144, 6))

f = fieldset_from_opendata(parameters, steps)

print("Content of downloaded datasets:")
print(f.ls(extra_keys=["endStep"],no_print=True))

print("\nFiles before processing in /tmp:")
list_files("/tmp")


if PARALLEL:
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [
            pool.submit(atomize_and_regrid, parameter, f, steps)
            for parameter in parameters
        ]
else:
    for parameter in parameters:
        atomize_and_regrid(parameter, f, steps)

print("\nFiles after processing in /tmp:")
list_files("/tmp")
