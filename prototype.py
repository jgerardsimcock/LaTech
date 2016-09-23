import xarray as xr, pandas as pd, numpy as np

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
	def __init__(self, value, symbolic=None):
		self.value=value

		if symbolic is None:
			if hasattr(value, 'attrs'):
				symbolic = value.attrs['symbol'] + '_{{{}}}'.format(','.join(value.dims))
			else:
				symbolic = str(value)


		self.symbolic=symbolic

	@staticmethod
	def _coerce(value):
		if not isinstance(value, Variable):
			return Variable(value)
		return value

	@property
	def attrs(self):
		return self.value.attrs


	def __add__(self, other):
		other = self._coerce(other)
		return Variable(self.value + other.value, '{} + {}'.format(self.symbolic, other.symbolic))


	def __radd__(self, other):
		other = self._coerce(other)
		return Variable(other.value + self.value, '{} + {}'.format(other.symbolic, self.symbolic))


	def __iadd__(self, other):
		return self.__add__(other)


	def __sub__(self, other):
		other = self._coerce(other)
		return Variable(self.value - other.value, '{} - {}'.format(self.symbolic, other.symbolic))


	def __rsub__(self, other):
		other = self._coerce(other)
		return Variable(other.value - self.value, '{} - {}'.format(other.symbolic, self.symbolic))


	def __isub__(self, other):
		return self.__sub__(other)


	def __mul__(self, other):
		other = self._coerce(other)
		return Variable(self.value * other.value, '\\left({}\\right)\\left({}\\right)'.format(self.symbolic, other.symbolic))


	def __rmul__(self, other):
		other = self._coerce(other)
		return Variable(other.value * self.value, '\\left({}\\right)\\left({}\\right)'.format(other.symbolic, self.symbolic))


	def __imul__(self, other):
		return self.__mul__(other)


	def __div__(self, other):
		other = self._coerce(other)
		return Variable(self.value / other.value, '\\frac{{\\left({}\\right)}}{{\\left({}\\right)}}'.format(self.symbolic, other.symbolic))


	def __rdiv__(self, other):
		other = self._coerce(other)
		return Variable(other.value / self.value, '\\frac{{\\left({}\\right)}}{{\\left({}\\right)}}'.format(other.symbolic, self.symbolic))


	def __idiv__(self, other):
		return self.__div__(other)


	def __pow__(self, other):
		other = self._coerce(other)
		return Variable(self.value ** other.value, '{{\\left({}\\right)}}^{{\\left({}\\right)}}'.format(self.symbolic, other.symbolic))


	def __rpow__(self, other):
		other = self._coerce(other)
		return Variable(other.value ** self.value, '{{\\left({}\\right)}}^{{\\left({}\\right)}}'.format(other.symbolic, self.symbolic))


	def __ipow__(self, other):
		return self.__pow__(other)


	def sum(self, dim=None):
		return Variable(self.value.sum(dim=dim), '\\sum{}{{\\left\\{{{}\\right\\}}}}'.format(('_{{{}}}'.format(dim) if dim is not None else ''), self.symbolic))

	def ln(self):
		return Variable(np.log(self.value), '\\ln{{\\left({}\\right)}}'.format(self.symbolic))

	def get_symbol(self):
		return self.attrs['symbol'] + '_{{{}}}'.format(','.join(self.value.dims))

	def equation(self):
		return '{} = {}'.format(self.get_symbol(), self.symbolic)

	def compute(self):
		'''
		right now, this just returns the value
		'''

		return self.value

def get_random_variable(dims):
	data = np.random.random(tuple([len(d[1]) for d in dims]))
	foo = xr.DataArray(data, coords=dims)
	return foo


class ClimateImpactLabDataAPI(object):
	'''
	Implements the interface for Climate Impact Lab users
	'''

	def __init__(self):
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


def main():
	# this is the only part that needs to be exposed to the user
	api = ClimateImpactLabDataAPI()

	alpha = api.get_variable('alpha')	
	gamma1 = api.get_variable('gamma1')	
	gamma2 = api.get_variable('gamma2')	
	gamma3 = api.get_variable('gamma3')	
	
	avg_days_per_bin = api.get_variable('avg_days_per_bin')	
	gdppc = api.get_variable('gdppc')	
	popdens = api.get_variable('popdens')

	temp = api.get_variable('temp')	

	# now that we have all our variables loaded, it's time for some math!
	betahat = alpha + gamma1*avg_days_per_bin + gamma2*(gdppc.ln()) + gamma3*(popdens.ln())

	betahat.attrs['symbol'] = '\\hat{{\\beta}}'

	print('\nbeta hat latex code:')
	print(betahat.equation()) # the insane part is that the subscripts on betahat are generated by the xarray computation!!

	print('\nbeta hat value:')
	print(betahat.compute())

	# let's simplify betahat's latex:
	betahat.symbolic = betahat.get_symbol()

	# now we compute mortality...
	mortality = (betahat*temp).sum(dim='bins')
	mortality.attrs['symbol'] = 'M'

	print('\nmortality latex:')
	print(mortality.equation()) # Note how the mortality subscripts are automatically lower dimension :)

	print('\nmortality value:')
	print(mortality.compute())

	# you can easily display the latex here: http://quicklatex.com/

	# compare the latex outputs to the math presented in the NAS presentation
	# http://sites.nationalacademies.org/cs/groups/dbassesite/documents/webpage/dbasse_172599.pdf


if __name__ == "__main__":
	main()



