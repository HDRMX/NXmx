import h5py
import numpy

class NXGroup(object):
  def __init__(self, name, attrs={}, parent=None):
    self._name = name
    self._attrs = attrs
    self._children = { }
    self._datasets = { }
    self._parent = parent

  def group(self, name, attrs={}):
    if not name in self._children:
      self._children[name] = NXGroup(name, attrs, parent=self)
    return self._children[name]

  def dataset(self, name, values, attrs={}, params={}):
    if not name in self._datasets:
      self._datasets[name] = NXDataset(name, values, attrs=attrs, parent=self,
                                       params=params)
    return self._datasets[name]

  def path(self):
    if self._parent:
      return '%s/%s' % (self._parent.path(), self._name)
    return self._name

  def h5(self, h5_file):
    group = h5_file.create_group(self._name)
    for attr, value in self._attrs.items():
      group.attrs[attr] = value
    for name, child in self._children.items():
      child.h5(group)
    for name, dataset in self._datasets.items():
      dataset.h5(group)
    return group

class NXDataset(object):
  def __init__(self, name, values, attrs={}, parent=None, params={}):
    self._name = name
    self._values = values
    self._attrs = attrs
    self._parent = parent
    self._params = params

  def path(self):
    if self._parent:
      return '%s/%s' % (self._parent.path(), self._name)
    return self._name

  def h5(self, h5_file):
    if hasattr(self._values, 'shape'):
      dataset = h5_file.create_dataset(self._name, self._values.shape,
                                       **self._params)
    else:
      dataset = h5_file.create_dataset(self._name, (), **self._params)
    dataset[...] = self._values
    for attr, value in self._attrs.items():
      dataset.attrs[attr] = value
    return dataset

def main(filename):
  entry = NXGroup('entry', attrs={'NX_class':'NXentry'})
  instrument = entry.group('instrument', attrs={'NX_class':'NXinstrument'})
  detector = instrument.group('detector', attrs={'NX_class':'NXdetector'})
  d2t = instrument.group('detector_2t', attrs={'NX_class':'NXpositioner'})
  d2t_data = d2t.dataset('two_theta', 0.0, {'units':'degrees',
                                            'translation_type':'rotation',
                                            'vector':[-1,0,0],
                                            'depends_on':'.'})
  dz = instrument.group('detector_z', attrs={'NX_class':'NXpositioner'})
  dz_data = dz.dataset('z', 100.0, {'units':'mm',
                                    'translation_type':'translation',
                                    'vector':[0,0,1],
                                    'depends_on':d2t_data.path()})
  transform = detector.group('transformations',
                             attrs={'NX_class':'NXtramsformations'})
  zeros = entry.dataset('zeros', numpy.zeros((16, 16, 16), dtype=numpy.int),
                        params={'chunks':(1, 16, 16),
                                'compression':'gzip',
                                'compression_opts':9})

  f = h5py.File(filename, 'w')
  entry.h5(f)
  f.close()

if __name__ == '__main__':
  import sys
  main(sys.argv[1])
