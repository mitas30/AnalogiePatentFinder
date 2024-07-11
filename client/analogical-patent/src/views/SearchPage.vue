<template>
  <v-container>
    <v-card class="w-75 mx-auto border-md">
      <v-row justify="start">
        <v-col cols="9" class="mt-4">
          <v-card-subtitle>あなたの解決したい問題を「(対象)の(パラメータ)を向上させたい」という形に変換して検索してください。</v-card-subtitle>
        </v-col>
      </v-row>
      <v-form>
        <v-row justify="center">
          <v-col cols="12">
            <v-text-field class="mt-4 w-75 mx-auto" v-model="problem.value" :counter="50" :rules="problem.rules"
              variant="underlined" label="対象" hint="パラメータを向上させたい対象を具体的に入力してください。 例)半導体モジュール、複合多孔質材料 など"></v-text-field>
          </v-col>
          <v-col cols="12">
            <v-autocomplete class="w-75 mx-auto" density="comfortable" :items="items" item-title="name" item-value="id"
              label="パラメータ(複数選択可能)" v-model="selected" multiple clearable variant="underlined">
            </v-autocomplete>
          </v-col>
        </v-row>
      </v-form>
      <v-row justify="center">
        <v-spacer></v-spacer>
        <v-col cols="4">
          <v-btn class="mb-3 border" :loading="load_flag" type="submit" @click="submit">検索</v-btn>
        </v-col>
      </v-row>
    </v-card>
  </v-container>
</template>

<script>
export default {
  //コンポーネントのリアクティブデータを定義する 関数の形
  //this.でアクセスしよう
  data() {
    return {
      items: [
        { id: "1,2", name: '重量を減らす' },
        { id: "3,4", name: '長さを短くする' },
        { id: "5,6", name: '面積を減らす' },
        { id: "7,8", name: '体積を減らす' },
        { id: "9", name: '速度を上げる' },
        { id: "10", name: '力を増やす' },
        { id: "11", name: '圧力を増やす' },
        { id: "12", name: '形状を改善する' },
        { id: "13", name: '安定性を高める' },
        { id: "14", name: '強度を高める' },
        { id: "15,16", name: '動作時間を延ばす' },
        { id: "17", name: '温度を管理する' },
        { id: "18", name: '照明の強度を上げる' },
        { id: "19,20", name: 'エネルギー使用効率を上げる' },
        { id: "21", name: '力率を上げる' },
        { id: "22", name: 'エネルギー損失を減らす' },
        { id: "23", name: '物質の損失を減らす' },
        { id: "24", name: '情報の損失を減らす' },
        { id: "25", name: '時間の損失を減らす' },
        { id: "26", name: '物質の量を減らす' },
        { id: "27", name: '信頼性を高める' },
        { id: "28", name: '測定精度を上げる' },
        { id: "29", name: '製造精度を上げる' },
        { id: "30", name: '外部の害を減らす' },
        { id: "31", name: '有害要因を減らす' },
        { id: "32", name: '製造の容易さを高める' },
        { id: "33", name: '操作の容易さを高める' },
        { id: "34", name: '修理の容易さを高める' },
        { id: "35", name: '適応性または多用途性を高める' },
        { id: "36", name: 'デバイスの複雑さを減らす' },
        { id: "37", name: '検出と測定の難しさを減らす' },
        { id: "38", name: '自動化の程度を上げる' },
        { id: "39", name: '生産性を上げる' }
      ],
      selected: [],
      load_flag:false,
      problem: {
        value: '',
        // JSでよく見る、アロー関数 (引数)=>{処理} rules:[list[function]]
        rules: [(value) => {
          if (value.length <= 50) return true
          return '50文字以内で入力してください'
        }],
        errorMessage: '',
        post: null,
      },
    };
  },
  methods: {
    submit() {
      this.load_flag = true;
      console.log("SearchPageからSearchResultsへ遷移。",
        "problem:", this.problem.value,
        "parameters:", JSON.stringify(this.selected)
      );
      // SPAによるページ遷移
      this.$router.push({
        path: '/results',
        query: {
          object: this.problem.value,
          parameters: JSON.stringify(this.selected)
        }
      });
    },
  },
};
</script>