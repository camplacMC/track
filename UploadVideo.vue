<template>
  <div class="page-container">
    <h2 class="page-title">上传视频</h2>
    <div class="controls">
      <el-upload
          action="http://localhost:5000/api/upload_video"
          :show-file-list="false"
          :on-success="handleUploadSuccess"
          :before-upload="beforeUpload"
      >
        <el-button class="btn">选择视频</el-button>
      </el-upload>

      <el-button
          class="btn"
          :disabled="!uploadedFile || isLoading"
          @click="handleRecognition"
      >{{ isLoading ? '识别中...' : '识别视频' }}</el-button>
    </div>  

    <!-- 🔄 加载动画 -->
    <div v-if="isLoading" class="loading-box">
      <div class="spinner"></div>
      正在识别视频，请稍候...
    </div>

    <div class="preview-area" v-if="video || recognizedVideo">
      <div v-if="video">
        <h3>原始视频</h3>
        <video :src="video" controls class="video-player"></video>
      </div>

      <div v-if="recognizedVideo">
        <h3>识别后视频</h3>
        <video :src="recognizedVideo" controls class="video-player"></video>
      </div>

      <div class="result-list" v-if="result">
        <h3>识别结果</h3>
        <div v-for="(item, i) in result" :key="i" class="result-box">
          <p><strong>编号:</strong> {{ item.label }}</p>
          <p><strong>品种:</strong> {{ item.breed }}</p>
          <p><strong>置信度:</strong> {{ item.breed_confidence }}</p>
          <a :href="`https://baike.baidu.com/item/${item.breed}`" target="_blank">更多信息</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UploadVideo',
  data() {
    return {
      video: null,
      recognizedVideo: null,
      uploadedFile: null,
      videoPath: null,
      result: null,
      isLoading: false // 🔄 新增加载状态
    };
  },
  methods: {
    handleUploadSuccess(res, file) {
      this.videoPath = res.file_path;
      this.uploadedFile = file.raw;
      this.video = URL.createObjectURL(this.uploadedFile);
      this.recognizedVideo = null;
      this.result = null;
    },
    beforeUpload(file) {
      const ok = file.type.startsWith('video/');
      if (!ok) this.$message.error('只能上传视频文件');
      return ok;
    },
    async handleRecognition() {
      if (!this.videoPath) return;
      this.isLoading = true; // 🔄 开始加载
      try {
        const res = await fetch('http://localhost:5000/api/recognize_video', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ file_path: this.videoPath })
        });
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);

        this.recognizedVideo = url;
        this.$message.success('识别完成');
      } catch (err) {
        this.$message.error('识别失败');
        console.error('识别出错:', err);
      } finally {
        this.isLoading = false; // 🔄 停止加载
      }
    }
  }
};
</script>

<style scoped>
.page-container {
  background-color: #fffdf8;
  color: #4d4030;
  padding: 2rem;
  border-radius: 1rem;
  border: 2px dashed #f6c78e;
}

.page-title {
  font-size: 1.6rem;
  font-weight: bold;
  color: #a05a00;
}

.controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.btn {
  background-color: #ffe4b5;
  border: none;
  border-radius: 1rem;
  padding: 0.7rem 1.4rem;
  font-weight: bold;
  color: #7a4b00;
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
}

.btn:hover {
  background-color: #ffd794;
  transform: translateY(-2px);
}

/* 🔄 加载动画样式 */
.loading-box {
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  font-weight: bold;
  color: #d17b00;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid #f7c98e;
  border-top: 3px solid #f09300;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.video-player {
  width: 100%;
  max-width: 480px;
  border-radius: 1rem;
  border: 2px solid #eedcb3;
  margin-bottom: 1rem;
}

.result-list {
  background-color: #fff8ed;
  border-radius: 1rem;
  padding: 1rem;
  border: 1px dashed #f0c789;
}

.result-box {
  background-color: #fff0dc;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 0.75rem;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

/* 响应式和动画保留 */
@media (max-width: 768px) {
  .controls {
    flex-direction: column;
    align-items: center;
  }
  .video-player {
    width: 90% !important;
  }
}

.page-container {
  animation: fadeIn 0.6s ease-in-out;
}
@keyframes fadeIn {
  0% { opacity: 0; transform: translateY(16px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>
