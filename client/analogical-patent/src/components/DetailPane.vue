<template>
  <v-container>
    <v-row justify="start">
      <v-col cols="2">
        <v-btn class="ma-2" color="primary" @click="$emit('deselect')">
          <v-icon>
            mdi-arrow-right-bold-outline
          </v-icon>
          閉じる
        </v-btn>
      </v-col>
      <v-spacer></v-spacer>
      <v-col cols="3">
        <v-btn variant="outlined" @click="redirectFullPatent">
          <v-icon start> mdi-script-text-outline</v-icon>
          特許の完全な情報を見る
        </v-btn>
      </v-col>
    </v-row>
    <v-sheet class="ma-2 pa-2">
      <h2 class="text-black">{{ selectedResult.heading }}</h2>
    </v-sheet>
    <v-row justify="center">
      <v-card class="text-left w-100 ma-2 pa-5">
        <v-card-title>基本情報</v-card-title>
        <v-card-text>
          <v-row justify="start">
            <v-col cols="2">
              <p>出願番号</p>
            </v-col>
            <v-col cols="9">
              <p> {{ selectedResult.apply_number }}</p>
            </v-col>
            <v-spacer> </v-spacer>
          </v-row>
          <v-row justify="start">
            <v-col cols="2">
              <p>発明の名称 </p>
            </v-col>
            <v-col cols="9">
              <p> {{ selectedResult.invent_name }}</p>
            </v-col>
            <v-spacer> </v-spacer>
          </v-row>
          <v-row justify="start">
            <v-col cols="2">
              <p>抽象化された解決策 </p>
            </v-col>
            <v-col cols="9">
              <p>{{ this.abstractSolution }}</p>
              <v-spacer></v-spacer>
            </v-col>
          </v-row>
          <v-row justify="start">
            <v-col cols="2">
              <p>専門用語付きの解決策 </p>
            </v-col>
            <v-col cols="9">
              <p>{{ this.solution }}</p>
              <v-spacer></v-spacer>
            </v-col>
          </v-row>
          <v-row justify="start">
            <v-col cols="2">
              <p>解決する問題 </p>
            </v-col>
            <v-col cols="9">
              <p>{{ selectedResult.problem }}</p>
            </v-col>
            <v-spacer> </v-spacer>
          </v-row>
          <v-row justify="start">
            <v-col cols="2">
              <p>解決策 </p>
            </v-col>
            <v-col cols="9">
              <p>{{ selectedResult.solve_way }}</p>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-row>

    <v-row justify="center" v-if="selectedResult && !this.is_explain">
      <v-col cols="8">
        <v-btn class="ma-2" @click="makeExplain" :loading="loading">
          <v-icon>mdi-button-cursor</v-icon>
          工夫の詳しい解説を作成する
        </v-btn>
      </v-col>
    </v-row>

    <v-row justify="center" v-if="selectedResult && this.is_explain">
      <v-col cols="12">
        <v-sheet class="ma-2 pa-2 text-left">
          <h3>導入</h3>
          <p> {{ this.intro }}</p><br>
          <h3>戦略</h3>
          <p> {{ this.strategy }}</p><br>
          <h3>応用</h3>
          <p> {{ this.application }}</p>
        </v-sheet>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      is_explain: false,
      intro: "",
      strategy: "",
      application: "",
      loading: false,
      abstractSolution:this.selectedResult.abstractSolution,
      solution:this.selectedResult.solution,
    }
  },
  created() {
    //すでに解説が作成されている特許の場合は、解説を取得する
    this.fetchExplanation();
  },
  props: {
    selectedResult: {
      type: Object,
      required: true
    },
  },
  watch: {
    async selectedResult() {
      this.is_explain = false;
      this.intro = "";
      this.strategy = "";
      this.application = "";
      //ついでに、すでに解説が作成されている特許の場合は、解説を取得する
      await this.fetchExplanation();
    }
  },
  methods: {
    async fetchExplanation() {
      console.log("説明の取得を試みている")
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/fetch_exist_explanation',
          {
            params: {
              apply_number: this.selectedResult.apply_number,
              parameter: this.selectedResult.parameter,
            }
          });
        if (response.data.is_exist==true){
          console.log("解説が存在したので、更新")
          this.is_explain = true;
          this.intro = response.data.intro;
          this.strategy = response.data.strategy;
          this.application = response.data.application;
        }
      } catch (error) {
        console.error(error);
      }
    },
    async redirectFullPatent() {
      if (this.selectedResult.full_url) {
        window.location.href = this.selectedResult.full_url;
      }
      try {
        //axios.postは、json形式でデータを送信する
        const response = await axios.post('http://127.0.0.1:5000/api/redirect_full_patent',
          {
            apply_number: this.selectedResult.apply_number
          });
        const redirect_url = response.data.url;
        window.location.href = redirect_url;
      }
      catch (error) {
        console.error(error);
      }
    },
    // 各特許についての解説を作成する
    async makeExplain() {
      this.loading=true;
      try {
        console.log(this.selectedResult)
        const response = await axios.post('http://127.0.0.1:5000/api/make_explain',
          {
            apply_number: this.selectedResult.apply_number,
            heading: this.selectedResult.solution,
            param_exp: this.selectedResult.parameter_attribute,
            parameter: this.selectedResult.parameter,
            key_id: this.selectedResult._id,
            target_object: this.selectedResult.object,
          });
        const data = response.data;
        console.log(data);
        //TODO 上のコンポーネントのデータも更新すること
        if(data.is_heading_improved==true){
          this.abstractSolution = data.abstractSolution;
          this.solution = data.solution;
        }
        this.is_explain = true;
        this.intro = data.intro;
        this.strategy = data.strategy;
        this.application = data.application;
      }
      catch (error) {
        console.error(error);
        this.loading=false;
      }
      this.loading=false;
    }
  },
}
</script>