import Vue from 'vue';
import Router from 'vue-router';
import SearchPage from '@/views/SearchPage.vue';
import PatentDetail from '@/views/PatentDetail.vue';

Vue.use(Router);

export default new Router({
  routes: [
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
  ]
});
