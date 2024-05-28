import { createRouter, createWebHistory } from 'vue-router';
import SearchPage from '@/views/SearchPage.vue';
import PatentDetail from '@/views/PatentDetail.vue';

const routes = [
  {
    path: '/',
    name: 'search',
    component: SearchPage
  },
  {
    path: '/patent/:id',
    name: 'patent-detail',
    component: PatentDetail
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

export default router;
