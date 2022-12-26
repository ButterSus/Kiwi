function renderLineNumbers(lines, code) {
    if (code == null || lines === 0) return
    let code_lines = document.createElement('pre');
    code_lines.className = 'highlight-code-lines'
    if (lines === 1){
        code_lines.innerHTML = padLeft(">", 2)
    }
    else{
        code_lines.innerHTML = Array.apply(null, Array(lines)).map(
            (_, index) => {
                return padLeft(index.toString(), 4)
            }
        ).join('\n')
    }
    const wrapper = document.createElement('div')
    wrapper.className = 'highlight-code-block'
    wrapper.appendChild(code_lines)
    code.parentNode.replaceChild(wrapper, code)
    wrapper.appendChild(code)
}

function padLeft(str, l) {
  return Array(l - str.length + 1).join(" ") + str;
}
