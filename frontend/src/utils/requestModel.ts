export interface RequestModel {
  method: string
  baseURL: string
  path: string
  query: QueryParam[]
  headers: Header[]
  body: Body
  auth?: Auth
  timeout?: number
}

export interface QueryParam {
  key: string
  value: string
  enabled: boolean
}

export interface Header {
  key: string
  value: string
  enabled: boolean
}

export interface Body {
  mode: 'none' | 'raw' | 'json' | 'formdata' | 'urlencoded' | 'binary'
  raw?: string
  json?: string
  formdata?: FormField[]
  urlencoded?: FormField[]
  binary?: File
}

export interface FormField {
  key: string
  value: string
  type: 'text' | 'file'
  enabled: boolean
}

export interface Auth {
  type: 'none' | 'basic' | 'bearer' | 'api_key'
  username?: string
  password?: string
  token?: string
  key?: string
  value?: string
  addTo?: 'header' | 'query'
}

export class RequestModelParser {
  static async parseCurl(curlCommand: string): Promise<RequestModel> {
    try {
      const curlconverter = await import('curlconverter')
      
      const harData = curlconverter.toHarString(curlCommand)
      const har = JSON.parse(harData)
      
      if (!har.log || !har.log.entries || har.log.entries.length === 0) {
        throw new Error('无法解析CURL命令，请检查格式')
      }
      
      const entry = har.log.entries[0]
      const request = entry.request
      
      console.log('HAR request URL:', request.url)
      // console.log('HAR request queryString:', request.queryString)
      
      const url = new URL(request.url)
      const baseURL = `${url.protocol}//${url.host}`
      const path = url.pathname
      
      const query: QueryParam[] = []
      
      if (request.queryString && request.queryString.length > 0) {
        request.queryString.forEach((param: any) => {
          query.push({ key: param.name, value: param.value || '', enabled: true })
        })
      } else {
        url.searchParams.forEach((value, key) => {
          query.push({ key, value, enabled: true })
        })
      }
      
      console.log('Parsed URL:', { baseURL, path, search: url.search, searchParams: Array.from(url.searchParams.entries()), query })
      
      const headers: Header[] = []
      
      if (request.cookies && request.cookies.length > 0) {
        const cookieValue = request.cookies
          .map((cookie: any) => `${cookie.name}=${cookie.value}`)
          .join('; ')
        headers.push({ key: 'Cookie', value: cookieValue, enabled: true })
      }
      
      request.headers.forEach((header: any) => {
        headers.push({ key: header.name, value: header.value, enabled: true })
      })
      
      // console.log('HAR headers:', request.headers)
      // console.log('HAR cookies:', request.cookies)
      console.log('Parsed headers:', headers)
      
      const body: Body = { mode: 'none' }
      if (request.postData) {
        const postData = request.postData
        const contentType = headers.find(h => h.key.toLowerCase() === 'content-type')?.value
        
        if (contentType?.includes('application/json')) {
          body.mode = 'json'
          body.json = postData.text || ''
        } else if (contentType?.includes('application/x-www-form-urlencoded')) {
          body.mode = 'urlencoded'
          body.urlencoded = []
          if (postData.params) {
            postData.params.forEach((param: any) => {
              body.urlencoded?.push({ 
                key: param.name, 
                value: param.value || '', 
                type: 'text', 
                enabled: true 
              })
            })
          }
        } else if (contentType?.includes('multipart/form-data')) {
          body.mode = 'formdata'
          body.formdata = []
          if (postData.params) {
            postData.params.forEach((param: any) => {
              body.formdata?.push({
                key: param.name,
                value: param.value || param.fileName || '',
                type: param.fileName ? 'file' : 'text',
                enabled: true
              })
            })
          }
        } else {
          body.mode = 'raw'
          body.raw = postData.text || ''
        }
      }
      
      return {
        method: request.method || 'GET',
        baseURL,
        path,
        query,
        headers,
        body,
        auth: RequestModelParser.parseAuth(headers),
        timeout: 30000
      }
    } catch (error) {
      console.error('Failed to parse cURL command:', error)
      throw new Error('cURL命令解析失败，请检查命令格式')
    }
  }
  
  static parseAuth(headers: Header[]): Auth | undefined {
    const authHeader = headers.find(h => h.key.toLowerCase() === 'authorization')
    if (authHeader) {
      const value = authHeader.value
      
      if (value.startsWith('Bearer ')) {
        return {
          type: 'bearer',
          token: value.substring(7)
        }
      }
      
      if (value.startsWith('Basic ')) {
        try {
          const decoded = atob(value.substring(6))
          const [username, password] = decoded.split(':')
          return {
            type: 'basic',
            username,
            password
          }
        } catch {
          return undefined
        }
      }
    }
    
    return undefined
  }
  
  static toCurl(model: RequestModel): string {
    let curl = `curl -X ${model.method}`
    
    const url = new URL(model.baseURL + model.path)
    model.query.forEach(param => {
      if (param.enabled && param.key) {
        url.searchParams.append(param.key, param.value)
      }
    })
    curl += ` '${url.toString()}'`
    
    model.headers.forEach(header => {
      if (header.enabled && header.key) {
        curl += ` -H '${header.key}: ${header.value}'`
      }
    })
    
    if (model.body.mode !== 'none' && model.body.raw) {
      curl += ` -d '${model.body.raw}'`
    }
    
    if (model.timeout) {
      curl += ` --max-time ${model.timeout / 1000}`
    }
    
    return curl
  }
  
  static toFormData(model: RequestModel): FormData {
    const formData = new FormData()
    
    if (model.body.mode === 'formdata' && model.body.formdata) {
      model.body.formdata.forEach(field => {
        if (field.enabled && field.key) {
          if (field.type === 'file' && field.value) {
            formData.append(field.key, field.value as any)
          } else {
            formData.append(field.key, field.value)
          }
        }
      })
    }
    
    return formData
  }
  
  static toURLSearchParams(model: RequestModel): URLSearchParams {
    const params = new URLSearchParams()
    
    if (model.body.mode === 'urlencoded' && model.body.urlencoded) {
      model.body.urlencoded.forEach(field => {
        if (field.enabled && field.key) {
          params.append(field.key, field.value)
        }
      })
    }
    
    return params
  }
}
