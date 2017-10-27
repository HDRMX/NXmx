import h5py
import numpy

def make_or_get_group(h5_file, path, attrs={}):
  if path in h5_file:
    return h5_file[path]
  group = h5_file.create_group(path)
  for attr, value in attrs.items():
    group.attrs[attr] = value
  return group

def create_string_dataset(h5_file, path, value, attrs={}):
  d = h5_file.create_dataset(path, (), dtype='S%d' % len(value))
  d[...] = value
  for attr, value in attrs.items():
    d.attrs[attr] = value
  return d

def create_float_scalar(h5_file, path, value, attrs={}):
  d = h5_file.create_dataset(path, (), dtype='f')
  d[...] = value
  for attr, value in attrs.items():
    d.attrs[attr] = value
  return d

def make_NXmx(h5_file):
  entry = make_or_get_group(h5_file, 'entry', {'NX_class':'NXentry'})
  create_string_dataset(h5_file, 'entry/definition', 'NXmx')
  instrument = make_or_get_group(entry, 'instrument',
                                 {'NX_class':'NXinstrument'})
  
def create_detector(h5_file):
  # first construct detector stages, detector_z, detector_2theta
  instrument = make_or_get_group(h5_file, 'entry/instrument')
  
  detector_2t = make_or_get_group(instrument, 'detector_2theta',
                                  {'NX_class':'NXpositioner'})

  detector_2t_d = create_float_scalar(detector_2t, 'two_theta', 0.0,
                                      {'units':'degrees',
                                       'translation_type':'rotation',
                                       'vector':[1,0,0]})

  detector_z = make_or_get_group(instrument, 'detector_z',
                                 {'NX_class':'NXpositioner'})

  detector_z_d = create_float_scalar(detector_z, 'z', 100.0,
                                     {'units':'mm',
                                      'translation_type':'translation',
                                      'vector':[0,0,1]})

  detector = make_or_get_group(instrument, 'detector',
                               {'NX_class':'NXdetector'})

  detector_t = make_or_get_group(detector, 'transformations',
                                 {'NX_class':'NXtransformations'})

  # make hard links in the transformations group
  detector_t['z'] = detector_z
  detector_t['two_theta'] = detector_2t
  
  
def create_goniometer(h5_file):
  pass

def create_beam(h5_file):
  pass

def create_data(h5_file):
  s = (16, 16, 16)
  d = h5_file.create_dataset('zeros', s, dtype='i', chunks=(1, 16, 16),
                             compression='gzip', compression_opts=9)
  d[...] = numpy.zeros(s, dtype=numpy.int)
  d.attrs['maximum_value'] = 0.0
  d.attrs['minimum_value'] = 0.0
  
def create_empty_hdf5_file(filename):
  f = h5py.File(filename, 'w')
  make_NXmx(f)
  create_detector(f)
  create_goniometer(f)
  create_beam(f)
  create_data(f)
  f.close()

if __name__ == '__main__':
  import sys
  create_empty_hdf5_file(sys.argv[1])
  
  
