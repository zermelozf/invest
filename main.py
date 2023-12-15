import streamlit as st
import pandas as pd
import numpy as np
from numpy_financial import irr

import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib.ticker import FuncFormatter


text = """1 8,400 12,011 12,422 12,586 12,749 0 0 0 0
2 16,800 19,210 20,383 20,861 21,344 2,133 2,243 2,287 2,332
3 25,200 26,150 28,406 29,347 30,310 10,527 10,979 11,163 11,348
4 33,600 33,064 36,734 38,299 39,920 18,775 19,996 20,499 21,011
5 42,000 39,947 45,377 47,741 50,221 27,434 30,010 31,098 32,220
6 50,400 46,794 54,345 57,700 61,263 35,402 39,655 41,487 43,400
7 58,800 53,600 63,648 68,204 73,101 43,299 49,699 52,517 55,494
8 67,200 60,362 73,296 79,283 85,794 51,053 60,061 64,115 68,451
9 75,600 67,075 83,300 90,966 99,404 58,669 70,752 76,310 82,333
10 84,000 73,736 93,673 103,286 113,998 66,151 81,783 89,136 97,208
15 126,000 106,165 151,482 175,717 204,463 102,049 143,248 164,946 190,444
20 168,000 136,951 220,450 270,089 332,977 136,941 218,808 267,144 328,114
25 210,000 176,316 321,438 417,542 547,983 176,316 321,438 417,542 547,983
30 210,000 162,688 379,594 542,246 781,094 162,688 379,594 542,246 781,094
40 210,000 137,801 529,352 914,946 1,588,037 137,801 529,352 914,946 1,588,037"""

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

tab = st.text_area('Investment table', text)
cash = st.number_input('Monthly payment', value=700)
r = st.selectbox(
    'Expected yearly return in %.',
    (0, 5, 7, 9), index=2
)

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
        ax2.set_ylim(0, 10)
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Fees (%)')
        ax2.plot(x, r - c_nofee, label=f'No Fee ({0})%', color='green')
        ax2.plot(x, r - c_infinity_table, label=f'Infinity (table) (>{np.nanmin(r - c_infinity_table):.2f}%)', color='blue')
        ax2.yaxis.tick_right()
        ax2.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y:.0f}%'))
        ax2.legend()
        ax2.title.set_text(f'Yearly Fees')
        f.suptitle(f"Investing {cash:,} EUR monthly at {r}%", fontsize=14)
        st.pyplot(f)
    
        zz = {v: k for k, v in yy.items()}
        n = sum(v_infinity_table < cost)
        st.info(f"It will cost you at least {np.nanmin(r - c_infinity_table):.2f}% in fees to subscribe to this plan")
        st.info(f"After 25 years, you will have paid {int(v_nofee[12] - v_infinity_table[12]):,} EUR of fees.")
        st.info(f"You will loose some money if you withdraw it before {n} years.")
        # st.info(f"To minimize fees you should exit on year {zz[np.nanargmin(r - c_infinity_table)]}")
