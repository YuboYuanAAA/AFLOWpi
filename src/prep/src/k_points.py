import AFLOWpi
import numpy


def _gen_nosym_kgrid(nk1,nk2,nk3,sk1=0,sk2=0,sk3=0,as_string=False):

    shift1 = 1.0/nk1*float(sk1)/2.0
    shift2 = 1.0/nk2*float(sk2)/2.0
    shift3 = 1.0/nk3*float(sk3)/2.0

    kdist1 = 1.0/nk1
    kdist2 = 1.0/nk2
    kdist3 = 1.0/nk3

    tot = nk1*nk2*nk3
    nk_str = '%s'%tot
#    if shift_gamma==True:
#        shift1-=0.5
#        shift2-=0.5
#        shift3-=0.5
    if as_string==True:
        for i in range(nk1):
            for j in range(nk2):
                for k in range(nk3):
                    nk_str+='\n%8.8f %8.8f %8.8f'%(float(i)*kdist1+shift1,float(j)*kdist2+shift2,float(k)*kdist3+shift3)
    else:
        nk_str=[]#numpy.zeros([tot,3])
        for i in range(nk1):
            for j in range(nk2):
                for k in range(nk3):
                    nk_str.append([float(i)*kdist1+shift1,float(j)*kdist2+shift2,float(k)*kdist3+shift3])
    nk_str=numpy.asarray(nk_str)

    return nk_str








