# -*- coding:utf-8 -*-

"""
PyHdust *beatlas* module: BeAtlas specific variables and functions.

BAmod class: there is no disk without a reference star.
BAstar clase: there is a stand-alone star.

:license: GNU GPL v3.0 (https://github.com/danmoser/pyhdust/blob/master/LICENSE)
"""
import os as _os
import numpy as _np
import struct as _struct
from glob import glob as _glob
from itertools import product as _product
import pyhdust.phc as _phc
import pyhdust as _hdt

try:
    import matplotlib.pyplot as _plt
except:
    print('# Warning! matplotlib module not installed!!!')

__author__ = "Daniel Moser"
__email__ = "dmfaes@gmail.com"


class BAstar(object):
    """ BeAtlas source star filename structure.

    See BAmod.
    """
    def __init__(self, f0):
        self.M = f0[f0.find('_M')+2:f0.find('_M')+7]
        self.ob = f0[f0.find('_ob')+3:f0.find('_ob')+7]
        self.Z = f0[f0.find('_Z')+2:f0.find('_Z')+7]
        self.H = f0[f0.find('_H')+2:f0.find('_H')+6]
        self.beta = f0[f0.find('_Z')+8:f0.find('_Z')+10]
        self.shape = f0[f0.rfind('_')+1:f0.rfind('_')+4]
        self._f0 = f0
    #
    def __repr__(self):
        return self._f0

class BAmod(BAstar):
    """ BeAtlas disk model filename structure.

    It could be f0.split('_'), but the f0.find('_X') way was chosen.

    See that the parameters sequence is not important for this reading (this
    may not be the case of other routines). And, by definition, the source star
    has a specific name added at the end of disk model name, starting with
    'Be_'. """
    def __init__ (self, f0):
        """ Class initialiser """
        BAstar.__init__(self, f0)
        self.param = False
        if f0.find('_PL') > -1:
            self.n = f0[f0.find('_PLn')+4:f0.find('_PLn')+7]
            self.param = True
        self.sig = f0[f0.find('_sig')+4:f0.find('_sig')+8]
        self.h = f0[f0.find('_h')+2:f0.find('_h')+5]
        self.Rd = f0[f0.find('_Rd')+3:f0.find('_Rd')+8]
    #
    def build(self, ctrlarr, listpars):
        """ Set full list of parameters. """
        for i in range(len(ctrlarr)):
            if i == 0:
                self.M = _phc.find_nearest(listpars[i], ctrlarr[i])
            if i == 1:
                self.ob = _phc.find_nearest(listpars[i], ctrlarr[i])
            if i == 2:
                self.Z = _phc.find_nearest(listpars[i], ctrlarr[i])
            if i == 3:
                self.H = _phc.find_nearest(listpars[i], ctrlarr[i])
            if i == 4:
                self.sig = _phc.find_nearest(listpars[i], ctrlarr[i])
            if i == 5:
                self.Rd = _phc.find_nearest(listpars[i], ctrlarr[i])
            if i == 6:
                self.h = _phc.find_nearest(listpars[i], ctrlarr[i])
            if len(listpars) == 9:
                if i == 7:
                    self.n = _phc.find_nearest(listpars[i], ctrlarr[i])
                    self.param = True
                if i == 8:
                    self.cosi = _phc.find_nearest(listpars[i], ctrlarr[i])
            else:
                if i == 7:
                    self.cosi = _phc.find_nearest(listpars[i], ctrlarr[i])
    #
    def getidx(self, minfo):
        """ Find index of current model in minfo array. """
        if len(minfo[0])==9:
            self.idx = (minfo[:,0]==self.M) & (minfo[:,1]==self.ob) &\
        (minfo[:,2]==self.Z) & (minfo[:,3]==self.H) & (minfo[:,4]==self.sig) &\
        (minfo[:,5]==self.Rd) & (minfo[:,6]==self.h) & (minfo[:,7]==self.n) &\
        (minfo[:,-1]==self.cosi)
        else:
            self.idx = (minfo[:,0]==self.M) & (minfo[:,1]==self.ob) &\
        (minfo[:,2]==self.Z) & (minfo[:,3]==self.H) & (minfo[:,4]==self.sig) &\
        (minfo[:,5]==self.Rd) & (minfo[:,6]==self.h) &\
        (minfo[:,-1]==self.cosi)
        return self.idx


vrots = [[259.759,354.834,417.792,464.549,483.847],\
     [252.050,346.163,406.388,449.818,468.126],\
     [245.127,336.834,399.983,448.076,467.806],\
     [239.522,329.496,388.734,432.532,450.806],\
     [234.301,321.139,379.297,423.241,441.122],\
     [228.538,313.797,370.343,412.488,429.914],\
     [219.126,299.656,354.547,395.821,413.008],\
     [211.544,288.840,341.081,380.426,396.978],\
     [203.438,279.328,328.666,365.697,380.660],\
     [197.823,268.964,316.901,353.568,368.506],\
     [192.620,262.688,308.208,341.963,356.410],\
     [187.003,255.125,299.737,332.511,346.043]]

obs = [1.1,1.2,1.3,1.4,1.45]

ms = [14.6, 12.5, 10.8, 9.6, 8.6, 7.7, 6.4, 5.5, 4.8, 4.2, 3.8,3.4]

Ms = _np.array([14.6, 12.5, 10.8, 9.6, 8.6, 7.7, 6.4, 5.5, 4.8, 4.2, 3.8, 3.4],\
dtype=str)

Tp11 = _np.array([28905.8,26945.8,25085.2,23629.3,22296.1,20919.7,\
18739.3,17063.8,15587.7,14300.3,13329.9,12307.1])

sig0 = _np.logspace(_np.log10(0.02),_np.log10(4.0),7)

Sig0 = ['{0:.2f}'.format(x) for x in sig0]

ns = [3.0, 3.5, 4.0, 4.5]

def rmMods(modn, Ms, clusters=['job']):
    """
    Remove the *.inp models of models `modn` according to the list structure
    below.

    | Masses list ans sig0 POSITION do be excluded
    | Ms = [
    | ['14.6', [0]],
    | ['12.5', [0,-1]],
    | ['10.8', [0,-1]],
    | ['09.6',  [0,-2,-1]],
    | ['08.6',  [0,-2,-1]],
    | ['07.7',  [0,-2,-1]],
    | ['06.4',  [0,-3,-2,-1]],
    | ['05.5',  [0,-3,-2,-1]],
    | ['04.8',  [-4,-3,-2,-1]],
    | ['04.2',  [-4,-3,-2,-1]],
    | ['03.8',  [-4,-3,-2,-1]],
    | ['03.4',  [-4,-3,-2,-1]],]

    INPUT: string, structured list

    OUTPUT: *files removed
    """
    #Create sig0 list
    sig0s = Sig0
    project = _phc.trimpathname(_os.getcwd())[1]
    for cl in clusters:
        file = open('{0}s/{0}s_{1}_mod{2}.sh'.format(cl, project, modn))
        lines = file.readlines()
        file.close()
        for item in Ms:
            M = item[0]
            exsig = item[1]
            for rm in exsig:
                _os.system('rm mod{0}/mod{0}*_sig{1}*_M{2}*.inp'.format(modn,
                sig0s[rm], M))
                print('# Deleted mod{0}/mod{0}*_sig{1}*_M{2}*.inp'.format(modn,
                sig0s[rm],M))
                _os.system('rm {3}s/mod{0}*_sig{1}*_M{2}*.{3}'.format(modn,
                sig0s[rm], M, cl))
                lines = [line for line in lines if (line.find('_sig{0}'.format(
                sig0s[rm]))==-1 or line.find('_M{0}'.format(M))==-1)]
        file = open('{0}s/{0}s_{1}_mod{2}.sh'.format(cl, project, modn), 'w')
        file.writelines(lines)
        file.close()
    #End prog
    return

def fsedList(fsedlist, param=True):
    """ Return the total of models and the parameters values in the fullsed list.

    The len of fsedlist is 9 (param=True) for the parametric case and 8
    to the VDD-ST one.

    The sequence is: M, ob(W), Z, H, sig, Rd, h, *n*, cos(i).

    It is assumed that all models have the same `observers` configuration."""
    nq = 9
    if not param:
        nq = 8
    listpar = [[] for i in range(nq)]
    nm = 0
    for sed in fsedlist:
        mod = BAmod(sed)
        if mod.param == param:
            nm += 1
            if mod.M not in listpar[0]:
                listpar[0].append(mod.M)
            if mod.ob not in listpar[1]:
                listpar[1].append(mod.ob)
            if mod.Z not in listpar[2]:
                listpar[2].append(mod.Z)
            if mod.H not in listpar[3]:
                listpar[3].append(mod.H)
            if mod.sig not in listpar[4]:
                listpar[4].append(mod.sig)
            if mod.Rd not in listpar[5]:
                listpar[5].append(mod.Rd)
            if mod.h not in listpar[6]:
                listpar[6].append(mod.h)
            if param:
                if mod.n not in listpar[7]:
                    listpar[7].append(mod.n)
            if listpar[-1] == []:
                sed2data = _hdt.readfullsed2(sed)
                listpar[-1] = list(sed2data[:,0,0])
    #
    for vals in listpar:
        vals.sort()
    return nm*len(listpar[-1]), listpar
    

def createBAsed(fsedlist, xdrpath, lbdarr, param=True, savetxt=False,
    ignorelum=False):
    """ Create the BeAtlas SED XDR release.

    | The file structure:
    | -n_quantities, n_lbd, n_models,
    | -n_qt_vals1, n_qt_vals2, .. n_qt_valsn
    | -quantities values =  M, ob(W), Z, H, sig, Rd, h, *n*, cos(i).
    | -(Unique) lbd array
    | -Loop:
    |   *model values
    |   *model SED

    | Definitions:
    | -photospheric models: sig0 = 0.00
    | -Parametric disk model default (`param` == True)
    | -VDD-ST models: n excluded (alpha and R0 fixed. Confirm?)
    | -The flux will be given in ergs/s/um2/um. If ignorelum==True, the usual
    |   F_lbda/F_bol unit will be given.

    Since the grid is not symmetric, there is no index to jump directly to the
    desired model. So the suggestion is to use the index matrix, or read the
    file line by line until find the model (if exists).
    """
    fsedlist.sort()
    nq = 9
    if not param:
        nq = 8
    nm, listpar = fsedList(fsedlist, param=param)
    header2 = []
    for vals in listpar:
        header2 += [len(vals)]
    nlb = len(lbdarr)
    header1 = [nq, nlb, nm]
    models = _np.zeros((nm, nlb))
    minfo = _np.zeros((nm, nq))
    k = 0
    for i in range(len(fsedlist)):
        mod = BAmod(fsedlist[i])
        #~ Select only `param` matching cases:
        if mod.param == param:
            sed2data = _hdt.readfullsed2(fsedlist[i])
            iL = 1.
            dist = _np.sqrt(4*_np.pi)
            if not ignorelum:
                j =  fsedlist[i].find('fullsed_mod')
                modn = fsedlist[i][j+11:j+13]
                log = fsedlist[i].replace('fullsed_mod','../mod{0}/mod'.format(modn)).\
                replace('.sed2','.log')
                if not _os.path.exists(log):
                    log = _glob(log.replace('../mod{0}/mod'.format(modn),
                    '../mod{0}/*mod'.format(modn)))
                    if len(log) >= 1:
                        log = log[0]
                    else:
                        print('# ERROR! No log file found for {0}'.format(fsedlist[i]))
                        raise SystemExit(0)
                f0 = open(log)
                lines = f0.readlines()
                f0.close()
                iL = _phc.fltTxtOccur('L =', lines, seq=2)*_phc.Lsun.cgs
                dist = 10.*_phc.pc.cgs
            for j in range(header2[-1]):
                #~  M, ob(W), Z, H, sig, Rd, h, *n*, cos(i).
                if param:
                    minfo[k*header2[-1]+j] = _np.array([ mod.M, mod.ob, mod.Z, mod.H,
                mod.sig, mod.Rd, mod.h, mod.n, listpar[-1][j] ]).astype(float)
                else:
                    minfo[k*header2[-1]+j] = _np.array([ mod.M, mod.ob, mod.Z, mod.H,
                mod.sig, mod.Rd, mod.h, listpar[-1][j] ]).astype(float)
                if len(sed2data[j,:,2]) != nlb:
                    models[k*header2[-1]+j] = _np.interp(lbdarr, sed2data[j,:,2],
                sed2data[j,:,3])*iL/4/_np.pi/dist**2
                else:
                    models[k*header2[-1]+j] = sed2data[j,:,3]*iL/4/_np.pi/dist**2
            k += 1
    #
    f0 = open(xdrpath, 'w')
    stfmt = '>{0}l'.format(3)
    f0.writelines(_struct.pack(stfmt, *header1))
    stfmt = '>{0}l'.format(nq)
    f0.writelines(_struct.pack(stfmt, *header2))
    for vals in listpar:
        stfmt = '>{0}f'.format(len(vals))
        f0.writelines(_struct.pack(stfmt, *_np.array(vals).astype(float)))
    stfmt = '>{0}f'.format(nlb)
    f0.writelines(_struct.pack(stfmt, *_np.array(lbdarr).astype(float)))
    for i in range(nm):
        stfmt = '>{0}f'.format(nq)
        f0.writelines(_struct.pack(stfmt, *minfo[i]))
        stfmt = '>{0}f'.format(nlb)
        f0.writelines(_struct.pack(stfmt, *_np.array(models[i]).astype(float)))
    f0.close()
    print('# XDR file {0} saved!'.format(xdrpath))

    if savetxt:
        f0 = open(xdrpath+'.txt', 'w')
        f0.writelines('{} \n'.format(header1))
        f0.writelines('{} \n'.format(header2))
        for vals in listpar:
            f0.writelines('{} \n'.format(vals))
        f0.writelines('{} \n'.format(lbdarr))
        for i in range(nm):
            f0.writelines('{} \n'.format(minfo[i]))
            f0.writelines('{} \n'.format(models[i]))
        f0.close()
        print('# TXT file {0} saved!'.format(xdrpath+'.txt'))
    return
    

def readBAsed(xdrpath, quiet=False):
    """ Read the BeAtlas SED release.

    | Definitions:
    | -photospheric models: sig0 (and other quantities) == 0.00
    | -Parametric disk model default (`param` == True)
    | -VDD-ST models: n excluded (alpha and R0 fixed. Confirm?)
    | -The models flux are given in ergs/s/cm2/um. If ignorelum==True in the
    |   XDR creation, F_lbda/F_bol unit will be given.

    INPUT: xdrpath

    | OUTPUT: listpar, lbdarr, minfo, models 
    | (list of mods parameters, lambda array (um), mods index, mods flux)
    """
    f = open(xdrpath).read()
    ixdr=0
    #~ 
    npxs = 3
    upck = '>{0}l'.format(npxs)
    header = _np.array(_struct.unpack(upck, f[ixdr:ixdr+npxs*4]) )
    ixdr+=npxs*4
    nq, nlb, nm = header
    #~ 
    npxs = nq
    upck = '>{0}l'.format(npxs)
    header = _np.array(_struct.unpack(upck, f[ixdr:ixdr+npxs*4]) )
    ixdr+=npxs*4
    #~ 
    listpar = [[] for i in range(nq)]
    for i in range(nq):
        npxs = header[i]
        upck = '>{0}f'.format(npxs)
        listpar[i] = _np.array(_struct.unpack(upck, f[ixdr:ixdr+npxs*4]) )
        ixdr+=npxs*4
    #~ 
    npxs = nlb
    upck = '>{0}f'.format(npxs)
    lbdarr = _np.array(_struct.unpack(upck, f[ixdr:ixdr+npxs*4]) )
    ixdr+=npxs*4
    #~ 
    npxs = nm*(nq+nlb)
    upck = '>{0}f'.format(npxs)
    models = _np.array(_struct.unpack(upck, f[ixdr:ixdr+npxs*4]) )
    ixdr+=npxs*4
    models = models.reshape((nm,-1))
    #this will check if the XDR is finished.
    if ixdr == len(f):
        if not quiet:
            print('# XDR {0} completely read!'.format(xdrpath))
    else:
        print('# Warning: XDR {0} not completely read!'.format(xdrpath))
        print('# length difference is {0}'.format( (len(f)-ixdr)/4 ) )
    #~ 
    return listpar, lbdarr, models[:,0:nq], models[:,nq:]


def interpolBA(params, ctrlarr, lparams, minfo, models, param=True):
    """ Interpola os `modelos` para os parametros `params` 

    | -params = from emcee minimization
    | -ctrlarr = the fixed value of M, ob(W), Z, H, sig, Rd, h, *n*, cos(i).
    |            If it is not fixed, use np.NaN.
    | -Parametric disk model default (`param` == True).

    This function always returns a valid result (i.e., extrapolations from the
    nearest values are always on).

    If it is a 'Non-squared grid' (asymmetric), it will return a zero array if
    a given model is not found.
    """
    nq = 9
    if not param:
        nq = 8
    if len(ctrlarr) != nq:
        print('# ERROR in ctrlarr!!')
        return
    params = params[:_np.sum(_np.isnan(ctrlarr))]
    nlb = len(models[0])
    outmodels = _np.empty((2**len(params),nlb))
    mod = BAmod('')
    parlims = _np.zeros((len(params), 2))
    j = 0
    for i in range(nq):
        if ctrlarr[i] is _np.NaN:
            parlims[j] = [_phc.find_nearest(lparams[i], params[j], bigger=False),
            _phc.find_nearest(lparams[i], params[j], bigger=True)]
            j+= 1
    j = 0
    for prod in _product(*parlims):
        allpars = _np.array(ctrlarr)
        idx = _np.isnan(allpars)
        allpars[idx] = prod
        mod.build(allpars, lparams)
        idx = mod.getidx(minfo)
        if _np.sum(idx) == 0:
            return _np.zeros(nlb)
        outmodels[j] = models[idx]
        j+= 1
    X0 = parlims[:,0]
    X1 = parlims[:,1]
    return _phc.interLinND(params, X0, X1, outmodels)


def breakJob(n, file):
	""" Break the jobs/jobs_Project_modn.sh into n files 
	../jobs_Project_modn_##.txt to be used with `dispara` """
	f0 = open(file)
	lines = f0.readlines()
	f0.close()
	lines.sort()
	lines = [line.replace('qsub ','') for line in lines]
	outname = _phc.trimpathname(file)[1].replace('.sh','')
	N = len(lines)
	for i in range(n):
		f0 = open('{0}_{1:02d}.txt'.format(outname, i), 'w')
		f0.writelines(lines[i*N/n:(i+1)*N/n])
		f0.close()
	print('# {0} files created!'.format(n))
	return


def correltable(pos):
    """ Create the correlation table of Domiciano de Souza+ 2014. """
    nwalkers = len(pos)
    ndim = len(pos[0])
    fig = _plt.figure()
    for i in range(ndim**2):
        ax = fig.add_subplot(ndim,ndim,i+1)
        if i+1 in [ 1+x*(ndim+1) for x in range(ndim) ]:
            ax.hist(pos[:,i/ndim], 20)
        else:
            ax.plot(pos[:,i/ndim], pos[:,i%ndim], 'o', markersize=2)
    _plt.savefig('correl.png', Transparent=True)
    _plt.close()
    print('# Figure "correl.png" saved!')
    return


### MAIN ###
if __name__ == "__main__":
    pass
