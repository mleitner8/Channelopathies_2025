

"""
wscale.py

Code to analyze the scaling of weights as a function of input dendritic location

Contributors: salvadordura@gmail.com
"""

import utils
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from cycler import cycler
import sys, os
import time
#import termplotlib as tpl
#import plotext as plt

def calculateEPSPs(params, data, somaLabel='soma', stimRange=[3000,4000], syn='exc'):
    out = {}
    secs = [s for s in params[1]['values']]
    locs = [s for s in params[0]['values']]

    for key, d in data.items(): #changed iteritems to items (python version change)
        #cellLabel = d['data']['V_soma'].keys()[0]
        vsoma = d['V_'+somaLabel]['cell_0']
        #vsoma = d['data']['V_'+somaLabel][cellLabel]
        if syn == 'exc':
            epsp = max(vsoma[stimRange[0]:stimRange[1]]) - vsoma[stimRange[0]-1] # max voltage between stim time - baseline
        elif syn == 'inh':
            epsp = min(vsoma[stimRange[0]:stimRange[1]]) - vsoma[stimRange[0]-1] # min voltage between stim time - baseline
        seg = (d['paramValues'][0], d['paramValues'][1])
        weight = d['paramValues'][1]
        #print(seg, weight, epsp, len(vsoma))
        out[tuple(seg)].append([weight, epsp])

    return out


def calculateEPSPsPops(params, data, somaLabel='soma', stimRange=[3000,4000], syn='exc'):
    out = {}

    pops = [p for p in params[2]['values']]
    secs = [s for s in params[1]['values']]
    locs = [s for s in params[0]['values']]
    print(pops,secs,locs)
    for pop in pops: 
        out[pop] = {}
        for sec,loc in zip(secs,locs): out[pop][(sec,loc)] = []

    for key, d in data.items(): #change iteritems to items
        #cellLabel = d['V_soma'].keys()[0] # d['simData']['V_soma'].keys()[0]
        vsoma = d['V_'+somaLabel]['cell_0']  #d['simData']['V_'+somaLabel][cellLabel]
        if syn == 'exc':
            epsp = max(vsoma[stimRange[0]:stimRange[1]]) - vsoma[stimRange[0]-1] # max voltage between stim time - baseline
        elif syn == 'inh':
            epsp = min(vsoma[stimRange[0]:stimRange[1]]) - vsoma[stimRange[0]-1] # min voltage between stim time - baseline
        pop = d['paramValues'][2]
        seg = (d['paramValues'][1], d['paramValues'][0])
        weight = d['paramValues'][3]
        #print(pop, seg, weight, epsp, len(vsoma))
        out[pop][tuple(seg)].append([weight, epsp])

    return out


def calculateWeightNorm(params, data, epspNorm=0.5, somaLabel='soma', stimRange=[3000,4000], savePath=None):

    epsp = calculateEPSPs(params, data, somaLabel=somaLabel, stimRange=stimRange)
    
    segs = [s for s in params[1]['values']]
    segs.sort()
    weightNorm = {}
    for seg in segs: weightNorm[seg[0]] = []  # empty list for each section
    for seg in segs:
        epspSeg = epsp[tuple(seg)]
        epspSeg.sort()
        x, y = zip(*epspSeg)
        f = interp1d(y, x, fill_value="extrapolate")
        w = f(epspNorm)
        if w < 0:
            x, y = zip(*epspSeg[:-1])
            f = interp1d(y, x, fill_value="extrapolate")
            w = f(epspNorm)
        wnorm = w / epspNorm
        weightNorm[seg[0]].append(wnorm)
        print('\n%s wscale = %.6f' % (str(seg), wnorm))
        if wnorm <= 0:
            plt.scatter(x, y)
            plt.xlabel('Stimulation Intensity')
            plt.ylabel('EPSP')
            plt.show()




        if savePath:
            import pickle
            with open(savePath+'_weightNorm.pkl', 'wb') as fileObj:
                pickle.dump(weightNorm, fileObj)


def calculateWeightNormPops(params, data, epspNorm=0.5, somaLabel='soma', stimRange=[3000,4000], savePath=None):
    epsp = calculateEPSPsPops(params, data, somaLabel=somaLabel, stimRange=stimRange)

    popSaveLabels = {'PT5B': 'PT_full'}
    pops = [p for p in params[2]['values']]
    secs = [s for s in params[1]['values']]
    locs = [s for s in params[0]['values']]
    segs=[]
    for sec,loc in zip(secs,locs): segs.append((sec,loc))
    segs.sort()
    weightNorm = {}

    for pop in pops:
        #print(pop)
        weightNorm[pop] = {}
        for seg in segs: weightNorm[pop][seg[0]] = []  # empty list for each section
        for seg in segs:
            #print(epsp[pop][seg], seg); quit()
            epspSeg = epsp[pop][seg]
            epspSeg.sort()
            x,y = zip(*epspSeg)
            #print(x,y)
            f = interp1d(y,x,fill_value="extrapolate")
            w = f(epspNorm)
            #print(w, seg[0])
            if w < 0:
                x, y = zip(*epspSeg[:-1])
                f = interp1d(y, x, fill_value="extrapolate")
                w = f(epspNorm)
            wnorm = w / epspNorm
            #print(wnorm)
            weightNorm[pop][seg[0]].append(wnorm)
            print('\n%s %s wscale = %.6f' % (pop, str(seg), wnorm))

            if wnorm <=0:
                plt.scatter(x,y)
                plt.xlabel('Stimulation Intensity')
                plt.ylabel('EPSP')
                plt.show()
            '''Plot EPSPs
            #if wnorm <=0:
            #    jj = f(x)
            #    plt.scatter(x, y)
                #plt.plot(x, f(x))
            #    plt.xlabel('Stimulation Intensity')
            #    plt.ylabel('EPSP')
            #    plt.show()
            #    quit()
            #jj = f(x)
            plt.figure()
            plt.scatter(x, y)
            #plt.plot(x, jj)
            plt.xlabel('Stimulation Intensity')
            plt.ylabel('EPSP')
            plt.savefig('plots/'+str(pop)+'_'+str(seg)+'.png')
            plt.close()
            '''

        #print(weightNorm[pop])
        if savePath:
            import pickle
            with open(savePath+popSaveLabels[pop]+'_weightNorm.pkl','wb') as fileObj:
                pickle.dump(weightNorm[pop], fileObj)


    return weightNorm



def plotEPSPs(epsp, dataFolder, batchLabel, addLegend=True, includeSegs = None):
    utils.setPlotFormat(numColors = 8)

    if len(params) == 3:
        pops = ['_']
        segs = includeSegs if includeSegs else [s for s in params[0]['values']]
        weights = params[2]['values']
        epspPops = {'_': epsp}
    elif len(params) == 4:
        pops = params[2]['values']
        segs = includeSegs if includeSegs else epsp[pops[0]].keys() # params[1]['values']
        weights = params[3]['values']
        epspPops = epsp

    for pop in pops:
        plt.figure(figsize=((12,8)))

        for seg in segs:
            if not seg[0].startswith('axon') and seg[1] not in [0.0,1.0]:
                epspSeg = epspPops[pop][tuple(seg)]
                if epspSeg:
                    epspSeg.sort()
                    x,y = zip(*epspSeg)
                    handles = plt.plot(x, y, marker='o', markersize=10, label=str(seg))

        plt.xlabel('Weight (of NetStim connection)')
        #xtick = np.arange(0.0, 0.0022, 0.0002)
        #plt.xticks(xtick, xtick)
        plt.ylabel('Somatic EPSP amplitude (mV) in response to 1 NetStim spike')
        if addLegend: plt.legend(title = 'Section', loc=2)
        if includeSegs:
            plt.savefig('%s/%s/%s_%s_epsp_subset.png' % (dataFolder, batchLabel, batchLabel, pop))
        else:
            plt.savefig('%s/%s/%s_%s_epsp.png' % (dataFolder, batchLabel, batchLabel, pop))
    
    #plt.show()



# main code
if __name__ == '__main__':

    # run batch E cells
    
    dataFolder = '../batchSims'
    batchLabel = 'wscaleUCDavis'   # v52_batch3'
    #loadFromFile = True

    ''' run via batch.py
    b = batch.weightNormE(pops=['IT2', 'IT4'], rule='IT2_reduced', weight=[0.0001])
    b.batchLabel = batchLabel  
    b.saveFolder = dataFolder+b.batchLabel
    b.method = 'grid'
    setRunCfg(b, 'mpi')
    b.run() # run batch
    '''

    # analyze batch E cells    
    params, data = utils.readBatchData(dataFolder, batchLabel, loadAll=True, saveAll=False, vars=[('simData', 'V_soma')], maxCombs=None)
    ts = int(1/0.01)
    weightNorm = calculateWeightNormPops(params, data,  somaLabel='soma', stimRange=[ts*700,ts*800], savePath=dataFolder+'/'+batchLabel+'/')
    print(weightNorm)
