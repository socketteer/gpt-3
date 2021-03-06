import random
from pprint import pprint

def check(parens):
    open = 0
    for i, c in enumerate(parens):
        open += 1 if c=="(" else 0
        open += -1 if c==")" else 0
        if open < -1:
            print(f"Broken early")
    return open

def balanced(n):
    s = ""
    count = 0
    for i in range(n):
        if random.randint(0, 1) or count == 0:
            s += " ("
            count += 1
        else:
            s += " )"
            count -= 1
    for i in range(count):
        s += " )"
    return s[1:]



check_parens = """
# ((((()))(((()))))
# (((()))(((()))))
# ()((((((()((())))))))(())
# ()()(())()()()
# (((()((()))))())
# (())()(())()(())
# (()((())))(((()())))
# ()()()(())
# ()((())())()
# ()()()(())()()()()
# ()()()()()
# ()()(()((())))
# ()()()()(((()()())))
# ((()((((()()))))))
# (()(())()(()))(
# ()(((()(((()))))))
# ()(())(()())()(())
# ()(((()(((()))))))
# ()(())((()))
# ((()())((())))((()))
# ()(((()(((()))))))
# ()(((((()()))))())
# ()(((()()())))()((())())
# ()(())(()())()(())
# ()(((()(((()))))))
# (((()())()(((())()(((()))))())()())))
(()((()(()()()))()())(()()())))
( ) ( ) ( ( ( ) ( ( ) ) ( ) ) )
( ) ( ( ( ( ( ) ) ) ) ( ) ( )
( ) ( ) ( ( ( ( ) ) ) ) ( ) ( )
( ) ( ) ( ( ( ( ( ) ) ) ) ( ) ( )
( ) ( ) ( ( ( ( ( ) ) ) ) ( ) ( )
( ) ( ) ( ( ( ( ( ) ) ) ) ( ) ( )
( ) ( ) ( ( ( ( ( ) ) ) ) ( ) ( )
( ) ( ) ( ( ( ( ( ) ) ) ) ( ) ( )
( ) ( ) ( ( ( ( ( ) ) ) ) ( ) ( )
( ( ) ) ( ( ( ( ( ) ( ) ( ) ) ) ) )
( ( ) ) ( ( ( ( ( ) ( ) ( ) ) ) ) )
( ( ) ) ( ( ( ( ( ) ( ) ( ) ) ) ) )
( ( ) ) ( ( ( ( ( ) ( ) ( ) ) ) ) )
( ( ) ) ( ( ( ( ( ) ( ) ( ) ) ) ) ) )
( ( ) ) ( ( ( ( ( ) ( ) ( ) ) ) ) )
"""



def main():
    # for i in range(50):
    #     print(balanced(random.randint(8, 15)))
    #
    #
    # pprint([
    #     check(parens)
    #     for parens in check_parens.split("\n")
    #     if parens and "#" not in parens
    # ])
    print(check("g(g(g(x)g(x)g(g(x)g(x)))))"))


if __name__ == "__main__":
    main()

