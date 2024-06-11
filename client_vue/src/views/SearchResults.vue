<template>
  <div>
    <div v-if="selectedResult" class="container">
      <div class="left-pane">
        <ul class="results-list">
          <li v-for="result in results" :key="result.id" @click="selectResult(result)">
            <div class="result-item">
              <h3>{{ result.title }}</h3>
              <p>{{ result.content }}</p>
            </div>
          </li>
        </ul>
      </div>
      <div class="right-pane">
        <div class="header">
          <fa :icon="['fas', 'arrow-right']" class="close-icon" @click="deselectResult" />
        </div>
        <iframe :src="selectedResult.url" class="iframe-content"></iframe>
      </div>
    </div>
    <div v-else>
      <ul class="results-list">
        <li v-for="result in results" :key="result.id" @click="selectResult(result)">
          <div class="result-item">
            <h3>{{ result.title }}</h3>
            <p>{{ result.content }}</p>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faArrowRight } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

library.add(faArrowRight);

export default {
  components: {
    fa: FontAwesomeIcon
  },
  data() {
    return {
      results: [],
      selectedResult: null
    };
  },
  methods: {
    async fetchResults(query) {
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/search', {
          params: { q: query }
        });
        console.log("API Response:", response.data.results); // デバッグ用のログ
        this.results = response.data;
      } catch (error) {
        console.error('Error fetching search results:', error);
      }
    },
    selectResult(result) {
      this.selectedResult = result;
    },
    deselectResult() {
      this.selectedResult = null;
    }
  },
  created() {
    const query = this.$route.query.q;
    if (query) {
      this.fetchResults(query);
    }
  }
};
</script>

<style scoped>
.container {
  display: flex;
  height: calc(100vh - 60px); /* 検索バーの高さを引いた値 */
}

.left-pane {
  width: 33%;
  overflow-y: auto;
  border-right: 1px solid #ccc;
  padding: 10px;
}

.right-pane {
  width: 67%;
  position: relative;
  overflow-y: auto;
}

.result-item {
  border: 1px solid #eee;
  padding: 10px;
  margin: 10px 0;
  cursor: pointer;
  transition: background-color 0.3s;
}

.result-item:hover {
  background-color: #f9f9f9;
}

.close-icon {
  position: fixed;
  left: 35%;
  top: 20px;
  cursor: pointer;
  font-size: 24px;
  padding: 10px;
  background: #fff;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.iframe-content {
  width: 100%;
  height: calc(100% - 40px); /* headerの高さを差し引いた値 */
  border: none;
}

.results-list {
  list-style-type: none; /* デフォルトのリストスタイルを削除 */
  padding: 0;
  margin: 0;
}
</style>
