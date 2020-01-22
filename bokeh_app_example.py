from bokeh.plotting import figure
from bokeh.models import ColorBar, LinearColorMapper
from bokeh.io import curdoc
from bokeh.models.tools import CustomJSHover, HoverTool
from bokeh.models.widgets import Slider
from bokeh.layouts import column

import xarray as xr

ds = xr.open_dataset('http://opendap.knmi.nl/knmi/thredds/dodsC/radarprecipclim/RAD_NL25_RAC_MFBS_01H_NC.nc#fillmismatch')

x_min = ds.x.values.min()
x_max = ds.x.values.max()
y_min = ds.y.values.min()
y_max = ds.y.values.max()
x_width = x_max - x_min
y_height = y_max - y_min

cm = LinearColorMapper(palette="Spectral11", low=0, high=20)

p = figure(
    x_range=(x_min, x_max), 
    y_range=(y_min, y_max),
    tooltips=[
        ("(x,y)", "($x{‘0,0’}, $y{‘0,0’})"),
        ("rainfall amount", "@image")
    ]
)

i = 10

im = p.image(
    # Note: Thet data hast to be inverted along the y-axis
    image=[ds.image1_image_data.isel(time=i).values[-1::-1, :]],
    x=x_min, 
    y=y_min, 
    dw=x_width,
    dh=y_height,
    color_mapper=cm,
)
p.title.text = str(ds.time.isel(time=i).values)[:22]

cb = ColorBar(color_mapper=cm, location=(0,0))
p.add_layout(cb, 'right')

def update_data(attr, old, new):
    im.data_source.data = {'image': [ds.image1_image_data.isel(time=new).values[-1::-1, :]]}
    p.title.text = str(ds.time.isel(time=new).values)[:22]

def update_R_max(attr, old, new):
    cm.high = new
    
time_slider = Slider(
    title="time_index", 
    value=0,
    start=0, 
    end=len(ds.time)-1, 
    step=1,
    callback_throttle=500,
)

R_max_slider = Slider(
    title="Maximal rainsum in mm",
    value=10,
    start=0,
    end=100,
    step=1,
)

time_slider.on_change('value_throttled', update_data)
R_max_slider.on_change('value', update_R_max)

curdoc().add_root(column(time_slider, R_max_slider, p))
