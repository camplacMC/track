<template>
  <div>
    <div class="image-card" v-if="image">
      <h3>原图</h3>
      <div class="img-frame">
        <img :src="image" alt="原图" />
      </div>
    </div>

    <div class="image-card" v-if="imageWithBoundingBoxes">
      <h3>识别结果图</h3>
      <div class="img-frame">
        <img :src="imageWithBoundingBoxes" alt="识别图" />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ImagePreview',
  props: {
    image: String,
    imageWithBoundingBoxes: String
  }
};
</script>

<style scoped>
.preview-area {
  display: flex;
  gap: 2rem;
  justify-content: center;
  flex-wrap: wrap;
}

.image-card {
  background-color: #fff5e0;
  padding: 1rem;
  border-radius: 1rem;
  width: 320px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 2px dashed #f4c57a;
}

.img-frame {
  background-color: #fefaf2;
  padding: 0.5rem;
  border-radius: 0.75rem;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border: 1px solid #eedcb3;
}

.img-frame img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
</style>
