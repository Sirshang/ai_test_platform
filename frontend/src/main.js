import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { gsap } from 'gsap'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

import './style.css'
import App from './App.vue'
import router from './router'
import { initMotionMedia } from './composables/useReducedMotion'

gsap.defaults({ ease: 'power2.out', duration: 0.5 })
initMotionMedia()

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })
app.mount('#app')
