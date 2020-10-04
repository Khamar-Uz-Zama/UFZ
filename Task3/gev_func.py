# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 09:02:10 2020

@author: miniussi
"""

#functions for GEV (both precipitation and streamflow)
#parameter estimation of GEV is based on annual maxima (function: gev_LMO

import numpy as np
from scipy.special import gamma
import pandas as pd
import matplotlib.pyplot as plt

#from charts.bar_chart import plot_chart
import plotly.graph_objs as go
import plotly.offline as plt
import plotly
import json

#data = pd.read_csv('stream_data.csv',sep=',')

def extract_max(data):
    
    maxima = np.sort(data.groupby(by='WY')['streamflow'].max())
    
    return np.asarray(maxima)
    
def T_to_p(T):
    
    #converts return period (user input) to non-exceedance probability p
    
    T = np.asarray(T)
    p = 1 - (1/T)
    
    return p 

def plotting_position(data):
    
    #computes plotting positions of a given array of data
    
    p = np.zeros(len(data))
    p[0] = 1/(len(data)+1)
    
    i = 1
    
    while i < len(data): 
        if data[i] == data[i-1]:
            ind_start = i-1
            i = i+1
            while data[i] == data[i-1]:
                i = i+1
            p_eq = i/(len(data)+1)
            p[ind_start:i-1] = p_eq*np.ones(i-ind_start)
        else:
            p[i] = (i+1)/(len(data)+1)
            i = i+1
    
    return p

def p_to_T(p):
    
    #converts non-exceedance probability to return period
    
    T = 1/(1-p)

    return T

def gev_LMOM(maxima): #here the estimation method is PWMs
#sample is a column of numpy values (block maxima)

    maxima = np.asarray(maxima)
    maxima = np.sort(maxima)
    n = np.size(maxima) 
    b0 = np.sum(maxima)/n #mean
    b1 = 0.0
    for j in range(0,n): 
        jj = j+1
        b1 = b1 + (jj - 1)/(n - 1)*maxima[j]
    
    b1 = b1/n
    b2 = 0.0
        
    for j in range(0,n): # skip first two elements
        jj  = j + 1 
        b2  = b2 + (jj-1)*(jj-2)/(n-1)/(n-2)*maxima[j]
        
    b2   = b2/n
    # L MOMENTS - linear combinations of PWMs
    L1   = b0
    L2   = 2*b1 - b0
    L3   = 6*b2-6*b1+b0
    t3   = L3/L2  #L skewness 
    
    #relations between L-moments and GEV parameters
    
    c = 2/(3 + t3) - np.log(2)/np.log(3)   
    k = 7.8590*c + 2.9554*c**2
    csi = -k                                      # usual shape 
    psi = L2*k/((1 - 2**(-k))*gamma(1 + k))       # scale 
    mu  = L1 - psi*(1 - gamma(1 + k))/k            # location
    par = [csi,mu,psi]
    
    return par #csi (shape), psi (scale) and mu (location)

#probabably the function gev_cdf is not needed
    
def gev_cdf(x,par):
    
    # x is the quantile for which I want to compute the cumulative distribution function
    # it can either be a single value or an array of values
    
    csi = par[0]; mu = par[1]; psi = par[2]
    F_GEV = np.exp( -(1 + csi/psi*(x-mu))**(-1/csi))
    
    return F_GEV

def gev_qle(p,par):
    
    #p is the value of non-exceedance probability for which I want to compute the corresponding quantile
    csi = par[0]; mu = par[1]; psi = par[2]
    x = mu+psi/csi*((-np.log(p))**(-csi)-1) 

    return x


def plot_ffc(ffc_obs, ffc_est, T_target, which, um):
    #         maxima, gev_ffc, T_target, 'Streamflow', 'm$^3$/s'
    #which can be 'Precipitation' or 'Streamflow'
    #um is the unit of measurement (standard)
    
    T_emp = p_to_T(plotting_position(ffc_obs))
    plt.semilogx(T_emp, ffc_obs, 'o', color = 'gray', markeredgecolor = 'k', markeredgewidth = 0.5, label = 'OBSERVED FFC')
    plt.semilogx(T_target, ffc_est, '-r', lw = 1, label = 'GEV FFC')
    plt.xlabel('RETURN PERIOD [years]')
    plt.ylabel('%s [%s]'%(which.upper(), um))
    plt.legend()

def get_gev_params(data):
    # Written by Khamar Uz Zama
    maxima = extract_max(data)
    maxima = extract_max(data)
    par_GEV = gev_LMOM(maxima)
    T_target = [2,10,20,50,100,200,500,1000,2000,5000,10000] #this is just an example of return period, it is the user-choice
    gev_ffc = gev_qle(T_to_p(T_target),par_GEV)

    return maxima, gev_ffc, T_target

def convt_to_df(T_target, gev_ffc):
    # Written by Khamar Uz Zama
    # Output file
    output = pd.DataFrame({'Return period [years]': pd.Series(T_target), 'Streamflow [m3/s]': pd.Series(gev_ffc)}) #this needs to be downloaded
    
    return output

def get_plotly_charts(ffc_obs, ffc_est, T_target, which = 'Streamflow', um = 'm$^3$/s'):
    # Written by Khamar Uz Zama
    # Converts the observations to plotly chart
    
    T_emp = p_to_T(plotting_position(ffc_obs))
    trace1 = go.Scatter(x=T_emp, y=ffc_obs, mode="markers", name="Observed ffc")
    trace2 = go.Scatter(x=T_target, y=ffc_est, name="GEV ffc")

    layout = go.Layout(title="Observed vs Estimated ffc", 
                       xaxis=dict(title='Return Period [years]'),
                       xaxis_type="log",
                       yaxis=dict(title='%s [%s]'%(which, um)))
    
    data = [trace1,trace2]
    fig = go.Figure(data=data, layout=layout)
    fig_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return fig_json

#    plt.semilogx(T_emp, ffc_obs, 'o', color = 'gray', markeredgecolor = 'k', markeredgewidth = 0.5, label = 'OBSERVED FFC')
#    plt.semilogx(T_target, ffc_est, '-r', lw = 1, label = 'GEV FFC')
#
#    plt.legend()
    
#maxima, gev_ffc, T_target = get_gev_params(data)
#plot_ffc(maxima, gev_ffc, T_target, 'Streamflow', 'm$^3$/s')
#
#
#
#output = convt_to_df(T_target, gev_ffc)

##for example
#maxima = extract_max(data)
#T_emp = p_to_T(plotting_position(maxima))
#par_GEV = gev_LMOM(maxima)
#T_target = [2,10,20,50,100,200,500,1000,2000,5000,10000] #this is just an example of return period, it is the user-choice
#gev_ffc = gev_qle(T_to_p(T_target),par_GEV)
#plot_ffc(maxima, gev_ffc, T_target, 'Streamflow', 'm$^3$/s') #this needs to be visualized 
#
##output file
#output = pd.DataFrame({'Return period [years]': pd.Series(T_target), 'Streamflow [m3/s]': pd.Series(gev_ffc)}) #this needs to be downloaded