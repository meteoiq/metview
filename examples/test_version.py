import metview as mv
from ecmwf.opendata import Client
from eccodes import *

# print version information
print(mv.version_info())

# download latest msl forecast for 24 hours
gribfilename = "/tmp/msl_24.grib2"
client = Client()
client.retrieve(
    type="fc",
    step=24,
    param=["msl"],
    target=gribfilename,
)
f = mv.Fieldset(path=gribfilename)

# test if gradient of field can be created or throws an exception
try:
    mv.gradient(f)
except:
    print(
        "Gradient of field cannot be produced, build option METVIEW_PYTHON_ONLY was set"
    )
else:
    print(
        "Gradient of field can be produced, build option METVIEW_PYTHON_ONLY was _not_ set"
    )

# test if regridding of field can be done or throws an exception
try:
    new = mv.regrid(data=f, grid=[2, 2])
except:
    print ("Regridding failed")
else:
    print ("Regridding done")
