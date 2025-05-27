import Vue from 'vue'
import Router from 'vue-router'

import UploadImage from '@/components/UploadImage.vue'
import UploadVideo from '@/components/UploadVideo.vue'
import History from '@/components/History.vue'

Vue.use(Router)

export default new Router({
  routes: [
    { path: '/', redirect: '/upload-image' },
    { path: '/upload-image', component: UploadImage },
    { path: '/upload-video', component: UploadVideo },
    { path: '/history', component: History },
  ]
})
