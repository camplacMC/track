<template>
  <div class="nav-bar">
    <router-link to="/upload-image">上传图片</router-link>
    <router-link to="/upload-video">上传视频</router-link>
    <router-link to="/history">历史对话</router-link>
  </div>
</template>

<style scoped>
.nav-bar {
  width: 220px;
  background-color: #fff5e6; /* 柔和奶油橙 */
  padding: 2rem;
  display: flex;
  flex-direction: column;
  border-right: 4px dashed #f3c17e;
  box-shadow: 4px 0 10px rgba(0, 0, 0, 0.05);
  border-radius: 0 1rem 1rem 0;
}

.nav-bar a {
  color: #4b3b2a;
  padding: 1rem;
  margin-bottom: 1rem;
  text-decoration: none;
  font-weight: bold;
  border-left: 4px solid transparent;
  border-radius: 8px;
  transition: all 0.2s;
  background-color: #fff8ee;
}

.nav-bar {
  background-color: #ffe9c9;
  border-left-color: #f3a952;
  color: #a05a00;
}

.nav-bar a:hover {
  background-color: #fff0db;
}
/* 全局通用动画和响应式样式 */
@media (max-width: 768px) {
  .nav-bar {
    width: 100%;
    flex-direction: row;
    overflow-x: auto;
    border-right: none;
    border-bottom: 4px dashed #f3c17e;
    border-radius: 0 0 1rem 1rem;
    justify-content: space-around;
  }
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

@keyframes ripple {
  to {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0;
  }
}

</style>
