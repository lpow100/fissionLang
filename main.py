import fission
import sys

using_file = False
curr = "i"
running_file = ""
for i, arg in enumerate(sys.argv[1:]):
    if arg[0] == "-":
        if len(arg) == 1:
            print(f"Error, missing argument value. Invalid argument: {arg} argument number: {i} ")
        else:
            curr += arg[1]
    else:
        running_file = arg
        using_file = True

text = ""
if using_file:
    with open(running_file,'r') as f:
        text = f.read()
    lex = fission.Lexer(text)
    lex.make_tokens()
    ASTlines = []
    for line in lex.tokens:
        parser = fission.Parser(line)
        parser.parse()
        ASTlines.append(parser.AST + [fission.Token(fission.TT_NEWLINE,"")])
    interpreter = fission.Interpreter()
    print(interpreter.interpret(ASTlines))
else:
    while True:
        text = input(">>> ")
        if text.lower() == "exit":
            break
        if text.count("{") > text.count("}"):
            while text.count("{") > text.count("}"):
                text += "\n" + input("... ")
        lex = fission.Lexer(text)
        lex.make_tokens()
        if "l" in curr:
            print(lex.tokens)
        ASTlines = []
        for line in lex.tokens:
            parser = fission.Parser(line)
            parser.parse()
            ASTlines.append(parser.AST + [fission.Token(fission.TT_NEWLINE,"")])
        if "p" in curr:
            print(*ASTlines,sep='\n')
        if "i" in curr:
            interpreter = fission.Interpreter()
            print(interpreter.interpret(ASTlines))