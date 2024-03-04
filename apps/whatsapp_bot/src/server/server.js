import express from 'express'
import { join } from 'path'
import { createReadStream } from 'fs'

const app = express()
const PORT = process.env.PORT || 3001

app.get('/qr', async (_, res) => {
    const PATH_QR = join(process.cwd(), `bot.qr.png`)
    const fileStream = createReadStream(PATH_QR)

    res.writeHead(200, { "Content-Type": "image/png" })
    fileStream.pipe(res)
})

export const server = (env) => {
    app.listen(PORT, () => {
        console.log(`server listening on port: ${PORT} -- env: ${env}`)
    })
}