<template>
  <div class="page-container">
    <h2 class="page-title">上传图片</h2>
    <div class="controls">
      <el-upload
          class="upload-btn"
          action="http://localhost:5000/api/upload"
          :show-file-list="false"
          :on-success="handleUploadSuccess"
          :before-upload="beforeUpload"
      >
        <el-button class="btn">选择图片</el-button>
      </el-upload>
      <el-button
          @click="handleRecognition"
          :disabled="!uploadedFile"
          class="btn"
          type="success"
      >
        识别图像
      </el-button>
    </div>

    <!-- 左右结构 -->
    <div class="result-container" v-if="image">
      <!-- 左边：垂直排列图像 -->
      <div class="left-images">
        <ImagePreview :image="image" :imageWithBoundingBoxes="imageWithBoundingBoxes" />
      </div>

      <!-- 右边：识别结果 -->
      <div class="right-results" v-if="result">
        <RecognitionResult :result="result" />
      </div>
    </div>
  </div>
</template>

<script>
import ImagePreview from "@/components/ImagePreview.vue";
import RecognitionResult from "@/components/RecognitionResult.vue";

export default {
  name: 'UploadImage',
  components: {
    ImagePreview,
    RecognitionResult
  },
  data() {
    return {
      image: null,
      imageWithBoundingBoxes: null,
      uploadedFile: null,
      result: null
    };
  },
  methods: {
    handleUploadSuccess(_, file) {
      this.image = URL.createObjectURL(file.raw || file);
      this.uploadedFile = file.raw || file;
    },
    beforeUpload(file) {
      const ok = file.type.startsWith('image/');
      if (!ok) this.$message.error('只能上传图片文件');
      return ok;
    },
    async handleRecognition() {
      if (!this.uploadedFile) {
        this.$message.error("请先上传图片");
        return;
      }

      const formData = new FormData();
      formData.append("file", this.uploadedFile);

      try {
        const response = await this.$axios.post("http://localhost:5000/api/recognize", formData);
        this.result = response.data.predictions;
        this.imageWithBoundingBoxes = `data:image/png;base64,${response.data.image}`;
        if (this.result.length === 0) {
          this.$message.error("没有检测到狗狗");
        } else {
          this.$message.success("识别成功");
        }
      } catch (error) {
        this.$message.error("识别失败，请重试！");
        console.error(error);
      }
    }
  }
};
</script>

<style scoped>

.result-container {
  display: flex;
  gap: 2rem;
  justify-content: flex-start;
  align-items: flex-start;
  margin-top: 2rem;
}

.left-images {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  flex-shrink: 0;
  align-self: flex-start;
  max-height: 600px; /* 图像区域最大高度限制 */
}

.right-results {
  flex: 1;
  min-width: 0;
  max-height: 600px;
  overflow-y: auto; /* 启用垂直滚动条 */
  padding-right: 0.5rem; /* 给滚动条留出一点空间 */
}

.page-container {
  background-color: #fffaf4;
  color: #3e3e3e;
  padding: 2rem;
  border-radius: 1rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  border: 3px dotted #f4d4a4;
}

.page-title {
  margin: 0;
  font-size: 1.6rem;
  font-weight: bold;
  color: #a05a00;
}

.controls {
  display: flex;
  gap: 1rem;
}

.btn {
  background-color: #ffe0b2;
  color: #663c00;
  border: none;
  border-radius: 1rem;
  padding: 0.6rem 1.5rem;
  font-weight: bold;
  box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
  transition: 0.3s;
}
.btn:hover {
  background-color: #ffd28a;
  transform: translateY(-2px);
}
.img-frame img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

/* 响应式 */
@media (max-width: 768px) {
  .controls {
    flex-direction: column !important;
    align-items: center;
  }
}

/* 动画 */
.page-container {
  animation: fadeIn 0.6s ease-in-out;
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

.btn {
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}
.btn:active {
  transform: scale(0.96);
}
.btn::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 120%;
  height: 120%;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  transform: translate(-50%, -50%) scale(0);
  animation: ripple 0.6s ease-out;
  pointer-events: none;
}
@keyframes ripple {
  to {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0;
  }
}
</style>
