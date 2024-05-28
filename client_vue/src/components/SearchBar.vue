<template>
    <div>
      <input v-model="query" placeholder="特許を検索" />
      <button @click="search">検索</button>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        query: ''
      };
    },
    methods: {
      search() {
        this.$emit('search', this.query);
      }
    }
  };
  </script>
  
  <style scoped>
  /* スタイルをここに追加 */
  </style>
  