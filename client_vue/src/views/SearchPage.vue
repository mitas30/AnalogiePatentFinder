<template>
  <div>
    <SearchBar @search="handleSearch" />
    <ul v-if="results.length > 0">
      <li v-for="result in results" :key="result.id">
        {{ result.title }}
        <router-link :to="{ name: 'patent-detail', params: { id: result.id } }">完全な情報を表示</router-link>
      </li>
    </ul>
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
      results: []
    };
  },
  methods: {
    async handleSearch(query) {
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
