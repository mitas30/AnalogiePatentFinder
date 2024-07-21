<template>
  <v-app>
    <v-system-bar color="secondary">
      System Bar
    </v-system-bar>
    <v-app-bar color="primary">
      <v-app-bar-title>
        Analogical Patent Finder
      </v-app-bar-title>
    </v-app-bar>
    <v-main>
      <!--router-viewで、vue-routerによるページ遷移を行う-->
      <router-view />
    </v-main>
    <v-footer color="primary" app>
      mitas30
    </v-footer>
  </v-app>
</template>

<script>
export default {
  name: 'App'
};
</script>

<style>
@import '@fortawesome/fontawesome-free/css/all.css';

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

body.modal-open {
  overflow: hidden;
}
</style>