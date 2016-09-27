
# compare the latex outputs to the math presented in the NAS presentation
# http://sites.nationalacademies.org/cs/groups/dbassesite/documents/webpage/dbasse_172599.pdf

	
import xarray as xr, pandas as pd, numpy as np
from IPython.display import display, Markdown, Latex


class Variable(object):
	'''
	Climate Impact Lab variable class

	Parameters
	----------
	value : coercable to xarray.DataArrays
		The underlying data set.

	symbolic : str (optional)
		Latex representation. For this example, assume we can pull 'symbol' 
		from attrs or use string representation of data.

	For math operations, this class uses the underlying 'value' attributes to do 
	the computation. Therefore, if we configure the objects to use dask rather 
	than in-memory, and figure out how to do the dask distributed computing, 
	this configuration should work.

	'''
	def __init__(self, value=None, symbolic=None, operations=[]):
		self.value=value

		if symbolic is None:
			if hasattr(value, 'attrs'):
				symbolic = value.attrs['symbol'] + '_{{{}}}'.format(','.join(value.dims))
			else:
				symbolic = str(value)


		self._symbolic=symbolic
		self.operations = operations

	def __repr__(self):
		return self.value.__repr__()

	def latex(self):
		display(Latex('${}$'.format(self.symbolic)))

	@staticmethod
	def _coerce(value):
		if not isinstance(value, Variable):
			return Variable(value, None, [])
		return value

	@property
	def attrs(self):
		return self.value.attrs

	@property
	def symbol(self):
		return self.attrs.get('symbol', None)

	@symbol.setter
	def symbol(self, value):
		self.attrs['symbol'] = value


	@property
	def symbolic(self):
		return self._symbolic


	@symbolic.setter
	def symbolic(self, value):
		 self._symbolic = '{}_{{{}}}'.format(value, ','.join(self.value.dims))


	def __add__(self, other):
		other = self._coerce(other)
		def oper(val=None):
			if val is None:
				if hasattr(val, 'copy'):
					val = self.value.copy()
				else:
					val = self.value
			return val + other.compute()
		return Variable(None, '{} + {}'.format(self.symbolic, other.symbolic), self.operations + [oper])


	def __radd__(self, other):
		other = self._coerce(other)
		def oper(val=None):
			if val is None:
				if hasattr(val, 'copy'):
					val = self.value.copy()
				else:
					val = self.value
			return other.compute() + val
		return Variable(None, '{} + {}'.format(other.symbolic, self.symbolic), self.operations + [oper])


	def __iadd__(self, other):
		return self.__add__(other)


	def __sub__(self, other):
		other = self._coerce(other)
		def oper(val=None):
			if val is None:
				if hasattr(val, 'copy'):
					val = self.value.copy()
				else:
					val = self.value
			return val - other.compute()
		return Variable(None, '{} - {}'.format(self.symbolic, other.symbolic), self.operations + [oper])


	def __rsub__(self, other):
		other = self._coerce(other)
		def oper(val=None):
			if val is None:
				if hasattr(val, 'copy'):
					val = self.value.copy()
				else:
					val = self.value
			return other.compute() - val
		return Variable(None, '{} - {}'.format(other.symbolic, self.symbolic), self.operations + [oper])


	def __isub__(self, other):
		return self.__sub__(other)


	def __mul__(self, other):
		other = self._coerce(other)
		def oper(val=None):
			if val is None:
				if hasattr(val, 'copy'):
					val = self.value.copy()
				else:
					val = self.value
			return val * other.compute()
		return Variable(None, '\\left({}\\right)\\left({}\\right)'.format(self.symbolic, other.symbolic), self.operations + [oper])


	def __rmul__(self, other):
		other = self._coerce(other)
		def oper(val=None):
			if val is None:
				if hasattr(val, 'copy'):
					val = self.value.copy()
				else:
					val = self.value
			return other.compute() * val
		return Variable(None, '\\left({}\\right)\\left({}\\right)'.format(other.symbolic, self.symbolic), self.operations + [oper])


	def __imul__(self, other):
		return self.__mul__(other)


	def __div__(self, other):
		other = self._coerce(other)
		def oper(val=None):
			if val is None:
				if hasattr(val, 'copy'):
					val = self.value.copy()
				else:
					val = self.value
			return val / other.compute()
		return Variable(None, '\\frac{{\\left({}\\right)}}{{\\left({}\\right)}}'.format(self.symbolic, other.symbolic), self.operations + [oper])


	def __rdiv__(self, other):
		other = self._coerce(other)
		def oper(val=None):
			if val is None:
				if hasattr(val, 'copy'):
					val = self.value.copy()
				else:
					val = self.value
			return other.compute() / val
		return Variable(None, '\\frac{{\\left({}\\right)}}{{\\left({}\\right)}}'.format(other.symbolic, self.symbolic), self.operations + [oper])


	def __idiv__(self, other):
		return self.__div__(other)


	def __pow__(self, other):
		other = self._coerce(other)
		def oper(val=None):
			if val is None:
				if hasattr(val, 'copy'):
					val = self.value.copy()
				else:
					val = self.value
			return val ** other.compute()
		return Variable(None, '{{\\left({}\\right)}}^{{\\left({}\\right)}}'.format(self.symbolic, other.symbolic), self.operations + [oper])


	def __rpow__(self, other):
		other = self._coerce(other)
		def oper(val=None):
			if val is None:
				if hasattr(val, 'copy'):
					val = self.value.copy()
				else:
					val = self.value
			return other.compute() ** val
		return Variable(None, '{{\\left({}\\right)}}^{{\\left({}\\right)}}'.format(other.symbolic, self.symbolic), self.operations + [oper])


	def __ipow__(self, other):
		return self.__pow__(other)


	def sum(self, dim=None):
		def oper(val=None):
			if val is None:
				if hasattr(val, 'copy'):
					val = self.value.copy()
				else:
					val = self.value
			return val.sum(dim=dim)
		return Variable(None, '\\sum{}{{\\left\\{{{}\\right\\}}}}'.format(('_{{{}}}'.format(dim) if dim is not None else ''), self.symbolic), self.operations + [oper])

	def ln(self):
		def oper(val=None):
			if val is None:
				if hasattr(val, 'copy'):
					val = self.value.copy()
				else:
					val = self.value
			return np.log(val)
		return Variable(None, '\\ln{{\\left({}\\right)}}'.format(self.symbolic), self.operations + [oper])

	def get_symbol(self):
		return self.attrs['symbol'] + '_{{{}}}'.format(','.join(self.value.dims))

	def compute(self, symbolic=''):
		'''
		right now, this just returns the value
		'''

		value = self.value
		
		for oper in self.operations:
			value = oper(value)

		return Variable(value, self.symbolic, [])

def get_random_variable(dims):
	data = np.random.random(tuple([len(d[1]) for d in dims]))
	foo = xr.DataArray(data, coords=dims)
	return foo


class ClimateImpactLabDataAPI(object):
	'''
	Implements the interface for Climate Impact Lab users
	'''

	def __init__(self, *args, **kwargs):
		self.populate_random_data()

	def populate_random_data(self):
		'''
		Provides dummy versions of the variables we need for this demo

		This method represents work that would be done beforehand. The data in 
		these variables should already be prepared in netCDF or csvv files. In 
		the production version, these datasets will also be probabilistic, and 
		climate variables will also be indexed by climate model.
		'''

		adm2 = range(1,25000)
		bins = range(12)
		time = range(100)

		self.temp = get_random_variable(dims=[('bins', bins), ('adm2', adm2), ('time', time)])
		self.temp.attrs['symbol'] = 'T'
		self.temp.attrs['description'] = 'NASA downscaled climate data'

		self.alpha = get_random_variable(dims=[('bins', bins)])
		self.alpha.attrs['symbol'] = '\\alpha'

		self.gamma1 = get_random_variable(dims=[('bins', bins)])
		self.gamma1.attrs['symbol'] = '{{\\gamma_1}}'

		self.gamma2 = get_random_variable(dims=[('bins', bins)])
		self.gamma2.attrs['symbol'] = '{{\\gamma_2}}'

		self.gamma3 = get_random_variable(dims=[('bins', bins)])
		self.gamma3.attrs['symbol'] = '{{\\gamma_3}}'

		self.avg_days_per_bin = get_random_variable(dims=[('bins', bins), ('adm2', adm2), ('time', time)])
		self.avg_days_per_bin.attrs['symbol'] = 'AvgDaysPerBin'

		self.gdppc = get_random_variable(dims=[('adm2', adm2), ('time', time)])
		self.gdppc.attrs['symbol'] = 'GdpPC'

		self.popdens = get_random_variable(dims=[('adm2', adm2), ('time', time)])
		self.popdens.attrs['symbol'] = 'PopDensity'


	def get_variable(self, varname):
		'''
		The actual API call. 
		'''

		return Variable(self.__dict__[varname])

	def configure(self, *args, **kwargs):
		print('API configuration updated')




