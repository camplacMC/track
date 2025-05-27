<template>
  <div class="history-page">
    <h2>识别历史记录</h2>
    <div class="card-container" v-if="history.length">
      <div class="history-card" v-for="(item, index) in history" :key="index">
        <template v-if="item.is_video">
          <video :src="item.file_url" class="history-image" controls></video>
        </template>
        <template v-else>
          <img :src="item.file_url" class="history-image" @click="viewDetail(item)"/>
        </template>
        <div class="history-info">
          <p class="timestamp">识别时间：{{ formatTimestamp(item.timestamp) }}</p>

          <template v-if="!item.is_video">
            <ul class="prediction-list">
              <li v-for="(p, i) in item.predictions" :key="i">
                {{ p.breed }}（{{ (p.breed_confidence * 100).toFixed(1) }}%）
              </li>
            </ul>
          </template>

          <button class="delete-button" @click="deleteHistory(item)">删除记录</button>
        </div>

      </div>
    </div>
    <div v-else class="empty">暂无历史记录。</div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      history: []
    };
  },
  mounted() {
    this.loadHistory();
  },
  methods: {
    loadHistory() {
      this.$axios.get("http://localhost:5000/api/history")
          .then(res => {
            this.history = res.data.map(item => ({
              ...item,
              is_video: !!item.video_object
            }));
          })
          .catch(err => {
            console.error("获取历史失败：", err);
          });
    },
    formatTimestamp(compact) {
      if (!compact || compact.length !== 15 || compact[8] !== '_') return compact;
      const year = compact.slice(0, 4);
      const month = compact.slice(4, 6);
      const day = compact.slice(6, 8);
      const hour = compact.slice(9, 11);
      const minute = compact.slice(11, 13);
      const second = compact.slice(13, 15);
      return `${year}-${month}-${day}T${hour}:${minute}:${second}`;
    },
    deleteHistory(item) {
      const confirmed = window.confirm(`确定要删除 ${this.formatTimestamp(item.timestamp)} 的记录吗？`);
      if (!confirmed) return;

      const data = {
        json_name: `${(item.upload_object || item.video_object).split('.')[0]}_${item.timestamp}.json`,
      };
      if (item.is_video) {
        data.video_name = item.video_object;
      } else {
        data.image_name = item.upload_object;
      }

      this.$axios.delete("http://localhost:5000/api/history", {data})
          .then(() => {
            this.history = this.history.filter(h => h !== item);
          })
          .catch(err => {
            console.error("删除失败：", err);
            alert("删除失败，请稍后重试。");
          });
    },
    viewDetail(item) {
      window.open(item.file_url, '_blank');
    }
  }
};
</script>

<style scoped>
.history-page {
  padding: 2rem;
  background-color: #fffdf6;
  min-height: 100vh;
  animation: fadeIn 0.6s ease-out;
}

h2 {
  margin-bottom: 1.5rem;
  color: #a05a00;
}

.card-container {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.history-card {
  width: 280px;
  background-color: #fff8ee;
  border: 2px solid #f7d199;
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s;
}

.history-card:hover {
  transform: translateY(-4px);
}

.history-image {
  width: 100%;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  cursor: pointer;
}

.history-info {
  font-size: 0.95rem;
  color: #4b3b2a;
}

.timestamp {
  font-style: italic;
  margin-bottom: 0.5rem;
}

.prediction-list {
  list-style: none;
  padding-left: 0;
}

.delete-button {
  margin-top: 0.5rem;
  background-color: #ff4f4f;
  border: none;
  padding: 6px 12px;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.delete-button:hover {
  background-color: #e04444;
}

.empty {
  color: #888;
  font-style: italic;
}

@keyframes fadeIn {
  0% {
    opacity: 0;
    transform: translateY(16px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
