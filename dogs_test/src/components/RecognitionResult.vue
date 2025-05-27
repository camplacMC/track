<template>
  <div class="recognition-result">
    <h3>识别结果</h3>
    <div v-for="item in pagedResult" :key="item.id" class="result-item">
      <p><strong>编号:</strong> {{ item.label }}</p>
      <p><strong>品种:</strong> {{ item.breed }}</p>
      <p><strong>置信度:</strong> {{ item.breed_confidence }}</p>
      <a :href="`https://baike.baidu.com/item/${item.breed}`" target="_blank">百度百科：{{ item.breed }}</a>
    </div>

    <!-- 分页器 -->
    <el-pagination
        small
        background
        layout="prev, pager, next"
        :total="result.length"
        :page-size="pageSize"
        :current-page.sync="currentPage"
        class="pagination"
    />
  </div>
</template>

<script>
export default {
  name: "RecognitionResult",
  props: {
    result: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      currentPage: 1,
      pageSize: 5, // 每页显示5条
    };
  },
  computed: {
    pagedResult() {
      const start = (this.currentPage - 1) * this.pageSize;
      return this.result.slice(start, start + this.pageSize);
    },
  },
  watch: {
    result() {
      this.currentPage = 1; // 当新结果到来时重置页码
    },
  },
};
</script>

<style scoped>
.recognition-result {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.result-item {
  background: #fff9ec;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  border: 1px solid #f3d9ac;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  font-size: 0.95rem;
}

.pagination {
  margin-top: 1rem;
  align-self: center;
}
</style>
