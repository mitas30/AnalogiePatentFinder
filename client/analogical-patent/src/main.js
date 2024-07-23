import { createApp } from 'vue';

//Vuetify
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

//Components
import App from './App.vue';
import router from './router';

const app = createApp(App);

const vuetify = createVuetify({
    components,
    directives,
    icons:{
      defaultSet: 'mdi',
    },
  })

//モダンjsの記法 : メソッドチェーン
app.use(router).use(vuetify).mount('#app');

