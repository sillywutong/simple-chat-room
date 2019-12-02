from random import randint

def is_prime(num, test_count):
    if num == 1:
        return False
    if test_count >= num:
        test_count = num - 1
    for x in range(test_count):
        val = randint(1, num - 1)
        if pow(val, num-1, num) != 1:
            return False
    return True

def generate_big_prime(n):
    found_prime = False
    while not found_prime:
        p = randint(2**(n-1), 2**n)
        if is_prime(p, 1000):
            return p



def gcd(a,b):
    r=a%b
    while(r!=0):
        a=b
        b=r
        r=a%b
    return b

# 欧拉函数-暴力循环版
def euler(a):
    count=0
    for i in range(1,a):
        if gcd(a,i)==1:
            count+=1
    return count

def order(a,n,b):
#   输出b在mod(a)中的阶
#   n是mod(a)群的阶
    p=1
    while(p<=n and (b**p%a!=1)):
          p+=1
    if p<=n:
          return p
    else:
          return -1

# 求任意数原根
def primitive_root(a):
    n=euler(a)
    print("done euler")
    prim=[]
    for b in range(2,a):
        print("in for")
        if order(a,n,b)==n:
            prim.append(b)
    print(prim)

