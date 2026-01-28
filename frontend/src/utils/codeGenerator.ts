import { RequestModel } from './requestModel'

export interface CodeTemplate {
  language: string
  extension: string
  generator: (curlCommand: string) => string
}

export class CodeGenerator {
  private static languageMap: Record<string, string> = {
    javascript: 'javascript',
    typescript: 'typescript',
    python: 'python',
    java: 'java',
    node: 'node',
    curl: 'http',
    php: 'php',
    go: 'go',
    csharp: 'csharp',
    ruby: 'ruby',
    swift: 'swift',
    kotlin: 'kotlin',
    rust: 'rust',
    dart: 'dart',
    objective_c: 'objc',
    shell: 'http',
    powershell: 'powershell',
    matlab: 'matlab',
    r: 'r',
    ansible: 'ansible',
    c: 'c',
    cfml: 'cfml',
    clojure: 'clojure',
    elixir: 'elixir',
    http: 'http',
    httpie: 'httpie',
    julia: 'julia',
    lua: 'lua',
    ocaml: 'ocaml',
    perl: 'perl',
    wget: 'wget'
  }

  private static languageLabels: Record<string, string> = {
    javascript: 'JavaScript',
    typescript: 'TypeScript',
    python: 'Python',
    java: 'Java',
    node: 'Node.js',
    curl: 'cURL',
    php: 'PHP',
    go: 'Go',
    csharp: 'C#',
    ruby: 'Ruby',
    swift: 'Swift',
    kotlin: 'Kotlin',
    rust: 'Rust',
    dart: 'Dart',
    objective_c: 'Objective-C',
    shell: 'Shell',
    powershell: 'PowerShell',
    matlab: 'MATLAB',
    r: 'R',
    ansible: 'Ansible',
    c: 'C',
    cfml: 'CFML',
    clojure: 'Clojure',
    elixir: 'Elixir',
    http: 'HTTP',
    httpie: 'HTTPie',
    julia: 'Julia',
    lua: 'Lua',
    ocaml: 'OCaml',
    perl: 'Perl',
    wget: 'Wget'
  }

  private static languageExtensions: Record<string, string> = {
    javascript: 'js',
    typescript: 'ts',
    python: 'py',
    java: 'java',
    node: 'js',
    curl: 'sh',
    php: 'php',
    go: 'go',
    csharp: 'cs',
    ruby: 'rb',
    swift: 'swift',
    kotlin: 'kt',
    rust: 'rs',
    dart: 'dart',
    objective_c: 'm',
    shell: 'sh',
    powershell: 'ps1',
    matlab: 'm',
    r: 'r',
    ansible: 'yml',
    c: 'c',
    cfml: 'cfm',
    clojure: 'clj',
    elixir: 'ex',
    http: 'http',
    httpie: 'http',
    julia: 'jl',
    lua: 'lua',
    ocaml: 'ml',
    perl: 'pl',
    wget: 'sh'
  }

  static async generateCode(model: RequestModel, language: string): Promise<string> {
    const curlCommand = this.buildCurlCommand(model)
    
    if (language === 'curl') {
      return curlCommand
    }
    
    const curlconverter = await import('curlconverter')

    const mappedLanguage = this.languageMap[language] || language

    try {
      switch (mappedLanguage) {
        case 'javascript':
          return curlconverter.toJavaScript(curlCommand)
        case 'python':
          return curlconverter.toPython(curlCommand)
        case 'java':
          return curlconverter.toJava(curlCommand)
        case 'node':
          return curlconverter.toNode(curlCommand)
        case 'http':
          return curlconverter.toHTTP(curlCommand)
        case 'php':
          return curlconverter.toPhp(curlCommand)
        case 'go':
          return curlconverter.toGo(curlCommand)
        case 'csharp':
          return curlconverter.toCSharp(curlCommand)
        case 'ruby':
          return curlconverter.toRuby(curlCommand)
        case 'swift':
          return curlconverter.toSwift(curlCommand)
        case 'kotlin':
          return curlconverter.toKotlin(curlCommand)
        case 'rust':
          return curlconverter.toRust(curlCommand)
        case 'dart':
          return curlconverter.toDart(curlCommand)
        case 'objc':
          return curlconverter.toObjectiveC(curlCommand)
        case 'powershell':
          return curlconverter.toPowershellWebRequest(curlCommand)
        case 'matlab':
          return curlconverter.toMATLAB(curlCommand)
        case 'r':
          return curlconverter.toR(curlCommand)
        case 'ansible':
          return curlconverter.toAnsible(curlCommand)
        case 'c':
          return curlconverter.toC(curlCommand)
        case 'cfml':
          return curlconverter.toCFML(curlCommand)
        case 'clojure':
          return curlconverter.toClojure(curlCommand)
        case 'elixir':
          return curlconverter.toElixir(curlCommand)
        case 'httpie':
          return curlconverter.toHttpie(curlCommand)
        case 'julia':
          return curlconverter.toJulia(curlCommand)
        case 'lua':
          return curlconverter.toLua(curlCommand)
        case 'ocaml':
          return curlconverter.toOCaml(curlCommand)
        case 'perl':
          return curlconverter.toPerl(curlCommand)
        case 'wget':
          return curlconverter.toWget(curlCommand)
        default:
          return curlconverter.toPython(curlCommand)
      }
    } catch (error) {
      console.error('Error generating code:', error)
      return `// Error generating code: ${error}`
    }
  }

  private static buildCurlCommand(model: RequestModel): string {
    const url = this.buildUrl(model)
    const method = model.method.toUpperCase()
    const headers = this.buildCurlHeaders(model)
    const body = this.buildCurlBody(model)

    console.log('Building curl command:', { url, method, headers, body })
    console.log('Model data:', { baseURL: model.baseURL, path: model.path, query: model.query })

    let curl = `curl -X ${method}`

    if (headers) {
      curl += ` ${headers}`
    }

    if (body) {
      curl += ` ${body}`
    }

    curl += ` '${url}'`

    console.log('Generated curl command:', curl)

    return curl
  }

  private static buildUrl(model: RequestModel): string {
    try {
      const url = new URL(model.baseURL + model.path)
      model.query.forEach(param => {
        if (param.enabled && param.key) {
          url.searchParams.append(param.key, param.value)
        }
      })
      return url.toString()
    } catch (error) {
      console.error('Error building URL:', error, { baseURL: model.baseURL, path: model.path })
      return model.baseURL + model.path
    }
  }

  private static buildCurlHeaders(model: RequestModel): string {
    const headers = model.headers.filter(h => h.enabled && h.key)

    return headers
      .map(h => {
        const value = h.value.replace(/"/g, '\\"')
        return `-H "${h.key}: ${value}"`
      })
      .join(' ')
  }

  private static buildCurlBody(model: RequestModel): string {
    if (model.body.mode === 'none') {
      return ''
    }

    const bodyValue = model.body.raw || model.body.json || ''
    if (!bodyValue) {
      return ''
    }

    switch (model.body.mode) {
      case 'raw':
      case 'json':
        return `-d '${bodyValue}'`
      case 'formdata':
        return '--data-urlencode "data"'
      case 'urlencoded':
        return `--data-urlencode "${bodyValue}"`
      case 'binary':
        return `--data-binary "@${bodyValue}"`
      default:
        return ''
    }
  }

  static getSupportedLanguages(): string[] {
    return Object.keys(this.languageMap)
  }

  static getLanguageLabel(language: string): string {
    return this.languageLabels[language] || language
  }

  static getLanguageExtension(language: string): string {
    return this.languageExtensions[language] || 'txt'
  }
}
