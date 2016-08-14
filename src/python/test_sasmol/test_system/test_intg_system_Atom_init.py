'''
    SASMOL: Copyright (C) 2011 Joseph E. Curtis, Ph.D. 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from unittest import main 
from mocker import Mocker, MockerTestCase
import sasmol.system as system

class Test_intg_system_Atom_init(MockerTestCase):

   def setUp(self):
      pass

   def test_default(self):
      '''
      test initializer with default input
      '''
      #
      o=system.Atom()
      self.assertEqual(o.id(),0)
      self.assertEqual(o.total_mass(),0.0)
      self.assertEqual(o.natoms(),0)
      self.assertEqual(o.mass(),None)
      self.assertEqual(o.coor(),None)
      self.assertEqual(o.com(),None)

   def test_id(self):
      '''
      test initializer with id
      '''
      #
      id=3
      o=system.Atom(id)
      self.assertEqual(o.id(),id)
      self.assertEqual(o.total_mass(),0.0)
      self.assertEqual(o.natoms(),0)
      self.assertEqual(o.mass(),None)
      self.assertEqual(o.coor(),None)
      self.assertEqual(o.com(),None)

   def tearDown(self):
      pass
        
   
   
if __name__ == '__main__': 
   main() 

