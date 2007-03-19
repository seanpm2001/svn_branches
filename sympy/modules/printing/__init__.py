"""Module for printing. Requires libxml2 and libxslt in order to do
transformations on the MathML, which is the underlying representation
that sympy uses

Examples
========
    >>> from sympy import *
    >>> from sympy.modules.printing import *
    
    >>> x = Symbol('x')
    >>> f = integrate(exp(x), x, evaluate=False)
    >>> print_gtk( f )
    
    >>> print_latex( f )


"""

from gtk import print_gtk
from latex import print_latex