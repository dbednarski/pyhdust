# -*- coding:utf-8 -*-

"""
PyHdust *input* module: Hdust input tools.

:co-author: Rodrigo Vieira
:license: GNU GPL v3.0 (https://github.com/danmoser/pyhdust/blob/master/LICENSE)
"""
import os as _os
import numpy as _np
from glob import glob as _glob
from itertools import product as _product
import pyhdust.phc as _phc
import pyhdust as _hdt

__author__ = "Daniel Moser"
__email__ = "dmfaes@gmail.com"

    
def makeDiskGrid(modn='01', mhvals=[1.5], hvals=[.6], rdvals=[18.6], mvals=None,
    sig0vals=None, doFVDD=False, sBdays=None, sBfiles=None, selsources='*',
    alpha=.5, mu=.5, R0r=300, Mdot11=False, path=None):
    """
    | ###CONFIG. OPTIONS
    | #MODEL NUMBER
    | modn        = '02'
    | #The following filter will be applied to the SOURCE selection (string fmt)
    | selsources = '*'
    |                              
    | #SUPERFICIAL DENSITY PROFILE EXPONENT
    | mvals       = [1.5,2.0,2.5,3.0]
    | #VERTICAL DENSITY PROFILE EXPONENT     
    | mhvals      = [1.5]
    | #FRACTION OF TEFF OF PRIMARY STAR
    | #This parameter sets if it you be FIXED to OB=1.1 case
    | hvals       = [72.]
    | #DISK RADIUS EQUATORIAL...    
    | rdvals      = [30.]
    | #SIGMA_0 VALUES
    | sig0vals    = _np.logspace(_np.log10(0.02),_np.log10(4.0),7)
    | 
    | #Do the Full VDD model for the corresponding sig0?
    | doFVDD = True 
    | alpha = 0.5
    | mu = 0.5
    | #WARNING: it only generates a single R0 value per batch. If you want to change 
    | # it, run it twice (or more)
    | R0r = 300
    | ###END CONFIG.
    """
    G = _phc.G.cgs
    Msun = _phc.Msun.cgs
    Rsun = _phc.Rsun.cgs
    kB = _phc.kB.cgs
    mH = _phc.mH.cgs
    yr = _phc.yr.cgs
  
    def doPL(prodI):
        '''
        Given a prodI (i.e., src,sig0,rd,h,m,mh), generates the Power-Law model 
        input
        '''
        src,sig0,rd,h,m,mh = prodI
        M,Req,Tp = _hdt.readscr(src)
        Mstr = str(M)
        M *= Msun
        Req *= Rsun

        Th = h*Tp/100.
        #a0 = (kB*h/100.*Tp/mu/mH)**.5
        a = (kB*Th/mu/mH)**.5
        n0 = (G*M/2./_np.pi)**.5*sig0/mu/mH/a/Req**1.5
        #Th = a**2*mu*mH/kB

        srcname = src.replace('source/','').replace('.txt','')
        suffix = '_PLn{0:.1f}_sig{1:.2f}_h{2:03.0f}_Rd{3:05.1f}_{4}'.format(\
        (m+mh),sig0,h,rd,srcname)
        
        wmod = mod[:]
        wmod[13]=wmod[13].replace('18.6',('%.2f' % rd))
        wmod[20]=wmod[20].replace('2.0',('%.2f' % m))
        wmod[33]=wmod[33].replace('1.5',('%.2f' % mh))
        wmod[40]=wmod[40].replace('18000.',('%.1f' % Th))      
        wmod[52]=wmod[52].replace('2.35E13',('%.2e' % n0))      
              
        f0=open('mod'+modn+'/mod'+modn+suffix+'.txt', 'w')
        f0.writelines(wmod)
        f0.close()
        return
    
    def doMdot(prodI):
        '''
        Given a prodI (i.e., src,sig0,rd,h,m,mh), generates the full VDD model 
        input
        '''
        src,sig0,rd,h,m,mh = prodI
        M,Req,Tp = _hdt.readscr(src)
        Mstr = str(M)
        M *= Msun
        Req *= Rsun

        Th = h*Tp/100.
        a = (kB*Th/mu/mH)**.5
        #a0 = (kB*h/100*Tp/mu/mH)**.5
        #a = a0*Req0*Req**.25/Req/Req**.25
        
        R0 = R0r*Req
        Mdot = sig0*Req**2*3*_np.pi*alpha*a**2/(G*M*R0)**.5   #SI units
        Mdot = Mdot/Msun*yr
        #Th = a**2*mu*mH/kB
        
        srcname = src.replace('source/','').replace('.txt','')
        #suffix = '_NI_Mdot{:.1e}_Rd{:.1f}_R0{:.1f}_alp{:.1f}_h{:.1f}_{}'.\
        #format(Mdot,rd,R0/Req,alpha,h,srcname)
        suffix = '_NIa{0:.1f}_sig{1:.2f}_h{2:03.0f}_Rd{3:05.1f}_{4}'.format(\
        alpha,sig0,h,rd,srcname)
    
        wmod = mod[:]
        wmod[13]=wmod[13].replace('18.6',('%.2f' % rd))
        wmod[18]=wmod[18].replace('1',('%d' % 2))
        wmod[23]=wmod[23].replace('1.',('%.2f' % alpha)) 
        wmod[24]=wmod[24].replace('= 0.',('= %.2f' % (R0/Req)))
        wmod[25]=wmod[25].replace('= 0',('= %d' % 1))
        wmod[31]=wmod[31].replace('0',('%d' % 1))  
        wmod[40]=wmod[40].replace('18000.','{0:.1f}'.format(Th)) 
        wmod[49]=wmod[49].replace('2',('%d' % 3))            
        wmod[55]=wmod[55].replace('1.E-9',('%.2e' % Mdot))
          
        f0=open('mod'+modn+'/mod'+modn+suffix+'.txt', 'w')
        f0.writelines(wmod)
        f0.close()
        return

    def doSB(prodI, hseq=False):
        '''
        Given a prodI (i.e., sources,rdvals,hvals,mhvals,sBdays,sBfiles),
        generates the Single Be based model input
        '''
    
        src,rd,h,mh,day,sfile = prodI
        M,Req,Tp = _hdt.readscr(src)
        Mstr = str(M)
        M *= Msun
        Req *= Rsun

        Th = h*Tp/100.
        #a0 = (kB*h/100.*Tp/mu/mH)**.5
        a = (kB*Th/mu/mH)**.5
        #~ n0 = (G*M/2./_np.pi)**.5*sig0/mu/mH/a/Req**1.5
        #Th = a**2*mu*mH/kB

        srcname = src.replace('source/','').replace('.txt','')
        
        wmod = mod[:]
        wmod[13]=wmod[13].replace('18.6',('%.2f' % rd))
        wmod[18]=wmod[18].replace('= 1','= 4')
        wmod[28]=wmod[28].replace('deltasco/Atsuo/1D/data/dSco_a035_01',(sfile))
        wmod[29]=wmod[29].replace('2.3',('%.2f' % (day/365.25)))
        if not hseq:
            wmod[33]=wmod[33].replace('1.5',('%.2f' % mh))
            suffix = '_SB{0}_{1:.1f}d_h{2:03.0f}_Rd{3:05.1f}_{4}'.format(\
            _phc.trimpathname(sfile)[1],day,h,rd,srcname)
        else:
            wmod[31]=wmod[31].replace('= 0','= 1')
            wmod[36]=wmod[36].replace('1.5',('%.2f' % mh))
            suffix = '_SB{0}_{1:.1f}d_hseq_Rd{2:05.1f}_{3}'.format(\
            _phc.trimpathname(sfile)[1],day,rd,srcname)

        wmod[40]=wmod[40].replace('18000.',('%.1f' % Th))      
              
        f0=open('mod'+modn+'/mod'+modn+suffix+'.txt', 'w')
        f0.writelines(wmod)
        f0.close()
        return
    
    ###TODO Setup Tpole = REF of a (scale height)    
    #Tps = dict(zip(Ms, Tp11))
    
    ###PROGRAM BEGINS
    path0 = _os.getcwd()
    if path != None:
        _os.chdir(path)
        if path[-1] != '/':
            path += '/'
    else:
        path = ''
    #Check modN folder
    if not _os.path.exists('mod{}'.format(modn)):
        _os.system('mkdir mod{}'.format(modn))
    
    #Select sources
    sources = _glob('source/'+selsources)
    
    #Load disk model
    f0 = open('{0}/refs/REF_disco.txt'.format(_hdt.hdtpath()))
    mod = f0.readlines()
    f0.close()

    if sBdays is None or sBfiles is None:
        for prodI in _product(sources,sig0vals,rdvals,hvals,mvals,mhvals):
            doPL(prodI)
            i = 0
            if doFVDD:
                i = 1
                doMdot(prodI)
        print('# {0:.0f} arquivos foram gerados !!'.format(len(sources)*\
        len(sig0vals)*len(rdvals)*len(hvals)*(len(mvals)+i)*len(mhvals)))
    else:
        for prodI in _product(sources,rdvals,hvals,mhvals,sBdays,sBfiles):
            doSB(prodI)
            i = 0
            if doFVDD:
                i = 1
                doSB(prodI, hseq=True)
        print('# {0:.0f} arquivos foram gerados !!'.format(len(sources)*\
        len(rdvals)*len(hvals)*len(sBdays)*(len(mhvals)+i)*len(sBfiles)))

    if path is not '':
        _os.chdir(path0)
    ###END PROGRAM    
    return


def makeInpJob(modn='01', nodes=512, simulations=['SED'],
    docases=[1,3], sim1=['step1'], sim2=['step1_ref'], composition=['pureH'],
    controls=['controls'], gridcells=['grid'], observers=['observers'],
    images=[''], clusters=['job'], srcid='',
    walltime='24:00:00', wcheck=False, email='$USER@localhost', chkout=False,
    st1max=20, st1refmax=24, ctrM=False, touch=False, srcNf=None, path=None):
    """
    Create INP+JOB files to run Hdust.

    All SOURCE files must initiate by "Be_". Otherwise, the `makeInpJob` will
    not work. This is to satisfies the criteria of a specific disk model for
    each source star.
    
    | ### Start edit here ###
    | modn = '02'
    | 
    | #clusters config
    | # job = AlphaCrucis; oar = MesoCentre Licallo; ge = MesoCentre FRIPP
    | clusters = ['job','oar','ge','bgp']
    | clusters = ['oar']
    | nodes    = 48
    | #if wcheck == True, walltime will be AUTOMATICALLY estimated
    | walltime = '3:00:00'
    | wcheck   = True
    | email    = 'user@gmail.com'
    | 
    | #Check if the outputs already exist
    | chkout = True
    | #Above the values below, the step1 will be considered done!
    | st1max = 26
    | st1refmax = 30
    | #Gera inp+job so' para o source com '1.45' no nome
    | #Nao funciona caracteres especiais como * ou ?
    | srcid       = '1.45'
    | srcid       = ''
    | #Se um dos 3 casos nao estiver presente, ele gera input comentado.
    | docases = [1,2,3]
    | #1 = step1  <> Gera inp+job so' para mod#/mod#.txt (SEM source, so disco)
    | #habilita ADDSUFFIX; retira OBSERVERS e IMAGES
    | sim1 = 'step1'
    | #2 = step1_refine 
    | sim2 = 'step1_refine'
    | #3 = outros <> Gera inp+job so' para mod#/mod#SOURCE.txt (post-proc.)
    | #retira ADDSUFFIX; adiciona OBSERVERS (e talvez IMAGES)
    | simulations = ['sed','h','brg','halpha','uv']
    | simulations = ['sed_sig','brg_M','halpha_M','uv','j','h','k','l','m','n','q1','q2']
    | simulations = ['SED','Ha']
    | images      = ['','h','brg','halpha','uv']
    | images        = simulations[:]
    | composition = 'pureH'
    | controls    = 'no_op'
    | controls    = 'controls'
    | ctrM        = False
    | gridcells   = 'grid'
    | observers   = 'obs'
    | touch       = True
    | ###stop edition here
    """
    def isFloat(x):
        try:
            a = float(x)
        except ValueError:
            return False
        else:
            return True
    
    def doCase1(inp,cases):
        case1 = inp[:]
        case1[0] = case1[0].replace('suffix',suf)
        case1[1] = case1[1].replace('pureH',composition)
        if ctrM:
            i = suf.find('_M')
            M = suf[i:i+7]
            case1[2] = case1[2].replace('controls',controls+M)
        else:
            case1[2] = case1[2].replace('controls',controls)
        case1[3] = case1[3].replace('grid',gridcells)
        case1[4] = case1[4].replace('step1',sim1)
        case1[5] = case1[5].replace('source',src)
        if 1 not in cases:
            for i in range(len(case1)):
                case1[i] = '!~ '+case1[i]
        return case1
        
    def doCase2(inp,cases):
        case1 = inp[:]
        case1[0] = case1[0].replace('suffix',suf)
        case1[1] = case1[1].replace('pureH',composition)
        if ctrM:
            i = suf.find('_M')
            M = suf[i:i+7]
            case1[2] = case1[2].replace('controls',controls+M)
        else:
            case1[2] = case1[2].replace('controls',controls)
        case1[3] = case1[3].replace('grid',gridcells)
        case1[4] = case1[4].replace('step1',sim2)
        case1[5] = case1[5].replace('source',src)
        if 2 not in cases:
            for i in range(len(case1)):
                case1[i] = '!~ '+case1[i]
        return case1
    
    def doCase3(inp,simchk):
        case3 = []
        for i in range(len(simulations)):
            case1 = inp[:]
            case1[0] = case1[0].replace('suffix',suf)
            case1[1] = case1[1].replace('pureH',composition)
            if ctrM:
                j = suf.find('_M')
                M = suf[j:j+7]
                case1[2] = case1[2].replace('controls',controls+M)
            else:
                case1[2] = case1[2].replace('controls',controls)
            case1[3] = case1[3].replace('grid',gridcells)
            case1[5] = case1[5].replace('source',src)
            if simulations[i] == 'SED':
                sig = suf[suf.find('_sig')+4:suf.find('_sig')+8]
                if isFloat(sig) and srcNf[i]:
                    case1[4] = case1[4].replace('step1','SED_sig{0}'.format(sig))
                else:
                    case1[4] = case1[4].replace('step1',simulations[i])
            elif srcNf[i]:
                case1[4] = case1[4].replace('step1','{0}_{1}'.format(\
                simulations[i],src))
            else:
                case1[4] = case1[4].replace('step1',simulations[i])
            case1.append("OBSERVERS   = '{0}'\n".format(observers))
            if images[i] != '':
                case1.append("IMAGES      = '{0}'\n".format(images[i]))
            case1.append('\n')
            if not simchk[i]:
                for i in range(len(case1)):
                    case1[i] = '!~ '+case1[i]
            case3 += case1
        return case3
        
    def doJobs(mod, sel, nodes, addtouch='\n'):
        #load Ref
        f0 = open('{0}/refs/REF.{1}'.format(_hdt.hdtpath(),sel))
        wout = f0.readlines()
        f0.close()
        
        outname = mod[mod.find('/')+1:].replace('txt',sel)
            
        f0 = open('{0}s/{0}s_{1}_mod{2}.sh'.format(sel,proj,modn),'a')
        if sel == 'job':
            wout[4]  = wout[4].replace('128','{0}'.format(nodes))
            wout[4]  = wout[4].replace('36:00:00','{0}'.format(walltime))
            wout[8]  = wout[8].replace('alexcarciofi@gmail.com','{0}'.format(email))
            wout[11] = wout[11].replace('hdust_bestar2.02.inp','{0}/{1}'.\
            format(proj,mod.replace('.txt','.inp')))
            if touch:
                wout[24] = addtouch
                modchmod = _phc.trimpathname(mod)
                modchmod[1] = modchmod[1].replace('.txt','*')
                wout[31] = 'chmod 664 {0}/{1}/*{2}\nchmod 664 log/*\nchmod 664 ../../tmp/*\n'.\
                format(proj, *modchmod)
            f0.writelines('qsub {0}/{1}s/{2}\n'.format(proj,sel,outname))
        elif sel == 'oar':
            wout[2]  = wout[2].replace('12','{0}'.format(nodes))
            wout[2]  = wout[2].replace('24:0:0','{0}'.format(walltime))
            wout[10] = wout[10].replace('hdust_bestar2.02.inp','{0}/{1}'.\
            format(proj,mod.replace('.txt','.inp')))
            f0.writelines('chmod a+x {0}/{1}s/{2}\n'.format(proj,sel,outname))
            f0.writelines('oarsub -S ./{0}/{1}s/{2}\n'.format(proj,sel,outname))      
        elif sel == 'ge':
            wout[3] = wout[3].replace('48','{0}'.format(nodes))
            wout[4] = wout[4].replace('45:00:00','{0}'.format(walltime))
            wout[7] = wout[7].replace('dmfaes@gmail.com','{0}'.format(email))
            wout[11] = wout[11].replace('hdust_bestar2.02.inp','{0}/{1}'.\
            format(proj,mod.replace('.txt','.inp')))
            f0.writelines('qsub -P hdust {0}/{1}s/{2}\n'.format(proj,sel,outname))
        elif sel == 'bgp':
            wout[14] = wout[14].replace('512','{0}'.format(nodes))
            nodes = int(nodes)
            if nodes%512 != 0:
                nrsv = (nodes//512+1)*128
            else:
                nrsv = (nodes//512)*128
            wout[10] = wout[10].replace('128','{0}'.format(nrsv))
            wout[4] = wout[4].replace('24:00:00','{0}'.format(walltime))
            wout[14] = wout[14].replace('hdust_bestar2.02.inp','{0}/{1}'.\
            format(proj,mod.replace('.txt','.inp')))
            f0.writelines('chmod +x {0}/{1}s/{2}\n'.format(proj,sel,outname))
            f0.writelines('llsubmit ./{0}/{1}s/{2}\n'.format(proj,sel,outname))
        f0.close()
        
        f0 = open('{0}s/{1}'.format(sel,outname),'w')
        f0.writelines(wout)
        print('# Saved: {0}s/{1}'.format(sel,outname))
        f0.close()
        return
    
    #PROGRAM START
    if srcNf == None:
        srcNf = len(simulations)*[False]
    path0 = _os.getcwd()
    if path != None:
        _os.chdir(path)
        if path[-1] != '/':
            path += '/'
    else:
        path = ''
    #obtain the actual directory
    proj = _os.getcwd() 
    proj = proj[proj.rfind('/')+1:]
    
    #Folder's checks
    for sel in clusters:
        if not _os.path.exists('{0}s'.format(sel)):
            _os.system('mkdir {0}s'.format(sel))
        elif _os.path.exists('{0}s/{0}s_{1}_mod{2}.sh'.format(sel,proj,modn)):
            _os.system('rm {0}s/{0}s_{1}_mod{2}.sh'.format(sel,proj,modn))
    
    #list of mods
    mods = _glob('mod{0}/mod{0}*.txt'.format(modn))
    
    #load REF_inp
    f0 = open('{0}/refs/REF_inp.txt'.format(_hdt.hdtpath()))
    inp = f0.readlines()
    f0.close()
    
    for mod in mods:
        #Write inps
        f0 = open(mod.replace('.txt','.inp'),'w')
        f0.writelines('PROJECT = {0}\nMODEL = {1}\n\n'.format(proj,modn))
    
        suf = mod[mod.find('_'):-4]
        src = mod[mod.find('Be_'):-4]
        if src.find(srcid) == -1:
            continue

        cases = docases[:]
        #Do the touch thing
        addtouch = '\n'
        addtouch += 'chmod 664 ../../tmp/*\nchmod 664 {0}/mod{1}/*\n'.format(proj,modn)
        if touch and ( (1 in cases) or (2 in cases) ):
            addtouch += 'touch {0}/{1}\n'.format(proj, mod.replace('.txt','.log'))
        if touch and 3 in cases:
            for sim in simulations:
                addtouch += 'touch {0}/{1}\n'.format(proj,mod.replace('.txt','.chk')).replace('mod{0}/mod{0}'.format(modn), 'mod{0}/{1}_mod{0}'.format(modn, sim))
                addtouch += 'touch {0}/{1}\n'.format(proj,mod.replace('.txt','.err')).replace('mod{0}/mod{0}'.format(modn), 'mod{0}/{1}_mod{0}'.format(modn, sim))
                addtouch += 'touch {0}/{1}\n'.format(proj,mod.replace('.txt','.log')).replace('mod{0}/mod{0}'.format(modn), 'mod{0}/{1}_mod{0}'.format(modn, sim))
                addtouch += 'touch {0}/{1}\n'.format(proj,mod.replace('.txt','_SEI.chk')).replace('mod{0}/mod{0}'.format(modn), 'mod{0}/{1}_mod{0}'.format(modn, sim))
                addtouch += 'touch {0}/{1}\n'.format(proj,mod.replace('.txt','_SEI.err')).replace('mod{0}/mod{0}'.format(modn), 'mod{0}/{1}_mod{0}'.format(modn, sim))
                addtouch += 'touch {0}/{1}\n'.format(proj,mod.replace('.txt','_SEI.log')).replace('mod{0}/mod{0}'.format(modn), 'mod{0}/{1}_mod{0}'.format(modn, sim))
                err90a = '{0}/{1}'.format(proj,mod.replace('.txt','.err').replace('mod{0}/mod{0}'.format(modn), 'mod{0}/{1}_mod{0}'.format(modn, sim)))
                err90b = '{0}/{1}'.format(proj,mod.replace('.txt','_SEI.err').replace('mod{0}/mod{0}'.format(modn), 'mod{0}/{1}_mod{0}'.format(modn, sim)))
                addtouch += 'touch {0}\n'.format(err90a[:90])
                addtouch += 'touch {0}\n'.format(err90b[:90])
                addtouch += 'touch {0}\n'.format(err90a[:90].replace(".err",".chk").replace(".er",".ch").replace(".e",".c"))
                addtouch += 'touch {0}\n'.format(err90b[:90].replace(".err",".chk").replace(".er",".ch").replace(".e",".c"))
        modchmod = _phc.trimpathname(mod)
        modchmod[1] = modchmod[1].replace('.txt','*')
        #~ addtouch += 'chmod 664 {0}/{1}/*{2}\n'.format(proj, *modchmod)

        #Set simulation check variable
        if 3 in cases:
            simchk = _np.ones(len(simulations), dtype=bool)
        else:    
            simchk = _np.zeros(len(simulations), dtype=bool)
    
        if _os.path.exists(mod.replace('.txt','{0:02d}.temp'.format(st1max))) \
        and chkout and 1 in cases:
            cases.remove(1)
        case1 = doCase1(inp,cases)
        f0.writelines(case1+['\n'])
    
        if _os.path.exists(mod.replace('.txt','{0:02d}.temp'.format(st1refmax)))\
         and chkout and 2 in cases:
            cases.remove(2)    
        case2 = doCase2(inp,cases)
        f0.writelines(case2+['\n'])
        
        if chkout and 3 in cases:
            for i in range(len(simulations)):
                outs2a = 'mod{0}/{1}_mod{0}{2}.sed2'.format(modn,simulations[i],suf)
                outs2b = 'mod{0}/{1}_mod{0}{2}_SEI.sed2'.format(modn,simulations[i],suf)
                if _os.path.exists(outs2a) or _os.path.exists(outs2b):
                    simchk[i] = False
            if True not in simchk:
                cases.remove(3)
        case3 = doCase3(inp,simchk)
        f0.writelines(case3)
        f0.close()
        
        #Def automatic walltime:
        if wcheck:
            h = 0 
            if 1 in cases:
                h+=1
            if 2 in cases:
                h+=1
            idx = _np.where(simchk==True)
            if len(idx[0])>0:
                extra = 4+len(idx[0])
                h = h+extra*48/nodes
            walltime = '{0}:0:0'.format(h)
        
        #Del old jobs
        for sel in clusters:
            outname = mod[mod.find('/')+1:].replace('txt',sel)
            if _os.path.exists('{0}s/{1}'.format(sel,outname)):
                _os.system('rm {0}s/{1}'.format(sel,outname))
        
        #Write jobs (if necessary)
        if len(cases)>0:
            for sel in clusters:
                doJobs(mod,sel,nodes,addtouch)

    if path is not '':
        _os.chdir(path0)
    #PROGRAM END
    return

def makeNoDiskGrid(modn, selsources, path=None):
    """
    #Create a model list with random disk parameters ("noCS" in filename)
    
    INPUT:  modn = '01'; selsources = '*' (filter that is applied to the SOURCE
    selection).

    OUTPUT: Files written
    """
    
    def doNoCS(src):
        '''
        Given a src, generates the noCS model input
        '''
        srcname = src.replace('source/','').replace('.txt','')
        suffix = '_noCS_{}'.format(srcname)
        
        wmod = mod[:]
        #Remove a disk does not work:
        #wmod[9]=wmod[9].replace('1','0')
        wmod[13]=wmod[13].replace('18.6','2.0')
              
        f0=open('mod'+modn+'/mod'+modn+suffix+'.txt', 'w')
        f0.writelines(wmod)
        f0.close()
        return
        
    ###PROGRAM BEGINS
    path0 = _os.getcwd()
    if path != None:
        _os.chdir(path)
        if path[-1] != '/':
            path += '/'
    else:
        path = ''
    #Check modN folder
    if not _os.path.exists('mod{}'.format(modn)):
        _os.system('mkdir mod{}'.format(modn))
    
    #Select sources
    sources = _glob('source/'+selsources)
    
    #Load disk model
    f0 = open('{0}/refs/REF_disco.txt'.format(_hdt.hdtpath()))
    mod = f0.readlines()
    f0.close()
    
    for prodI in _product(sources):
        prodI = prodI[0]
        doNoCS(prodI)
    print('# {:.0f} arquivos foram gerados !!'.format(len(sources)))
    if path is not "":
        _os.chdir(path0)
    ###END PROGRAM
    return


def makeSimulLine(vrots, basesims, Rs, hwidth, Ms, Obs, suffix):
    """
    | vrots = [[167.023,229.187,271.072,301.299,313.702],
    |          [177.998,244.636,290.596,324.272,338.298],
    |          [192.612,267.017,318.288,355.320,370.638],
    |          [202.059,281.667,335.158,373.716,389.782],
    |          [209.244,292.409,358.626,410.439,430.844],
    |          [214.407,297.661,357.799,402.628,420.683]]
    
    | vrots = [[259.759,354.834,417.792,464.549,483.847],
    |          [252.050,346.163,406.388,449.818,468.126],
    |          [245.127,336.834,399.983,448.076,467.806],
    |          [239.522,329.496,388.734,432.532,450.806],
    |          [234.301,321.139,379.297,423.241,441.122],
    |          [228.538,313.797,370.343,412.488,429.914],
    |          [219.126,299.656,354.547,395.821,413.008],
    |          [211.544,288.840,341.081,380.426,396.978],
    |          [203.438,279.328,328.666,365.697,380.660],
    |          [197.823,268.964,316.901,353.568,368.506],
    |          [192.620,262.688,308.208,341.963,356.410],
    |          [187.003,255.125,299.737,332.511,346.043]]
    |         
    | basesims = ['simulation/Brg.txt','simulation/Ha.txt']
    | Rs = [12000, 20000]
    | 
    | Ms = [4.00,5.00,7.00,9.00,12.00,15.00]
    | Ms = [14.6, 12.5, 10.8, 9.6, 8.6, 7.7, 6.4, 5.5, 4.8, 4.2, 3.8, 3.4]
    | Obs = [1.1,1.2,1.3,1.4,1.45]
    | suffix = 'H0.30_Z0.014_bE_Ell'
    """
    c = _phc.c.cgs

    for prodI in _product(Ms,Obs,basesims):
        M,Ob,basesim = prodI
    
        f0 = open(basesim)
        mod = f0.readlines()
        f0.close()
        
        srcid = 'Be_M{0:05.2f}_ob{1:.2f}'.format(M,Ob)
                
        i = Ms.index(M)
        j = Obs.index(Ob)
        k = basesims.index(basesim)
        R = Rs[k]
        nmod = mod[:]
        vel = '{0:.1f}'.format(hwidth+vrots[i][j])
        nmod[103] = nmod[103].replace('1020.',vel)
        n = str(int(round(2*(hwidth+vrots[i][j])*R/c*1e5)))
        print(srcid, n)
        nmod[100] = nmod[100].replace('100',n)
    
        f0 = open(basesim.replace('.txt','_{0}_{1}.txt'.format(srcid, suffix)),'w')
        f0.writelines(nmod)
        f0.close()
    return


def makeStarGrid(oblats, Hfs, path=None):
    """
    | INPUT: oblats = [1.1,1.2,1.3,1.4,1.45] (example)
    | Hfs = [0.3] (example)

    Masses list a Z value are inside `geneve_par.pro` file.
    """
    path0 = _os.getcwd()
    if path != None:
        _os.chdir(path)
        if path[-1] != '/':
            path += '/'
    else:
        path = ''
    if not _os.path.exists('stmodels'):
        _os.system('mkdir stmodels')
    try:
        runIDL = True 
        import pidly
    except ImportError:
        print('# This system do not have pIDLy installed...')
        runIDL = False
        
    if runIDL:
        key = raw_input('# Do you want to run "geneve_par" (y/other):')
        if key != 'y':
            runIDL = False
    
    if runIDL:
        import pidly
        idl = pidly.IDL()
        propath = _hdt.hdtpath()+'/refs/'
        idl('cd,"{0}"'.format(propath))
        idl('.r geneve_par')
        for ob in oblats:
            for H in Hfs:
                idl('geneve_par, {}, {}, /oblat,/makeeps'.format(ob,H))
                _os.system('mv {}/geneve_lum.eps stmodels/geneve_lum_{:.2f}_{:.2f}.eps'.format(propath,ob,H))
                _os.system('mv {}/geneve_rp.eps stmodels/geneve_rp_{:.2f}_{:.2f}.eps'.format(propath,ob,H))
                _os.system('mv {}/geneve_par.txt stmodels/oblat{}_h{}.txt'.format(propath,ob,H))
        idl.close()
    
    f0 = open('{0}/refs/REF_estrela.txt'.format(_hdt.hdtpath()))
    mod = f0.readlines()
    f0.close()

    if not _os.path.exists('source'):
        _os.system('mkdir source')
    
    for ob in oblats:                        
        for H in Hfs:  
            f0 = open('stmodels/oblat{}_h{}.txt'.format(ob,H))                     
            matriz = f0.readlines() 
            f0.close()
            Omega,W,Beta = map(float, matriz[1].split())
            
            m2 = []
            for i in range(4,len(matriz)):
                    if len(matriz[i])>1:
                        m2 += [matriz[i].split()[1:]]
            matriz = _np.array(m2, dtype=float)
            M      = matriz[:,0]            #MASS (SOLAR MASSES)
            M = list(M)
            Rp     = matriz[:,1]           #POLAR RADIUS (SOLAR RADII)
            Rp = list(Rp)
            L      = matriz[:,2]           #LUMINOSITY (in solar lum.)
            L = list(L)
            Z      = [0.014]                                 #METALLICITY(=Zsolar) 
                                                               #(other options: 0.006, 0.002)
            
            print 'Omega = ', Omega; print 'W     = ', W; print 'beta  = ', Beta;
            print 'M     = ', M; print 'Rp    = ', Rp; print 'L     = ', L
            print "%.0f arquivos gerados\n" % (len(M)*len(Hfs))
        
            #DEFINE ALL INDEX
            for MI in M:
                a     = M.index(MI)
                Raio  = Rp[a]
                Lum   = L[a]
        
                for RpI in Rp:        
                    b = Rp.index(RpI)
                    for LI in L:
                        d = L.index(LI)
                        for ZI in Z:
                            g = Z.index(ZI)
                            suffix = '_M{:05.2f}_ob{:.2f}_H{:.2f}_Z{}_bE_Ell'. \
                                        format(MI,ob,H,ZI,Beta,RpI,LI)
    
                            #REGISTRA VALORES
                            wmod = mod[:]        
                            wmod[3]=wmod[3].replace('10.3065',('%.2f' % MI))
                            wmod[4]=wmod[4].replace('5.38462',('%.2f' % Raio))
                            wmod[5]=wmod[5].replace('0.775',('%.4f' % W))            
                            wmod[6]=wmod[6].replace('7500.',('%.2f' % Lum))
                            wmod[7]=wmod[7].replace('0.25',('%.5f' % Beta))
    
                            f0=open('source/Be'+suffix+'.txt', 'w')
                            f0.writelines(wmod)
                            f0.close()
    #
    if path is not "":
        _os.chdir(path0)
    return


def makeSimulDens(dbase, basesim):
    """
    Sets the SED simulations number of photos so that the signal/noise level
    is approximately constant at visible polarization.

    |dbase = _np.logspace(_np.log10(0.02),_np.log10(4.0),7)
    |basesim = 'simulation/sed.txt'
    """
    f0 = open(basesim)
    mod = f0.readlines()
    f0.close()
    #fact = 2.  Tempo execucao = d/1e13*fact
    #Nf0 = 500000000
    for d in dbase:
        srcid = 'sig{0:.2f}'.format(d)
        #alpha = .39794
        #beta =  13.87219
        alpha = 0.34588
        beta =  8.50927
        newd = int(10**(-alpha*_np.log10(d)+beta))
        print('{}, N_f = {:.2f}e+9'.format(srcid, newd/1e9))
        nmod = mod[:]
        nmod[9]=nmod[9].replace('500000000','{}'.format(newd))
        f0 = open(basesim.replace('.txt','_{}.txt'.format(srcid)),'w')
        f0.writelines(nmod)
        f0.close()
    #a = raw_input('asdads')
    return 

### MAIN ###
if __name__ == "__main__":
    pass
