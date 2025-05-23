class Error:
    def __init__(self, title:str, body:str):
        self.title = title
        self.body = body
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return f"{self.title}:\n\t{self.body}"

TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_TIMES = "TIMES"
TT_DIVIDE = "DIVIDE"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_LCURLY = "LCURLY"
TT_RCURLY = "RCURLY"
TT_STRING = "STRING"
TT_WORD = "WORD"
TT_ASSIGN = "ASSIGN"
TT_EQ = "EQ"
TT_NE = "NE"
TT_LT = "LT"
TT_LTE = "LTE"
TT_GT = "GT"
TT_GTE = "GTE"
TT_TYPE = "TYPE"
TT_NEWLINE = "NEWLINE"
TT_CODEBLOCK = "CODEBLOCK"
TT_BOOL = "BOOL"

LOWERCASE_LETTERS = "abcdefghijklmnopqrstuvwxyz"
UPPERCASE_LETTERS = LOWERCASE_LETTERS.upper()
ALL_LETTERS = LOWERCASE_LETTERS + UPPERCASE_LETTERS

VALUE_TYPES = (TT_INT,TT_FLOAT,TT_STRING,TT_BOOL)
OPERATOR_TYPES = (TT_PLUS,TT_MINUS,TT_TIMES,TT_DIVIDE)
PARENTHESES = (TT_LPAREN,TT_RPAREN)
CURLY_BRACKETS = (TT_LCURLY,TT_RCURLY)
COMPARISON_TYPES = (TT_EQ,TT_NE,TT_LT,TT_LTE,TT_GT,TT_GTE)

INBUILT_TYPES = ("int","float","string","bool")
INBUILT_WORDS = ("if","else","while")
INBUILT_FUNCTIONS = ("print","input","asInt")

# "TYPE":[CODE]
code_blocks = {}

class Token:
    def __init__(self, type:str, value:str):
        self.type = type
        self.value = value
    def __str__(self):
        output = self.type
        if self.type == TT_STRING:
            output += " \"" + self.value + "\""
        elif self.type in VALUE_TYPES:
            output += " " + self.value
        return output
    def __repr__(self):
        return self.__str__()
    
variables:dict = {"pi":Token(TT_FLOAT,"3.14192653589")}

def get_words():
    return tuple(INBUILT_FUNCTIONS.keys()) + INBUILT_TYPES + tuple(variables.keys())

class Lexer:
    def __init__(self,text,is_filepath=False):
        if is_filepath:
            with open(text,"r") as f:
                self.code = f.read()
        else:
            self.code = text
        self.tokens = [[]]
        self.index = 0

    def make_tokens(self):
        while self.index < len(self.code):
            match self.code[self.index]:
                case ' ' | '\t':
                    pass #just skip whitespace
                case '\n':
                    self.tokens.append([])
                case '+':
                    self.tokens[-1].append(Token(TT_PLUS,""))
                case '-':
                    self.tokens[-1].append(Token(TT_MINUS,""))
                case '*':
                    self.tokens[-1].append(Token(TT_TIMES,""))
                case '/':
                    self.tokens[-1].append(Token(TT_DIVIDE,""))
                case '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9':
                    num = self.makeNumber()
                    self.tokens[-1].append(num)
                case '(':
                    self.tokens[-1].append(Token(TT_LPAREN,""))
                case ')':
                    self.tokens[-1].append(Token(TT_RPAREN,""))
                case '{':
                    self.tokens[-1].append(Token(TT_LCURLY,""))
                case '}':
                    self.tokens[-1].append(Token(TT_RCURLY,""))
                case '=' | '<' | '>':
                    self.tokens[-1].append(self.makeEqual())
                case '"' | '\'':
                    self.tokens[-1].append(self.makeString())
                case _:
                    if self.code[self.index] in ALL_LETTERS:
                        self.tokens[-1].append(self.makeWord())
                    else:
                        print("Bad error D:",self.code[self.index])
                        return
            self.index += 1
        return

    def makeNumber(self):
        curr = ""
        if self.code[self.index - 1] == '-' and self.index != 0:
            curr = "-"
            self.tokens = self.tokens[:-1]
        isFloat = False
        while self.index < len(self.code):
            match self.code[self.index]:
                case '.':
                    isFloat = True
                    curr += self.code[self.index]
                case '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9':
                    curr += self.code[self.index]
                case _:
                    self.index -= 1
                    return Token(TT_FLOAT if isFloat else TT_INT,curr)
            self.index += 1
        return Token(TT_FLOAT if isFloat else TT_INT,curr)
    
    def makeWord(self):
        curr = ""
        while self.index < len(self.code):
            if self.code[self.index] in ALL_LETTERS:
                curr += self.code[self.index]
            else:
                self.index -= 1
                break
            self.index += 1
        return Token(TT_WORD if curr not in INBUILT_TYPES else TT_TYPE,curr)
    
    def makeString(self):
        startingChar = self.code[self.index]
        self.index += 1 # starting qoute
        curr = ""
        while self.index < len(self.code):
            if self.code[self.index] == startingChar:
                self.index -= 1
                break
            curr += self.code[self.index]
            self.index += 1
        self.index += 1 # ending qoute
        return Token(TT_STRING,curr)
        
    def makeEqual(self):
        first = self.code[self.index]
        self.index += 1
        if self.index >= len(self.code):
            return Token(TT_ASSIGN,"")
        second = self.code[self.index]
        if first == '=':
            if second == '=':
                return Token(TT_EQ,"")
            else:
                self.index -= 1
                return Token(TT_ASSIGN,"")
        elif first == '<':
            if second == '=':
                return Token(TT_LTE,"")
            else:
                self.index -= 1
                return Token(TT_LT,"")
        elif first == '>':
            if second == '=':
                return Token(TT_GTE,"")
            else:
                self.index -= 1
                return Token(TT_GT,"")


class Parser:
    def __init__(self, tokens:list[Token]):
        self.AST = []
        self.tokens = tokens
        self.index = 0

    def parse(self):
        self.index = 0
        self.AST = self.expr()
    
    def factor(self):
        node = None
        if self.index >= len(self.tokens):
            return node
        if self.tokens[self.index].type in (*CURLY_BRACKETS,*VALUE_TYPES):
            node = [self.tokens[self.index]]
            self.index += 1
            if node[0].type == TT_LCURLY and self.index < len(self.tokens):
                # one liner code block :3333
                old = self.expr()
                self.index += 1
                node += [old,self.term()]
        elif self.tokens[self.index].type == TT_WORD:
            node = [self.tokens[self.index]]
            self.index += 1
            if node[0].value in INBUILT_WORDS:
                old = self.expr()
                self.index += 1
                node += [old,self.term()]
            if self.index >= len(self.tokens):
                return node
            if self.tokens[self.index].type == TT_LPAREN:
                while self.tokens[self.index].type == TT_LPAREN:
                    oldNode = self.tokens[self.index]
                    self.index += 1
                    center = self.expr()
                    if type(center) == Token:
                        if center.type == TT_RPAREN:
                            node = [node, oldNode, center]
                    else:
                        centerHas=False
                        for token in center:
                            if type(token) == Token:
                                if token.type == TT_RPAREN:
                                    centerHas=True
                                    node = [node, oldNode, center]
                        if not centerHas:
                            node = [node, oldNode, center, self.factor()]
                    self.index += 1
                    if self.index >= len(self.tokens):
                        return node
        elif self.tokens[self.index].type == TT_TYPE:
            self.index += 1
            node = [self.tokens[self.index-1],self.factor(),self.expr()]
        elif self.tokens[self.index].type == TT_ASSIGN:
            self.index += 1
            node = [self.tokens[self.index-1],self.factor()]
        elif self.tokens[self.index].type == TT_RPAREN:
            node = self.tokens[self.index]
        return node
    
    def paren(self):
        node = self.factor()
        if self.index >= len(self.tokens):
            return node
        while self.tokens[self.index].type == TT_LPAREN:
            oldNode = self.tokens[self.index]
            self.index += 1
            node = [oldNode, self.expr(), self.factor()]
            if self.index >= len(self.tokens):
                return node
        return node
    
    def assignment(self):
        node = self.paren()
        if self.index >= len(self.tokens):
            return node
        while self.tokens[self.index].type == TT_ASSIGN:
            if type(node) == list:
                if node[0].type != TT_WORD and len(node[0]) != 1:
                   return Error("AssignmentError","Cannot assign to a value")
            elif node.type != TT_WORD:
                return Error("AssignmentError","Cannot assign to a value")
            oldNode = self.tokens[self.index]
            self.index += 1
            node = [node[0], [oldNode, self.expr()]]
            if self.index >= len(self.tokens):
                return node
        return node
    
    def equality(self):
        node = self.assignment()
        if self.index >= len(self.tokens):
            return node
        while self.tokens[self.index].type in COMPARISON_TYPES:
            oldNode = self.tokens[self.index]
            self.index += 1
            node = [node, oldNode, self.assignment()]
            if self.index >= len(self.tokens):
                return node
        return node

    def term(self):
        node = self.equality()
        if self.index >= len(self.tokens):
            return node
        while self.tokens[self.index].type == TT_TIMES or self.tokens[self.index].type == TT_DIVIDE:
            oldNode = self.tokens[self.index]
            self.index += 1
            node = [node, oldNode, self.equality()]
            if self.index >= len(self.tokens):
                return node
        return node
    
    def expr(self):
        node = self.term()
        if self.index >= len(self.tokens):
            return node
        while self.tokens[self.index].type == TT_MINUS or self.tokens[self.index].type == TT_PLUS:
            oldNode = self.tokens[self.index]
            self.index += 1
            node = [node, oldNode, self.term()]
            if self.index >= len(self.tokens):
                return node
        return node

class Interpreter:
    def __init__(self):
        self.code_block = []
    def interpret(self,tokens,ignoreCodeBlockAmount=0) -> list | Token:
        
        pos = 0
        curr = None
        number = None
        operator = None
        in_paren = False
        if isinstance(tokens,Error):
            return tokens
        if tokens is []:
            return None
        elif type(tokens) == None:
            return None
        elif type(tokens) == Token:
            return tokens
            
        while pos < len(tokens):
            if isinstance(tokens[pos],list):
                curr = self.interpret(tokens[pos],ignoreCodeBlockAmount)
            elif isinstance(tokens[pos], Token):
                curr = tokens[pos]
            if isinstance(curr,Error):
                return curr
            elif isinstance(curr, Token):
                if len(self.code_block) > ignoreCodeBlockAmount:
                    self.code_block[-1][2].append(curr)
                if curr.type == TT_RCURLY:
                    print('\n',self.code_block[-1],'\n')
                    output = self.interpret(self.code_block[-1][1],1+ignoreCodeBlockAmount)
                    if self.code_block[-1][0] == "if":
                        if output.value == "True":
                            self.interpret(self.code_block[-1][2],1+ignoreCodeBlockAmount)
                    if self.code_block[-1][0] == "while":
                        while output.value == "True":
                            self.interpret(self.code_block[-1][2],1+ignoreCodeBlockAmount)
                            output = self.interpret(self.code_block[-1][1],1+ignoreCodeBlockAmount)
                    self.code_block = self.code_block[0:-1]
                if len(self.code_block) > ignoreCodeBlockAmount:
                    pos += 1
                    continue
                if curr.type == TT_TYPE:
                    # This is special we just jump right in
                    pos += 1
                    middle = tokens[pos]
                    if type(middle) == list:
                        if type(middle[0]) == Token:
                            if middle[0].type != TT_WORD and len(middle) == 1:
                                return Error("Syntax Error"," function or variable assignment.")
                            elif middle[0].type == TT_WORD and len(middle) == 1:
                                name = middle[0]
                        if type(middle[0]) == list: #this only happens with functions
                            name = middle[0][0]
                            if middle[1].type == TT_LPAREN:
                                pass #why TF am I already adding functions
                    if type(middle) == Token:
                        if middle.type != TT_WORD:
                            return Error("AssignmentError",f"function or variable assignment: {middle}")
                        else:
                            name = middle
                    pos += 1
                    end = tokens[pos]
                    if end[0].type == TT_ASSIGN:
                        if curr.value in variables.keys():
                            return Error("AssignmentError","Cannot initialize an already existing variable.")     
                        variables[name.value] = self.interpret(end[1],ignoreCodeBlockAmount)
                        print(variables)
                    else:
                        return Error("AssignmentError","variable assignment.")
                if curr.type == TT_WORD:
                    
                    if pos+1 < len(tokens):
                        pos += 1
                        if type(tokens[pos]) == list:
                            temp = None
                            if type(tokens[pos][0]) == list:
                                temp = tokens[pos][0][0]
                            else:
                                temp = tokens[pos][0]
                            if temp.type == TT_ASSIGN:
                                if curr.value not in variables.keys():
                                    return Error("AssignmentError","Missing variable type initializer.")        
                                if len(tokens[pos]) > 1:
                                    variables[curr.value] = self.interpret(tokens[pos][1],ignoreCodeBlockAmount)
                                else:
                                    return Error("AssignmentError","Missing value")   
                            elif temp.type == TT_LPAREN:
                                if curr.value in INBUILT_WORDS:
                                    # make codeblock
                                    if tokens[pos][2].type != TT_RPAREN:
                                        return Error("FunctionCallError","Missing the right paren")  
                                    pos += 1
                                    #                       statement    conition        expression
                                    self.code_block.append([curr.value,tokens[pos-1][1],[          ]])
                                    pos += 1
                        elif tokens[pos].type == TT_LPAREN:
                                if curr.value not in INBUILT_FUNCTIONS + INBUILT_WORDS:
                                    return Error("AssignmentError","Missing variable type initializer.")      
                                pos += 1  
                                if curr.value in INBUILT_FUNCTIONS: # these functions are hardcoded
                                    if curr.value == "print":
                                        print(self.interpret(tokens[pos],ignoreCodeBlockAmount).value)
                                    if curr.value == "input":
                                        number = Token(TT_STRING,input(self.interpret(tokens[pos],ignoreCodeBlockAmount).value))
                                    if curr.value == "asInt":
                                        toConvert = self.interpret(tokens[pos],ignoreCodeBlockAmount).value
                                        try:
                                            number = int(toConvert)
                                        except:
                                            return Error("Conversion Error","Cannot convert to int")
                                pos += 1
                                if len(tokens) <= pos:
                                    return Error("FunctionCallError","Missing the right paren")   
                                if tokens[pos].type != TT_RPAREN:
                                    return Error("FunctionCallError","Missing the right paren")      
                    if curr.value in variables.keys():
                        number = variables[curr.value]
                    else:
                        number = curr
                if curr.type == TT_LPAREN:
                    pos += 1
                    curr = self.interpret(tokens[pos])
                    in_paren = True
                    #if not in_paren:
                    #    print("Error: Extra ending paren")
                    #else:
                    #    in_paren = False
                if curr.type in VALUE_TYPES:
                    if number == None:
                        number = curr
                    else:
                        # Calculations
                        number = self.calculate(number,operator,curr)
                        if isinstance(number,Error):
                            return number
                elif curr.type in OPERATOR_TYPES + COMPARISON_TYPES:
                    operator = curr
            pos += 1
        return number

    def calculate(self,firstValue:Token,middleValue:Token,secondValue:Token):
        operationType = None
        firstNum = None
        secondNum = None
        # Automatic Conversion from INT to FLOAT when a FLOAT is in the calculation
        if (firstValue.type == TT_FLOAT and secondValue.type in (TT_INT,TT_BOOL)) or (firstValue.type in (TT_INT,TT_BOOL) and secondValue.type == TT_FLOAT):
            operationType = TT_FLOAT
            if firstValue.type == TT_BOOL:
                firstNum = 1.0 if firstValue.value == "true" else 0.0
            else:
                firstNum = float(firstValue.value)
            
            if secondValue.type == TT_BOOL:
                secondNum = 1.0 if secondValue.value == "true" else 0.0
            else:
                secondNum = float(secondValue.value)
        elif firstValue.type in (TT_INT,TT_BOOL) and secondValue.type in (TT_INT,TT_BOOL):
            operationType = TT_INT
            if firstValue.type == TT_BOOL:
                firstNum = 1 if firstValue.value == "true" else 0
            else:
                firstNum = float(firstValue.value)
            
            if secondValue.type == TT_BOOL:
                secondNum = 1 if secondValue.value == "true" else 0
            else:
                secondNum = int(secondValue.value)
        if firstNum == None and secondNum == None:
            return Error("SyntaxError"," Syntax")
        if middleValue.type == TT_PLUS:
            return Token(operationType,str(firstNum+secondNum))
        elif middleValue.type == TT_MINUS:
            return Token(operationType,str(firstNum-secondNum))
        elif middleValue.type == TT_TIMES:
            return Token(operationType,str(firstNum*secondNum))
        elif middleValue.type == TT_DIVIDE:
            if firstNum == 0 or secondNum == 0:
                return Error("DivisionWithZeroError","Cannot do division with 0")
            return Token(operationType,str(firstNum/secondNum))
        elif middleValue.type == TT_EQ:
            return Token(TT_BOOL,str(firstNum == secondNum))
        elif middleValue.type == TT_NE:
            return Token(TT_BOOL,str(firstNum != secondNum))
        elif middleValue.type == TT_GT:
            return Token(TT_BOOL,str(firstNum > secondNum))
        elif middleValue.type == TT_GTE:
            return Token(TT_BOOL,str(firstNum >= secondNum))
        elif middleValue.type == TT_LT:
            return Token(TT_BOOL,str(firstNum <= secondNum))
        elif middleValue.type == TT_LTE:
            return Token(TT_BOOL,str(firstNum <= secondNum))