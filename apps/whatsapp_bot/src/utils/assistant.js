import axios from 'axios'

export const queryAssistant = async (id, q) => {
    const url = `${process.env.PARROT_HOST}/query?id=${id}&q=${q}&source=whatsapp`
    
    try {
        const response = await axios.get(url)
        const data = response.data.data.answer
        
        return data
    } catch (error) {
        throw error
    }
}