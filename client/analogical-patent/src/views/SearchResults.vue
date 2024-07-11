<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="8">
        <v-alert v-if="alert_is_visible" :type="'error'" class="mt-4" title="検索エラー">
          {{ alert_text }}
        </v-alert>
      </v-col>
    </v-row>
    <v-row v-if="!alert_is_visible">
      <v-col :cols="selected_patent ? 4 : 12">
        <v-container>
          <v-row>
            <v-col v-for="result in results" :key="result.id" @click="selectResult(result)" cols="12">
              <v-card :title="result.invent_name" :text="result.heading" variant="outlined">
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </v-col>
      <v-divider v-if="selected_patent" vertical />
      <v-col v-if="selected_patent" cols="8">
        <RightPane :selectedResult="selected_patent" @deselect="deselectResult" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios';
import RightPane from '@/components/DetailPane.vue';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faArrowRight } from '@fortawesome/free-solid-svg-icons';

library.add(faArrowRight);

// export default{} で、objectを定義しているらしい
// objectは、オブジェクトリテラルという書き方。
export default {
  components: {
    RightPane
  },
  data() {
    return {
      results: [],
      alert_text: '検索時にエラーが発生しました。もう一度お試しください。',
      alert_is_visible: false,
      selected_patent: null,
    };
  },
  // vmは、toのインスタンスを指す。next関数の中で使用すること。
  //async関数では、基本的にtry-catch文を使うほうが良い(awaitのエラーをキャッチして、関数の実行を停止させない)
  //現在なら、async-await文を使おう 呼び出すasync関数は、その中が同期処理になっていることが大切
  //beforeRouteEnterは、フック関数の一つ。
  async beforeRouteEnter(to, from, next) {
    const problem = to.query.object;
    const parameters = JSON.parse(to.query.parameters);
    console.log("Problem:", problem, "\nSelected:", parameters);
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/search', {
      params: 
      { problem:problem, 
        selected:JSON.stringify(parameters) }
    })
      //next(function)の形式
      next((vm) => {
        vm.results = response.data;
        console.log(vm.results);
      });
    } catch (error) {
      next((vm) => {
        console.error(error);
        vm.alert_is_visible = true;
      })
    }
  },
  methods: {
    selectResult(result) {
      this.selected_patent = result;
    },
    deselectResult() {
      this.selected_patent = null;
    }
  },
};
</script>
