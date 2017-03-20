'''
System is the main module that contains the base classes that
describe the objects in the system.  An instance of the system
can be created of Atom, Molecule, or System classes.

For purely atomic based systems, a set of utilities are provided
to hold information, to calculate properties, and to manipulate
the structures in space.  In addition, basic file input / output
is provided in the Mol class (and inherited up the classes
as dictated by the calling code).
'''

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# from __future__ import unicode_literals


#    SASMOL: Copyright (C) 2011 Joseph E. Curtis, Ph.D.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#   SYSTEM
#
#    12/4/2009     --    initial coding          :    jc
#    12/10/2009    --    doc strings             :    jc
#    01/11/2010    --    new design pattern      :    jc
#    12/25/2015    --    refactored for release  :    jc
#    07/23/2016    --    refactored for Python 3 :    jc
#    08/19/2016    --    added doc strings       :    jc
#
#        1         2         3         4         5         6         7
# 34567890123456789012345678901234567890123456789012345678901234567890123456789


import os
import numpy
import sasmol.file_io as file_io
import sasmol.calculate as calculate
import sasmol.operate as operate
import sasmol.subset as subset
import sasmol.properties as properties
import sasmol.topology as topology
import sasmol.view as view

import sasmol.config as config


class Atom(file_io.Files, calculate.Calculate, operate.Move, subset.Mask,
           properties.Atomic, topology.Topology, view.View):
    '''
    Base class containing methods to define system objects.

    Atom is the base class to build and deal with molecular systems.
    The class inherits file input/output, calcuation, manipulation, subset,
    atom properties, topology, and viewing from other samsol classes.

    Class has several initialization options

    Parameters
    ----------
    args
        optional integer : self._id

    kwargs
        optional keyword arguments
            string filename (filename = 'hiv1_gag.pdb') : default = None
            integet id (id=3) : default = 0
            boolean debug (debug = True) : default = None

    Returns
    -------
    system object
        if called with string (or with filename kwarg) returns
        an initialized system object with data read in using
        file_io.read_pdb()

    Examples
    -------

    Since subsequent classes in this file inherit from Atom and the
    common use case involves molecules, examples will use the Molecule()
    class instead of Atom.

    Intantiate a Molecule reading a PDB to get the definitions

    >>> import sasmol.system as system
    >>> molecule = system.Molecule(filename='hiv1_gag.pdb')

    Intantiate a Molecule based of input definitions

    >>> molecule = system.Molecule(create={'natoms': 24, 'name': 'Ar'})

    Other instance definition examples (not-exhaustive)

    >>> molecule = system.Molecule()
    >>> molecule = system.Molecule(id=7)
    >>> molecule = system.Molecule(debug=True)
    >>> molecule = system.Molecule('hiv1_gag.pdb')
    >>> molecule = system.Molecule(filename='hiv1_gag.pdb', id=0,
                                   debug=False)

    Example of how setters and getters work.  Below, the original index
    values are adjusted by a value (-10) and setIndex() is used to assign
    the new list to the molecule

    >>> molecule.index()[0]
    1
    >>> offset = -10
    >>> index = [x + offset for x in xrange(molecule.natoms())]
    >>> molecule.setIndex(index)
    >>> molecule.index()[0]
    -10

    Note
    ----

    `self` parameter is not shown in the ``Parameters`` section
    of the documentation


    Many "setters" and "getters" methods are defined in this class.  See source
    code for details.


    ### attributes of len(natoms):

        # python lists:

            list_keys = ['_residue_flag', '_occupancy', '_charge', '_atom',
                         '_chain', '_segname', '_beta', '_loc', '_element',
                        '_name', '_rescode', '_moltype', '_resname',
                        '_charmm_type', '_atom_charge', '_atom_vdw',
                        '_residue_charge', '_one_letter_resname' ]


        # numpy arrays: note that _coor has dimensions (number of frames,
                                                        natoms, 3)

        numpy_keys = ['_original_index', '_original_resid', '_index', '_resid',
                      '_mass', '_coor', '_minimum', '_maximum', '_pmi']


    ### attributes with variable list lenghts:

        #python lists:

        short_keys = ['_resnames', '_chains', '_resids', '_elements',
                      '_segnames', '_betas', '_names', '_moltypes',
                    '_occupancies' ]
        # numpy arrays

        numpy_short_keys = ['_names_mask', '_resnames_mask', '_resids_mask',
                            '_chains_mask', '_occupancies_mask', '_betas_mask',
                            '_elements_mask', '_segnames_mask']

    ### integer attributes

        int_keys = ['_number_of_chains', '_number_of_betas',
                    '_number_of_resids', '_number_of_names',
                    '_number_of_moltypes', '_number_of_resnames',
                    '_number_of_segnames', '_number_of_elements', '_id',
                    '_number_of_occupancies', '_number_of_frames', '_natoms' ]


    ### float attributes

        float_keys = ['_total_mass', '_com', '_rg']

    ### strings, dictionaries, and flags

        other_keys = ['_fasta', '_header', '_conect', '_debug', '_formula',
                      '_unitcell']

    '''

    def __init__(self, *args, **kwargs):
        self._filename = kwargs.pop('filename', None)
        parameters = kwargs.pop('create', None)
        self._id = kwargs.pop('id', 0)
        self._debug = kwargs.pop('debug', None)

        self._total_mass = 0.0
        self._natoms = 0
        self._mass = None
        self._coor = None
        self._com = None
        self._conect = []

        if config.__logging_level__ == 'DEBUG':
            self._debug = True

        self._defined_with_input_file = False
        self._defined_from_parameters = False
        self._argument_flag = False
        self._id_flag = False

        try:
            if self._filename is not None:
                if(os.path.isfile(self._filename)):
                    self.read_pdb(self._filename)
                    self._defined_with_input_file = True
            elif parameters is not None:
                self.creator(**parameters)
                self._defined_from_parameters = True
            else:
                for argument in args:
                    self._argument_flag = True
                    if(os.path.isfile(str(argument))):
                        try:
                            self.read_pdb(argument)
                            self._defined_with_input_file = True
                            self._filename = argument
                            break
                        except:

                            pass
                    else:
                        try:
                            self._id = int(argument)
                            self._id_flag = True
                            break
                        except:
                            pass

        except:
            pass

    def __repr__(self):

        if self._defined_with_input_file:
            return "sasmol object initialized with filename = " + self._filename
        elif self._argument_flag and not self._id_flag:
            return "sasmol object (no file found)"
        elif self._defined_from_parameters:
            return "sasmol object initialized using input parameters"
        else:
            return "sasmol object"

    def __add__(self, other):
        '''
        Override the python __add__ method to combine molecules

        Parameters
        ----------
        other
            system object

        kwargs
            optional keyword arguments

        Returns
        -------
        None
            modified system object

        Examples
        -------

        >>> import sasmol.system as system
        >>> molecule_1 = system.Molecule(filename='hiv1_gag.pdb')
        >>> molecule_2 = system.Molecule(filename='lysozyme.pdb')
        >>> molecule_1.natoms()
        6730
        >>> molecule_2.natoms()
        1960

        >>> molecule_3 = molecule_1 + molecule_2
        >>> molecule_3.natoms()
        8690
        >>> molecule_3.index()[-1]
        8690

        >>> molecule_4 = sum([molecule_1, molecule_2, molecule_3])
        >>> molecule_4.natoms()
        17380
        >>> molecule_4.index()[-1]
        17380

        Note
        ____

        An assertion error will occur if items are missing from either molecule

        self._natoms is updated based on the len(self._names)

        self._index is reset to start at 1 and end at self._natoms

        '''
        values = self.field_definitions()

        natoms = self._natoms + other._natoms
        values.pop('natoms')

        # combine the numpy arrays
        assert self._coor.shape[0] == other._coor.shape[0], (
            'inconsistent number of frames')
        assert self._coor.shape[2] == 3, 'improperly shaped coordinates'
        assert other._coor.shape[2] == 3, 'improperly shaped coordinates'
        coor = []
        for i in range(len(self._coor)):
            coor.append(numpy.vstack((self._coor[i], other._coor[i])))
        coor = numpy.array(coor)
        assert len(coor[0]) == natoms
        values.pop('coor')

        resid = numpy.append(self._resid, other._resid)
        assert len(resid) == natoms, 'resid definition/s incorrect'
        values.pop('resid')

        values.pop('index')  # reindexed combined results from 1

        # combine the lists
        for key in values.keys():
            _key = '_{}'.format(key)
            values[key] = self.__dict__[_key] + other.__dict__[_key]
            assert len(values[key]) == natoms, 'missing {} entries'.format(key)

        values['natoms'] = natoms
        values['coor'] = coor
        values['resid'] = resid
        return Molecule(create=values)

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)


    def append(self, other, **kwargs):
        '''
        Override the python __add__ method to combine other molecule into
        instance molecule

        Parameters
        ----------
        other
            system object

        kwargs
            optional keyword arguments

        Returns
        -------
        None
            modified system object

        Examples
        -------

        >>> import sasmol.system as systemdef_dict
        >>> molecule_1 = system.Molecule(filename='hiv1_gag.pdb')
        >>> molecule_2 = system.Molecule(filename='lysozyme.pdb')
        >>> molecule_1.natoms()
        6730
        >>> molecule_2.natoms()
        1960

        >>> molecule_1.append(molecule_2)
        >>> molecule_1.natoms()
        8690
        >>> molecule_1.index()[-1]
        8690


        Note
        ____

        If an item is missing in the other molecule then the original item is
        not altered

        self._natoms is updated based on the len(self._names)

        self._index is reset to start at 1 and end at self._natoms

        Currently no check is made on the number of frames in each molecule
        that are being added together.

        '''

        for key, value in self.__dict__.iteritems():
            try:
                if isinstance(value, list):
                    self.__dict__[key].extend(other.__dict__[key])
                elif isinstance(value, numpy.ndarray):
                    if key == '_coor':
                        self.__dict__[key] = numpy.concatenate(
                            (self.__dict__[key], other.__dict__[key]), axis=1)
                    elif len(value.shape) == 1:
                        self.__dict__[key] = numpy.concatenate(
                            (self.__dict__[key], other.__dict__[key]))
                    else:
                        print(
                            'numpy array not added for self.__dict__[key]: ' +
                            str(key))

            except:
                pass

            self._natoms = len(self._name)
            self._index = numpy.array([x + 1 for x in xrange(self._natoms)],
                                      numpy.int)

        self._update_unique_properties()

    def create(self, natoms, **kwargs):
        parameters = {'natoms': natoms}
        parameters.update(kwargs)
        self.creator(**parameters)

    def creator(self, **kwargs):
        '''
        This method is used to populate the fields required for a sasmol object
        to use read_pdb() and write_pdb() methods from file_io.

        Default inputs are itemized below. The values are assigned to all
        atoms in the molecule.

        Once defined, attributes can be set using setters in the Atom class.

        Class has several initialization options

        Parameters
        ----------
        kwargs:
            natoms
                integer : number listof atoms in the molecule

            atom
                string  : name of ATOM keyword, typically either ATOM or HETATM

            index
                numpy array of integers : atom number

            name
                string : atom name

            loc
                string : alt loc

            resname
                string  : residue name

            chain
                string  : chain name

            resid
                integer list : residue number

            rescode
                string  : residue code

            coor
                numpy float array : x, y, z coordinates

            occupancy
                string  : occupancy value

            beta
                string  : beta value

            segname
                string  : segment name

            element
                string  : element name

            charge
                string  : element charge

        Returns
        -------
        system object

        Examples
        -------
        >>> import sasmol.system as system
        >>> molecule = system.Molecule()
        >>> molecule.creator(2048, name='O')
        >>> molecule.natoms()
        2048
        >>> molecule.names()
        ['O']
        >>> molecule.creator(1024, name='Ar', segname='ARG0')
        >>> molecule.natoms()
        1024
        >>> molecule.names()
        ['Ar']
        >>> molecule.segnames()
        ['ARG0']
        >>> index = [x for x in xrange(34,40)]
        >>> molecule.creator(6, name='He', index=index)
        >>> molecule.index()[0]
        34
        >>> molecule.original_index()
        [34, 35, 36, 37, 38, 39]

        '''
        # setup the default values
        pdb_defaults = self.field_definitions()
        pdb_defaults['index'] = None
        pdb_defaults['coor'] = None
        pdb_defaults['resid'] = None
        pdb_defaults['natoms'] = 1
        pdb_defaults['atom'] = 'ATOM'
        pdb_defaults['loc'] = ' '
        pdb_defaults['resname'] = 'DUM'
        pdb_defaults['chain'] = 'A'
        pdb_defaults['name'] = 'C'
        pdb_defaults['rescode'] = ' '
        pdb_defaults['occupancy'] = '0.00'
        pdb_defaults['beta'] = '0.00'
        pdb_defaults['segname'] = 'DUM'
        pdb_defaults['element'] = 'C'
        pdb_defaults['charge'] = ' '

        # populate the values required to write a pdb
        natoms_default = pdb_defaults.pop('natoms')
        self._natoms = kwargs.pop('natoms', natoms_default)

        for key in ['index', 'resid']:
            _key = '_{}'.format(key)
            val_default = pdb_defaults.pop(key)
            val = kwargs.pop(key, val_default)
            if val is not None and len(val) == self._natoms:
                self.__dict__[_key] = val
            else:
                self.__dict__[_key] = numpy.arange(self._natoms) + 1

        coor_default = pdb_defaults.pop('coor')
        coor = kwargs.pop('coor', coor_default)
        try:
            assert coor is not None
            assert 3 == coor.shape[2]
            assert self._natoms == coor.shape[1]
            self._coor = coor
        except (IndexError, AttributeError, AssertionError):
            self._coor = numpy.zeros((1, self._natoms, 3), numpy.float)

        for key in pdb_defaults.keys():
            val = kwargs.pop(key, pdb_defaults.pop(key))
            _key = '_{}'.format(key)
            if type(val) is list and len(val) == self._natoms:
                self.__dict__[_key] = val
            else:
                self.__dict__[_key] = [val] * self._natoms

        # populate the values returned when reading a pdb
        (protein_resnames, dna_resnames, rna_resnames, nucleic_resnames,
         water_resnames) = self.get_resnames()
        moltype = dict.fromkeys(protein_resnames, 'protein')
        moltype.update(dict.fromkeys(rna_resnames, 'rna'))
        moltype.update(dict.fromkeys(dna_resnames, 'dna'))
        moltype.update(dict.fromkeys(water_resnames, 'water'))
        self._moltype = [moltype.get(rn, 'other') for rn in self._resname]

        self._update_unique_properties()

        self._original_index = numpy.copy(self._index)
        self._original_resid = numpy.copy(self._resid)
        self._residue_flag = [False] * self._natoms
        self._header = []

        # return self for __add__
        return self

    def _update_unique_properties(self):
        properties = ['beta', 'chain', 'element', 'moltype', 'name', 'resid',
                      'resname', 'segname', 'occupancy']
        for key in properties:
            _key = '_{}'.format(key)
            if _key in self.__dict__.keys():
                if key != 'occupancy':

                    _keys = '{}s'.format(_key)
                    self.__dict__[_keys] = list(set(self.__dict__[_key]))

                    _number_of_key = '_number_of_{}'.format(key)
                    self.__dict__[_number_of_key] = len(self.__dict__[_keys])

                else:
                    self._occupancies = list(set(self._occupancy))
                    self._number_of_occupancies = len(self._occupancies)

    def setId(self, newValue):
        self._id = newValue

    def id(self):
        return self._id

        # properties

    def number_of_frames(self):
        return self._coor[:, 0, 0].shape[0]

    def setNumber_of_frames(self, newValue):
        self._number_of_frames = newValue

    def atom(self):
        return self._atom

    def setAtom(self, newValue):
        self._atom = newValue

    def index(self):
        return self._index

    def setIndex(self, newValue):
        self._index = newValue

    def original_index(self):
        return self._original_index

    def setOriginal_index(self, newValue):
        self._original_index = newValue

    def original_resid(self):
        return self._original_resid

    def setOriginal_resid(self, newValue):
        self._original_resid = newValue

    def name(self):
        return self._name

    def setName(self, newValue):
        self._name = newValue

    def loc(self):
        return self._loc

    def setLoc(self, newValue):
        self._loc = newValue

    def resname(self):
        return self._resname

    def setResname(self, newValue):
        self._resname = newValue

    def chain(self):
        return self._chain

    def setChain(self, newValue):
        self._chain = newValue

    def resid(self):
        return self._resid

    def setResid(self, newValue):
        self._resid = newValue

    def coor(self):
        return self._coor

    def setCoor(self, newValue):
        self._coor = newValue

    def rescode(self):
        return self._rescode

    def setRescode(self, newValue):
        self._rescode = newValue

    def occupancy(self):
        return self._occupancy

    def setOccupancy(self, newValue):
        self._occupancy = newValue

    def beta(self):
        return self._beta

    def setBeta(self, newValue):
        self._beta = newValue

    def segname(self):
        return self._segname

    def setSegname(self, newValue):
        self._segname = newValue

    def element(self):
        return self._element

    def setElement(self, newValue):
        self._element = newValue

    def charge(self):
        return self._charge

    def setCharge(self, newValue):
        self._charge = newValue

    def atom_charge(self):
        return self._atom_charge

    def setAtom_charge(self, newValue):
        self._atom_charge = newValue

    def atom_vdw(self):
        return self._atom_vdw

    def setAtom_vdw(self, newValue):
        self._atom_vdw = newValue

    def formula(self):
        return self._formula

    def setFormula(self, newValue):
        self._formula = newValue

    def mass(self):
        return self._mass

    def setMass(self, newValue):
        self._mass = newValue

    def total_mass(self):
        if(self._total_mass is None):
            self._total_mass = calculate.Calculate.calcmass(self)
        return self._total_mass

    def setTotal_mass(self, newValue):
        self._total_mass = newValue

    def natoms(self):
        return self._natoms

    def setNatoms(self, newValue):
        self._natoms = newValue

    def number_of_atoms(self):
        return self._number_of_atoms

    def setNumber_of_atoms(self, newValue):
        self._number_of_atoms = newValue

    def moltype(self):
        return self._moltype

    def setMoltype(self, newValue):
        self._moltype = newValue


class Molecule(Atom):
    '''
    Molecule is a class that is used to describe molecules. It inherits
    attributes from Atom.  An example of a molecule is
    a single protein, a single nucleic acid strand.

    Class has several initialization options

    Parameters
    ----------
    args
        optional integer : self._id

    kwargs
        optional keyword arguments
            string filename (filename = 'hiv1_gag.pdb') : default = None
            integet id (id=3) : default = 0
            boolean debug (debug = True) : default = None

    Returns
    -------
    system object
        if called with string (or with filename kwarg) returns
        an initialized system object with data read in using
        file_io.read_pdb()

    Examples
    --------

    >>> import sasmol.system as system
    >>> molecule = system.Molecule(filename='hiv1_gag.pdb')
    >>> molecule = system.Molecule()
    >>> molecule = system.Molecule(id=7)
    >>> molecule = system.Molecule(debug=True)
    >>> molecule = system.Molecule('hiv1_gag.pdb')
    >>> molecule = system.Molecule(filename='hiv1_gag.pdb', id=0, debug=False)

    '''

    def fasta(self):
        return self._fasta

    def setFasta(self, newValue):
        self._fasta = newValue

    def setCharmm_type(self, newValue):
        self._charmm_type = newValue

    def charmm_type(self):
        return self._charmm_type

    def header(self):
        return self._header

    def setHeader(self, newValue):
        self._header = newValue

    def unitcell(self):
        return self._unitcell

    def setUnitcell(self, newValue):
        self._unitcell = newValue

    def rg(self):
        return self._rg

    def setRg(self, newValue):
        self._rg = newValue

    def pmi(self):
        return self._pmi

    def setPmi(self, newValue):
        self._pmi = newValue

    def minimum(self):
        return self._minimum

    def setMinimum(self, newValue):
        self._minimum = newValue

    def maximum(self):
        return self._maximum

    def setMaximum(self, newValue):
        self._maximum = newValue

    def one_letter_resname(self):
        return self._one_letter_resname

    def setOne_letter_resname(self, newValue):
        self._one_letter_resname = newValue

    def com(self):
        return self._com

    def setCom(self, newValue):
        self._com = newValue

    def center_of_mass(self):
        return self._center_of_mass

    def setCenter_of_mass(self, newValue):
        self._center_of_mass = newValue

    def names(self):
        return self._names

    def setNames(self, newValue):
        self._names = newValue

    def resnames(self):
        return self._resnames

    def setResnames(self, newValue):
        self._resnames = newValue

    def resids(self):
        return self._resids

    def setResids(self, newValue):
        self._resids = newValue

    def chains(self):
        return self._chains

    def setChains(self, newValue):
        self._chains = newValue

    def segnames(self):
        return self._segnames

    def setSegnames(self, newValue):
        self._segnames = newValue

    def occupancies(self):
        return self._occupancies

    def setOccupancies(self, newValue):
        self._occupancies = newValue

    def betas(self):
        return self._betas

    def setBetas(self, newValue):
        self._betas = newValue

    def moltypes(self):
        return self._moltypes

    def setMoltypes(self, newValue):
        self._moltypes = newValue

    def elements(self):
        return self._elements

    def setElements(self, newValue):
        self._elements = newValue

    def names_mask(self):
        return self._names_mask

    def setNames_mask(self, newValue):
        self._names_mask = newValue

    def resnames_mask(self):
        return self._resnames_mask

    def setResnames_mask(self, newValue):
        self._resnames_mask = newValue

    def resids_mask(self):
        return self._resids_mask

    def setResids_mask(self, newValue):
        self._resids_mask = newValue

    def chains_mask(self):
        return self._chains_mask

    def setChains_mask(self, newValue):
        self._chains_mask = newValue

    def occupancies_mask(self):
        return self._occupancies_mask

    def setOccupancies_mask(self, newValue):
        self._occupancies_mask = newValue

    def betas_mask(self):
        return self._betas_mask

    def setBetas_mask(self, newValue):
        self._betas_mask = newValue

    def elements_mask(self):
        return self._elements_mask

    def setElements_mask(self, newValue):
        self._elements_mask = newValue

    def segnames_mask(self):
        return self._segnames_mask

    def setSegnames_mask(self, newValue):
        self._segnames_mask = newValue

    def number_of_names(self):
        return self._number_of_names

    def setNumber_of_names(self, newValue):
        self._number_of_names = newValue

    def number_of_resnames(self):
        return self._number_of_resnames

    def setNumber_of_resnames(self, newValue):
        self._number_of_resnames = newValue

    def number_of_resids(self):
        return self._number_of_resids

    def setNumber_of_resids(self, newValue):
        self._number_of_resids = newValue

    def number_of_chains(self):
        return self._number_of_chains

    def setNumber_of_chains(self, newValue):
        self._number_of_chains = newValue

    def number_of_segnames(self):
        return self._number_of_segnames

    def setNumber_of_segnames(self, newValue):
        self._number_of_segnames = newValue

    def number_of_occupancies(self):
        return self._number_of_occupancies

    def setNumber_of_occupancies(self, newValue):
        self._number_of_occupancies = newValue

    def number_of_betas(self):
        return self._number_of_betas

    def setNumber_of_betas(self, newValue):
        self._number_of_betas = newValue

    def number_of_moltypes(self):
        return self._number_of_moltypes

    def setNumber_of_moltypes(self, newValue):
        self._number_of_moltypes = newValue

    def number_of_elements(self):
        return self._number_of_elements

    def setNumber_of_elements(self, newValue):
        self._number_of_elements = newValue

    def residue_charge(self):
        return self._residue_charge

    def setResidue_charge(self, newValue):
        self._residue_charge = newValue

    def conect(self):
        return self._conect

    def setConect(self, newValue):
        self._conect = newValue

    def residue_flag(self):
        try:
            return self._residue_flag
        except:
            self._residue_flag = False
            return self._residue_flag

    def setResidue_flag(self, newValue):
        self._residue_flag = newValue


class System(Atom):
    '''
    System is a class that is used to aggregate all components. It inherits
    all of attributes from Atom.

    Class has several initialization options

    Parameters
    ----------
    args
        optional integer : self._id

    kwargs
        optional keyword arguments
            string filename (filename = 'hiv1_gag.pdb') : default = None
            integet id (id=3) : default = 0
            boolean debug (debug = True) : default = None

    Returns
    -------
    system object
        if called with string (or with filename kwarg) returns
        an initialized system object with data read in using
        file_io.read_pdb()

    Examples
    -------

    >>> import sasmol.system as system
    >>> molecule = system.System(filename='hiv1_gag.pdb')
    >>> molecule = system.System()
    >>> molecule = system.System(id=7)
    >>> molecule = system.System(debug=True)
    >>> molecule = system.System('hiv1_gag.pdb')
    >>> molecule = system.System(filename='hiv1_gag.pdb', id=0, debug=False)

    '''
