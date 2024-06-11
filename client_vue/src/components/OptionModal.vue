<template>
    <div class="modal-overlay" @click.self="close">
      <div class="modal-content">
        <h2>オプション検索</h2>
        <!-- オプション検索の内容をここに追加 -->
      </div>
    </div>
  </template>
  
  <script>
  export default {
    methods: {
      close() {
        this.$emit('close');
      }
    }
  };
  </script>
  
  <style scoped>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  
  .modal-content {
    background: white;
    padding: 20px;
    border-radius: 8px;
    width: 50%;
    max-width: 600px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  }
  </style>
  