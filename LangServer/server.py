from pygls.server import LanguageServer

# Default libraries
# -----------------

from typing import List
import lsprotocol.types as lsp

# Custom libraries
# ----------------

from LangServer.mcData import MCData


class KiwiCompletion:
    mcData: MCData
    params: lsp.CompletionParams

    def __init__(self):
        self.mcData = MCData('1.19')

    def getItems(self) -> List[lsp.CompletionItem]:
        return list(map(
            lsp.CompletionItem,
            self.mcData.criterias_keys()
        ))

    def complete(self, params: lsp.CompletionParams):
        self.params = params
        return lsp.CompletionList(
            is_incomplete=False,
            items=self.getItems()
        )


class KiwiLanguageServer(LanguageServer):
    kiwiCompletion: KiwiCompletion

    def __init__(self, *args):
        super().__init__(*args)
        self.kiwiCompletion = KiwiCompletion()

        @self.feature(
            lsp.INITIALIZE
        )
        def initialize(params: lsp.InitializeParams):
            print('begin')
            print()

        @self.feature(
            lsp.TEXT_DOCUMENT_COMPLETION, lsp.CompletionOptions(
                trigger_characters=['.']
            )
        )
        def completion(params: lsp.CompletionParams):
            return self.kiwiCompletion.complete(params)


KiwiLanguageServer('example-server', 'v0.1')\
    .start_tcp('127.0.0.1', 8080)
