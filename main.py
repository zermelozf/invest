import streamlit as st
import pandas as pd
import numpy as np
from numpy_financial import irr

import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib.ticker import FuncFormatter

def human_format(num, pos):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000
    return '%.1f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

yy = {
    1: 0,  2: 1,  3: 2,  4: 3,  5: 4,  6: 5,  
    7: 6,  8: 7,  9: 8, 10: 9, 15: 10, 20: 11, 
    25: 12, 30: 13, 40: 14
}

def c(v):
    cost = [-cash for _ in range(25 * 12)] + [0 for _ in range((40 - 25) * 12)]
    ans = []
    for y in x:
        c = cost[:12 * y]
        c[-1] += v[yy[y]]
        ans.append(irr(c) * 1200)
    return np.array(ans)

formatter = FuncFormatter(human_format)

st.title('Investment Plan Fees Calculator')

tab = st.text_area('Investment table', '')
cash = st.number_input('Monthly payment', 700)
r = st.number_input('Expected Return', 5, help='The expected number must be in the table.')

def no_fees(years, cash, r=0.05):
    s = 0
    for i in range(years * 12):
        s *= (1 + r / 12)
        if (i / 12) < 25:
            s += cash
    return s

if tab != '':
    data = []
    rows = tab.split('\n')
    for row in rows:
        values = row.split(' ')
        data.append([int(v.replace(',', '')) for v in values])
    data = pd.DataFrame(data, columns=['year', 'paid', 'v0%', 'v5%', 'v7%', 'v9%', '0%', '5%', '7%', '9%'])

    if f'{r}%' not in data.columns:
        st.warning(f'{r}% was not found in the investment table')
    else:
        x = data['year'].values
        v_nofee = np.array([no_fees(i, cash=cash, r=r/100) for i in x])
        v_infinity_table = data[f'{r}%'].values
        cost = [cash * 12 * y for y in x if y <= 25] + [cash * 12 * 25 for y in x if y > 25]

        f, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Value')
        ax1.yaxis.tick_right()
        ax1.yaxis.set_major_formatter(formatter)
        ax1.plot(x, v_nofee, label=f'No Fees ({int(v_nofee[12]):,} EUR after 25 years)', color='green', alpha=0.5)
        ax1.plot(x, v_infinity_table, label=f'Infinity (table) ({v_infinity_table[12]:,} EUR after 25 years)', color='blue')
        ax1.plot(x, cost, label=f'Invested Amount ({cost[12]:,} EUR after 25 years)', color='grey', alpha=0.5)
        ax1.tick_params(axis='y')
        ax1.yaxis.tick_right()
        ax1.legend()
        ax1.title.set_text(f'Exit Value')

        c_nofee = c(v_nofee)
        c_infinity_table = c(v_infinity_table)
        ax2.set_ylim(0, r)
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Fees (%)')
        ax2.plot(x, r - c_nofee, label=f'No Fee ({0})%', color='green')
        ax2.plot(x, r - c_infinity_table, label=f'Infinity (table) (>{min(r - c_infinity_table[12:]):.2f}%)', color='blue')
        ax2.yaxis.tick_right()
        ax2.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y:.0f}%'))
        ax2.legend()
        ax2.title.set_text(f'Yearly Fees')
        f.suptitle(f"Investing {cash:,} EUR monthly at {r}%", fontsize=14)
        st.pyplot(f)