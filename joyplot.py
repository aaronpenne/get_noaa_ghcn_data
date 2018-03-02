##############################################################################
# FIXME Ploting needs to get moved to different file
##############################################################################

import seaborn as sns
import matplotlib.pyplot as plt


# Filter data to years with complete records (1921 to 2017 after doing
# inspection with df.pivot_table(values='TMAX', columns='YEAR', aggfunc='count'))
year_filter = [str(i) for i in range(1921,2017)]
df = df_all.loc[df_all['YEAR'].isin(year_filter)]
bandwidth = 0.4

def joyplot(element, row, df, xlimit):
    plt.figure()
    
    # Create axes for each Year, one row per Year
    g = sns.FacetGrid(data=df,
                      row=row,  # Determines which value to group by, in this case the different values in the 'Year' column
                      hue=row,  # Similar to row. Enables the date labels on each subplot
                      aspect=70,   # Controls aspect ratio of entire figure
                      size=0.3,    # Controls vertical height of each subplot
                      palette=sns.color_palette("Set2", 1))  # Uses a nice green for the area
    
    # Create KDE area plots
    g.map(sns.kdeplot, element, bw=bandwidth, clip_on=False, shade=True, alpha=1)
    
    # Create KDE line plots to outline the areas
    g.map(sns.kdeplot, element, bw=bandwidth, clip_on=False, color='black')
    
    # Create the psuedo x-axes
    g.map(plt.axhline, y=0, lw=2, clip_on=False, color='black')
    
    # Define and use a simple function to label the plot in axes coordinates
    # https://seaborn.pydata.org/examples/kde_joyplot.html
    def label(x, color, label):
        ax = plt.gca()
        ax.set_xlim(xlimit)
        ax.text(0, 0.07, 
                label,
                family='monospace',
                fontsize=12,
                color='black', 
                ha='left',
                va='center',
                transform=ax.transAxes)
    g.map(label, element)
    
    # Overlap the plots to give the ridgeline effect
    g.fig.subplots_adjust(hspace=-.7)
    
    # Clean up axes and remove subplot titles
    g.set_titles('')
    g.set(yticks=[])
    #plt.xticks([0, 1, 2, 3], 
    #           ['Constitutional Ban',
    #            'Statutory Ban',
    #            'No Law',
    #            'Legal'],
    #            rotation=90,
    #            fontsize=12,
    #            fontname='monospace')
    plt.xlabel('')
    g.despine(bottom=True, left=True)
    
    # Add titles and annotations
    #plt.text(1, 8.5,
    #         'State Same Sex Marriage Laws in the USA',
    #         fontdict=font_h1)
    #plt.text(1, 8.3,
    #         'Percent of states w/each law type from 1995-2015',
    #         fontdict=font_h2)
    #plt.text(4, -1.8,
    #         '© Aaron Penne 2018\nSource: Pew Research Center',
    #         fontdict=font_sub)
    
    g.savefig('{}joy_{}_{}.png'.format(output_dir, row, element), dpi=200, bbox_inches='tight')
    plt.close


# Set up plotting and formatting of viz
sns.set(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})
font_h1 = {'family': 'monospace',
           'color': 'black',
           'weight': 'bold',
           'size': 16,
           'horizontalalignment': 'center'}
font_h2 = {'family': 'monospace',
           'color': 'black',
           'size': 14,
           'horizontalalignment': 'center'}
font_sub = {'family': 'monospace',
            'color': 'black',
            'weight': 'regular',
            'size': 10,
            'horizontalalignment': 'right'}

joyplot('PRCP', 'MONTH', df, [-20, 20])
joyplot('TMAX', 'MONTH', df, [-5, 50])
joyplot('TMIN', 'MONTH', df, [-5, 50])
joyplot('TAVG_CALC', 'MONTH', df, [-5, 50])

joyplot('PRCP', 'YEAR', df, [-20, 20])
joyplot('TMAX', 'YEAR', df, [-5, 50])
joyplot('TMIN', 'YEAR', df, [-5, 50])
joyplot('TAVG_CALC', 'YEAR', df, [-5, 50])

joyplot('PRCP', 'DAY', df, [-20, 20])
joyplot('TMAX', 'DAY', df, [-5, 50])
joyplot('TMIN', 'DAY', df, [-5, 50])
joyplot('TAVG_CALC', 'DAY', df, [-5, 50])