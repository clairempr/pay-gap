# % matplotlib
# notebook

# create visualization showing pay gap for the Netherlands
# over the period 2008 - 2015
# with data obtained from CBS Open data StatLine
# https://opendata.cbs.nl/statline/portal.html?_la=en&_catalog=CBS
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from os import path

# some constants for data files
data_dir = './data'
age_data_file = '81901NED_UntypedDataSet_24102017_212134.csv'
sector_data_file = '81920NED_UntypedDataSet_24102017_212143.csv'

# use codes to get age groupings
characteristics = {
    10690: '15 to 20',
    10700: '20 to 25',
    10710: '25 to 30',
    10720: '30 to 35',
    10730: '35 to 40',
    10740: '40 to 45',
    10750: '45 to 50',
    10760: '50 to 55',
    10770: '55 to 60',
    10780: '60 to 65',
    10790: '65 to 75',
    10000: 'Total'
}

total_code = 10000

sectors = {
    301000: 'Agriculture, forestry and fishing',
    307500: 'Manufacturing',
    346600: 'Energy',
    348000: 'Water and waste management',
    350000: 'Construction',
    354200: 'Wholesale and retail',
    383100: 'Transportation and storage',
    389100: 'Hotel and food service',
    391600: 'Information and communication',
    396300: 'Financial institutions',
    402000: 'Real estate',
    403300: 'Consultancy',
    417400: 'Government',
    419000: 'Education',
    422400: 'Health and social work',
}

# define color and contrasting darker color
# for given palette
palette = sns.color_palette('Blues', 4)
light_color = palette[1]
med_color = palette[2]
dark_color = palette[3]


def main():
    # read dataset for pay gap by age
    age_df = read_age_data()

    # read dataset for pay gap by sector
    sector_df = read_sector_data()

    # turn the period column into just a year
    for df in [age_df, sector_df]:
        df['Period'] = df.apply(lambda x: x['Period'][0:4], axis=1).astype(int)

    # make sure both dataframes cover the same periods
    min_year = max(age_df['Period'].min(), sector_df['Period'].min())
    max_year = min(age_df['Period'].max(), sector_df['Period'].max())

    age_df = age_df[(age_df['Period'] >= min_year) & (age_df['Period'] <= max_year)]
    sector_df = sector_df[(sector_df['Period'] >= min_year) & (sector_df['Period'] <= max_year)]

    show_plots(age_df, sector_df)


# read from dataset titled 'Beloningsverschil man-vrouw; kenmerken'
# ('Pay gap male-female; characteristics')
# id 81901NED
def read_age_data():
    df = pd.read_csv(path.join(data_dir, age_data_file), sep=';') \
        .rename(index=str, columns={'Perioden': 'Period',
                                    'KenmerkenBaanWerknemer': 'Characteristic',
                                    'BeloningsverschilTussenManEnVrouw_1': 'Difference'})

    # only keep rows with characteristics that we want
    df = df[df['Characteristic'].isin(characteristics)]

    return df


# read from dataset titled 'Beloningsverschil man-vrouw; SBI 2008'
# ('Pay gap male-female; SBI 2008')
# id 81920NED
def read_sector_data():
    df = pd.read_csv(path.join(data_dir, sector_data_file), sep=';') \
        .rename(index=str, columns={'Perioden': 'Period',
                                    'BedrijfstakkenBranchesSBI2008': 'Sector',
                                    'BeloningsverschilTussenManEnVrouw_1': 'Difference'})

    # only keep rows with characteristics that we want
    df = df[df['Sector'].isin(sectors)]

    return df


def show_plots(age_df, sector_df):
    periods = age_df['Period'].unique()
    plt.figure(figsize=(8, 12))
    plt.subplot2grid((9, 2), (0, 0), colspan=2, rowspan=2)
    plt.subplot2grid((9, 2), (2, 0), colspan=2, rowspan=3)
    plt.subplot2grid((9, 2), (5, 0), colspan=2, rowspan=4)
    fig = plt.gcf()

    axes = fig.axes
    # turn off ticks for all axes
    for ax in axes:
        ax.tick_params(
            bottom='off',
            left='off')
        ax.set_axisbelow(True)

    fig.suptitle('Average hourly wage of women in the Netherlands\nas percentage of the average hourly wage of men',
                 x=0.596)
    fig.subplots_adjust(hspace=2.5, top=0.88, left=0.295)
    caption = 'Source: Centraal Bureau voor de Statistiek \n(https://www.cbs.nl/en-gb)'
    fig.text(.6, 0.035, caption, ha='center', fontsize=12)

    plot_total_gap(axes[0], age_df, periods)
    plot_gap_per_age(axes[1], age_df, periods)
    plot_gap_per_sector(axes[2], sector_df, periods)

    sns.set_style('dark')
    fig.savefig('wage_gap.png')
    plt.show()



def plot_total_gap(ax, age_df, periods):
    total_gap = age_df[age_df['Characteristic'] == total_code]['Difference']
    bars = ax.bar(periods, total_gap, color=med_color)

    min_x, max_x = (60, 100)
    ax.set_ylim(bottom=min_x, top=max_x)
    # direct label each bar with y axis values
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() - 9, str(int(bar.get_height())),
                ha='center', color='w')
    # y axis ticks every 20
    ax.set_yticks(np.arange(min_x, max_x + 1, 20))
    ax.set_title('Total per year')


def plot_gap_per_age(ax, age_df, periods):
    end_year = periods[-1]
    end_year_data = age_df[age_df['Period'] == end_year]
    by_ages = end_year_data[end_year_data['Characteristic'] != total_code]['Difference']
    age_categories = [characteristics[key] for key in sorted(characteristics.keys()) if key != total_code]
    y_pos = np.arange(len(age_categories))
    colors = [dark_color if value == by_ages.max() else med_color for value in by_ages]
    bars = ax.barh(y_pos, by_ages, color=colors)
    ax.set_yticklabels(age_categories)
    ax.set_title('By age, ' + str(end_year))
    set_up_hbar_plot(ax, y_pos, bars)


def plot_gap_per_sector(ax, sector_df, periods):
    end_year = periods[-1]
    end_year_data = sector_df[sector_df['Period'] == end_year]
    by_sector = end_year_data.sort_values('Difference', axis=0, ascending=False)
    sector_categories = [sectors[code] for code in by_sector['Sector']]
    y_pos = np.arange(len(sector_categories))
    bars = ax.barh(y_pos, by_sector['Difference'], color=med_color)
    ax.set_yticklabels(sector_categories)
    ax.set_title('By sector, ' + str(end_year))
    set_up_hbar_plot(ax, y_pos, bars)


def set_up_hbar_plot(ax, y_pos, bars):
    ax.xaxis.grid(True)
    ax.set_xlim(left=70, right=105)
    plot_100_line(ax, bars)
    ax.set_yticks(y_pos)
    ax.invert_yaxis()  # labels read top-to-bottom


# plot a line at 100 to represent average hourly wage for men
def plot_100_line(ax, bars):
    # use zorder to make sure line is drawn behind bars
    bars_zorder = bars[0].get_zorder()
    ax.axvline(x=100, color='red', alpha=0.4, linestyle='solid', lw=0.9,
               zorder=bars_zorder - 0.0001)


main()