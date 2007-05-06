from basic import Basic
from symbol import Symbol
from numbers import Rational, Real, ImaginaryUnit
from functions import log, exp
from sympy.core.stringPict import prettyForm, stringPict


class pole_error(ZeroDivisionError):
    pass

class Pow(Basic):
    """
    Usage
    =====
        This class represent's the power of two elements. so whenever you call '**', an 
        instance of this class is created. 
        
    Notes
    =====
        When an instance of this class is created, the method .eval() is called and will
        preform some inexpensive symplifications. 

        
    Examples
    ========
        >>> from sympy import *
        >>> x = Symbol('x')
        >>> type(x**2)
        <class 'sympy.core.power.Pow'>
        >>> (x**2)[:]
        [x, 2]
    
    See also
    ========
        L{Add.eval}
    """
        
    mathml_tag = "power"

    def __init__(self,a,b):
        Basic.__init__(self)
        self._args = [Basic.sympify(a), Basic.sympify(b)]

        
    def __str__(self):
        from addmul import Pair
        if self.exp == -1:
            if isinstance(self.base, Pair):
                return "(1/(%s))" % str(self.base)
            else:
                return "(1/%s)" % str(self.base)

        f = ""
        if isinstance(self.base,Pair) or isinstance(self.base,Pow):
            f += "(%s)"
        else:
            f += "%s"
        f += "**"
        if isinstance(self.exp,Pair) or isinstance(self.exp,Pow) \
            or (isinstance(self.exp,Rational) and \
            (not self.exp.is_integer or (self.exp.is_integer and \
            int(self.exp) < 0)) ):
            f += "(%s)"
        else:
            f += "%s"
        return f % (str(self.base), str(self.exp))
    
        
    def __pretty__(self):
        if self.exp == Rational(1,2): # if it's a square root
            bpretty = self.base.__pretty__()
            bl = int((bpretty.height() / 2.0) + 0.5)

            s2 = stringPict("\\/")
            for x in xrange(1, bpretty.height()):
                s3 = stringPict(" " * (2*x+1) + "/")
                s2 = stringPict(*s2.top(s3))
            s2.baseline = -1

            s = stringPict("__" + "_" * bpretty.width())
            s = stringPict(*s.below("%s" % str(bpretty)))
            s = stringPict(*s.left(s2))
            return prettyForm(str(s), baseline=bl)
        elif self.exp == -1:
            # things like 1/x
            return prettyForm("1") / self.base.__pretty__()
        a, b = self._args
        return a.__pretty__()**b.__pretty__()
    
    
    def __latex__(self):
        from addmul import Pair
        f = ""
        if isinstance(self.base,Pair) or isinstance(self.base,Pow):
            f += "{(%s)}"
        else:
            f += "{%s}"
        f += "^"
        if isinstance(self.exp,Pair) or isinstance(self.exp,Pow) \
            or (isinstance(self.exp,Rational) and \
            (not self.exp.is_integer or (self.exp.is_integer and \
            int(self.exp) < 0)) ):
            f += "{(%s)}"
        else:
            f += "{%s}"
        return f % (self.base.__latex__(),self.exp.__latex__())
    
    def __mathml__(self):
        import xml.dom.minidom
        if self._mathml:
            return self._mathml
        dom = xml.dom.minidom.Document()
        x = dom.createElement("apply")
        x_1 = dom.createElement(self.mathml_tag)
        x.appendChild(x_1)
        for arg in self._args:
            x.appendChild( arg.__mathml__() )
        self._mathml = x
        return self._mathml
        
    @property
    def base(self):
        return self._args[0]
    
    @property
    def exp(self):
        return self._args[1]
        
    def eval(self):
        from addmul import Mul
        if isinstance(self.exp, Rational) and self.exp.iszero():
            return Rational(1)
        
        if isinstance(self.exp, Rational) and self.exp.isone():
            return self.base
        
        if isinstance(self.base, Rational) and self.base.iszero():
            if isinstance(self.exp,Rational):# and self.exp.is_integer:
                if self.exp.iszero():
                    raise pole_error("pow::eval(): 0^0.")
                elif self.exp < 0:
                    raise pole_error("%s: Division by 0." % str(self))
            return Rational(0)
        
        if isinstance(self.base, Rational) and self.base.isone():
            return Rational(1)
        
        if isinstance(self.base, Real) and isinstance(self.exp,Real):
            return self
        
        if isinstance(self.base, Rational) and isinstance(self.exp, Rational):
            if self.exp.is_integer:
                if self.exp > 0: 
                    return Rational(self.base.p ** self.exp.p , self.base.q ** self.exp.p)
                else:
                    return Rational(self.base.q ** (-self.exp.p) , self.base.p ** (-self.exp.p) )
            if self.base == -1:
                # calculate the roots of -1
                from sympy.modules.trigonometric import sin, cos
                from sympy.core.numbers import pi
                r = cos(pi/self.exp.q) + ImaginaryUnit()*sin(pi/self.exp.q)
                return r**self.exp.p
                        
                
            if self.base.is_integer:
                a = int(self.base)
                bq = self.exp.q
                if a > 0:
                    const = 1 # constant, will multiply the final result (it will do nothing in this case)
                if a < 0:
                    const = (-1)** (self.exp)  # do sqrt(-4) -> I*4
                    a = -a
                x = int(a**(1./bq)+0.5)
                if x**bq == a: # if we can write self.base as integer**self.exp.q
                    assert isinstance(x,int)
                    return const*Rational(x)**self.exp.p
                elif self.base < 0:
                    # case base negative && not a perfect number, like sqrt(-2)
                    # TODO: implement for exponent of 1/4, 1/6, 1/8, etc.
                    return ((-1)**self.exp)*Pow(-self.base, self.exp, evaluate=False)
                    
        if isinstance(self.base, Pow): 
            return Pow(self.base.base,self.base.exp*self.exp)
        
        if isinstance(self.base, exp): 
            if self.base.is_number:
                return exp(self.exp*self.base._args)
            
        if isinstance(self.base, Mul): 
            a,b = self.base.getab()
            if self.exp==-1 or (isinstance(a,Rational) and a.evalf()>0):
                return (Pow(a,self.exp) * Pow(b,self.exp))
            
        if isinstance(self.base,ImaginaryUnit):
            if isinstance(self.exp,Rational) and self.exp.is_integer:
                if int(self.exp) % 2 == 0:
                    return Rational(-1) ** ((int(self.exp) % 4)/2)
                
        if isinstance(self.exp,Rational) and self.exp.is_integer:
            if isinstance(self.base,Mul):
                if int(self.exp) % 2 == 0:
                    n = self.base[0]
                    if n.is_number and n < 0:
                        return (-self.base)**self.exp
                    
        if isinstance(self[0],Real) and self[1].is_number:
            return Real(self[0]**self[1].evalf())
        
        if not self.base.is_commutative:
            if isinstance(self.exp, Rational) and self.exp.is_integer:
                    n = int(self.exp)
                    #only try to simplify it for low exponents (for speed
                    #reasons).
                    if n > 1 and n < 10:
                        r = self.base
                        for i in range(n-1):
                            r = r * self.base
                        return r
        return self
        

    def evalf(self):
        if self.base.is_number and self.exp.is_number:
            return Real(float(self.base)**float(self.exp))
            #FIXME: we need a way of raising a decimal to the power of a decimal (it doesen't work if self.exp is not an integer
        else:
            raise ValueError

    @property
    def is_commutative(self):
        return self.base.is_commutative and self.exp.is_commutative
        
    def diff(self,sym):
        f = self.base
        g = self.exp
        return (self*(g*log(f)).diff(sym))
        
    def series(self,sym,n):
        if not self.exp.has(sym):
            if isinstance(self.base,Symbol): return self
            try:
                return Basic.series(self,sym,n)
            except pole_error:
                #self=self.expand()
                if isinstance(self.exp,Rational) and self.exp.isminusone():
                    g = self.base.series(sym,n)
                    #write g as g=c0*w^e0*(1+Phi)
                    #1/g is then 1/g=c0*w^(-e0)/(1+Phi)
                    #plus we expand 1/(1+Phi)=1-Phi+Phi**2-Phi**3...
                    c0,e0 = g.leadterm(sym)
                    Phi = (g/(c0*sym**e0)-1).expand()
                    e = 0
                    for i in range(n):
                        e += (-1)**i * Phi**i
                    e *= sym ** (-e0) / c0
                    #print n,Phi,c0,e0,g,self.base
                    return e.expand()
                if not isinstance(self.exp,Rational):
                    e = exp(self.exp * log(self.base))
                    return e.series(sym,n)
                #self.base is kind of:  1/x^2 + 1/x + 1 + x + ...
                e = self.base.series(sym,n)
                ldeg = e.ldegree(sym)
                #print "power:",e,self.exp,ldeg,e.eval()
                s= ((e*sym**(-ldeg)).expand()**self.exp).series(sym,n+
                        int(ldeg.evalf()))
                return (s * sym**(ldeg * self.exp)).expand()
        try:
            return Basic.series(self,sym,n)
        except pole_error:
            try:
                a=self.base.series(sym,n)
                b=self.exp.series(sym,n)
                return Basic.series((a**b),sym,n)
            except pole_error:
                e = exp((self.exp*log(self.base)))
                return e.series(sym,n)
            
    def expand(self):
        from addmul import Mul
        if isinstance(self.exp, (Real, Rational)):
            if self.exp.is_integer:
                n = int(self.exp)
                if n > 1:
                    a = self.base
                    while n > 1:
                        a = Mul(a,self.base,evaluate=False)
                        #a *= self.base
                        n -= 1
                    return a.expand()
        return Pow(self[0].expand(),self[1].expand())
        return self

    def combine(self):
        from functions import exp
        a = self[0].combine()
        b = self[1].combine()
        if isinstance(a, exp):
            return exp(a[0]*b)
        return self

    def evalc(self):
        e=self.expand()
        if e!=self:
            return e.evalc()
        if isinstance(e.base, Symbol):
            #this is wrong for nonreal exponent
            return self
        print self
        raise NotImplementedError
        
    def subs(self,old,new):
        if self == old:
            return new
        elif exp(self.exp * log(self.base)) == old:
            return new
        else:
            return (self.base.subs(old,new) ** self.exp.subs(old,new))

    def match(self, pattern, syms=None):
        from symbol import Symbol
        if syms == None:
            syms = pattern.atoms(type=Symbol)
        def addmatches(r1,r2):
            l1 = list(r1)
            l2 = list(r2)
            if l1 == l2:
                if l1 != []:
                    #fix it in a general case
                    assert len(l1)==1
                    p = l1[0]
                    if r1[p] != r2[p]:
                        return None
            r1.update(r2)
            return r1
        from addmul import Mul
        if isinstance(pattern, Mul):
            return Mul(Rational(1),self,evaluate = False).match(pattern,syms)
        if not isinstance(pattern, Pow):
            return None
        r1 = self[0].match(pattern[0],syms)
        if r1!=None:
            r2 = self[1].match(pattern[1],syms)
            #print r1,r2,"<--",self[1],pattern[1],syms
            if r2!=None:
                return addmatches(r1,r2)
        return None

