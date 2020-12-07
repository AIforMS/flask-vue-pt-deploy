import Vue from 'vue'
import Router from 'vue-router'
import LandingPage from '@/components/LandingPage'
import Login from '@/components/Login'


Vue.use(Router)

const router =  new Router({
  routes: [
    {
      path: '/',
      name: 'LandingPage',
      component: LandingPage,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/login',
      name: 'Login',
      component: Login
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = window.localStorage.getItem('f-token')
  console.log('index.js:' + token)
  if (to.matched.some(record => record.meta.requiresAuth) && (!token || token === null)) {
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else if (token && to.name == 'Login') {
    // 用户已登录，但又去访问登录页面时不让他过去
    next({
      path: from.fullPath
    })
  }  else {
    next()
  }
})

export default router
