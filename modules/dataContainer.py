'''!@namespace modules.dataContainer

@brief This module holds implementation for class DataContainer to store data

provided by user and generated by other classes.
'''

import numpy as np
from collections import namedtuple
from transform import transform_path
import warnings
warnings.filterwarnings("ignore")

class DataContainer(object):
    """!@brief A DataContainer contains all data associated with a single path.

    Class DataContainer provides a container to store data associated
    with a single path specified by user.
    """
    """
    #### Attributes:

    - n: Number of time points.

    - path_desired: User-specified desired path of dipole moment
    projection  described by x and y (in this order). A numpy
    ndarray of shape  (n,2).

    - field: Control fields e_x and e_y at each time point
    calculated by  PathToField. A numpy.ndarray of shape of (n,2).

    - path_actual: Path of dipole moment projection described by x
    and y that is resulted from the control field. A numpy.ndarray
    of shape (n,2).

    - state: Weights of (2m+1) basis describing the system at each
    time point. A numpy  ndarray of shape ((2m+1),n).

    - noise_stat_mean: mean x and y at each time point. A numpy
    ndarray of shape (n,2).
    
    - noise_stat_sd: standard deviation of x and y at each time
    point. A numpy ndarray of shape (n,2).

    """

    def __init__(self, path):
        """Initialize an object of DataContainer with a desired path.

        Parameters:

            path: A numpy.ndarray of shape (n,2) and each row contains
            (in this order) x- and y-projection of dipole moment.

            dt: (Optional) Time difference between two adjacent time 
            points

        Raises:

            TypeError: if input is not an instance of numpy.ndarray

            ValueError: if input numpy.ndarray is not n-by-2, or
                        contains nan or inf

        """
        
        #check type and shape of input path
        if not isinstance(path, np.ndarray):
            errmsg = ("DataContainer can only be instantiated with "
                      "nx2 numpy.ndarray as input argument.")
            raise TypeError(errmsg)
        if (path.ndim is not 2) or (path.shape[1] is not 2):
            errmsg = ("DataContainer can only be instantiated with nx2 "
                      "numpy.ndarray as input argument.")
            raise ValueError(errmsg)
        #check nan or inf in input path
        if np.isnan(path).any() or np.isinf(path).any():
            errmsg = ("DataContainer can only be instantiated with "
                      "nx2 numpy ndarray as input argument.")
            raise ValueError(errmsg)

        #attr calculated from input path
        ## User-specified path that is processed by interpolating 
        ## and smoothing for compatibility with solver. 
        ## n-by-2 np.ndarray
        path_transformed,dt = transform_path(path[:,0:].astype(float))
        self.path_desired = path_transformed
        ## Number of time points
        self.n = path_transformed.shape[0]
        ## Time difference between two adjacent time points in atomic units
        self.dt_atomic = dt
        self._t_atomic = np.arange(self.n*self.dt_atomic,
                                   step=self.dt_atomic, dtype=float)
        
        #attr initialized with all entries being zeros but of correct
        #shapes
        ## Time vector
        self.t = None
        ## Control field calculated by PathToField solver. n-by-2
        ## np.ndarray.
        self.field = np.zeros((self.n, 2),dtype=complex)
        ## Path predicted by the control field calculated. Shape same
        ## as `path_desired`
        self.path_actual = np.zeros_like(self.path_desired)
        ## Weights of 2m+1 basis describing the system. Each column is
        ## a 2m+1 vector for a time point. (2m+1)xn np.ndarray.
        self.state = None
        ## Mean of paths from noisy fields.
        self.noise_stat_mean = np.zeros((self.n, 2))
        ## Standard deviation of paths from noisy fields.
        self.noise_stat_sd = np.zeros((self.n, 2))





