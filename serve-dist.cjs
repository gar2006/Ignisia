const http = require('http')
const fs = require('fs')
const path = require('path')

const root = path.resolve(__dirname, 'dist')
const port = 4173

const mime = {
  '.css': 'text/css; charset=utf-8',
  '.html': 'text/html; charset=utf-8',
  '.ico': 'image/x-icon',
  '.jpeg': 'image/jpeg',
  '.jpg': 'image/jpeg',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
}

http
  .createServer((req, res) => {
    const pathname = (req.url || '/').split('?')[0]
    const target = pathname === '/' ? '/index.html' : pathname
    const filePath = path.join(root, target)

    if (!filePath.startsWith(root)) {
      res.writeHead(403)
      res.end('Forbidden')
      return
    }

    fs.readFile(filePath, (error, data) => {
      if (error) {
        fs.readFile(path.join(root, 'index.html'), (fallbackError, fallbackData) => {
          if (fallbackError) {
            res.writeHead(404)
            res.end('Not found')
            return
          }

          res.writeHead(200, {
            'Content-Type': 'text/html; charset=utf-8',
          })
          res.end(fallbackData)
        })
        return
      }

      res.writeHead(200, {
        'Content-Type': mime[path.extname(filePath)] || 'application/octet-stream',
      })
      res.end(data)
    })
  })
  .listen(port, '127.0.0.1', () => {
    console.log(`Static preview running at http://127.0.0.1:${port}`)
  })
