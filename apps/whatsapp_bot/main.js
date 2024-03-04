import dotenv from 'dotenv'
import { WhatsAppBot } from './src/app.js'
import { server } from './src/server/server.js'

const main = async () => {
    const env = process.env.env || 'dev'
    const path = `config/.env.${env}`
    
    dotenv.config({ path })

    const bot = new WhatsAppBot()
    await bot.run()
    
    await server(env)
}

main()