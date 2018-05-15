
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import math
from datetime import datetime
import imageio

mpl.rcParams['font.family'] = 'monospace'

# Set output directory, make it if needed
output_dir = os.path.realpath('output')
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

# Get input data
input_file = os.path.join('data', 'usc.csv')
df = pd.read_csv(input_file, parse_dates=[0])


year_list = []
for year in range(1922, 2018):
    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
    year_list.append(year)
    length = len(year_list)
    for i, segment in enumerate(year_list):
        dp = df.loc[df['YEAR']==segment, ['MM/DD/YYYY', 'MONTH', 'TMAX']].reset_index(drop=True)
        y = dp['TMAX'].rolling(14).mean()
        x = dp['MM/DD/YYYY'].apply(lambda dt: dt.replace(year=2000))
#        dp = dp.groupby(by='MONTH').max()
        alpha = math.exp(1-(1/((i+1)/length)**2))+0.05
        if segment == year_list[-1]:
            plt.plot(x, y, color='#800000', alpha=alpha)
        else:
            plt.plot(x, y, color='#3f3f3f', alpha=alpha)        
        plt.title(year)
    plt.ylim((0, 500))
    fig.savefig(os.path.join(output_dir, '{}.png'.format(year)),
            dpi=fig.dpi,
            bbox_inches='tight',
            pad_inches=0.3)
    plt.close()
        
# Make gif
png_files = [f for f in os.listdir(output_dir) if f.endswith('.png')]
png_files.sort()

charts = []
length = len(png_files)-1
for i, f in enumerate(png_files):
    charts.append(imageio.imread(os.path.join(output_dir, f)))
    # Append the actual charts extra to 'pause' the gif
    if i == length | i == 0:
        for j in range(35):
            charts.append(imageio.imread(os.path.join(output_dir, f)))

# Save gif
imageio.mimsave(os.path.join(output_dir, 'temperature_usc.gif'), charts, format='GIF', duration=0.2)
