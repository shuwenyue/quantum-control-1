'''noiseanalyser.py
'''

import numpy as np
from solvers import FieldToPath
from joblib import Parallel, delayed

class NoiseAnalyser(object):
    """this part does some noise analysis for a given field

    """

    def __init__(self,smoothfield,dt,variance,numfield,processors=4):
        self.field=smoothfield
        self.dt=dt
        self.numfield=numfield
        self.variance=variance
        self.processors = processors
        self.path=np.empty((len(self.field), 2 * self.numfield),dtype=complex)
        
 
    def calc_noisy_field(self):
        noisy_field=np.empty((len(self.field), 2 * self.numfield), dtype=complex)
        for i in range(self.numfield):
            sx=np.random.normal(0, self.variance, len(self.field))
            sy=np.random.normal(0, self.variance, len(self.field))
            noisy_field[:,0+i*2]=self.field[:,0]+np.transpose(sx)*self.field[:,0]
            noisy_field[:,1+i*2]=self.field[:,1]+np.transpose(sy)*self.field[:,1]
            
        self.noisy_field = noisy_field.astype(float)
       
     
    def calc_a_path(self, i):
        #def calc_a_path(i):
        path_solver = FieldToPath(self.noisy_field[:,[i*2,i*2+1]], self.dt)
        # Then invoke the solve() method of the path_solver object
        path_solver.solve()
        return path_solver.export()[1]

    def calc_path(self):
        '''Parallel version of calc_a_path'''
        noisy_paths = Parallel(n_jobs=self.processors)(delayed(self.calc_a_path)(i) for i in range(0,self.numfield))
        for i in range(0, len(noisy_paths)):
            self.path[:,[i*2,i*2+1]] = noisy_paths[i]
 
    def calc_statistic(self):
        xcollec= np.zeros((len(self.path),self.numfield))
        ycollec= np.zeros((len(self.path),self.numfield))
        for j in range(len(self.path)):
            for i in range(2*self.numfield):
                mod=i%2
                if mod==0:
                    xcollec[j,int(i/2)]=self.path[j,i]
                else:
                    ycollec[j,int((i-1)/2)]=self.path[j,i]
        pathxmean = np.zeros(len(self.path))
        pathymean = np.zeros_like(pathxmean)
        pathxvar = np.zeros_like(pathxmean)
        pathyvar = np.zeros_like(pathxmean)
        for i in range(len(self.path)):
            pathxmean[i]=sum(xcollec[i,:])/self.numfield
            pathymean[i]=sum(ycollec[i,:])/self.numfield
            pathxvar[i] =np.var(xcollec[i,:])
            pathyvar[i] =np.var(ycollec[i,:])
        self.pathmean = np.stack((pathxmean,pathymean),axis=1)
        self.pathvar = np.stack((pathxvar,pathyvar),axis=1)

    def analyze(self):
        self.calc_noisy_field()
        self.calc_path()
        self.calc_statistic()

        return self.pathmean.astype(float), self.pathvar.astype(float)

