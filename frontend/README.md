# Randevu Rezervasyon Sistemi - Frontend

Bu proje, Randevu Rezervasyon Sistemi'nin React ve Vite ile geliştirilmiş frontend arayüzünü içerir.

## Gerekli Kurulumlar (Prerequisites)

Projeyi çalıştırabilmek için sisteminizde **Node.js** ve **Yarn** paket yöneticisinin kurulu olması gerekmektedir.

### Windows İçin

1.  **Node.js Kurulumu:**

      * [Node.js resmi web sitesine](https://nodejs.org/) gidin.
      * **LTS (Long Term Support)** versiyonunu indirip standart kurulum adımlarını takip edin.
      * Kurulum tamamlandıktan sonra, bir terminal (CMD veya PowerShell) açıp `node -v` ve `npm -v` komutlarıyla kurulumu doğrulayın.

2.  **Yarn Kurulumu:**

      * Node.js ile birlikte gelen `npm`'i kullanarak Yarn'ı kurun. Terminale aşağıdaki komutu yazın:
        ```bash
        npm install --global yarn
        ```
      * `yarn --version` komutuyla kurulumu doğrulayın.

### Arch Linux İçin

1.  **Node.js ve Yarn Kurulumu:**
      * Bir terminal açın ve `pacman` paket yöneticisini kullanarak hepsini tek komutla kurun:
        ```bash
        sudo pacman -S nodejs npm yarn
        ```
      * `node -v` ve `yarn --version` komutlarıyla kurulumu doğrulayın.

-----

## Projeyi Başlatma (Getting Started)

Gerekli programları kurduktan sonra, aşağıdaki adımları izleyerek projeyi yerel makinenizde çalıştırabilirsiniz.

1.  **Projeyi Klonlayın (Eğer daha önce yapmadıysanız):**

    ```bash
    git clone <PROJE_REPO_URL>
    ```

2.  **Frontend Klasörüne Gidin:**

    ```bash
    cd RandevuRezervasyonSistemi/frontend
    ```

3.  **Gerekli Paketleri Yükleyin:**
    `yarn`, `package.json` dosyasını okuyarak projenin ihtiyaç duyduğu tüm paketleri kuracaktır.

    ```bash
    yarn
    ```

4.  **Geliştirme Sunucusunu Başlatın:**
    Bu komut, projeyi `http://localhost:5173` (veya benzeri bir portta) çalıştıracaktır.

    ```bash
    yarn dev
    ```








# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
