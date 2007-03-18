import hashing
from basic import Basic
from symbol import Symbol
from numbers import Rational,Real,Number,ImaginaryUnit
from functions import log,exp
from prettyprint import StringPict

class pole_error(Exception):
    pass

class Pow(Basic):

    def __init__(self,a,b):
        Basic.__init__(self)
        self.base = self.sympify(a)
        self.exp = self.sympify(b)
        
    def hash(self):
        if self.mhash: 
            return self.mhash.value
        self.mhash=hashing.mhash()
        self.mhash.addstr(str(type(self)))
        self.mhash.add(self.base.hash())
        self.mhash.add(self.exp.hash())
        return self.mhash.value
        
    def print_sympy(self):
        from addmul import Pair
        f = ""
        if isinstance(self.base,Pair) or isinstance(self.base,Pow):
            f += "(%s)"
        else:
            f += "%s"
        f += "^"
        if isinstance(self.exp,Pair) or isinstance(self.exp,Pow) \
            or (isinstance(self.exp,Rational) and \
            (not self.exp.isinteger() or (self.exp.isinteger() and \
            int(self.exp) < 0)) ):
            f += "(%s)"
        else:
            f += "%s"
        return f % (self.base.print_sympy(),self.exp.print_sympy())

    def print_tex(self):
        from addmul import Pair
        f = ""
        if isinstance(self.base,Pair) or isinstance(self.base,Pow):
            f += "{(%s)}"
        else:
            f += "{%s}"
        f += "^"
        if isinstance(self.exp,Pair) or isinstance(self.exp,Pow) \
            or (isinstance(self.exp,Rational) and \
            (not self.exp.isinteger() or (self.exp.isinteger() and \
            int(self.exp) < 0)) ):
            f += "{(%s)}"
        else:
            f += "{%s}"
        return f % (self.base.print_tex(),self.exp.print_tex())

    def print_pretty(self):
        a, b = self.base, self.exp
        apretty = a.print_pretty()
        if isinstance(b, Rational) and b.p==1 and b.q==2:
            return apretty.root()
        if not isinstance(a, Symbol):
            apretty = apretty.parens()
        bpretty = b.print_pretty()
        exponent = bpretty.left(' '*apretty.width())
        apretty = apretty.right(' '*bpretty.width())
        return apretty.top(exponent)
        
    def get_baseandexp(self):
        return (self.base,self.exp)
        
    def eval(self):
        from addmul import Mul
        if isinstance(self.exp,Rational) and self.exp.iszero():
            return Rational(1)
        if isinstance(self.exp,Rational) and self.exp.isone():
            return self.base
        if isinstance(self.base,Rational) and self.base.iszero():
            if isinstance(self.exp,Rational):# and self.exp.isinteger():
                if self.exp.iszero():
                    raise pole_error("pow::eval(): 0^0.")
                elif self.exp < 0:
                    raise pole_error("pow::eval(): Division by 0.")
            return Rational(0)
        
        if isinstance(self.base,Rational) and self.base.isone():
            return Rational(1)
        
        if isinstance(self.base,Real) and isinstance(self.exp,Real):
            return self
        
        if isinstance(self.base, Rational) and isinstance(self.exp, Rational):
            if self.exp.isinteger():
                if self.exp > 0: 
                    return Rational(self.base.p ** self.exp.p , self.base.q ** self.exp.p)
                else:
                    return Rational(self.base.q ** (-self.exp.p) , self.base.p ** (-self.exp.p) )
                
            if self.base.isinteger():
                a = int(self.base)
                bq = self.exp.q
                if a>0:
                    x = int(a**(1./bq)+0.5)
                    if x**bq == a:
                        assert isinstance(x,int)
                        return Rational(x)**self.exp.p
        if isinstance(self.base,Pow): 
            return Pow(self.base.base,self.base.exp*self.exp)
        if isinstance(self.base,exp): 
            if self.base.arg.isnumber():
                return exp(self.exp*self.base.arg)
        if isinstance(self.base,Mul): 
            a,b = self.base.getab()
            if self.exp==-1 or (isinstance(a,Rational) and a.evalf()>0):
                return (Pow(a,self.exp) * Pow(b,self.exp))
        if isinstance(self.base,ImaginaryUnit):
            if isinstance(self.exp,Rational) and self.exp.isinteger():
                if int(self.exp) == 2:
                    return -Rational(1)
        if isinstance(self.exp,Rational) and self.exp.isinteger():
            if isinstance(self.base,Mul):
                if int(self.exp) % 2 == 0:
                    n= self.base.args[0]
                    if n.isnumber() and n<0:
                        return (-self.base)**self.exp
        return self
        
    def evalf(self):
        if self.base.isnumber() and self.exp.isnumber():
            return Real(float(self.base)**float(self.exp))
            #FIXME: we need a way of raising a decimal to the power of a decimal (it doesen't work if self.exp is not an integer
        else:
            raise ValueError

    def commutative(self):
        return self.base.commutative() and self.exp.commutative()
        
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
        if isinstance(self.exp,Number):
            if self.exp.isinteger():
                n = int(self.exp)
                if n > 1:
                    a = self.base
                    while n > 1:
                        a = Mul(a,self.base,evaluate=False)
                        #a *= self.base
                        n -= 1
                    return a.expand()
        return self

    def evalc(self):
        e=self.expand()
        if e!=self:
            return e.evalc()
        if isinstance(e.base, Symbol):
            #this is wrong for nonreal exponent
            return self
        raise NotImplementedError
        
    def subs(self,old,new):
        if self == old:
            return new
        elif exp(self.exp * log(self.base)) == old:
            return new
        else:
            return (self.base.subs(old,new) ** self.exp.subs(old,new))
