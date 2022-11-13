from typing import Type
import tokenize
import subprocess
import KiwiAST


from pegen.parser import Parser, Tokenizer


subprocess.run(
    "python -m pegen KiwiParser/grammar.gram -o KiwiParser/__init__.py -v".split(),
    stdout=subprocess.DEVNULL
)
KiwiParser: Type[Parser] = ...
exec("from KiwiParser import KiwiParser")
with open('KiwiAST/example.kiwi') as file:
    tokengen = tokenize.generate_tokens(file.readline)
    tokenizer = Tokenizer(tokengen)
    parser = KiwiParser(tokenizer)
    tree = parser.start()
    tree: KiwiAST.Module