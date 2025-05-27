<template>
  <div class="app-wrapper">
    <header class="app-header">
      <h1>狗的品种识别</h1>
    </header>
    <div class="app-container">
      <NavBar />
      <div class="main-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue'

export default {
  name: 'App',
  components: { NavBar },
}
</script>

<style scoped>
.app-wrapper {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #fff9f2;
}

/* ⬇️ 精简后的标题栏 */
.app-header {
  width: 100%;
  background-color: #fff0db;
  padding: 0.6rem 1.2rem;
  text-align: center;
  border-bottom: 2px dashed #f3c17e;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  z-index: 2;
}

.app-header h1 {
  margin: 0;
  font-size: 1.25rem;
  color: #a05a00;
  font-weight: bold;
  text-shadow: 0.5px 0.5px #fff8e5;
}

/* 主体区域布局：侧边栏 + 内容 */
.app-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.main-content {
  flex: 1;
  padding: 2rem;
  background-color: #fffaf2;
  overflow-y: auto;
}
</style>
