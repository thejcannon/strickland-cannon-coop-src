import { Plugin } from '@nuxt/types'
import openpgp, { key as openpgpKey, message as openpgpMessage } from "openpgp"
import { NuxtAxiosInstance } from "@nuxtjs/axios"

const axiosPlugin: Plugin = (context) => {
    context.$axios.interceptors.response.use(async (response) => {
        if (response.data.startsWith("-----BEGIN PGP MESSAGE-----")) {
            const { keys: [privateKey] } = await openpgpKey.readArmored(window.localStorage.getItem("gpgPrivateKey"));
            await privateKey.decrypt(window.localStorage.getItem("gpgPassphrase")!);
            const result = await openpgp.decrypt({
                message: await openpgpMessage.readArmored(response.data),
                privateKeys: [privateKey]
            })
            response.data = JSON.parse(result.data)
        }
        return Promise.resolve(response)
    })
}

export default axiosPlugin;
