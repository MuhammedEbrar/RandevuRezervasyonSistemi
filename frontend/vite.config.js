import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Vite'ın yerel ağdaki isteklere de yanıt vermesini sağlar.
    // Bu, ngrok'un Vite sunucusuna ulaşabilmesi için gereklidir.
    host: true,

    // İzin verilen host'ları belirtir.
    allowedHosts: [
      // Tüm ngrok alt alan adlarına izin verir.
      // Baştaki nokta (.) bir wildcard (joker karakter) görevi görür.
      '.ngrok-free.app'
    ]
  }
})
