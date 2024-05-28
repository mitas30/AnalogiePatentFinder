<template>
    <div>
      <SearchBar @search="handleSearch" />
      <button @click="$router.go(-1)">← 戻る</button>
      <div v-if="patent">
        <h2>{{ patent.title }}</h2>
        <p>{{ patent.description }}</p>
      </div>
    </div>
  </template>
  
  <script>
  import SearchBar from '@/components/SearchBar.vue';
  
  export default {
    components: {
      SearchBar
    },
    data() {
      return {
        patent: null
      };
    },
    async created() {
      const id = this.$route.params.id;
      // ダミーAPIコール
      console.log(`APIから取得する特許ID: ${id}`);
      // ダミーの特許情報を設定
      this.patent = {
        title: `Dummy Patent ${id}`,
        description: `Details for Dummy Patent ${id}`
      };
    },
    methods: {
      async handleSearch(query) {
        this.$router.push({ name: 'search', query: { q: query } });
        // ダミーAPIコール
        console.log(`APIに送信するクエリ: ${query}`);
        // ダミーの検索結果を設定
        this.results = [
          { id: 1, title: `Dummy Patent 1 for "${query}"` },
          { id: 2, title: `Dummy Patent 2 for "${query}"` }
        ];
      }
    }
  };
  </script>
  
  <style scoped>
  /* スタイルをここに追加 */
  </style>
  