import { createRouter, createWebHistory } from 'vue-router';
import SearchPage from '@/views/SearchPage.vue';
import SearchResults from '@/views/SearchResults.vue';

const routes = [
  {
    path: '/',
    name: 'search',
    component: SearchPage
  },
  {
    path: '/results',
    name: 'search-results',
    component: SearchResults
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

export default router;
