import os
import tempfile
from dolfin import *

class BaseSolver(object):

    @staticmethod
    def default_parameters():
        raise NotImplementedError
    
    @staticmethod
    def parameter_parsers():
        """
        Should be overridden by solver subclass, and return a dictionary of
        possible conversions in the format

        { "parname": [lambda s: conversion_1(s),
                      lambda s: conversion_2(s), ...]}
        
        a "default converter" lambda s: s is always used if no conversion works
        for example:

        {"f":    [lambda s: Constant(float(s)),
                  lambda s: Expression(f)],
         "mesh": []} 
        
        would mean that parameters f are read as constants if possible,
        expressions if not (and as strings if that doesn't work either)
        while the mesh parameter is just stored as string without any conversion
        """
        
        ## specify arguments as a dict {argname: list of possible "conversions"}

        raise NotImplementedError



    def solve(self):
        raise NotImplementedError

    def update_parameters(self, new_parameters):
        for parname in new_parameters:
            # try all conversions until you find one which works. 
            # is self.__class__ ok?
            parsers = self.__class__.parameter_parsers()[parname]
            parsers.append(lambda s: s) # default if nothing works

            for parser in parsers:
                try:
                    self.params[parname] = parser(new_parameters[parname])
                    break
                except:
                    continue

    
    def __init__(self, params):
        self.params = self.__class__.default_parameters()
        self.update_parameters(params)

        

    def get_mesh(self):
        domain = self.params["domain"]

        if domain == "UnitInterval":
                mesh = UnitIntervalMesh(20)
        elif domain == "UnitSquare":
                   mesh = UnitSquareMesh(20, 20)
        elif domain == "UnitCube":
                mesh = UnitCubeMesh(5, 5, 5)
        elif domain == "Dolfin":
                here = os.path.dirname(__file__)
                mesh = Mesh(os.path.join(here, "dolfin.xml.gz"))
        else:
            raise ValueError, "Unknown domain: {}".format(domain)

        return mesh

    def plot(self):
	# Plot solution
        tmpfile = tempfile.NamedTemporaryFile(dir='/tmp', delete=False,
                  suffix=".png", prefix="fenicsbot_")
        tmpfile_name = tmpfile.name
        tmpfile.close()

	plot(self.solution).write_png(tmpfile_name[:-4])
        return tmpfile_name
