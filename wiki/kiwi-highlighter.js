Array.prototype.includes = function (value) {
    return this.indexOf(value) !== -1
}

String.prototype.characterize = function (callback) {
    const characters = this.split('');
    let options = {};

    for (let i = 0; i < this.length; i++) {
        options = callback(characters[i]);
    }
}

const keywords = [
    'continue', 'public', 'namespace', 'else', 'pass',
    'while', 'if', 'function', 'promise', 'return', 'break', 'private'
];
const functions = ['print'];
const data_types = ['bool', 'score', 'scoreboard', 'str', 'fstr']
const value_states = ['true', 'false', 'none']

function highlight_construct(textarea , highlight, code) {
    highlight.innerHTML = null
    const triggerHighlight = function () {
        const tokens = tokenize(textarea.innerText);
        highlight.innerHTML = '';
        for (let i = 0; i < tokens.length; i++) {
            const token = tokens[i];
            const span = document.createElement('span');
            span.className = 'highlight-' + token.type;
            span.innerText = token.value;
            highlight.appendChild(span);
        }
        const lines = textarea.innerText.split('\n');
        highlight.scrollTop = textarea.scrollTop;
        return lines.length - 1
    };

    textarea.addEventListener('input', triggerHighlight);
    textarea.addEventListener('scroll', function (event) {
        highlight.scrollTop = this.scrollTop;
    });

    const tabCode = 9;
    const leftParenthesisCode = 40;
    textarea.addEventListener('keydown', function (event) {
        switch (event.keyCode) {
            case tabCode:
                event.preventDefault();
                this.value += '    ';
                break;
        }
    });

    textarea.textContent = code;
    highlight.textContent = code;
    return triggerHighlight()
}

function tokenize(inputString) {
    let peekToken;
    const tokens = [];
    let lexedValue = '';
    let currentToken = null;

    function newSpaceToken() {
        currentToken = {type: 'space', value: ' '};
        lexedValue = '';
    }

    function parseLexedValueToToken() {
        if (lexedValue) {
            if (keywords.includes(lexedValue)) {
                tokens.push({type: 'keyword', value: lexedValue})
            } else if (functions.includes(lexedValue)) {
                tokens.push({type: 'function', value: lexedValue})
            } else if (data_types.includes(lexedValue)) {
                tokens.push({type: 'data-type', value: lexedValue})
            } else if (value_states.includes(lexedValue)) {
                tokens.push({type: 'value-state', value: lexedValue})
            } else if (lexedValue !== '') {
                if (true) {
                    tokens.push({type: 'default', value: lexedValue})
                } else {
                    tokens.push({type: 'number', value: lexedValue})
                }
            }
            lexedValue = '';
        }
    }

    function lex(char) {
        if (char !== ' ' && currentToken && currentToken.type === 'space') {
            tokens.push(currentToken);
            lexedValue = '';
            currentToken = null;
        }

        switch (char) {
            case ' ':
                if (keywords.includes(lexedValue)) {
                    tokens.push({type: 'keyword', value: lexedValue})
                    newSpaceToken();
                } else if (functions.includes(lexedValue)) {
                    tokens.push({type: 'function', value: lexedValue})
                    newSpaceToken();
                } else if (data_types.includes(lexedValue)) {
                    tokens.push({type: 'data-type', value: lexedValue})
                    newSpaceToken();
                }else if (value_states.includes(lexedValue)) {
                    tokens.push({type: 'value-state', value: lexedValue})
                    newSpaceToken();
                } else if (lexedValue !== '') {
                    if (true) {
                        tokens.push({type: 'default', value: lexedValue})
                    } else {
                        tokens.push({type: 'number', value: lexedValue})
                    }
                    newSpaceToken();
                } else if (currentToken) {
                    currentToken.value += ' '
                } else {
                    newSpaceToken();
                }
                break;

            case '"':
            case '\'':
                if (currentToken) {
                    if (currentToken.type === 'string') {
                        if (currentToken.value[0] === char) {
                            currentToken.value += char
                            tokens.push(currentToken)
                            currentToken = null;
                        } else {
                            currentToken.value += char
                        }
                    } else if (currentToken.type === 'comment') {
                        currentToken.value += char
                    }
                } else {
                    if (lexedValue) {
                        tokens.push({type: 'default', value: lexedValue});
                        lexedValue = '';
                    }
                    currentToken = {type: 'string', value: char}
                }
                break;

            case '=':
            case '+':
            case '-':
            case '*':
            case '/':
            case '%':
            case '&':
            case '|':
            case '>':
            case '<':
            case '!':
                if (currentToken) {
                    currentToken.value += char;
                } else {
                    parseLexedValueToToken();
                    tokens.push({type: 'operator', value: char})
                }
                break;

            case '#':
                if (currentToken) {
                    currentToken.value += char;
                } else {
                    parseLexedValueToToken();
                    currentToken = {type: 'comment', value: char}
                }
                break;

            case ':':
                if (currentToken) {
                    currentToken.value += char;
                } else {
                    parseLexedValueToToken();
                    tokens.push({type: 'colon', value: char});
                }
                break;

            case '(':
                if (currentToken) {
                    currentToken.value += char;
                } else {
                    parseLexedValueToToken();
                    tokens.push({type: 'left-parentheses', value: char});
                }
                break;

            case ')':
                if (currentToken) {
                    currentToken.value += char;
                } else {
                    parseLexedValueToToken();
                    tokens.push({type: 'right-parentheses', value: char});
                }
                break;

            case '[':
                if (currentToken) {
                    currentToken.value += char;
                } else {
                    parseLexedValueToToken();
                    tokens.push({type: 'left-bracket', value: char});
                }
                break;

            case ']':
                if (currentToken) {
                    currentToken.value += char;
                } else {
                    parseLexedValueToToken();
                    tokens.push({type: 'right-bracket', value: char});
                }
                break;

            case ',':
                if (currentToken) {
                    currentToken.value += char;
                } else {
                    parseLexedValueToToken();
                    tokens.push({type: 'comma', value: char});
                }
                break;

            case '\n':
                if (currentToken) {
                    switch (currentToken.type) {
                        case 'string':
                        case 'comment':
                            tokens.push(currentToken)
                            currentToken = null;
                            break;
                        default:
                    }
                } else {
                    parseLexedValueToToken();
                    lexedValue = '';
                }
                tokens.push({type: 'newline', value: '\n'});
                break;

            case ';':
                if (currentToken) {
                    currentToken.value += char;
                } else {
                    parseLexedValueToToken();
                    tokens.push({type: 'semicolon', value: char});
                }
                break;

            default:
                if (currentToken) {
                    currentToken.value += char;
                } else {
                    lexedValue += char
                }

                break;
        }
    }

    /* Lexing the input codes */
    inputString.characterize(lex);

    /* Rest of the lexed value or token which is unfinished */
    parseLexedValueToToken();

    if (currentToken) tokens.push(currentToken)

    /* Secondary Parse to Match Some Patterns */
    let isFunctionArgumentScope = false;
    const tokenCount = tokens.length;
    for (let i = 0; i < tokenCount; i++) {
        const token = tokens[i];
        if (token.type === 'default' && isFunctionArgumentScope) {
            token.type = 'argument';
        } else if (token.type === 'left-parentheses') {
            peekToken = tokens[i - 1];
            if (peekToken && peekToken.type === 'function-name') isFunctionArgumentScope = true;
        } else if (token.type === 'right-parentheses') {
            isFunctionArgumentScope = false;
        }
    }

    return tokens
}
