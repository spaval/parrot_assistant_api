import BotWhatsapp from '@bot-whatsapp/bot'
import QRPortalWeb from  '@bot-whatsapp/portal'
import BaileysProvider from  '@bot-whatsapp/provider/baileys'
import MockAdapter from  '@bot-whatsapp/database/mock'
import { queryAssistant } from  './utils/assistant.js'

const DEFAULT_MESSAGE_ERROR = 'En este momento no puedo responderte, por favor inténtalo más tarde.'

const mainFlow = BotWhatsapp.addKeyword(BotWhatsapp.EVENTS.WELCOME)
    .addAction(async (ctx, { flowDynamic, state }) => {
      let answer = DEFAULT_MESSAGE_ERROR
      try {
        answer = await queryAssistant(ctx.from, ctx.body)
      } catch (e) {
        console.log(`[ERROR]: ${e.message}`)
      } finally {
        await flowDynamic(answer)
      }
    })

export class WhatsAppBot {
  constructor() {
    this.adapterFlow = BotWhatsapp.createFlow([mainFlow])
    this.adapterProvider = BotWhatsapp.createProvider(BaileysProvider)
    this.adapterDB = new MockAdapter()
  }

  run() {
    BotWhatsapp.createBot({
      flow: this.adapterFlow,
      provider: this.adapterProvider,
      database: this.adapterDB,
    })

    QRPortalWeb()
  }
}