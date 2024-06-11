<template>
  <div>
    <SearchBar :history="searchHistory" @search="handleSearch" @add-history="addHistory" />
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
      searchHistory: []
    };
  },
  methods: {
    async handleSearch(query) {
      // URLを遷移させるだけで、データの取得はSearchResults.vueで行う
      this.$router.push({ name: 'search-results', query: { q: query } });
    },
    addHistory(query) {
      if (!this.searchHistory.includes(query)) {
        this.searchHistory.push(query);
        if (this.searchHistory.length > 5) {
          this.searchHistory.shift();
        }
        this.saveHistory();
      }
    },
    loadHistory() {
      const history = localStorage.getItem('searchHistory');
      if (history) {
        this.searchHistory = JSON.parse(history);
      }
    },
    saveHistory() {
      localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory));
    }
  },
  created() {
    this.loadHistory();
  }
};
</script>

<style scoped>
/* スタイルをここに追加 */
</style>
