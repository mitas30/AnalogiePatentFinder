<template>
  <div class="search-container">
    <div class="search-bar-container">
      <i class="fas fa-search search-icon"></i>
      <input
        v-model="query"
        @keyup.enter="search"
        @focus="showHistory"
        placeholder="特許を検索"
        class="search-bar"
      />
      <i class="fas fa-cogs search-option-icon" @click="toggleOptions"></i>
    </div>
    <ul v-if="showHistoryList && history.length > 0" class="history-list">
      <li v-for="item in history" :key="item" @click="selectHistory(item)">
        {{ item }}
      </li>
    </ul>
    <OptionModal v-if="showOptions" @close="toggleOptions" />
  </div>
</template>

<script>
import OptionModal from '@/components/OptionModal.vue';

export default {
  components: {
    OptionModal
  },
  props: {
    history: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      query: '',
      showHistoryList: false,
      showOptions: false
    };
  },
  methods: {
    search() {
      this.$emit('search', this.query);
      this.addHistory(this.query);
      this.showHistoryList = false;
    },
    showHistory() {
      console.log('showHistory called');
      this.showHistoryList = true;
    },
    addHistory(query) {
      this.$emit('add-history', query);
    },
    selectHistory(item) {
      this.query = item;
      this.search();
    },
    toggleOptions() {
      this.showOptions = !this.showOptions;
    }
  }
};
</script>

<style scoped>
@import '@fortawesome/fontawesome-free/css/all.css';

html, body {
  height: 100%;
  margin: 0;
  overflow: hidden;
}

.search-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: #f5f5f5;
  margin: 0;
}

.search-bar-container {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 50%;
  max-width: 600px;
  position: relative;
}

.search-bar {
  flex-grow: 1;
  padding: 10px 20px;
  font-size: 18px;
  border: 1px solid #ccc;
  border-radius: 24px;
  outline: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  padding-left: 40px;
  padding-right: 40px;
}

.search-bar:focus {
  border-color: #4285f4;
  box-shadow: 0 2px 8px rgba(66, 133, 244, 0.5);
}

.search-icon {
  position: absolute;
  left: 10px;
  font-size: 20px;
  color: #ccc;
}

.search-option-icon {
  position: absolute;
  right: 10px;
  font-size: 20px;
  color: #ccc;
  cursor: pointer;
  transition: color 0.3s ease;
}

.search-option-icon:hover {
  color: #4285f4;
}

.history-list {
  list-style-type: none;
  padding: 0;
  margin: 10px 0 0;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  width: 50%;
  max-width: 600px;
}

.history-list li {
  padding: 10px 20px;
  cursor: pointer;
  transition: background 0.2s;
}

.history-list li:hover {
  background: #f5f5f5;
}
</style>
