# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 23:22:51 2018

@author: masahiro
"""

import pandas as pd
import os
from numba.decorators import jit

@jit
def main():
    df=pd.read_csv("output1"+"-100percent.csv",header=None)
    df.to_csv('output_sum.csv',header=False,index=False)
    df_sum=pd.read_csv('output_sum.csv',header=None)

    cnt=1
    for n in range(2,200):
        if os.path.exists("output"+str(n)+"-100percent.csv")==True:
            df = pd.read_csv("output"+str(n)+"-100percent.csv",header=None)
            df_sum[str(n)]=df[0]
            df_sum.to_csv('output_sum.csv',header=False,index=False)
            cnt+=1
            print(str(cnt)+","+str(n))
        else:
            print(str(cnt)+","+str(n))
   
main()